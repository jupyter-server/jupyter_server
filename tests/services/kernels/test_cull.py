import asyncio
import datetime
import json
import os
import platform
import uuid
import warnings

import jupyter_client
import pytest
from tornado.httpclient import HTTPClientError
from traitlets.config import Config

CULL_TIMEOUT = 30 if platform.python_implementation() == "PyPy" else 5
CULL_INTERVAL = 1

sample_kernel_json_with_metadata = {
    "argv": ["cat", "{connection_file}"],
    "display_name": "Test kernel",
    "metadata": {"cull_idle_timeout": 0},
}


@pytest.fixture(autouse=True)
def suppress_deprecation_warnings():
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message="The synchronous MappingKernelManager",
            category=DeprecationWarning,
        )
        yield


@pytest.fixture
def jp_kernelspec_with_metadata(jp_data_dir):
    """Configures some sample kernelspecs in the Jupyter data directory."""
    kenrel_spec_name = "sample_with_metadata"
    sample_kernel_dir = jp_data_dir.joinpath("kernels", kenrel_spec_name)
    sample_kernel_dir.mkdir(parents=True)
    # Create kernel json file
    sample_kernel_file = sample_kernel_dir.joinpath("kernel.json")
    kernel_json = sample_kernel_json_with_metadata.copy()
    sample_kernel_file.write_text(json.dumps(kernel_json))
    # Create resources text
    sample_kernel_resources = sample_kernel_dir.joinpath("resource.txt")
    sample_kernel_resources.write_text("resource")


@pytest.mark.parametrize(
    "jp_server_config",
    [
        # Test the synchronous case
        Config(
            {
                "ServerApp": {
                    "kernel_manager_class": "jupyter_server.services.kernels.kernelmanager.MappingKernelManager",
                    "MappingKernelManager": {
                        "cull_idle_timeout": CULL_TIMEOUT,
                        "cull_interval": CULL_INTERVAL,
                        "cull_connected": False,
                    },
                }
            }
        ),
        # Test the async case
        Config(
            {
                "ServerApp": {
                    "kernel_manager_class": "jupyter_server.services.kernels.kernelmanager.AsyncMappingKernelManager",
                    "AsyncMappingKernelManager": {
                        "cull_idle_timeout": CULL_TIMEOUT,
                        "cull_interval": CULL_INTERVAL,
                        "cull_connected": False,
                    },
                }
            }
        ),
    ],
)
async def test_cull_idle(jp_fetch, jp_ws_fetch):
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


@pytest.mark.parametrize(
    "jp_server_config",
    [
        # Test the synchronous case
        Config(
            {
                "ServerApp": {
                    "kernel_manager_class": "jupyter_server.services.kernels.kernelmanager.MappingKernelManager",
                    "MappingKernelManager": {
                        "cull_idle_timeout": CULL_TIMEOUT,
                        "cull_interval": CULL_INTERVAL,
                        "cull_connected": True,
                    },
                }
            }
        ),
        # Test the async case
        Config(
            {
                "ServerApp": {
                    "kernel_manager_class": "jupyter_server.services.kernels.kernelmanager.AsyncMappingKernelManager",
                    "AsyncMappingKernelManager": {
                        "cull_idle_timeout": CULL_TIMEOUT,
                        "cull_interval": CULL_INTERVAL,
                        "cull_connected": True,
                    },
                }
            }
        ),
    ],
)
async def test_cull_connected(jp_fetch, jp_ws_fetch):
    r = await jp_fetch("api", "kernels", method="POST", allow_nonstandard_methods=True)
    kernel = json.loads(r.body.decode())
    kid = kernel["id"]

    # Open a websocket connection.
    ws = await jp_ws_fetch("api", "kernels", kid, "channels")
    session_id = uuid.uuid1().hex
    message_id = uuid.uuid1().hex
    await ws.write_message(
        json.dumps(
            {
                "channel": "shell",
                "header": {
                    "date": datetime.datetime.now(tz=datetime.UTC).isoformat(),
                    "session": session_id,
                    "msg_id": message_id,
                    "msg_type": "execute_request",
                    "username": "",
                    "version": "5.2",
                },
                "parent_header": {},
                "metadata": {},
                "content": {
                    "code": f"import time\ntime.sleep({CULL_TIMEOUT-1})",
                    "silent": False,
                    "allow_stdin": False,
                    "stop_on_error": True,
                },
                "buffers": [],
            }
        )
    )

    r = await jp_fetch("api", "kernels", kid, method="GET")
    model = json.loads(r.body.decode())
    assert model["connections"] == 1
    culled = await get_cull_status(
        kid, jp_fetch
    )  # connected, but code cell still running. Should not be culled
    assert not culled
    culled = await get_cull_status(kid, jp_fetch)  # still connected, but idle... should be culled
    assert culled
    ws.close()


async def test_cull_idle_disable(jp_fetch, jp_ws_fetch, jp_kernelspec_with_metadata):
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
    culled = await get_cull_status(kid, jp_fetch)  # not connected, should not be culled
    assert not culled


# Pending kernels was released in Jupyter Client 7.1
# It is currently broken on Windows (Jan 2022). When fixed, we can remove the Windows check.
# See https://github.com/jupyter-server/jupyter_server/issues/672
@pytest.mark.skipif(
    os.name == "nt" or jupyter_client._version.version_info < (7, 1),
    reason="Pending kernels require jupyter_client >= 7.1 on non-Windows",
)
@pytest.mark.parametrize(
    "jp_server_config",
    [
        Config(
            {
                "ServerApp": {
                    "kernel_manager_class": "jupyter_server.services.kernels.kernelmanager.AsyncMappingKernelManager",
                    "AsyncMappingKernelManager": {
                        "cull_idle_timeout": CULL_TIMEOUT,
                        "cull_interval": CULL_INTERVAL,
                        "cull_connected": False,
                        "default_kernel_name": "bad",
                        "use_pending_kernels": True,
                    },
                }
            }
        )
    ],
)
@pytest.mark.timeout(30)
async def test_cull_dead(jp_fetch, jp_ws_fetch, jp_serverapp, jp_kernelspecs):
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
