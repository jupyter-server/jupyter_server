import asyncio
import json
from unittest.mock import MagicMock

from jupyter_client.jsonutil import json_clean, json_default
from jupyter_client.session import Session
from tornado.httpserver import HTTPRequest

from jupyter_server.serverapp import ServerApp
from jupyter_server.services.kernels.connection.channels import ZMQChannelsWebsocketConnection
from jupyter_server.services.kernels.websocket import KernelWebsocketHandler


async def test_websocket_connection(jp_serverapp):
    app: ServerApp = jp_serverapp
    kernel_id = await app.kernel_manager.start_kernel()
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
