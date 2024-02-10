"""Test Base Handlers"""
import os
import warnings
from unittest.mock import MagicMock

import pytest
from tornado.httpclient import HTTPClientError
from tornado.httpserver import HTTPRequest
from tornado.httputil import HTTPHeaders

from jupyter_server.auth import AllowAllAuthorizer, IdentityProvider
from jupyter_server.auth.decorator import allow_unauthenticated
from jupyter_server.base.handlers import (
    APIHandler,
    APIVersionHandler,
    AuthenticatedFileHandler,
    AuthenticatedHandler,
    FileFindHandler,
    FilesRedirectHandler,
    JupyterHandler,
    RedirectWithParams,
)
from jupyter_server.serverapp import ServerApp
from jupyter_server.utils import url_path_join


def test_authenticated_handler(jp_serverapp):
    app: ServerApp = jp_serverapp
    request = HTTPRequest("OPTIONS")
    request.connection = MagicMock()
    handler = AuthenticatedHandler(app.web_app, request)
    for key in list(handler.settings):
        del handler.settings[key]
    handler.settings["headers"] = {"Content-Security-Policy": "foo"}

    assert handler.content_security_policy == "foo"
    assert handler.skip_check_origin()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        assert handler.login_handler == handler.identity_provider.login_handler_class
        assert isinstance(handler.authorizer, AllowAllAuthorizer)
        assert isinstance(handler.identity_provider, IdentityProvider)


def test_jupyter_handler(jp_serverapp):
    app: ServerApp = jp_serverapp
    headers = HTTPHeaders({"Origin": "foo"})
    request = HTTPRequest("OPTIONS", headers=headers)
    request.connection = MagicMock()
    handler = JupyterHandler(app.web_app, request)
    for key in list(handler.settings):
        del handler.settings[key]
    handler.settings["mathjax_url"] = "foo"
    handler.settings["mathjax_config"] = "bar"
    assert handler.mathjax_url == "/foo"
    assert handler.mathjax_config == "bar"
    handler.settings["terminal_manager"] = None
    assert handler.terminal_manager is None
    handler.settings["allow_origin"] = True  # type:ignore[unreachable]
    handler.set_cors_headers()
    handler.settings["allow_origin"] = False
    handler.settings["allow_origin_pat"] = "foo"
    handler.settings["allow_credentials"] = True
    handler.set_cors_headers()
    assert handler.check_referer() is True


class NoAuthRulesHandler(JupyterHandler):
    def options(self) -> None:
        self.finish({})


class PermissiveHandler(JupyterHandler):
    @allow_unauthenticated
    def options(self) -> None:
        self.finish({})


@pytest.mark.parametrize(
    "jp_server_config", [{"ServerApp": {"allow_unauthenticated_access": True}}]
)
async def test_jupyter_handler_auth_permissive(jp_serverapp, jp_fetch):
    app: ServerApp = jp_serverapp
    app.web_app.add_handlers(
        ".*$",
        [
            (url_path_join(app.base_url, "no-rules"), NoAuthRulesHandler),
            (url_path_join(app.base_url, "permissive"), PermissiveHandler),
        ],
    )

    # should allow access by default when no authentication rules are set up
    res = await jp_fetch("no-rules", method="OPTIONS", headers={"Authorization": ""})
    assert res.code == 200

    # should allow access by default when `@allow_unauthenticated` is used
    res = await jp_fetch("permissive", method="OPTIONS", headers={"Authorization": ""})
    assert res.code == 200


@pytest.mark.parametrize(
    "jp_server_config", [{"ServerApp": {"allow_unauthenticated_access": False}}]
)
async def test_jupyter_handler_auth_required(jp_serverapp, jp_fetch):
    app: ServerApp = jp_serverapp
    app.web_app.add_handlers(
        ".*$",
        [
            (url_path_join(app.base_url, "no-rules"), NoAuthRulesHandler),
            (url_path_join(app.base_url, "permissive"), PermissiveHandler),
        ],
    )

    # should permit access when `@allow_unauthenticated` is used
    res = await jp_fetch("permissive", method="OPTIONS", headers={"Authorization": ""})
    assert res.code == 200

    # should forbid access when no authentication rules are set up
    with pytest.raises(HTTPClientError) as exception:
        # note: using OPTIONS because GET and HEAD cause redirects to login page
        # which prevents the test from finishing; disabling `follow_redirects`
        # is not supported by `jp_fetch` yet.
        res = await jp_fetch("no-rules", method="OPTIONS", headers={"Authorization": ""})
    assert exception.value.code == 403


def test_api_handler(jp_serverapp):
    app: ServerApp = jp_serverapp
    headers = HTTPHeaders({"Origin": "foo"})
    request = HTTPRequest("OPTIONS", headers=headers)
    request.connection = MagicMock()
    handler = APIHandler(app.web_app, request)
    for key in list(handler.settings):
        del handler.settings[key]
    handler.options()


async def test_authenticated_file_handler(jp_serverapp, tmpdir):
    app: ServerApp = jp_serverapp
    headers = HTTPHeaders({"Origin": "foo"})
    request = HTTPRequest("HEAD", headers=headers)
    request.connection = MagicMock()
    test_file = tmpdir / "foo"
    with open(test_file, "w") as fid:
        fid.write("hello")

    handler = AuthenticatedFileHandler(app.web_app, request, path=str(tmpdir))
    for key in list(handler.settings):
        if key != "contents_manager":
            del handler.settings[key]
    handler.check_xsrf_cookie = MagicMock()  # type:ignore[method-assign]
    handler._jupyter_current_user = "foo"  # type:ignore[assignment]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        head = handler.head("foo")
        if head:
            await head
    assert handler.get_status() == 200


async def test_api_version_handler(jp_serverapp):
    app: ServerApp = jp_serverapp
    request = HTTPRequest("GET")
    request.connection = MagicMock()
    handler = APIVersionHandler(app.web_app, request)
    handler._transforms = []
    handler.get()
    assert handler.get_status() == 200


async def test_files_redirect_handler(jp_serverapp):
    app: ServerApp = jp_serverapp
    request = HTTPRequest("GET")
    request.connection = MagicMock()
    test_file = os.path.join(app.contents_manager.root_dir, "foo")
    with open(test_file, "w") as fid:
        fid.write("hello")
    handler = FilesRedirectHandler(app.web_app, request)
    handler._transforms = []
    await handler.get("foo")
    assert handler.get_status() == 302


def test_redirect_with_params(jp_serverapp):
    app: ServerApp = jp_serverapp
    request = HTTPRequest("GET")
    request.connection = MagicMock()
    request.query = "foo"
    handler = RedirectWithParams(app.web_app, request, url="foo")
    handler._transforms = []
    handler.get()
    assert handler.get_status() == 301


async def test_static_handler(jp_serverapp, tmpdir):
    async def async_magic():
        pass

    MagicMock.__await__ = lambda x: async_magic().__await__()

    test_file = tmpdir / "foo"
    with open(test_file, "w") as fid:
        fid.write("hello")

    app: ServerApp = jp_serverapp
    request = HTTPRequest("GET", str(test_file))
    request.connection = MagicMock()

    handler = FileFindHandler(app.web_app, request, path=str(tmpdir))
    handler._transforms = []
    await handler.get("foo")
    assert handler._headers["Cache-Control"] == "no-cache"

    handler.settings["static_immutable_cache"] = [str(tmpdir)]
    await handler.get("foo")
    assert handler._headers["Cache-Control"] == "public, max-age=31536000, immutable"
