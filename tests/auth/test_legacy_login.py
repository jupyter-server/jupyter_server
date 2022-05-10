"""
Test legacy login config via ServerApp.login_handler_class
"""

import json

import pytest
from traitlets.config import Config

from jupyter_server.auth.identity import LegacyIdentityProvider
from jupyter_server.auth.login import LoginHandler
from jupyter_server.auth.security import passwd
from jupyter_server.serverapp import ServerApp

# re-run some login tests with legacy login config
from .test_identity import test_password_required, test_validate_security  # noqa
from .test_login import (  # noqa
    login,
    test_change_password,
    test_login_cookie,
    test_logout,
)

# Don't raise on deprecation warnings in this module testing deprecated behavior
pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")


class CustomLoginHandler(LoginHandler):
    @classmethod
    def get_user(cls, handler):
        header_user = handler.request.headers.get("test-user")
        if header_user:
            if header_user == "super":
                return super().get_user(handler)
            return header_user
        else:
            return None


@pytest.fixture
def login_headers():
    return {"test-user": "super"}


@pytest.fixture
def jp_server_config():
    cfg = Config()
    cfg.ServerApp.login_handler_class = CustomLoginHandler
    return cfg


@pytest.fixture
def identity_provider_class():
    # for tests imported from test_identity.py
    return LegacyIdentityProvider


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
