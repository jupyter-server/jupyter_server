import pytest
from jupyter_server.extension.utils import (
    list_extensions_in_configd,
    configd_enabled,
    ExtensionPoint,
    ExtensionPackage,
    ExtensionManager
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


def test_extension_point_api():
    # Import mock extension metadata
    from .mockextensions import _jupyter_server_extension_paths

    # Testing the first path (which is an extension app).
    metadata_list = _jupyter_server_extension_paths()
    point = metadata_list[0]

    module = point["module"]
    app = point["app"]

    print(point)
    e = ExtensionPoint(metadata=point)
    assert e.module_name == module
    assert e.name == app.name
    assert app is not None
    assert callable(e.load)
    assert callable(e.link)


def test_extension_package_api():
    # Import mock extension metadata
    from .mockextensions import _jupyter_server_extension_paths

    # Testing the first path (which is an extension app).
    metadata_list = _jupyter_server_extension_paths()
    path1 = metadata_list[0]
    app = path1["app"]

    e = ExtensionPackage(name='tests.extension.mockextensions')
    e.extension_points
    assert hasattr(e, "extension_points")
    assert len(e.extension_points) == len(metadata_list)
    assert app.name in e.extension_points


def test_extension_manager_api():
    # Import mock extension metadata
    from .mockextensions import _jupyter_server_extension_paths

    # Testing the first path (which is an extension app).
    metadata_list = _jupyter_server_extension_paths()

    jpserver_extensions = {
        "tests.extension.mockextensions": True
    }
    manager = ExtensionManager(jpserver_extensions=jpserver_extensions)
    assert len(manager.extensions) == 1
    assert len(manager.extension_points) == len(metadata_list)
    assert "mockextension" in manager.extension_points
    assert "tests.extension.mockextensions.mock1" in manager.extension_points