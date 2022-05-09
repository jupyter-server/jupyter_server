"""
Test legacy login config via ServerApp.login_handler_class
"""

import json
from functools import wraps
from urllib.parse import urlencode

import pytest
from tornado.httpclient import HTTPClientError
from tornado.httputil import parse_cookie
from traitlets.config import Config

from jupyter_server.auth.identity import LegacyIdentityProvider
from jupyter_server.auth.login import LoginHandler
from jupyter_server.auth.security import passwd
from jupyter_server.serverapp import ServerApp
from jupyter_server.utils import url_path_join

# Don't raise on deprecation warnings in this module testing deprecated behavior
pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")


def record_calls(f):
    """Decorator to record call history"""
    f._calls = []

    @wraps(f)
    def wrapped_f(*args, **kwargs):
        f._calls.append((args, kwargs))
        return f(*args, **kwargs)

    return wrapped_f


class CustomLoginHandler(LoginHandler):
    @classmethod
    @record_calls
    def get_user(cls, handler):
        header_user = handler.request.headers.get("test-user")
        if header_user:
            if header_user == "super":
                return super().get_user(handler)
            return header_user
        else:
            return None


@pytest.fixture
def jp_server_config():
    cfg = Config()
    cfg.ServerApp.login_handler_class = CustomLoginHandler
    return cfg


def test_legacy_identity_config(jp_serverapp):
    # setting login_handler_class sets LegacyIdentityProvider
    app = ServerApp()
    idp = jp_serverapp.identity_provider
    assert type(idp) is LegacyIdentityProvider
    assert idp.login_available
    assert idp.auth_enabled
    assert idp.token
    assert idp.get_handlers() == [
        ("/login", idp.login_handler_class),
        ("/logout", idp.logout_handler_class),
    ]


async def test_legacy_identity_api(jp_serverapp, jp_fetch):
    response = await jp_fetch("/api/me", headers={"test-user": "pinecone"})
    assert response.code == 200
    model = json.loads(response.body.decode("utf8"))
    assert model["identity"]["username"] == "pinecone"


async def test_legacy_base_class(jp_serverapp, jp_fetch):
    response = await jp_fetch("/api/me", headers={"test-user": "super"})
    assert "Set-Cookie" in response.headers
    cookie = response.headers["Set-Cookie"]
    assert response.code == 200
    model = json.loads(response.body.decode("utf8"))
    user_id = model["identity"]["username"]  # a random uuid
    assert user_id

    response = await jp_fetch("/api/me", headers={"test-user": "super", "Cookie": cookie})
    model2 = json.loads(response.body.decode("utf8"))
    # second request, should trigger cookie auth
    assert model2["identity"] == model["identity"]


async def test_legacy_login(jp_serverapp, http_server_client, jp_base_url, jp_fetch):
    login_url = url_path_join(jp_base_url, "login")
    first = await http_server_client.fetch(login_url)
    cookie_header = first.headers["Set-Cookie"]
    xsrf = parse_cookie(cookie_header).get("_xsrf", "")
    new_password = "super-secret"

    async def login(form_fields):
        form = {"_xsrf": xsrf}
        form.update(form_fields)
        try:
            resp = await http_server_client.fetch(
                login_url,
                method="POST",
                body=urlencode(form),
                headers={"Cookie": cookie_header},
                follow_redirects=False,
            )
        except HTTPClientError as e:
            resp = e.response
        assert resp.code == 302, "Should have returned a redirect!"
        return resp

    resp = await login(
        dict(password=jp_serverapp.identity_provider.token, new_password=new_password)
    )
    cookie = resp.headers["Set-Cookie"]
    id_resp = await jp_fetch("/api/me", headers={"test-user": "super", "Cookie": cookie})
    assert id_resp.code == 200
    model = json.loads(id_resp.body.decode("utf8"))
    user_id = model["identity"]["username"]  # a random uuid

    # verify password change with second login
    resp2 = await login(dict(password=new_password))
    cookie = resp.headers["Set-Cookie"]
    id_resp = await jp_fetch("/api/me", headers={"test-user": "super", "Cookie": cookie})
    assert id_resp.code == 200
    model = json.loads(id_resp.body.decode("utf8"))
    user_id2 = model["identity"]["username"]  # a random uuid
    assert user_id2 == user_id


def test_deprecated_config():
    cfg = Config()
    cfg.ServerApp.token = token = "asdf"
    cfg.ServerApp.password = password = passwd("secrets")
    app = ServerApp(config=cfg)
    app.initialize([])
    app.init_configurables()
    assert app.identity_provider.token == token
    assert app.token == token
    assert app.identity_provider.hashed_password == password
    assert app.password == password


def test_deprecated_config_priority():
    cfg = Config()
    cfg.ServerApp.token = "ignored"
    cfg.IdentityProvider.token = token = "idp_token"
    cfg.ServerApp.password = passwd("ignored")
    cfg.PasswordIdentityProvider.hashed_password = password = passwd("used")
    app = ServerApp(config=cfg)
    app.initialize([])
    app.init_configurables()
    assert app.identity_provider.token == token
    assert app.identity_provider.hashed_password == password
