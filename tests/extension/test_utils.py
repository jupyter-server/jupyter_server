import pytest
from jupyter_server.extension.utils import (
    list_extensions_in_configd,
    configd_enabled,
    validate_extension
)

# Use ServerApps environment because it monkeypatches
# jupyter_core.paths and provides a config directory
# that's not cross contaminating the user config directory.
pytestmark = pytest.mark.usefixtures("environ")


@pytest.fixture
def configd(env_config_path):
    """A pathlib.Path object that acts like a jupyter_server_config.d folder."""
    configd = env_config_path.joinpath('jupyter_server_config.d')
    configd.mkdir()
    return configd


ext1_json_config = """\
{
    "ServerApp": {
        "jpserver_extensions": {
            "ext1_config": true
        }
    }
}
"""

@pytest.fixture
def ext1_config(configd):
    config = configd.joinpath("ext1_config.json")
    config.write_text(ext1_json_config)


ext2_json_config = """\
{
    "ServerApp": {
        "jpserver_extensions": {
            "ext2_config": false
        }
    }
}
"""


@pytest.fixture
def ext2_config(configd):
    config = configd.joinpath("ext2_config.json")
    config.write_text(ext2_json_config)


def test_list_extension_from_configd(ext1_config, ext2_config):
    extensions = list_extensions_in_configd()
    assert "ext2_config" in extensions
    assert "ext1_config" in extensions


def test_config_enabled(ext1_config):
    assert configd_enabled("ext1_config")


def test_validate_extension():
    # enabled at sys level
    assert validate_extension('tests.extension.mockextensions.mockext_sys')
    # enabled at sys, disabled at user
    assert validate_extension('tests.extension.mockextensions.mockext_both')
    # enabled at user
    assert validate_extension('tests.extension.mockextensions.mockext_user')
    # enabled at Python
    assert validate_extension('tests.extension.mockextensions.mockext_py')