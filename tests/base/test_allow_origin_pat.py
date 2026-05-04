"""Tests for allow_origin_pat origin validation using re.fullmatch()

(GHSA-24qx-w28j-9m6p and CVE-2026-40110)

allow_origin_pat must match the full origin string. re.match() only anchors at the
start, allowing "https://trusted.example.com.evil.com" to bypass a pattern intended
to match only "https://trusted.example.com".
"""

import warnings
from unittest.mock import MagicMock

import pytest
from tornado.httpserver import HTTPRequest
from tornado.httputil import HTTPHeaders

from jupyter_server.auth.login import LoginHandler
from jupyter_server.base.handlers import JupyterHandler
from jupyter_server.base.websocket import WebSocketMixin

TRUSTED_PAT = r"https://trusted\.example\.com"
TRUSTED_ORIGIN = "https://trusted.example.com"

BYPASS_ORIGINS = [
    "https://trusted.example.com.evil.com",
    "https://trusted.example.comedy",
    "https://trusted.example.com:9999",
]


def _make_handler(jp_serverapp, origin=None, host="localhost:8888", referer=None):
    headers = {"Host": host}
    if origin:
        headers["Origin"] = origin
    if referer:
        headers["Referer"] = referer
    request = HTTPRequest("GET", headers=HTTPHeaders(headers))
    request.connection = MagicMock()
    handler = JupyterHandler(jp_serverapp.web_app, request)
    handler.settings["allow_origin"] = ""
    handler.settings["allow_origin_pat"] = TRUSTED_PAT
    # skip_check_origin() requires async auth context; bypass it to reach pattern matching
    handler.skip_check_origin = lambda: False
    return handler


@pytest.mark.parametrize("origin", BYPASS_ORIGINS)
def test_check_origin_rejects_bypass(jp_serverapp, origin):
    with pytest.warns(UserWarning, match="allow_origin_pat.*"):
        assert not _make_handler(jp_serverapp, origin=origin, host="other.host:8888").check_origin()


def test_check_origin_allows_trusted(jp_serverapp):
    assert _make_handler(jp_serverapp, origin=TRUSTED_ORIGIN, host="other.host:8888").check_origin()


@pytest.mark.parametrize("origin", BYPASS_ORIGINS)
def test_check_referer_rejects_bypass(jp_serverapp, origin):
    handler = _make_handler(jp_serverapp, host="other.host:8888", referer=f"{origin}/page")
    with pytest.warns(UserWarning, match="allow_origin_pat.*"):
        assert not handler.check_referer()


@pytest.mark.parametrize("origin", BYPASS_ORIGINS)
def test_set_cors_headers_rejects_bypass(jp_serverapp, origin):
    with pytest.warns(UserWarning, match="allow_origin_pat.*"):
        handler = _make_handler(jp_serverapp, origin=origin)
        handler.set_cors_headers()
        assert handler._headers.get("Access-Control-Allow-Origin") != origin


@pytest.mark.parametrize("attacker_origin", BYPASS_ORIGINS)
def test_login_redirect_safe_rejects_bypass(jp_serverapp, attacker_origin):
    request = HTTPRequest("GET", headers=HTTPHeaders({"Host": "localhost:8888"}))
    request.connection = MagicMock()
    with pytest.warns(UserWarning, match="allow_origin_pat.*"):
        handler = LoginHandler(jp_serverapp.web_app, request)
        handler.settings["allow_origin"] = ""
        handler.settings["allow_origin_pat"] = TRUSTED_PAT

        redirected_to = []
        handler.redirect = lambda url, *a, **kw: redirected_to.append(url)
        handler._redirect_safe(f"{attacker_origin}/capture", default=jp_serverapp.base_url)

        assert redirected_to[0] != f"{attacker_origin}/capture"


@pytest.mark.parametrize("attacker_origin", BYPASS_ORIGINS)
def test_websocket_check_origin_rejects_bypass(jp_serverapp, attacker_origin):
    request = HTTPRequest(
        "GET",
        headers=HTTPHeaders({"Origin": attacker_origin, "Host": "other.host:8888"}),
    )
    request.connection = MagicMock()

    class TestWSHandler(WebSocketMixin, JupyterHandler):
        pass

    handler = TestWSHandler(jp_serverapp.web_app, request)
    handler.settings["allow_origin"] = ""
    handler.settings["allow_origin_pat"] = TRUSTED_PAT
    handler.skip_check_origin = lambda: False

    with pytest.warns(UserWarning, match="allow_origin_pat.*"):
        assert not handler.check_origin(attacker_origin)


def test_truncated_pattern_warns_and_blocks(jp_serverapp):
    """Prefix-only pattern (e.g. 'https://trusted') emits UserWarning and blocks the request."""
    handler = _make_handler(
        jp_serverapp, origin="https://trusted.example.com", host="other.host:8888"
    )
    handler.settings["allow_origin_pat"] = r"https://trusted"

    with pytest.warns(UserWarning, match="only matched the request origin as a prefix"):
        result = handler.check_origin()

    assert not result
