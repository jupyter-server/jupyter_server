import sys
import pytest
from traitlets.config import Config
from jupyter_server.services.kernels.kernelmanager import AsyncMappingKernelManager


@pytest.fixture
def server_config():
    return Config({
        'ServerApp': {
            'MappingKernelManager': {
                'allowed_message_types': ['kernel_info_request']
            }
        }
    })


def test_config(serverapp):
    assert serverapp.kernel_manager.allowed_message_types == ['kernel_info_request']


async def test_async_kernel_manager(configurable_serverapp):
    argv = ['--ServerApp.kernel_manager_class=jupyter_server.services.kernels.kernelmanager.AsyncMappingKernelManager']
    app = configurable_serverapp(argv=argv)
    assert isinstance(app.kernel_manager, AsyncMappingKernelManager)

