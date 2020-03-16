import pytest
from traitlets.config import Config


@pytest.fixture
def config():
    return Config({
        'ServerApp': {
            'AsyncMappingKernelManager': {
                'allowed_message_types': ['kernel_info_request']
            }
        }
    })


def test_config(serverapp):
    assert serverapp.kernel_manager.allowed_message_types == ['kernel_info_request']
