"""Sessions made by the server copy ``transport_encrypted`` from the kernel manager.

A kernel that uses CurveZMQ may send unsigned messages. The server's own
Sessions must then skip the HMAC check, like the kernel manager's Session does.
"""

from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from jupyter_client import protocol_version as client_protocol_version  # type:ignore[attr-defined]
from jupyter_client.session import Session
from tornado.httpserver import HTTPRequest

from jupyter_server._tz import utcnow
from jupyter_server.services.kernels import kernelmanager
from jupyter_server.services.kernels.connection.base import _copy_transport_encrypted
from jupyter_server.services.kernels.connection.channels import ZMQChannelsWebsocketConnection
from jupyter_server.services.kernels.websocket import KernelWebsocketHandler

requires_transport_encrypted = pytest.mark.skipif(
    not Session().has_trait("transport_encrypted"),
    reason="jupyter_client Session has no transport_encrypted trait",
)


class StubStream:
    """A stand-in for a kernel ZMQ stream.

    It records the on_recv callback. When the server sends a message on it,
    it answers with ``reply``, like a kernel would.
    """

    def __init__(self, reply=None):
        self.reply = reply
        self.callback = None
        self.socket = SimpleNamespace(closed=False)

    def on_recv(self, callback):
        self.callback = callback

    def send_multipart(self, msg_list, copy=True):
        if self.reply is not None:
            self.callback(self.reply)

    def close(self):
        self.socket.closed = True


def unsigned_kernel_session(key):
    """A kernel-side Session that sends unsigned messages, as it may over CurveZMQ."""
    return Session(key=key, transport_encrypted=True, sign_encrypted_messages=False)


def serialize_unsigned(session, msg_type, content):
    msg_list = session.serialize(session.msg(msg_type, content=content))
    # [DELIM, signature, header, parent_header, metadata, content]
    assert msg_list[1] == b""
    return msg_list


async def start_kernel(app, transport_encrypted):
    kernel_id = await app.kernel_manager.start_kernel()
    kernel = app.kernel_manager.get_kernel(kernel_id)
    # jupyter_client sets this when the kernel has CURVE keys.
    kernel.session.transport_encrypted = transport_encrypted
    return kernel_id, kernel


async def prepare_connection(app, kernel, kernel_info_reply):
    """Run ZMQChannelsWebsocketConnection.prepare() with a stub kernel_info channel."""
    request = HTTPRequest("foo", "GET")
    request.connection = MagicMock()
    handler = KernelWebsocketHandler(app.web_app, request)
    handler.ws_connection = MagicMock()
    handler.ws_connection.is_closing = lambda: False
    conn = ZMQChannelsWebsocketConnection(parent=kernel, websocket_handler=handler)
    handler.connection = conn
    conn.kernel_info_channel = StubStream(reply=kernel_info_reply)
    await conn.prepare()
    return conn


def watch_activity_on_stub(app, kernel_id, kernel, monkeypatch):
    """Restart activity watching on a stub IOPub stream.

    Returns the stub stream and the Session that start_watching_activity created.
    """
    app.kernel_manager.stop_watching_activity(kernel_id)
    iopub = StubStream()
    created = []

    def recording_session(**kwargs):
        session = Session(**kwargs)
        created.append(session)
        return session

    monkeypatch.setattr(kernel, "connect_iopub", lambda *args, **kwargs: iopub)
    monkeypatch.setattr(kernelmanager, "Session", recording_session)
    app.kernel_manager.start_watching_activity(kernel_id)
    (session,) = created
    return iopub, session


@requires_transport_encrypted
async def test_websocket_session_accepts_unsigned_with_transport_encrypted(jp_serverapp):
    _, kernel = await start_kernel(jp_serverapp, transport_encrypted=True)
    info = {"protocol_version": client_protocol_version, "implementation": "unsigned"}
    reply = serialize_unsigned(
        unsigned_kernel_session(kernel.session.key), "kernel_info_reply", info
    )

    conn = await prepare_connection(jp_serverapp, kernel, reply)

    assert conn.session.transport_encrypted is True
    assert conn._kernel_info_future.result() == info


@requires_transport_encrypted
async def test_websocket_session_rejects_unsigned_without_transport_encrypted(jp_serverapp):
    _, kernel = await start_kernel(jp_serverapp, transport_encrypted=False)
    info = {"protocol_version": client_protocol_version, "implementation": "unsigned"}
    reply = serialize_unsigned(
        unsigned_kernel_session(kernel.session.key), "kernel_info_reply", info
    )

    conn = await prepare_connection(jp_serverapp, kernel, reply)

    assert conn.session.transport_encrypted is False
    # The reply is dropped as a bad kernel_info reply.
    assert conn._kernel_info_future.result() == {}
    _, fed_msg_list = conn.session.feed_identities(reply)
    with pytest.raises(ValueError, match="Unsigned Message"):
        conn.session.deserialize(fed_msg_list)


@requires_transport_encrypted
async def test_activity_session_accepts_unsigned_with_transport_encrypted(
    jp_serverapp, monkeypatch
):
    kernel_id, kernel = await start_kernel(jp_serverapp, transport_encrypted=True)
    iopub, session = watch_activity_on_stub(jp_serverapp, kernel_id, kernel, monkeypatch)
    status = serialize_unsigned(
        unsigned_kernel_session(kernel.session.key), "status", {"execution_state": "idle"}
    )
    earlier = utcnow() - timedelta(hours=1)
    kernel.last_activity = earlier

    iopub.callback(status)

    assert session.transport_encrypted is True
    assert kernel.execution_state == "idle"
    assert kernel.last_activity > earlier


@requires_transport_encrypted
async def test_activity_session_rejects_unsigned_without_transport_encrypted(
    jp_serverapp, monkeypatch
):
    kernel_id, kernel = await start_kernel(jp_serverapp, transport_encrypted=False)
    iopub, session = watch_activity_on_stub(jp_serverapp, kernel_id, kernel, monkeypatch)
    status = serialize_unsigned(
        unsigned_kernel_session(kernel.session.key), "status", {"execution_state": "idle"}
    )
    earlier = utcnow() - timedelta(hours=1)
    kernel.last_activity = earlier

    with pytest.raises(ValueError, match="Unsigned Message"):
        iopub.callback(status)

    assert session.transport_encrypted is False
    assert kernel.execution_state == "starting"
    assert kernel.last_activity == earlier


def test_copy_transport_encrypted_source_without_trait():
    # A source without the trait (older jupyter_client) leaves the target unencrypted.
    target = Session()
    _copy_transport_encrypted(SimpleNamespace(), target)  # type:ignore[arg-type]
    assert getattr(target, "transport_encrypted", False) is False
