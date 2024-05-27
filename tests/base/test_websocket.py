"""Test Base Websocket classes"""

import logging
import time
from unittest.mock import MagicMock, patch

import pytest
from tornado.httpclient import HTTPClientError
from tornado.httpserver import HTTPRequest
from tornado.httputil import HTTPHeaders
from tornado.websocket import WebSocketClosedError, WebSocketHandler

from jupyter_server.auth import IdentityProvider, User
from jupyter_server.auth.decorator import allow_unauthenticated
from jupyter_server.base.handlers import JupyterHandler
from jupyter_server.base.websocket import WebSocketMixin
from jupyter_server.serverapp import ServerApp
from jupyter_server.utils import JupyterServerAuthWarning, url_path_join


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


class MockJupyterHandler(MockHandler, JupyterHandler):
    pass


class NoAuthRulesWebsocketHandler(MockJupyterHandler):
    pass


class PermissiveWebsocketHandler(MockJupyterHandler):
    @allow_unauthenticated
    def get(self, *args, **kwargs) -> None:
        return super().get(*args, **kwargs)


@pytest.mark.parametrize(
    "jp_server_config", [{"ServerApp": {"allow_unauthenticated_access": True}}]
)
async def test_websocket_auth_permissive(jp_serverapp, jp_ws_fetch):
    app: ServerApp = jp_serverapp
    app.web_app.add_handlers(
        ".*$",
        [
            (url_path_join(app.base_url, "no-rules"), NoAuthRulesWebsocketHandler),
            (url_path_join(app.base_url, "permissive"), PermissiveWebsocketHandler),
        ],
    )

    # should always permit access when `@allow_unauthenticated` is used
    ws = await jp_ws_fetch("permissive", headers={"Authorization": ""})
    ws.close()

    # should allow access when no authentication rules are set up
    ws = await jp_ws_fetch("no-rules", headers={"Authorization": ""})
    ws.close()


@pytest.mark.parametrize(
    "jp_server_config", [{"ServerApp": {"allow_unauthenticated_access": False}}]
)
async def test_websocket_auth_required(jp_serverapp, jp_ws_fetch):
    app: ServerApp = jp_serverapp
    app.web_app.add_handlers(
        ".*$",
        [
            (url_path_join(app.base_url, "no-rules"), NoAuthRulesWebsocketHandler),
            (url_path_join(app.base_url, "permissive"), PermissiveWebsocketHandler),
        ],
    )

    # should always permit access when `@allow_unauthenticated` is used
    ws = await jp_ws_fetch("permissive", headers={"Authorization": ""})
    ws.close()

    # should forbid access when no authentication rules are set up
    with pytest.raises(HTTPClientError) as exception:
        ws = await jp_ws_fetch("no-rules", headers={"Authorization": ""})
    assert exception.value.code == 403


class IndiscriminateIdentityProvider(IdentityProvider):
    async def get_user(self, handler):
        return User(username="test")


@pytest.mark.parametrize(
    "jp_server_config", [{"ServerApp": {"allow_unauthenticated_access": False}}]
)
async def test_websocket_auth_respsects_identity_provider(jp_serverapp, jp_ws_fetch):
    app: ServerApp = jp_serverapp
    app.web_app.add_handlers(
        ".*$",
        [(url_path_join(app.base_url, "no-rules"), NoAuthRulesWebsocketHandler)],
    )

    def fetch():
        return jp_ws_fetch("no-rules", headers={"Authorization": ""})

    # If no identity provider is set the following request should fail
    # because the default tornado user would not be found:
    with pytest.raises(HTTPClientError) as exception:
        await fetch()
    assert exception.value.code == 403

    iidp = IndiscriminateIdentityProvider()
    # should allow access with the user set be the identity provider
    with patch.dict(jp_serverapp.web_app.settings, {"identity_provider": iidp}):
        ws = await fetch()
        ws.close()


class PermissivePlainWebsocketHandler(MockHandler):
    # note: inherits from MockHandler not MockJupyterHandler
    @allow_unauthenticated
    def get(self, *args, **kwargs) -> None:
        return super().get(*args, **kwargs)


@pytest.mark.parametrize(
    "jp_server_config",
    [
        {
            "ServerApp": {
                "allow_unauthenticated_access": False,
                "identity_provider": IndiscriminateIdentityProvider(),
            }
        }
    ],
)
async def test_websocket_auth_warns_mixin_lacks_jupyter_handler(jp_serverapp, jp_ws_fetch):
    app: ServerApp = jp_serverapp
    app.web_app.add_handlers(
        ".*$",
        [(url_path_join(app.base_url, "permissive"), PermissivePlainWebsocketHandler)],
    )

    with pytest.warns(
        JupyterServerAuthWarning,
        match="WebSocketMixin sub-class does not inherit from JupyterHandler",
    ):
        ws = await jp_ws_fetch("permissive", headers={"Authorization": ""})
        ws.close()
