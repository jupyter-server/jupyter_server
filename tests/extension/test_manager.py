import pytest
from jupyter_server.extension.manager import (
    ExtensionPoint,
    ExtensionPackage,
    ExtensionManager,
    ExtensionMetadataError,
    ExtensionModuleNotFound
)

# Use ServerApps environment because it monkeypatches
# jupyter_core.paths and provides a config directory
# that's not cross contaminating the user config directory.
pytestmark = pytest.mark.usefixtures("environ")


def test_extension_point_api():
    # Import mock extension metadata
    from .mockextensions import _jupyter_server_extension_points

    # Testing the first path (which is an extension app).
    metadata_list = _jupyter_server_extension_points()
    point = metadata_list[0]

    module = point["module"]
    app = point["app"]

    e = ExtensionPoint(metadata=point)
    assert e.module_name == module
    assert e.name == app.name
    assert app is not None
    assert callable(e.load)
    assert callable(e.link)


def test_extension_point_metadata_error():
    # Missing the "module" key.
    bad_metadata = {"name": "nonexistent"}
    with pytest.raises(ExtensionMetadataError):
        ExtensionPoint(metadata=bad_metadata)


def test_extension_point_notfound_error():
    bad_metadata = {"module": "nonexistent"}
    with pytest.raises(ExtensionModuleNotFound):
        ExtensionPoint(metadata=bad_metadata)


def test_extension_package_api():
    # Import mock extension metadata
    from .mockextensions import _jupyter_server_extension_points

    # Testing the first path (which is an extension app).
    metadata_list = _jupyter_server_extension_points()
    path1 = metadata_list[0]
    app = path1["app"]

    e = ExtensionPackage(name='tests.extension.mockextensions')
    e.extension_points
    assert hasattr(e, "extension_points")
    assert len(e.extension_points) == len(metadata_list)
    assert app.name in e.extension_points


def test_extension_package_notfound_error():
    with pytest.raises(ExtensionModuleNotFound):
        ExtensionPackage(name="nonexistent")


def test_extension_manager_api():
    jpserver_extensions = {
        "tests.extension.mockextensions": True
    }
    manager = ExtensionManager()
    manager.from_jpserver_extensions(jpserver_extensions)
    assert len(manager.extensions) == 1
    assert "tests.extension.mockextensions" in manager.extensions

