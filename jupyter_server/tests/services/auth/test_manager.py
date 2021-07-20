"""Tests for authorization"""
import json
import time

import pytest
from jupyter_client.kernelspec import NATIVE_KERNEL_NAME
from nbformat import writes
from nbformat.v4 import new_notebook
from tornado.httpclient import HTTPClientError

from jupyter_server.base.zmqhandlers import ZMQStreamHandler
from jupyter_server.services.auth.manager import AuthorizationManager
from jupyter_server.services.auth.utils import HTTP_METHOD_TO_AUTH_ACTION
from jupyter_server.services.auth.utils import match_url_to_resource
from jupyter_server.services.security import csp_report_uri


class AuthorizationManagerforTesting(AuthorizationManager):

    # Set these class attributes from within a test
    # to verify that they match the arguments passed
    # by the REST API.
    permissions = {}

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

    def is_authorized(self, handler, subject, action, resource):
        # Parse Request
        if isinstance(handler, ZMQStreamHandler):
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
    return {"ServerApp": {"authorization_manager_class": AuthorizationManagerforTesting}}


@pytest.fixture
async def populated_server_with_resources(tmp_path, jp_serverapp, jp_fetch):
    ### Setup stuff for the Contents API
    # Add a notebook on disk
    contents_dir = tmp_path / jp_serverapp.root_dir
    p = contents_dir / "dir_for_testing"
    p.mkdir(parents=True, exist_ok=True)

    # Create a notebook
    nb = writes(new_notebook(), version=4)
    nbname = p.joinpath("nb_for_testing.ipynb")
    nbname.write_text(nb, encoding="utf-8")

    ### Setup
    session_model = await jp_serverapp.session_manager.create_session(path="foo")
    kernel_id = await jp_serverapp.kernel_manager.start_kernel()
    nbpath = "dir_for_testing/nb_for_testing.ipynb"
    kernelspec = NATIVE_KERNEL_NAME
    ## add custom kernelspec
    return nbpath, kernel_id, kernelspec, session_model


@pytest.fixture
def send_request(jp_fetch, jp_ws_fetch):
    """Send to Jupyter Server and return response code."""

    async def _(http_request):
        url = http_request.pop("url")
        if url.endswith("channels"):
            fetch = jp_ws_fetch
        else:
            fetch = jp_fetch

        try:
            r = await fetch(url, **http_request, allow_nonstandard_methods=True)
            # kernel requests take some time.
            if url.startswith("/api/kernels"):
                time.sleep(1)
            code = r.code
        except HTTPClientError as err:
            code = err.code

        print(code, url, http_request)
        return code

    return _


@pytest.fixture
async def get_http_requests(populated_server_with_resources):
    nbpath, kernel_id, kernelspec, session_model = await populated_server_with_resources
    session_id = session_model["id"]
    return [
        {
            "method": "GET",
            "url": f"/view/{nbpath}",
        },
        {
            "method": "GET",
            "url": "/api/contents",
        },
        {"method": "POST", "url": "/api/contents", "body": json.dumps({"type": "directory"})},
        {"method": "PUT", "url": "/api/contents/foo", "body": json.dumps({"type": "directory"})},
        {"method": "PATCH", "url": f"/api/contents/{nbpath}", "body": json.dumps({"path": nbpath})},
        {
            "method": "DELETE",
            "url": f"/api/contents/{nbpath}",
        },
        {
            "method": "GET",
            "url": "/api/kernels",
        },
        {
            "method": "GET",
            "url": f"/api/kernels/{kernel_id}",
        },
        {
            "method": "GET",
            "url": f"/api/kernels/{kernel_id}/channels",
        },
        {
            "method": "POST",
            "url": f"/api/kernels/{kernel_id}/interrupt",
        },
        {
            "method": "POST",
            "url": f"/api/kernels/{kernel_id}/restart",
        },
        {
            "method": "DELETE",
            "url": f"/api/kernels/{kernel_id}",
        },
        {
            "method": "POST",
            "url": "/api/kernels",
        },
        {"method": "GET", "url": "/api/kernelspecs"},
        {"method": "GET", "url": f"/api/kernelspecs/{kernelspec}"},
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
            "url": f"/api/sessions/{session_id}",
        },
        {"method": "PATCH", "url": f"/api/sessions/{session_id}", "body": "{}"},
        {
            "method": "DELETE",
            "url": f"/api/sessions/{session_id}",
        },
        {
            "method": "POST",
            "url": "/api/sessions",
            "body": json.dumps({"path": "foo", "type": "bar"}),
        },
    ]


# -------- Test scenarios -----------


async def test_authorized_requests(send_request, jp_serverapp, get_http_requests):
    # Create a server with no permissions
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
            "view",
            "shutdown",
        ],
    }
    jp_serverapp.authorization_manager.permissions = permissions

    http_requests = await get_http_requests

    for http_request in http_requests:
        code = await send_request(http_request)
        assert code in [200, 201, 204, None]  # Websockets don't return a code.


async def test_unauthorized_requests(send_request, jp_serverapp, get_http_requests):
    # Create a server with no permissions
    permissions = {"actions": [], "resources": []}
    jp_serverapp.authorization_manager.permissions = permissions

    http_requests = await get_http_requests

    for http_request in http_requests:
        code = await send_request(http_request)
        assert code == 401
