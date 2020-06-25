import pytest
from jupyter_server.extension.manager import (
    ExtensionPoint,
    ExtensionPackage,
    ExtensionManager,
    ExtensionMetadataError,
    ExtensionModuleNotFound
)


def test_extension_point_api():
    # Import mock extension metadata
    from .mockextensions import _jupyter_server_extension_paths

    # Testing the first path (which is an extension app).
    metadata_list = _jupyter_server_extension_paths()
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


def test_extension_package_notfound_error():
    with pytest.raises(ExtensionModuleNotFound):
        ExtensionPackage(name="nonexistent")


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

