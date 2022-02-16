import os
import unittest.mock as mock

import pytest
from jupyter_core.paths import jupyter_config_path

from jupyter_server.extension.manager import ExtensionManager
from jupyter_server.extension.manager import ExtensionMetadataError
from jupyter_server.extension.manager import ExtensionModuleNotFound
from jupyter_server.extension.manager import ExtensionPackage
from jupyter_server.extension.manager import ExtensionPoint

# Use ServerApps environment because it monkeypatches
# jupyter_core.paths and provides a config directory
# that's not cross contaminating the user config directory.
pytestmark = pytest.mark.usefixtures("jp_environ")


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
    assert e.validate()


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

    e = ExtensionPackage(name="jupyter_server.tests.extension.mockextensions")
    e.extension_points
    assert hasattr(e, "extension_points")
    assert len(e.extension_points) == len(metadata_list)
    assert app.name in e.extension_points
    assert e.validate()


def test_extension_package_notfound_error():
    with pytest.raises(ExtensionModuleNotFound):
        ExtensionPackage(name="nonexistent")


def _normalize_path(path_list):
    return [p.rstrip(os.path.sep) for p in path_list]


def test_extension_manager_api(jp_serverapp):
    jpserver_extensions = {"jupyter_server.tests.extension.mockextensions": True}
    manager = ExtensionManager(serverapp=jp_serverapp)
    assert manager.config_manager
    expected = _normalize_path(os.path.join(jupyter_config_path()[0], "serverconfig"))
    assert _normalize_path(manager.config_manager.read_config_path[0]) == expected
    manager.from_jpserver_extensions(jpserver_extensions)
    assert len(manager.extensions) == 1
    assert "jupyter_server.tests.extension.mockextensions" in manager.extensions


def test_extension_manager_linked_extensions(jp_serverapp):
    name = "jupyter_server.tests.extension.mockextensions"
    manager = ExtensionManager(serverapp=jp_serverapp)
    manager.add_extension(name, enabled=True)
    manager.link_extension(name)
    assert name in manager.linked_extensions


def test_extension_manager_fail_add(jp_serverapp):
    name = "jupyter_server.tests.extension.notanextension"
    manager = ExtensionManager(serverapp=jp_serverapp)
    manager.add_extension(name, enabled=True)  # should only warn
    jp_serverapp.reraise_server_extension_failures = True
    with pytest.raises(ExtensionModuleNotFound):
        manager.add_extension(name, enabled=True)


def test_extension_manager_fail_link(jp_serverapp):
    name = "jupyter_server.tests.extension.mockextensions.app"
    with mock.patch(
        "jupyter_server.tests.extension.mockextensions.app.MockExtensionApp.parse_command_line",
        side_effect=RuntimeError,
    ):
        manager = ExtensionManager(serverapp=jp_serverapp)
        manager.add_extension(name, enabled=True)
        manager.link_extension(name)  # should only warn
        jp_serverapp.reraise_server_extension_failures = True
        with pytest.raises(RuntimeError):
            manager.link_extension(name)


def test_extension_manager_fail_load(jp_serverapp):
    name = "jupyter_server.tests.extension.mockextensions.app"
    with mock.patch(
        "jupyter_server.tests.extension.mockextensions.app.MockExtensionApp.initialize_handlers",
        side_effect=RuntimeError,
    ):
        manager = ExtensionManager(serverapp=jp_serverapp)
        manager.add_extension(name, enabled=True)
        manager.link_extension(name)
        manager.load_extension(name)  # should only warn
        jp_serverapp.reraise_server_extension_failures = True
        with pytest.raises(RuntimeError):
            manager.load_extension(name)
