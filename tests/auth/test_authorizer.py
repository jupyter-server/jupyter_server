"""Tests for authorization"""
import json

import pytest
from jupyter_client.kernelspec import NATIVE_KERNEL_NAME
from nbformat import writes
from nbformat.v4 import new_notebook

from jupyter_server.services.security import csp_report_uri


@pytest.fixture
def jp_server_config(jp_server_authorizer):
    return {
        "ServerApp": {"authorizer_class": jp_server_authorizer},
        "jpserver_extensions": {"jupyter_server_terminals": True},
    }


@pytest.fixture
def jp_server_auth_resources(jp_server_auth_core_resources):
    # terminal plugin doesn't have importable url patterns
    # get these from terminal/__init__.py
    for url_regex in [
        r"/terminals/websocket/(\w+)",
        "/api/terminals",
        r"/api/terminals/(\w+)",
    ]:
        jp_server_auth_core_resources[url_regex] = "terminals"
    return jp_server_auth_core_resources


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
