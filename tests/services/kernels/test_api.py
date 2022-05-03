import json
import os
import time

import jupyter_client
import pytest
import tornado
from jupyter_client.kernelspec import NATIVE_KERNEL_NAME
from tornado.httpclient import HTTPClientError

from jupyter_server.utils import url_path_join

from ...utils import expected_http_error

TEST_TIMEOUT = 60


@pytest.fixture
def pending_kernel_is_ready(jp_serverapp):
    async def _(kernel_id):
        km = jp_serverapp.kernel_manager
        if getattr(km, "use_pending_kernels", False):
            kernel = km.get_kernel(kernel_id)
            if getattr(kernel, "ready", None):
                await kernel.ready

    return _


configs: list = [
    {
        "ServerApp": {
            "kernel_manager_class": "jupyter_server.services.kernels.kernelmanager.MappingKernelManager"
        }
    },
    {
        "ServerApp": {
            "kernel_manager_class": "jupyter_server.services.kernels.kernelmanager.AsyncMappingKernelManager"
        }
    },
]


# Pending kernels was released in Jupyter Client 7.1
# It is currently broken on Windows (Jan 2022). When fixed, we can remove the Windows check.
# See https://github.com/jupyter-server/jupyter_server/issues/672
if os.name != "nt" and jupyter_client._version.version_info >= (7, 1):
    # Add a pending kernels condition
    c = {
        "ServerApp": {
            "kernel_manager_class": "jupyter_server.services.kernels.kernelmanager.AsyncMappingKernelManager"
        },
        "AsyncMappingKernelManager": {"use_pending_kernels": True},
    }
    configs.append(c)


@pytest.fixture(params=configs)
def jp_server_config(request):
    return request.param


async def test_no_kernels(jp_fetch):
    r = await jp_fetch("api", "kernels", method="GET")
    kernels = json.loads(r.body.decode())
    assert kernels == []


@pytest.mark.timeout(TEST_TIMEOUT)
async def test_default_kernels(jp_fetch, jp_base_url):
    r = await jp_fetch("api", "kernels", method="POST", allow_nonstandard_methods=True)
    kernel = json.loads(r.body.decode())
    assert r.headers["location"] == url_path_join(jp_base_url, "/api/kernels/", kernel["id"])
    assert r.code == 201
    assert isinstance(kernel, dict)

    report_uri = url_path_join(jp_base_url, "/api/security/csp-report")
    expected_csp = "; ".join(
        ["frame-ancestors 'self'", "report-uri " + report_uri, "default-src 'none'"]
    )
    assert r.headers["Content-Security-Policy"] == expected_csp


@pytest.mark.timeout(TEST_TIMEOUT)
async def test_main_kernel_handler(jp_fetch, jp_base_url, jp_serverapp, pending_kernel_is_ready):
    # Start the first kernel
    r = await jp_fetch(
        "api", "kernels", method="POST", body=json.dumps({"name": NATIVE_KERNEL_NAME})
    )
    kernel1 = json.loads(r.body.decode())
    assert r.headers["location"] == url_path_join(jp_base_url, "/api/kernels/", kernel1["id"])
    assert r.code == 201
    assert isinstance(kernel1, dict)

    report_uri = url_path_join(jp_base_url, "/api/security/csp-report")
    expected_csp = "; ".join(
        ["frame-ancestors 'self'", "report-uri " + report_uri, "default-src 'none'"]
    )
    assert r.headers["Content-Security-Policy"] == expected_csp

    # Check that the kernel is found in the kernel list
    r = await jp_fetch("api", "kernels", method="GET")
    kernel_list = json.loads(r.body.decode())
    assert r.code == 200
    assert isinstance(kernel_list, list)
    assert kernel_list[0]["id"] == kernel1["id"]
    assert kernel_list[0]["name"] == kernel1["name"]

    # Start a second kernel
    r = await jp_fetch(
        "api", "kernels", method="POST", body=json.dumps({"name": NATIVE_KERNEL_NAME})
    )
    kernel2 = json.loads(r.body.decode())
    assert isinstance(kernel2, dict)

    # Get kernel list again
    r = await jp_fetch("api", "kernels", method="GET")
    kernel_list = json.loads(r.body.decode())
    assert r.code == 200
    assert isinstance(kernel_list, list)
    assert len(kernel_list) == 2

    # Interrupt a kernel
    await pending_kernel_is_ready(kernel2["id"])
    r = await jp_fetch(
        "api",
        "kernels",
        kernel2["id"],
        "interrupt",
        method="POST",
        allow_nonstandard_methods=True,
    )
    assert r.code == 204

    # Restart a kernel
    await pending_kernel_is_ready(kernel2["id"])
    r = await jp_fetch(
        "api",
        "kernels",
        kernel2["id"],
        "restart",
        method="POST",
        allow_nonstandard_methods=True,
    )
    restarted_kernel = json.loads(r.body.decode())
    assert restarted_kernel["id"] == kernel2["id"]
    assert restarted_kernel["name"] == kernel2["name"]

    # Start a kernel with a path
    r = await jp_fetch(
        "api",
        "kernels",
        method="POST",
        body=json.dumps({"name": NATIVE_KERNEL_NAME, "path": "/foo"}),
    )
    kernel3 = json.loads(r.body.decode())
    assert isinstance(kernel3, dict)


@pytest.mark.timeout(TEST_TIMEOUT)
async def test_kernel_handler(jp_fetch, jp_serverapp, pending_kernel_is_ready):
    # Create a kernel
    r = await jp_fetch(
        "api", "kernels", method="POST", body=json.dumps({"name": NATIVE_KERNEL_NAME})
    )
    kernel_id = json.loads(r.body.decode())["id"]
    r = await jp_fetch("api", "kernels", kernel_id, method="GET")
    kernel = json.loads(r.body.decode())
    assert r.code == 200
    assert isinstance(kernel, dict)
    assert "id" in kernel
    assert kernel["id"] == kernel_id

    # Requests a bad kernel id.
    bad_id = "111-111-111-111-111"
    with pytest.raises(tornado.httpclient.HTTPClientError) as e:
        await jp_fetch("api", "kernels", bad_id, method="GET")
    assert expected_http_error(e, 404)

    # Delete kernel with id.
    await pending_kernel_is_ready(kernel_id)
    r = await jp_fetch(
        "api",
        "kernels",
        kernel_id,
        method="DELETE",
    )
    assert r.code == 204

    # Get list of kernels
    try:
        await pending_kernel_is_ready(kernel_id)
    # If the kernel is already deleted, no need to await.
    except tornado.web.HTTPError:
        pass
    r = await jp_fetch("api", "kernels", method="GET")
    kernel_list = json.loads(r.body.decode())
    assert kernel_list == []

    # Request to delete a non-existent kernel id
    bad_id = "111-111-111-111-111"
    with pytest.raises(tornado.httpclient.HTTPClientError) as e:
        await jp_fetch("api", "kernels", bad_id, method="DELETE")
    assert expected_http_error(e, 404, "Kernel does not exist: " + bad_id)


@pytest.mark.timeout(TEST_TIMEOUT)
async def test_kernel_handler_startup_error(jp_fetch, jp_serverapp, jp_kernelspecs):
    if getattr(jp_serverapp.kernel_manager, "use_pending_kernels", False):
        return

    # Create a kernel
    with pytest.raises(HTTPClientError):
        await jp_fetch("api", "kernels", method="POST", body=json.dumps({"name": "bad"}))


@pytest.mark.timeout(TEST_TIMEOUT)
async def test_kernel_handler_startup_error_pending(
    jp_fetch, jp_ws_fetch, jp_serverapp, jp_kernelspecs
):
    if not getattr(jp_serverapp.kernel_manager, "use_pending_kernels", False):
        return

    jp_serverapp.kernel_manager.use_pending_kernels = True
    # Create a kernel
    r = await jp_fetch("api", "kernels", method="POST", body=json.dumps({"name": "bad"}))
    kid = json.loads(r.body.decode())["id"]

    with pytest.raises(HTTPClientError):
        await jp_ws_fetch("api", "kernels", kid, "channels")


@pytest.mark.timeout(TEST_TIMEOUT)
async def test_connection(jp_fetch, jp_ws_fetch, jp_http_port, jp_auth_header):
    # Create kernel
    r = await jp_fetch(
        "api", "kernels", method="POST", body=json.dumps({"name": NATIVE_KERNEL_NAME})
    )
    kid = json.loads(r.body.decode())["id"]

    # Get kernel info
    r = await jp_fetch("api", "kernels", kid, method="GET")
    model = json.loads(r.body.decode())
    assert model["connections"] == 0

    # Open a websocket connection.
    ws = await jp_ws_fetch("api", "kernels", kid, "channels")

    # Test that it was opened.
    r = await jp_fetch("api", "kernels", kid, method="GET")
    model = json.loads(r.body.decode())
    assert model["connections"] == 1

    # Close websocket
    ws.close()
    # give it some time to close on the other side:
    for _ in range(10):
        r = await jp_fetch("api", "kernels", kid, method="GET")
        model = json.loads(r.body.decode())
        if model["connections"] > 0:
            time.sleep(0.1)
        else:
            break

    r = await jp_fetch("api", "kernels", kid, method="GET")
    model = json.loads(r.body.decode())
    assert model["connections"] == 0
