from collections import OrderedDict

import pytest

try:
    from jupyter_core.paths import prefer_environment_over_user
except ImportError:
    prefer_environment_over_user = None

from traitlets.tests.utils import check_help_all_output

from jupyter_server.config_manager import BaseJSONConfigManager
from jupyter_server.extension.serverextension import (
    DisableServerExtensionApp,
    ListServerExtensionsApp,
    ServerExtensionApp,
    ToggleServerExtensionApp,
    _get_config_dir,
    toggle_server_extension_python,
)

# Use ServerApps environment because it monkeypatches
# jupyter_core.paths and provides a config directory
# that's not cross contaminating the user config directory.
pytestmark = pytest.mark.usefixtures("jp_environ")


def test_help_output():
    check_help_all_output("jupyter_server.extension.serverextension")
    check_help_all_output("jupyter_server.extension.serverextension", ["enable"])
    check_help_all_output("jupyter_server.extension.serverextension", ["disable"])
    check_help_all_output("jupyter_server.extension.serverextension", ["install"])
    check_help_all_output("jupyter_server.extension.serverextension", ["uninstall"])


def get_config(sys_prefix=True):
    cm = BaseJSONConfigManager(config_dir=_get_config_dir(sys_prefix=sys_prefix))
    data = cm.get("jupyter_server_config")
    return data.get("ServerApp", {}).get("jpserver_extensions", {})


def test_enable(jp_env_config_path, jp_extension_environ):
    toggle_server_extension_python("mock1", True)
    config = get_config()
    assert config["mock1"]


def test_disable(jp_env_config_path, jp_extension_environ):
    toggle_server_extension_python("mock1", True)
    toggle_server_extension_python("mock1", False)

    config = get_config()
    assert not config["mock1"]


@pytest.mark.skipif(prefer_environment_over_user is None, reason="Requires jupyter_core 5.0+")
def test_merge_config(jp_env_config_path, jp_configurable_serverapp, jp_extension_environ):
    # Toggle each extension module with a JSON config file
    # at the sys-prefix config dir.
    toggle_server_extension_python(
        "tests.extension.mockextensions.mockext_sys",
        enabled=True,
        sys_prefix=True,
    )
    toggle_server_extension_python(
        "tests.extension.mockextensions.mockext_user",
        enabled=True,
        user=True,
    )

    # Write this configuration in two places, sys-prefix and user.
    # sys-prefix supercedes users, so the extension should be disabled
    # when these two configs merge.
    toggle_server_extension_python(
        "tests.extension.mockextensions.mockext_both",
        enabled=False,
        sys_prefix=True,
    )
    toggle_server_extension_python(
        "tests.extension.mockextensions.mockext_both",
        enabled=True,
        user=True,
    )

    mockext_py = "tests.extension.mockextensions.mockext_py"
    argv = ["--ServerApp.jpserver_extensions", f"{mockext_py}=True"]

    # Enable the last extension, mockext_py, using the CLI interface.
    app = jp_configurable_serverapp(config_dir=str(jp_env_config_path), argv=argv)
    # Verify that extensions are enabled and merged in proper order.
    extensions = app.jpserver_extensions
    assert extensions["tests.extension.mockextensions.mockext_user"]
    assert extensions["tests.extension.mockextensions.mockext_sys"]
    assert extensions["tests.extension.mockextensions.mockext_py"]
    # Merging should causes this extension to be disabled.
    if prefer_environment_over_user():
        assert not extensions["tests.extension.mockextensions.mockext_both"]


@pytest.mark.parametrize(
    "jp_server_config",
    [
        {
            "ServerApp": {
                "jpserver_extensions": OrderedDict(
                    [
                        ("tests.extension.mockextensions.mock2", True),
                        ("tests.extension.mockextensions.mock1", True),
                    ]
                )
            }
        }
    ],
)
def test_load_ordered(jp_serverapp, jp_server_config):
    assert jp_serverapp.mockII is True, "Mock II should have been loaded"
    assert jp_serverapp.mockI is True, "Mock I should have been loaded"
    assert jp_serverapp.mock_shared == "II", "Mock II should be loaded after Mock I"


def test_server_extension_apps(jp_env_config_path, jp_extension_environ):
    app = ToggleServerExtensionApp()
    app.extra_args = "mock1"
    app.start()

    app = DisableServerExtensionApp()
    app.extra_args = "mock1"
    app.start()

    app = ListServerExtensionsApp()
    app.start()


def test_server_extension_app():
    app = ServerExtensionApp()
    app.launch_instance(["list"])
