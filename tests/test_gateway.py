"""Test GatewayClient"""
import asyncio
import json
import logging
import os
import uuid
from datetime import datetime, timedelta
from email.utils import format_datetime
from http.cookies import SimpleCookie
from io import BytesIO
from queue import Empty
from unittest.mock import MagicMock, patch

import pytest
import tornado
from tornado.httpclient import HTTPRequest, HTTPResponse
from tornado.web import HTTPError

from jupyter_server.gateway.managers import (
    ChannelQueue,
    GatewayClient,
    GatewayKernelManager,
)
from jupyter_server.utils import ensure_async

from .utils import expected_http_error


def generate_kernelspec(name):
    argv_stanza = ["python", "-m", "ipykernel_launcher", "-f", "{connection_file}"]
    spec_stanza = {
        "spec": {
            "argv": argv_stanza,
            "env": {},
            "display_name": name,
            "language": "python",
            "interrupt_mode": "signal",
            "metadata": {},
        }
    }
    kernelspec_stanza = {"name": name, "spec": spec_stanza, "resources": {}}
    return kernelspec_stanza


# We'll mock up two kernelspecs - kspec_foo and kspec_bar
kernelspecs: dict = {
    "default": "kspec_foo",
    "kernelspecs": {
        "kspec_foo": generate_kernelspec("kspec_foo"),
        "kspec_bar": generate_kernelspec("kspec_bar"),
    },
}


# maintain a dictionary of expected running kernels.  Key = kernel_id, Value = model.
running_kernels = {}


def generate_model(name):
    """Generate a mocked kernel model.  Caller is responsible for adding model to running_kernels dictionary."""
    dt = datetime.utcnow().isoformat() + "Z"
    kernel_id = str(uuid.uuid4())
    model = {
        "id": kernel_id,
        "name": name,
        "last_activity": str(dt),
        "execution_state": "idle",
        "connections": 1,
    }
    return model


async def mock_gateway_request(url, **kwargs):
    method = "GET"
    if kwargs["method"]:
        method = kwargs["method"]

    request = HTTPRequest(url=url, **kwargs)

    endpoint = str(url)

    # Fetch all kernelspecs
    if endpoint.endswith("/api/kernelspecs") and method == "GET":
        response_buf = BytesIO(json.dumps(kernelspecs).encode("utf-8"))
        response = await ensure_async(HTTPResponse(request, 200, buffer=response_buf))
        return response

    # Fetch named kernelspec
    if endpoint.rfind("/api/kernelspecs/") >= 0 and method == "GET":
        requested_kernelspec = endpoint.rpartition("/")[2]
        kspecs: dict = kernelspecs["kernelspecs"]
        if requested_kernelspec in kspecs:
            response_str = json.dumps(kspecs.get(requested_kernelspec))
            response_buf = BytesIO(response_str.encode("utf-8"))
            response = await ensure_async(HTTPResponse(request, 200, buffer=response_buf))
            return response
        else:
            raise HTTPError(404, message="Kernelspec does not exist: %s" % requested_kernelspec)

    # Create kernel
    if endpoint.endswith("/api/kernels") and method == "POST":
        json_body = json.loads(kwargs["body"])
        name = json_body.get("name")
        env = json_body.get("env")
        kspec_name = env.get("KERNEL_KSPEC_NAME")
        assert name == kspec_name  # Ensure that KERNEL_ env values get propagated
        model = generate_model(name)
        running_kernels[model.get("id")] = model  # Register model as a running kernel
        response_buf = BytesIO(json.dumps(model).encode("utf-8"))
        response = await ensure_async(HTTPResponse(request, 201, buffer=response_buf))
        return response

    # Fetch list of running kernels
    if endpoint.endswith("/api/kernels") and method == "GET":
        kernels = []
        for kernel_id in running_kernels.keys():
            model = running_kernels.get(kernel_id)
            kernels.append(model)
        response_buf = BytesIO(json.dumps(kernels).encode("utf-8"))
        response = await ensure_async(HTTPResponse(request, 200, buffer=response_buf))
        return response

    # Interrupt or restart existing kernel
    if endpoint.rfind("/api/kernels/") >= 0 and method == "POST":
        requested_kernel_id, sep, action = endpoint.rpartition("/api/kernels/")[2].rpartition("/")

        if action == "interrupt":
            if requested_kernel_id in running_kernels:
                response = await ensure_async(HTTPResponse(request, 204))
                return response
            else:
                raise HTTPError(404, message="Kernel does not exist: %s" % requested_kernel_id)
        elif action == "restart":
            if requested_kernel_id in running_kernels:
                response_str = json.dumps(running_kernels.get(requested_kernel_id))
                response_buf = BytesIO(response_str.encode("utf-8"))
                response = await ensure_async(HTTPResponse(request, 204, buffer=response_buf))
                return response
            else:
                raise HTTPError(404, message="Kernel does not exist: %s" % requested_kernel_id)
        else:
            raise HTTPError(404, message="Bad action detected: %s" % action)

    # Shutdown existing kernel
    if endpoint.rfind("/api/kernels/") >= 0 and method == "DELETE":
        requested_kernel_id = endpoint.rpartition("/")[2]
        if requested_kernel_id not in running_kernels:
            raise HTTPError(404, message="Kernel does not exist: %s" % requested_kernel_id)

        running_kernels.pop(
            requested_kernel_id
        )  # Simulate shutdown by removing kernel from running set
        response = await ensure_async(HTTPResponse(request, 204))
        return response

    # Fetch existing kernel
    if endpoint.rfind("/api/kernels/") >= 0 and method == "GET":
        requested_kernel_id = endpoint.rpartition("/")[2]
        if requested_kernel_id in running_kernels:
            response_str = json.dumps(running_kernels.get(requested_kernel_id))
            response_buf = BytesIO(response_str.encode("utf-8"))
            response = await ensure_async(HTTPResponse(request, 200, buffer=response_buf))
            return response
        else:
            raise HTTPError(404, message="Kernel does not exist: %s" % requested_kernel_id)


mocked_gateway = patch("jupyter_server.gateway.managers.gateway_request", mock_gateway_request)
mock_gateway_url = "http://mock-gateway-server:8889"
mock_http_user = "alice"


def mock_websocket_create_connection(recv_side_effect=None):
    def helper(*args, **kwargs):
        mock = MagicMock()
        mock.recv = MagicMock(side_effect=recv_side_effect)
        return mock

    return helper


@pytest.fixture
def init_gateway(monkeypatch):
    """Initializes the server for use as a gateway client."""
    # Clear the singleton first since previous tests may not have used a gateway.
    GatewayClient.clear_instance()
    monkeypatch.setenv("JUPYTER_GATEWAY_URL", mock_gateway_url)
    monkeypatch.setenv("JUPYTER_GATEWAY_HTTP_USER", mock_http_user)
    monkeypatch.setenv("JUPYTER_GATEWAY_REQUEST_TIMEOUT", "44.4")
    monkeypatch.setenv("JUPYTER_GATEWAY_CONNECT_TIMEOUT", "44.4")
    monkeypatch.setenv("JUPYTER_GATEWAY_LAUNCH_TIMEOUT_PAD", "1.1")
    monkeypatch.setenv("JUPYTER_GATEWAY_ACCEPT_COOKIES", "false")
    yield
    GatewayClient.clear_instance()


async def test_gateway_env_options(init_gateway, jp_serverapp):
    assert jp_serverapp.gateway_config.gateway_enabled is True
    assert jp_serverapp.gateway_config.url == mock_gateway_url
    assert jp_serverapp.gateway_config.http_user == mock_http_user
    assert (
        jp_serverapp.gateway_config.connect_timeout == jp_serverapp.gateway_config.request_timeout
    )
    assert jp_serverapp.gateway_config.connect_timeout == 44.4
    assert jp_serverapp.gateway_config.launch_timeout_pad == 1.1
    assert jp_serverapp.gateway_config.accept_cookies is False

    GatewayClient.instance().init_static_args()
    assert GatewayClient.instance().KERNEL_LAUNCH_TIMEOUT == 43


async def test_gateway_cli_options(jp_configurable_serverapp):
    argv = [
        "--gateway-url=" + mock_gateway_url,
        "--GatewayClient.http_user=" + mock_http_user,
        "--GatewayClient.connect_timeout=44.4",
        "--GatewayClient.request_timeout=96.0",
        "--GatewayClient.launch_timeout_pad=5.1",
    ]

    GatewayClient.clear_instance()
    app = jp_configurable_serverapp(argv=argv)

    assert app.gateway_config.gateway_enabled is True
    assert app.gateway_config.url == mock_gateway_url
    assert app.gateway_config.http_user == mock_http_user
    assert app.gateway_config.connect_timeout == 44.4
    assert app.gateway_config.request_timeout == 96.0
    assert app.gateway_config.launch_timeout_pad == 5.1
    GatewayClient.instance().init_static_args()
    assert (
        GatewayClient.instance().KERNEL_LAUNCH_TIMEOUT == 90
    )  # Ensure KLT gets set from request-timeout - launch_timeout_pad
    GatewayClient.clear_instance()


@pytest.mark.parametrize(
    "request_timeout,kernel_launch_timeout,expected_request_timeout,expected_kernel_launch_timeout",
    [(50, 10, 50, 45), (10, 50, 55, 50)],
)
async def test_gateway_request_timeout_pad_option(
    jp_configurable_serverapp,
    monkeypatch,
    request_timeout,
    kernel_launch_timeout,
    expected_request_timeout,
    expected_kernel_launch_timeout,
):
    argv = [
        f"--GatewayClient.request_timeout={request_timeout}",
        "--GatewayClient.launch_timeout_pad=5",
    ]

    GatewayClient.clear_instance()
    app = jp_configurable_serverapp(argv=argv)

    monkeypatch.setattr(GatewayClient, "KERNEL_LAUNCH_TIMEOUT", kernel_launch_timeout)
    GatewayClient.instance().init_static_args()

    assert app.gateway_config.request_timeout == expected_request_timeout
    assert GatewayClient.instance().KERNEL_LAUNCH_TIMEOUT == expected_kernel_launch_timeout

    GatewayClient.clear_instance()


cookie_expire_time = format_datetime(datetime.now() + timedelta(seconds=180))


@pytest.mark.parametrize(
    "accept_cookies,expire_arg,expire_param,existing_cookies,cookie_exists",
    [
        (False, None, None, "EXISTING=1", False),
        (True, None, None, "EXISTING=1", True),
        (True, "Expires", cookie_expire_time, None, True),
        (True, "Max-Age", "-360", "EXISTING=1", False),
    ],
)
async def test_gateway_request_with_expiring_cookies(
    jp_configurable_serverapp,
    accept_cookies,
    expire_arg,
    expire_param,
    existing_cookies,
    cookie_exists,
):
    argv = [f"--GatewayClient.accept_cookies={accept_cookies}"]

    GatewayClient.clear_instance()
    jp_configurable_serverapp(argv=argv)

    cookie: SimpleCookie = SimpleCookie()
    cookie.load("SERVERID=1234567; Path=/")
    if expire_arg:
        cookie["SERVERID"][expire_arg] = expire_param

    GatewayClient.instance().update_cookies(cookie)

    args = {}
    if existing_cookies:
        args["headers"] = {"Cookie": existing_cookies}
    connection_args = GatewayClient.instance().load_connection_args(**args)

    if not cookie_exists:
        assert "SERVERID" not in (connection_args["headers"].get("Cookie") or "")
    else:
        assert "SERVERID" in connection_args["headers"].get("Cookie")
    if existing_cookies:
        assert "EXISTING" in connection_args["headers"].get("Cookie")

    GatewayClient.clear_instance()


async def test_gateway_class_mappings(init_gateway, jp_serverapp):
    # Ensure appropriate class mappings are in place.
    assert jp_serverapp.kernel_manager_class.__name__ == "GatewayMappingKernelManager"
    assert jp_serverapp.session_manager_class.__name__ == "GatewaySessionManager"
    assert jp_serverapp.kernel_spec_manager_class.__name__ == "GatewayKernelSpecManager"


async def test_gateway_get_kernelspecs(init_gateway, jp_fetch):
    # Validate that kernelspecs come from gateway.
    with mocked_gateway:
        r = await jp_fetch("api", "kernelspecs", method="GET")
        assert r.code == 200
        content = json.loads(r.body.decode("utf-8"))
        kspecs = content.get("kernelspecs")
        assert len(kspecs) == 2
        assert kspecs.get("kspec_bar").get("name") == "kspec_bar"


async def test_gateway_get_named_kernelspec(init_gateway, jp_fetch):
    # Validate that a specific kernelspec can be retrieved from gateway (and an invalid spec can't)
    with mocked_gateway:
        r = await jp_fetch("api", "kernelspecs", "kspec_foo", method="GET")
        assert r.code == 200
        kspec_foo = json.loads(r.body.decode("utf-8"))
        assert kspec_foo.get("name") == "kspec_foo"

        with pytest.raises(tornado.httpclient.HTTPClientError) as e:
            await jp_fetch("api", "kernelspecs", "no_such_spec", method="GET")
        assert expected_http_error(e, 404)


async def test_gateway_session_lifecycle(init_gateway, jp_root_dir, jp_fetch):
    # Validate session lifecycle functions; create and delete.

    # create
    session_id, kernel_id = await create_session(jp_root_dir, jp_fetch, "kspec_foo")

    # ensure kernel still considered running
    assert await is_kernel_running(jp_fetch, kernel_id) is True

    # interrupt
    await interrupt_kernel(jp_fetch, kernel_id)

    # ensure kernel still considered running
    assert await is_kernel_running(jp_fetch, kernel_id) is True

    # restart
    await restart_kernel(jp_fetch, kernel_id)

    # ensure kernel still considered running
    assert await is_kernel_running(jp_fetch, kernel_id) is True

    # delete
    await delete_session(jp_fetch, session_id)
    assert await is_kernel_running(jp_fetch, kernel_id) is False


async def test_gateway_kernel_lifecycle(init_gateway, jp_fetch):
    # Validate kernel lifecycle functions; create, interrupt, restart and delete.

    # create
    kernel_id = await create_kernel(jp_fetch, "kspec_bar")

    # ensure kernel still considered running
    assert await is_kernel_running(jp_fetch, kernel_id) is True

    # interrupt
    await interrupt_kernel(jp_fetch, kernel_id)

    # ensure kernel still considered running
    assert await is_kernel_running(jp_fetch, kernel_id) is True

    # restart
    await restart_kernel(jp_fetch, kernel_id)

    # ensure kernel still considered running
    assert await is_kernel_running(jp_fetch, kernel_id) is True

    # delete
    await delete_kernel(jp_fetch, kernel_id)
    assert await is_kernel_running(jp_fetch, kernel_id) is False


@pytest.mark.parametrize("missing_kernel", [True, False])
async def test_gateway_shutdown(init_gateway, jp_serverapp, jp_fetch, missing_kernel):
    # Validate server shutdown when multiple gateway kernels are present or
    # we've lost track of at least one (missing) kernel

    # create two kernels
    k1 = await create_kernel(jp_fetch, "kspec_bar")
    k2 = await create_kernel(jp_fetch, "kspec_bar")

    # ensure they're considered running
    assert await is_kernel_running(jp_fetch, k1) is True
    assert await is_kernel_running(jp_fetch, k2) is True

    if missing_kernel:
        running_kernels.pop(k1)  # "terminate" kernel w/o our knowledge

    with mocked_gateway:
        await jp_serverapp.kernel_manager.shutdown_all()

    assert await is_kernel_running(jp_fetch, k1) is False
    assert await is_kernel_running(jp_fetch, k2) is False


@patch("websocket.create_connection", mock_websocket_create_connection(recv_side_effect=Exception))
async def test_kernel_client_response_router_notifies_channel_queue_when_finished(
    init_gateway, jp_serverapp, jp_fetch
):
    # create
    kernel_id = await create_kernel(jp_fetch, "kspec_bar")

    # get kernel manager
    km: GatewayKernelManager = jp_serverapp.kernel_manager.get_kernel(kernel_id)

    # create kernel client
    kc = km.client()

    await ensure_async(kc.start_channels())

    with pytest.raises(RuntimeError):
        await kc.iopub_channel.get_msg(timeout=10)

    all_channels = [
        kc.shell_channel,
        kc.iopub_channel,
        kc.stdin_channel,
        kc.hb_channel,
        kc.control_channel,
    ]
    assert all(channel.response_router_finished if True else False for channel in all_channels)

    await ensure_async(kc.stop_channels())

    # delete
    await delete_kernel(jp_fetch, kernel_id)


async def test_channel_queue_get_msg_with_invalid_timeout():
    queue = ChannelQueue("iopub", MagicMock(), logging.getLogger())

    with pytest.raises(ValueError):
        await queue.get_msg(timeout=-1)


async def test_channel_queue_get_msg_raises_empty_after_timeout():
    queue = ChannelQueue("iopub", MagicMock(), logging.getLogger())

    with pytest.raises(Empty):
        await asyncio.wait_for(queue.get_msg(timeout=0.1), 2)


async def test_channel_queue_get_msg_without_timeout():
    queue = ChannelQueue("iopub", MagicMock(), logging.getLogger())

    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(queue.get_msg(timeout=None), 1)


async def test_channel_queue_get_msg_with_existing_item():
    sent_message = {"msg_id": 1, "msg_type": 2}
    queue = ChannelQueue("iopub", MagicMock(), logging.getLogger())
    queue.put_nowait(sent_message)

    received_message = await asyncio.wait_for(queue.get_msg(timeout=None), 1)

    assert received_message == sent_message


async def test_channel_queue_get_msg_when_response_router_had_finished():
    queue = ChannelQueue("iopub", MagicMock(), logging.getLogger())
    queue.response_router_finished = True

    with pytest.raises(RuntimeError):
        await queue.get_msg()


#
# Test methods below...
#
async def create_session(root_dir, jp_fetch, kernel_name):
    """Creates a session for a kernel.  The session is created against the server
    which then uses the gateway for kernel management.
    """
    with mocked_gateway:
        nb_path = root_dir / "testgw.ipynb"
        body = json.dumps(
            {"path": str(nb_path), "type": "notebook", "kernel": {"name": kernel_name}}
        )

        # add a KERNEL_ value to the current env and we'll ensure that that value exists in the mocked method
        os.environ["KERNEL_KSPEC_NAME"] = kernel_name

        # Create the kernel... (also tests get_kernel)
        r = await jp_fetch("api", "sessions", method="POST", body=body)
        assert r.code == 201
        model = json.loads(r.body.decode("utf-8"))
        assert model.get("path") == str(nb_path)
        kernel_id = model.get("kernel").get("id")
        # ensure its in the running_kernels and name matches.
        running_kernel = running_kernels.get(kernel_id)
        assert running_kernel is not None
        assert kernel_id == running_kernel.get("id")
        assert model.get("kernel").get("name") == running_kernel.get("name")
        session_id = model.get("id")

        # restore env
        os.environ.pop("KERNEL_KSPEC_NAME")
        return session_id, kernel_id


async def delete_session(jp_fetch, session_id):
    """Deletes a session corresponding to the given session id."""
    with mocked_gateway:
        # Delete the session (and kernel)
        r = await jp_fetch("api", "sessions", session_id, method="DELETE")
        assert r.code == 204
        assert r.reason == "No Content"


async def is_kernel_running(jp_fetch, kernel_id):
    """Issues request to get the set of running kernels"""
    with mocked_gateway:
        # Get list of running kernels
        r = await jp_fetch("api", "kernels", method="GET")
        assert r.code == 200
        kernels = json.loads(r.body.decode("utf-8"))
        assert len(kernels) == len(running_kernels)
        for model in kernels:
            if model.get("id") == kernel_id:
                return True
        return False


async def create_kernel(jp_fetch, kernel_name):
    """Issues request to retart the given kernel"""
    with mocked_gateway:
        body = json.dumps({"name": kernel_name})

        # add a KERNEL_ value to the current env and we'll ensure that that value exists in the mocked method
        os.environ["KERNEL_KSPEC_NAME"] = kernel_name

        r = await jp_fetch("api", "kernels", method="POST", body=body)
        assert r.code == 201
        model = json.loads(r.body.decode("utf-8"))
        kernel_id = model.get("id")
        # ensure its in the running_kernels and name matches.
        running_kernel = running_kernels.get(kernel_id)
        assert running_kernel is not None
        assert kernel_id == running_kernel.get("id")
        assert model.get("name") == kernel_name

        # restore env
        os.environ.pop("KERNEL_KSPEC_NAME")
        return kernel_id


async def interrupt_kernel(jp_fetch, kernel_id):
    """Issues request to interrupt the given kernel"""
    with mocked_gateway:
        r = await jp_fetch(
            "api",
            "kernels",
            kernel_id,
            "interrupt",
            method="POST",
            allow_nonstandard_methods=True,
        )
        assert r.code == 204
        assert r.reason == "No Content"


async def restart_kernel(jp_fetch, kernel_id):
    """Issues request to retart the given kernel"""
    with mocked_gateway:
        r = await jp_fetch(
            "api",
            "kernels",
            kernel_id,
            "restart",
            method="POST",
            allow_nonstandard_methods=True,
        )
        assert r.code == 200
        model = json.loads(r.body.decode("utf-8"))
        restarted_kernel_id = model.get("id")
        # ensure its in the running_kernels and name matches.
        running_kernel = running_kernels.get(restarted_kernel_id)
        assert running_kernel is not None
        assert restarted_kernel_id == running_kernel.get("id")
        assert model.get("name") == running_kernel.get("name")


async def delete_kernel(jp_fetch, kernel_id):
    """Deletes kernel corresponding to the given kernel id."""
    with mocked_gateway:
        # Delete the session (and kernel)
        r = await jp_fetch("api", "kernels", kernel_id, method="DELETE")
        assert r.code == 204
        assert r.reason == "No Content"
