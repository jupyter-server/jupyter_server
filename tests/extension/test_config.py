import pytest
from jupyter_core.paths import jupyter_config_path

from jupyter_server.extension.config import ExtensionConfigManager

# Use ServerApps environment because it monkeypatches
# jupyter_core.paths and provides a config directory
# that's not cross contaminating the user config directory.
pytestmark = pytest.mark.usefixtures("jp_environ")


@pytest.fixture
def configd(jp_env_config_path):
    """A pathlib.Path object that acts like a jupyter_server_config.d folder."""
    configd = jp_env_config_path.joinpath("jupyter_server_config.d")
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
    manager = ExtensionConfigManager(read_config_path=jupyter_config_path())
    extensions = manager.get_jpserver_extensions()
    assert "ext2_config" in extensions
    assert "ext1_config" in extensions
