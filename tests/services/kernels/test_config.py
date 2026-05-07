import pytest
from traitlets.config import Config

from jupyter_server.services.kernels.kernelmanager import (
    AsyncMappingKernelManager,
    MappingKernelManager,
)


@pytest.fixture
def jp_server_config():
    return Config(
        {"ServerApp": {"MappingKernelManager": {"allowed_message_types": ["kernel_info_request"]}}}
    )


def test_config(jp_serverapp):
    assert jp_serverapp.kernel_manager.allowed_message_types == ["kernel_info_request"]


def test_async_kernel_manager(jp_configurable_serverapp):
    argv = [
        "--ServerApp.kernel_manager_class=jupyter_server.services.kernels.kernelmanager.AsyncMappingKernelManager"
    ]
    app = jp_configurable_serverapp(argv=argv)
    assert isinstance(app.kernel_manager, AsyncMappingKernelManager)


def test_not_server_kernel_manager(jp_configurable_serverapp):
    argv = [
        "--AsyncMappingKernelManager.kernel_manager_class=jupyter_client.ioloop.manager.AsyncIOLoopKernelManager"
    ]
    with pytest.warns(FutureWarning, match="is not a subclass of 'ServerKernelManager'"):
        jp_configurable_serverapp(argv=argv)


def test_kernel_start_env_enable_curve_sets_variable():
    km = MappingKernelManager(enable_curve=True)

    source_env = {"EXISTING": "1"}
    launch_env = km._kernel_start_env(source_env)

    assert launch_env["EXISTING"] == "1"
    assert launch_env["JUPYTER_ENABLE_CURVE"] == "1"
    assert "JUPYTER_ENABLE_CURVE" not in source_env
