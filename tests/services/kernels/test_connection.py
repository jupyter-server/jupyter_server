import asyncio
import gc
import json
import os
import sys
from unittest.mock import MagicMock, patch

import pytest
from jupyter_client.jsonutil import json_clean, json_default
from jupyter_client.session import Session
from tornado.httpserver import HTTPRequest
from zmq.eventloop.zmqstream import ZMQStream

from jupyter_server.serverapp import ServerApp
from jupyter_server.services.kernels.connection.channels import ZMQChannelsWebsocketConnection
from jupyter_server.services.kernels.websocket import KernelWebsocketHandler


async def test_websocket_connection(jp_serverapp: ServerApp) -> None:
    app = jp_serverapp
    kernel_id = await app.kernel_manager.start_kernel()  # type:ignore[has-type]
    kernel = app.kernel_manager.get_kernel(kernel_id)
    request = HTTPRequest("foo", "GET")
    request.connection = MagicMock()
    handler = KernelWebsocketHandler(app.web_app, request)
    handler.ws_connection = MagicMock()
    handler.ws_connection.is_closing = lambda: False
    conn = ZMQChannelsWebsocketConnection(parent=kernel, websocket_handler=handler)
    handler.connection = conn
    await conn.prepare()
    conn.connect()
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
    request = HTTPRequest("foo", "GET")
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
