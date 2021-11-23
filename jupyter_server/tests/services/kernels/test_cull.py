import asyncio
import json
import platform

import pytest
from tornado.httpclient import HTTPClientError
from traitlets.config import Config


@pytest.fixture(params=["MappingKernelManager", "AsyncMappingKernelManager"])
def jp_argv(request):
    return [
        "--ServerApp.kernel_manager_class=jupyter_server.services.kernels.kernelmanager."
        + request.param
    ]


CULL_TIMEOUT = 30 if platform.python_implementation() == "PyPy" else 5
CULL_INTERVAL = 1


@pytest.fixture
def jp_server_config():
    return Config(
        {
            "ServerApp": {
                "MappingKernelManager": {
                    "cull_idle_timeout": CULL_TIMEOUT,
                    "cull_interval": CULL_INTERVAL,
                    "cull_connected": False,
                }
            }
        }
    )


async def test_cull_idle(jp_fetch, jp_ws_fetch, jp_cleanup_subprocesses):
    r = await jp_fetch("api", "kernels", method="POST", allow_nonstandard_methods=True)
    kernel = json.loads(r.body.decode())
    kid = kernel["id"]

    # Open a websocket connection.
    ws = await jp_ws_fetch("api", "kernels", kid, "channels")

    r = await jp_fetch("api", "kernels", kid, method="GET")
    model = json.loads(r.body.decode())
    assert model["connections"] == 1
    culled = await get_cull_status(kid, jp_fetch)  # connected, should not be culled
    assert not culled
    ws.close()
    culled = await get_cull_status(kid, jp_fetch)  # not connected, should be culled
    assert culled
    await jp_cleanup_subprocesses()


async def test_cull_dead(
    jp_fetch, jp_ws_fetch, jp_serverapp, jp_cleanup_subprocesses, jp_kernelspecs
):
    if not hasattr(jp_serverapp.kernel_manager, "use_pending_kernels"):
        return

    jp_serverapp.kernel_manager.use_pending_kernels = True
    jp_serverapp.kernel_manager.default_kernel_name = "bad"
    r = await jp_fetch("api", "kernels", method="POST", allow_nonstandard_methods=True)
    kernel = json.loads(r.body.decode())
    kid = kernel["id"]

    # Open a websocket connection.
    with pytest.raises(HTTPClientError):
        await jp_ws_fetch("api", "kernels", kid, "channels")

    r = await jp_fetch("api", "kernels", kid, method="GET")
    model = json.loads(r.body.decode())
    assert model["connections"] == 0
    culled = await get_cull_status(kid, jp_fetch)  # connected, should not be culled
    assert culled
    await jp_cleanup_subprocesses()


async def get_cull_status(kid, jp_fetch):
    frequency = 0.5
    culled = False
    for _ in range(
        int((CULL_TIMEOUT + CULL_INTERVAL) / frequency)
    ):  # Timeout + Interval will ensure cull
        try:
            r = await jp_fetch("api", "kernels", kid, method="GET")
            json.loads(r.body.decode())
        except HTTPClientError as e:
            assert e.code == 404
            culled = True
            break
        else:
            await asyncio.sleep(frequency)
    return culled
