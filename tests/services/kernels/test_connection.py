import asyncio
import json
from unittest.mock import MagicMock

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
