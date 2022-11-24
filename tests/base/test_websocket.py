"""Test Base Websocket classes"""
import logging
import time
from unittest.mock import MagicMock

import pytest
from tornado.httpserver import HTTPRequest
from tornado.httputil import HTTPHeaders
from tornado.websocket import WebSocketClosedError, WebSocketHandler

from jupyter_server.base.websocket import WebSocketMixin
from jupyter_server.serverapp import ServerApp


class MockHandler(WebSocketMixin, WebSocketHandler):
    allow_origin = "*"
    allow_origin_pat = ""
    log = logging.getLogger()


@pytest.fixture
def mixin(jp_serverapp):
    app: ServerApp = jp_serverapp
    headers = HTTPHeaders({"Host": "foo"})
    request = HTTPRequest("GET", headers=headers)
    request.connection = MagicMock()
    return MockHandler(app.web_app, request)


def test_web_socket_mixin(mixin):
    assert mixin.check_origin("foo") is True
    mixin.allow_origin = ""
    assert mixin.check_origin("") is False
    mixin.allow_origin_pat = "foo"
    assert mixin.check_origin("foo") is True
    mixin.clear_cookie()
    assert mixin.get_status() == 200


def test_web_socket_mixin_ping(mixin):
    mixin.ws_connection = MagicMock()
    mixin.ws_connection.is_closing = lambda: False
    mixin.send_ping()


def test_ping_client_terminated(mixin):
    mixin.ws_connection = MagicMock()
    mixin.ws_connection.client_terminated = True
    mixin.send_ping()
    with pytest.raises(WebSocketClosedError):
        mixin.write_message("hello")


async def test_ping_client_timeout(mixin):
    mixin.on_pong("foo")
    mixin.settings["ws_ping_timeout"] = 0.1
    time.sleep(0.3)
    mixin.ws_connection = MagicMock()
    mixin.ws_connection.is_closing = lambda: False
    mixin.send_ping()
    with pytest.raises(WebSocketClosedError):
        mixin.write_message("hello")
