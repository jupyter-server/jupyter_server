"""Tests for authorization"""
import json

import pytest
from jupyter_client.kernelspec import NATIVE_KERNEL_NAME
from nbformat import writes
from nbformat.v4 import new_notebook
from tornado.httpclient import HTTPClientError
from tornado.websocket import WebSocketHandler

from jupyter_server.auth.authorizer import Authorizer
from jupyter_server.auth.utils import HTTP_METHOD_TO_AUTH_ACTION, match_url_to_resource
from jupyter_server.services.security import csp_report_uri


class AuthorizerforTesting(Authorizer):

    # Set these class attributes from within a test
    # to verify that they match the arguments passed
    # by the REST API.
    permissions: dict = {}

    def normalize_url(self, path):
        """Drop the base URL and make sure path leads with a /"""
        base_url = self.parent.base_url
        # Remove base_url
        if path.startswith(base_url):
            path = path[len(base_url) :]
        # Make sure path starts with /
        if not path.startswith("/"):
            path = "/" + path
        return path

    def is_authorized(self, handler, user, action, resource):
        # Parse Request
        if isinstance(handler, WebSocketHandler):
            method = "WEBSOCKET"
        else:
            method = handler.request.method
        url = self.normalize_url(handler.request.path)

        # Map request parts to expected action and resource.
        expected_action = HTTP_METHOD_TO_AUTH_ACTION[method]
        expected_resource = match_url_to_resource(url)

        # Assert that authorization layer returns the
        # correct action + resource.
        assert action == expected_action
        assert resource == expected_resource

        # Now, actually apply the authorization layer.
        return all(
            [
                action in self.permissions.get("actions", []),
                resource in self.permissions.get("resources", []),
            ]
        )


@pytest.fixture
def jp_server_config():
    return {"ServerApp": {"authorizer_class": AuthorizerforTesting}}


@pytest.fixture
def send_request(jp_fetch, jp_ws_fetch):
    """Send to Jupyter Server and return response code."""

    async def _(url, **fetch_kwargs):
        if url.endswith("channels") or "/websocket/" in url:
            fetch = jp_ws_fetch
        else:
            fetch = jp_fetch

        try:
            r = await fetch(url, **fetch_kwargs, allow_nonstandard_methods=True)
            code = r.code
        except HTTPClientError as err:
            code = err.code
        else:
            if fetch is jp_ws_fetch:
                r.close()

        print(code, url, fetch_kwargs)
        return code

    return _


HTTP_REQUESTS = [
    {
        "method": "GET",
        "url": "/view/{nbpath}",
    },
    {
        "method": "GET",
        "url": "/api/contents",
    },
    {
        "method": "POST",
        "url": "/api/contents",
        "body": json.dumps({"type": "directory"}),
    },
    {
        "method": "PUT",
        "url": "/api/contents/foo",
        "body": json.dumps({"type": "directory"}),
    },
    {
        "method": "PATCH",
        "url": "/api/contents/{nbpath}",
        "body": json.dumps({"path": "/newpath"}),
    },
    {
        "method": "DELETE",
        "url": "/api/contents/{nbpath}",
    },
    {
        "method": "GET",
        "url": "/api/kernels",
    },
    {
        "method": "GET",
        "url": "/api/kernels/{kernel_id}",
    },
    {
        "method": "GET",
        "url": "/api/kernels/{kernel_id}/channels",
    },
    {
        "method": "POST",
        "url": "/api/kernels/{kernel_id}/interrupt",
    },
    {
        "method": "POST",
        "url": "/api/kernels/{kernel_id}/restart",
    },
    {
        "method": "DELETE",
        "url": "/api/kernels/{kernel_id}",
    },
    {
        "method": "POST",
        "url": "/api/kernels",
    },
    {"method": "GET", "url": "/api/kernelspecs"},
    {"method": "GET", "url": "/api/kernelspecs/{kernelspec}"},
    {"method": "GET", "url": "/api/nbconvert"},
    {"method": "GET", "url": "/api/spec.yaml"},
    {"method": "GET", "url": "/api/status"},
    {"method": "GET", "url": "/api/config/foo"},
    {"method": "PUT", "url": "/api/config/foo", "body": "{}"},
    {"method": "PATCH", "url": "/api/config/foo", "body": "{}"},
    {
        "method": "POST",
        "url": "/".join(tuple(csp_report_uri.split("/")[1:])),
    },
    {
        "method": "GET",
        "url": "/api/sessions",
    },
    {
        "method": "GET",
        "url": "/api/sessions/{session_id}",
    },
    {"method": "PATCH", "url": "/api/sessions/{session_id}", "body": "{}"},
    {
        "method": "DELETE",
        "url": "/api/sessions/{session_id}",
    },
    {
        "method": "POST",
        "url": "/api/sessions",
        "body": json.dumps({"path": "foo", "type": "bar"}),
    },
    {
        "method": "POST",
        "url": "/api/terminals",
        "body": "",
    },
    {
        "method": "GET",
        "url": "/api/terminals",
    },
    {
        "method": "GET",
        "url": "/terminals/websocket/{term_name}",
    },
    {
        "method": "DELETE",
        "url": "/api/terminals/{term_name}",
    },
]

HTTP_REQUESTS_PARAMETRIZED = [(req["method"], req["url"], req.get("body")) for req in HTTP_REQUESTS]

# -------- Test scenarios -----------


@pytest.mark.parametrize("method, url, body", HTTP_REQUESTS_PARAMETRIZED)
@pytest.mark.parametrize("allowed", (True, False))
async def test_authorized_requests(
    request,
    io_loop,
    send_request,
    tmp_path,
    jp_serverapp,
    method,
    url,
    body,
    allowed,
):
    # Setup stuff for the Contents API
    # Add a notebook on disk
    contents_dir = tmp_path / jp_serverapp.root_dir
    p = contents_dir / "dir_for_testing"
    p.mkdir(parents=True, exist_ok=True)

    # Create a notebook
    nb = writes(new_notebook(), version=4)
    nbname = p.joinpath("nb_for_testing.ipynb")
    nbname.write_text(nb, encoding="utf-8")

    # Setup
    nbpath = "dir_for_testing/nb_for_testing.ipynb"
    kernelspec = NATIVE_KERNEL_NAME
    km = jp_serverapp.kernel_manager

    if "session" in url:
        request.addfinalizer(lambda: io_loop.run_sync(km.shutdown_all))
        session_model = await jp_serverapp.session_manager.create_session(path="foo")
        session_id = session_model["id"]

    if "kernel" in url:
        request.addfinalizer(lambda: io_loop.run_sync(km.shutdown_all))
        kernel_id = await km.start_kernel()
        kernel = km.get_kernel(kernel_id)
        # kernels take a moment to be ready
        # wait for it to respond
        kc = kernel.client()
        kc.start_channels()
        await kc.wait_for_ready()
        kc.stop_channels()

    if "terminal" in url:
        term_manager = jp_serverapp.web_app.settings["terminal_manager"]
        request.addfinalizer(lambda: io_loop.run_sync(term_manager.terminate_all))
        term_model = term_manager.create()
        term_name = term_model["name"]

    url = url.format(**locals())
    if allowed:
        # Create a server with full permissions
        permissions = {
            "actions": ["read", "write", "execute"],
            "resources": [
                "contents",
                "kernels",
                "kernelspecs",
                "nbconvert",
                "sessions",
                "api",
                "config",
                "csp",
                "server",
                "terminals",
            ],
        }
        expected_codes = {200, 201, 204, None}  # Websockets don't return a code
    else:
        permissions = {"actions": [], "resources": []}
        expected_codes = {403}
    jp_serverapp.authorizer.permissions = permissions

    code = await send_request(url, body=body, method=method)
    assert code in expected_codes
