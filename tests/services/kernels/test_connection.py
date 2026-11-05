import asyncio
import gc
import json
import os
import sys
from unittest.mock import MagicMock, patch

import pytest
from jupyter_client.jsonutil import json_clean, json_default
from jupyter_client.session import Session
from zmq.eventloop.zmqstream import ZMQStream

from jupyter_server.serverapp import ServerApp
from jupyter_server.services.kernels.connection.channels import ZMQChannelsWebsocketConnection
from jupyter_server.services.kernels.websocket import KernelWebsocketHandler
from tests.utils import http_request


async def test_websocket_connection(jp_serverapp: ServerApp) -> None:
    app = jp_serverapp
    kernel_id = await app.kernel_manager.start_kernel()  # type:ignore[has-type]
    kernel = app.kernel_manager.get_kernel(kernel_id)
    request = http_request("foo", "GET")
    request.connection = MagicMock()
    handler = KernelWebsocketHandler(app.web_app, request)
    handler.ws_connection = MagicMock()
    handler.ws_connection.is_closing = lambda: False
    conn = ZMQChannelsWebsocketConnection(parent=kernel, websocket_handler=handler)
    handler.connection = conn
    await conn.prepare()
    await conn.connect()
    await asyncio.wrap_future(conn.nudge())
    session: Session = kernel.session
    msg = session.msg("data_pub", content={"a": "b"})
    data = json.dumps(
        json_clean(msg),
        default=json_default,
        ensure_ascii=False,
        allow_nan=False,
    )
    conn.handle_incoming_message(data)
    conn.handle_outgoing_message("iopub", session.serialize(msg))
    assert (
        conn.websocket_handler.select_subprotocol(["v1.kernel.websocket.jupyter.org"])
        == "v1.kernel.websocket.jupyter.org"
    )
    conn.write_stderr("test", {})
    conn.on_kernel_restarted()
    conn.on_restart_failed()
    conn._on_error("shell", msg, session.serialize(msg))


def _make_connection(app, kernel, session_id=None, timeout=0.01):
    """Build a ZMQChannelsWebsocketConnection with a mocked handler."""
    request = http_request("foo", "GET")
    request.connection = MagicMock()
    handler = KernelWebsocketHandler(app.web_app, request)
    handler.ws_connection = MagicMock()
    handler.ws_connection.is_closing = lambda: False
    conn = ZMQChannelsWebsocketConnection(parent=kernel, websocket_handler=handler)
    handler.connection = conn
    if session_id:
        conn.session.session = session_id
    conn.kernel_info_timeout = timeout
    return conn


@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
async def test_nudge_cleanup_closes_transient_channels_when_iopub_closed(
    jp_serverapp: ServerApp,
) -> None:
    """If iopub is closed before nudge's cleanup callback fires (websocket
    teardown race), cleanup must still close the transient shell/control
    sockets it owns. Previously iopub.stop_on_recv() raised OSError inside
    the done-callback and aborted cleanup, leaving shell+control open."""
    app = jp_serverapp
    km = app.kernel_manager
    kernel_id = await km.start_kernel()
    kernel = km.get_kernel(kernel_id)
    await asyncio.sleep(1)

    conn = _make_connection(app, kernel)
    await conn.prepare()
    conn.create_stream()
    conn.kernel_info_timeout = 0.1

    # Track transient ZMQStreams created by nudge() from this point forward.
    created: list = []
    orig_init = ZMQStream.__init__

    def tracking_init(self, *args, **kwargs):
        orig_init(self, *args, **kwargs)
        created.append(self)

    ZMQStream.__init__ = tracking_init  # type: ignore[method-assign]
    try:
        # nudge() synchronously registers on_recv callbacks on iopub, then
        # returns. Close iopub immediately after so that when the cleanup
        # done-callback eventually fires, iopub is already closed and
        # iopub.stop_on_recv() hits the OSError path.
        f = conn.nudge()
        conn.channels["iopub"].close()
        try:
            await asyncio.wait_for(asyncio.wrap_future(f), timeout=2.0)
        except Exception:
            pass
        await asyncio.sleep(0.2)
    finally:
        ZMQStream.__init__ = orig_init  # type: ignore[method-assign]

    still_open = [s for s in created if not s.closed()]
    assert not still_open, (
        f"nudge leaked {len(still_open)} transient ZMQStream(s) when iopub "
        f"was closed before cleanup fired"
    )


@pytest.mark.skipif(sys.platform != "linux", reason="Requires /proc/self/fd")
@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
async def test_no_fd_leak_on_buffer_restore_with_port_change(jp_serverapp: ServerApp) -> None:
    """Verify that stale buffered channels are closed when ports change on reconnect."""
    app = jp_serverapp
    km = app.kernel_manager
    kernel_id = await km.start_kernel()
    kernel = km.get_kernel(kernel_id)
    await asyncio.sleep(1)

    session_id = "fixed-session-for-test"

    # Warm up
    conn = _make_connection(app, kernel, session_id=session_id)
    conn.create_stream()
    try:
        await conn.nudge()
    except Exception:
        pass
    for s in conn.channels.values():
        if not s.closed():
            s.close()
    gc.collect()
    await asyncio.sleep(1)

    baseline_fds = len(os.listdir(f"/proc/{os.getpid()}/fd"))

    for _ in range(100):
        conn1 = _make_connection(app, kernel, session_id=session_id)
        conn1.create_stream()
        try:
            await conn1.nudge()
        except Exception:
            pass
        km._kernel_connections.setdefault(kernel_id, 0)
        km._kernel_connections[kernel_id] = 0
        km.start_buffering(kernel_id, conn1.session_key, conn1.channels)

        conn2 = _make_connection(app, kernel, session_id=session_id)
        km._kernel_connections[kernel_id] = 1
        with patch.object(km, "ports_changed", return_value=True):
            connected = conn2.connect()
        if connected:
            try:
                await connected
            except Exception:
                pass
        for s in conn2.channels.values():
            if not s.closed():
                s.close()
        conn2.channels = {}

    gc.collect()
    await asyncio.sleep(2)
    gc.collect()
    final_fds = len(os.listdir(f"/proc/{os.getpid()}/fd"))
    assert final_fds - baseline_fds <= 5, (
        f"FD leak detected: {final_fds - baseline_fds} FDs leaked "
        f"after 100 buffer-restore-with-port-change cycles"
    )


@pytest.mark.skipif(sys.platform != "linux", reason="Requires /proc/self/fd")
@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
async def test_no_fd_leak_on_disconnect_with_orphaned_kernel_info_channel(
    jp_serverapp: ServerApp,
) -> None:
    """When a kernel does not reply to kernel_info_request (e.g. rogue/hung),
    kernel_info_channel is left open after nudge. It must be closed on
    disconnect, including the single-tab last-connection path that triggers
    start_buffering."""
    app = jp_serverapp
    km = app.kernel_manager
    kernel_id = await km.start_kernel()
    kernel = km.get_kernel(kernel_id)
    await asyncio.sleep(1)

    # Warm up
    conn = _make_connection(app, kernel)
    conn.create_stream()
    conn.kernel_info_channel = km.connect_shell(kernel_id)
    ZMQChannelsWebsocketConnection._open_sockets.add(conn)
    km._kernel_connections[kernel_id] = 1
    conn.disconnect()
    gc.collect()
    await asyncio.sleep(1)

    baseline_fds = len(os.listdir(f"/proc/{os.getpid()}/fd"))

    for _ in range(100):
        conn = _make_connection(app, kernel)
        conn.create_stream()
        # Simulate rogue kernel: kernel_info_channel opened but reply never arrives
        conn.kernel_info_channel = km.connect_shell(kernel_id)
        ZMQChannelsWebsocketConnection._open_sockets.add(conn)
        # Natural single-tab flow: last connection disconnects -> start_buffering
        km._kernel_connections[kernel_id] = 1
        conn.disconnect()

    gc.collect()
    await asyncio.sleep(2)
    gc.collect()
    final_fds = len(os.listdir(f"/proc/{os.getpid()}/fd"))
    assert final_fds - baseline_fds <= 5, (
        f"FD leak detected: {final_fds - baseline_fds} FDs leaked after 100 "
        f"disconnects with orphaned kernel_info_channel"
    )


@pytest.mark.skipif(sys.platform == "win32", reason="Times out on Windows")
async def test_disconnect_resolves_orphaned_kernel_info_future(jp_serverapp: ServerApp) -> None:
    """Disconnecting with an orphaned kernel_info channel should not leave
    kernel_manager._kernel_info_future pending, which would block reconnects
    waiting for a never-arriving kernel_info reply."""
    app = jp_serverapp
    km = app.kernel_manager
    kernel_id = await km.start_kernel()
    kernel = km.get_kernel(kernel_id)

    conn1 = _make_connection(app, kernel, timeout=5.0)
    conn1.create_stream()
    conn1.session.key = kernel.session.key
    conn1.session_key = f"{kernel_id}:{conn1.session.session}"

    # Simulate an in-flight kernel_info request that never gets a reply.
    conn1.kernel_info_channel = km.connect_shell(kernel_id)
    km._kernel_info_future = conn1._kernel_info_future

    # Force the buffering early-return path in disconnect().
    # disconnect() first decrements the connection count via
    # notify_disconnect(), so start at 1 to reach the == 0 branch.
    km._kernel_connections[kernel_id] = 1
    ZMQChannelsWebsocketConnection._open_sockets.add(conn1)
    conn1.disconnect()

    # Regression check: pending shared future must be resolved by disconnect.
    assert conn1._kernel_info_future.done()

    # A new connection should not block waiting on the stale pending future.
    conn2 = _make_connection(app, kernel, timeout=0.2)
    conn2.create_stream()
    conn2.session.key = kernel.session.key
    conn2.kernel_info_timeout = 0.2
    await asyncio.wait_for(asyncio.wrap_future(conn2.request_kernel_info()), timeout=1.0)


async def _recv_ws_until(ws, want_msg_type, channel, timeout=15.0):
    """Read ws messages until (want_msg_type on channel) or timeout."""
    from jupyter_server.services.kernels.connection.base import (
        deserialize_msg_from_ws_v1,
    )

    loop = asyncio.get_event_loop()
    deadline = loop.time() + timeout
    while loop.time() < deadline:
        try:
            raw = await asyncio.wait_for(
                ws.read_message(), timeout=max(0.1, deadline - loop.time())
            )
        except asyncio.TimeoutError:
            return None
        if raw is None:
            return None
        channel_name, msg_list = deserialize_msg_from_ws_v1(raw)
        if channel_name == channel:
            header = json.loads(msg_list[0])
            if header.get("msg_type") == want_msg_type:
                return msg_list
    return None


async def _ws_connect_v1(jp_http_port, jp_base_url, jp_auth_header, *parts, params=None):
    """Open a kernel websocket with the v1 subprotocol.

    pytest-jupyter 0.7 (the minimum supported version) drops the
    ``subprotocols`` kwarg instead of forwarding it, so call
    ``tornado.websocket.websocket_connect`` directly; this works with
    every supported tornado/pytest-jupyter combination.
    """
    import urllib.parse

    import tornado.httpclient
    import tornado.websocket
    from tornado.escape import url_escape

    from jupyter_server.utils import url_path_join

    path_url = url_escape(url_path_join(*parts), plus=False)
    base_path_url = url_path_join(jp_base_url, path_url)
    urlparts = urllib.parse.urlparse(f"ws://localhost:{jp_http_port}")
    urlparts = urlparts._replace(path=base_path_url, query=urllib.parse.urlencode(params or {}))
    req = tornado.httpclient.HTTPRequest(
        urlparts.geturl(), headers=dict(jp_auth_header), connect_timeout=120
    )
    return await tornado.websocket.websocket_connect(
        req, subprotocols=["v1.kernel.websocket.jupyter.org"]
    )


async def test_replaced_stale_connection_does_not_steal_replies(
    jp_fetch, jp_http_port, jp_base_url, jp_auth_header, monkeypatch
):
    """Regression test for
    https://github.com/jupyter-server/jupyter_server/issues/1719

    Reconnecting with the same session_id while the previous websocket is
    still in open(), followed by a kernel restart, must not starve the new
    websocket of shell replies: the stale connection's ZMQ sockets share the
    same session identity and would otherwise steal the kernel's ROUTER
    entry when its stalled connect() eventually runs.
    """
    from jupyter_server.services.kernels.connection.base import (
        serialize_msg_to_ws_v1,
    )

    session_id = "stale-session-1719"
    r = await jp_fetch("api", "kernels", method="POST", body=json.dumps({"name": "python3"}))
    kid = json.loads(r.body.decode())["id"]

    # Gate the FIRST connection's connect(): simulates the server still being
    # in open() (e.g. kernel holding the GIL, no kernel_info reply yet).
    gate = asyncio.Event()
    a_connect_entered = asyncio.Event()
    a_connect_done = asyncio.Event()
    b_connect_futures: list = []
    orig_connect = ZMQChannelsWebsocketConnection.connect
    calls = {"n": 0}

    def gated_connect(self):
        calls["n"] += 1
        if calls["n"] == 1:
            a_connect_entered.set()

            async def wait_then_connect():
                await gate.wait()
                # match open() semantics: it awaits the future connect() returns
                fut = orig_connect(self)
                if fut is not None:
                    await asyncio.wrap_future(fut)
                return fut

            task = asyncio.ensure_future(wait_then_connect())
            task.add_done_callback(lambda _t: a_connect_done.set())
            return task
        fut = orig_connect(self)
        b_connect_futures.append(fut)
        return fut

    monkeypatch.setattr(ZMQChannelsWebsocketConnection, "connect", gated_connect)

    ws_b = None
    task_a = asyncio.ensure_future(
        _ws_connect_v1(
            jp_http_port,
            jp_base_url,
            jp_auth_header,
            "api",
            "kernels",
            kid,
            "channels",
            params={"session_id": session_id},
        )
    )
    try:
        # A's connect() was entered (so its handler/session is registered)
        # and is now stalled inside open().
        await asyncio.wait_for(a_connect_entered.wait(), timeout=5)

        # Client reloads: ws B with the SAME session_id replaces A.
        ws_b = await _ws_connect_v1(
            jp_http_port,
            jp_base_url,
            jp_auth_header,
            "api",
            "kernels",
            kid,
            "channels",
            params={"session_id": session_id},
        )
        # Wait until B's connection finished nudging (its open() completed).
        deadline = asyncio.get_event_loop().time() + 15
        while not b_connect_futures:
            assert asyncio.get_event_loop().time() < deadline, "B never connected"
            await asyncio.sleep(0.05)
        if b_connect_futures[0] is not None:
            await asyncio.wait_for(asyncio.wrap_future(b_connect_futures[0]), timeout=15)

        # Restart the kernel (same ports).
        r = await jp_fetch("api", "kernels", kid, "restart", method="POST", body=b"")
        assert r.code == 200
        # Wait until the restarted kernel reports idle via the REST API.
        deadline = asyncio.get_event_loop().time() + 30
        while True:
            kr = await jp_fetch("api", "kernels", kid, method="GET")
            if json.loads(kr.body.decode()).get("execution_state") == "idle":
                break
            assert asyncio.get_event_loop().time() < deadline, (
                "kernel did not become idle after restart"
            )
            await asyncio.sleep(0.2)

        # Release A's stalled connect() and wait for it to run its course.
        gate.set()
        await asyncio.wait_for(a_connect_done.wait(), timeout=15)

        # B must still get shell replies.
        session = Session()
        msg = session.msg("kernel_info_request")
        await ws_b.write_message(serialize_msg_to_ws_v1(msg, "shell", session.pack), binary=True)
        reply = await _recv_ws_until(ws_b, "kernel_info_reply", "shell", timeout=15)
        assert reply is not None, (
            "new websocket received no kernel_info_reply after same-session "
            "reconnect + kernel restart (#1719)"
        )
    finally:
        if ws_b is not None:
            ws_b.close()
        if task_a.done() and not task_a.cancelled():
            if task_a.exception() is None:
                # close the replaced websocket's client side cleanly so it is
                # not left for GC (__del__ raises otherwise)
                task_a.result().close()
        else:
            task_a.cancel()
            # consume the cancelled task so its outcome is never hidden
            try:
                await task_a
            except (asyncio.CancelledError, Exception):
                pass
        try:
            await jp_fetch("api", "kernels", kid, method="DELETE")
        except Exception:
            pass


def _make_kernel_ws_connection(jp_serverapp, kernel_id):
    kernel = jp_serverapp.kernel_manager.get_kernel(kernel_id)
    request = http_request("foo", "GET")
    request.connection = MagicMock()
    handler = KernelWebsocketHandler(jp_serverapp.web_app, request)
    handler.ws_connection = MagicMock()
    handler.ws_connection.is_closing = lambda: False
    conn = ZMQChannelsWebsocketConnection(parent=kernel, websocket_handler=handler)
    handler.connection = conn
    return conn


async def test_disconnect_before_connect_keeps_counter_balanced(jp_serverapp):
    """disconnect() before connect() must not decrement another connection's
    count, and the later stalled connect() must abort without channels."""
    mkm = jp_serverapp.kernel_manager
    kernel_id = await mkm.start_kernel()
    try:
        conn = _make_kernel_ws_connection(jp_serverapp, kernel_id)
        await conn.prepare()

        live = _make_kernel_ws_connection(jp_serverapp, kernel_id)
        await live.prepare()
        await live.connect()
        assert mkm._kernel_connections[kernel_id] == 1

        # conn is closed (stale-session replacement) BEFORE its connect() ran.
        conn.disconnect()
        assert mkm._kernel_connections[kernel_id] == 1
        assert mkm.get_buffer(kernel_id, conn.session_key) is None

        result = conn.connect()
        assert result is not None
        await asyncio.wrap_future(result)
        assert conn.channels == {}
        assert mkm._kernel_connections[kernel_id] == 1

        live.disconnect()
        assert mkm._kernel_connections[kernel_id] == 0
    finally:
        await mkm.shutdown_kernel(kernel_id, now=True)


async def test_double_disconnect_decrements_once(jp_serverapp):
    """disconnect() is idempotent: the counter is decremented exactly once."""
    mkm = jp_serverapp.kernel_manager
    kernel_id = await mkm.start_kernel()
    try:
        conn = _make_kernel_ws_connection(jp_serverapp, kernel_id)
        await conn.prepare()
        await conn.connect()
        assert mkm._kernel_connections[kernel_id] == 1
        conn.disconnect()
        assert mkm._kernel_connections[kernel_id] == 0
        conn.disconnect()  # e.g. websocket close after stale replacement: no-op
        assert mkm._kernel_connections[kernel_id] == 0
        assert conn._close_future.done()
    finally:
        await mkm.shutdown_kernel(kernel_id, now=True)


async def test_early_disconnect_does_not_poison_replacement_buffer(jp_serverapp):
    """A stale connection disconnected before its connect() ran must not
    store a session buffer of empty channels that the replacement connection
    would restore."""
    mkm = jp_serverapp.kernel_manager
    kernel_id = await mkm.start_kernel()
    try:
        first = _make_kernel_ws_connection(jp_serverapp, kernel_id)
        await first.prepare()
        await first.connect()
        first.disconnect()
        assert mkm._kernel_connections[kernel_id] == 0
        mkm.stop_buffering(kernel_id)

        stale = _make_kernel_ws_connection(jp_serverapp, kernel_id)
        stale.session.session = "same-session"
        await stale.prepare()
        stale.disconnect()  # replaced while stalled in open()
        assert mkm.get_buffer(kernel_id, stale.session_key) is None

        repl = _make_kernel_ws_connection(jp_serverapp, kernel_id)
        repl.session.session = "same-session"
        await repl.prepare()
        await repl.connect()
        assert set(repl.channels) >= {"shell", "iopub", "control", "stdin"}
        repl.disconnect()
    finally:
        await mkm.shutdown_kernel(kernel_id, now=True)
