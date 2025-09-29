import pytest
from traitlets.config import Config

from jupyter_client.asynchronous.client import AsyncKernelClient
from jupyter_client.blocking.client import BlockingKernelClient
from jupyter_client.client import KernelClient
from jupyter_server.services.kernels.kernelmanager import AsyncMappingKernelManager, ServerKernelManager
from jupyter_server.utils import import_item


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


def test_server_kernel_manager_client_traits_via_config():
    """Test that ServerKernelManager client traits can be configured via Config object."""
    config = Config()
    config.ServerKernelManager.client_class = "jupyter_client.blocking.client.BlockingKernelClient"
    config.ServerKernelManager.client_factory = BlockingKernelClient

    km = ServerKernelManager(config=config)
    assert km.client_class == "jupyter_client.blocking.client.BlockingKernelClient"
    assert km.client_factory == BlockingKernelClient


def test_server_kernel_manager_client_traits_default_values():
    """Test that ServerKernelManager client traits have correct default values."""
    km = ServerKernelManager()
    assert km.client_class == "jupyter_client.asynchronous.AsyncKernelClient"
    # Default client_factory should be the AsyncKernelClient class
    assert km.client_factory == AsyncKernelClient


def test_server_kernel_manager_client_class_string_configuration():
    """Test that client_class can be configured with different string values."""
    config = Config()
    config.ServerKernelManager.client_class = "jupyter_client.client.KernelClient"

    km = ServerKernelManager(config=config)
    assert km.client_class == "jupyter_client.client.KernelClient"
