import sys
import pytest
from collections import OrderedDict

from types import SimpleNamespace

from traitlets.tests.utils import check_help_all_output

from ..utils import mkdir

from jupyter_server.serverapp import ServerApp
from jupyter_server.extension import serverextension
from jupyter_server.extension.serverextension import (
    validate_server_extension,
    toggle_server_extension_python,
    _get_config_dir
)
from jupyter_server.config_manager import BaseJSONConfigManager


def test_help_output():
    check_help_all_output('jupyter_server.extension.serverextension')
    check_help_all_output('jupyter_server.extension.serverextension', ['enable'])
    check_help_all_output('jupyter_server.extension.serverextension', ['disable'])
    check_help_all_output('jupyter_server.extension.serverextension', ['install'])
    check_help_all_output('jupyter_server.extension.serverextension', ['uninstall'])


def get_config(sys_prefix=True):
    cm = BaseJSONConfigManager(config_dir=_get_config_dir(sys_prefix=sys_prefix))
    data = cm.get("jupyter_server_config")
    return data.get("ServerApp", {}).get("jpserver_extensions", {})


def test_enable():
    toggle_server_extension_python('mock1', True)
    config = get_config()
    assert config['mock1']


def test_disable():
    toggle_server_extension_python('mock1', True)
    toggle_server_extension_python('mock1', False)

    config = get_config()
    assert not config['mock1']


def test_merge_config(
    env_config_path,
    configurable_serverapp
    ):
    # enabled at sys level
    validate_server_extension('tests.extension.mockextensions.mockext_sys')
    # enabled at sys, disabled at user
    validate_server_extension('tests.extension.mockextensions.mockext_both')
    # enabled at user
    validate_server_extension('tests.extension.mockextensions.mockext_user')
    # enabled at Python
    validate_server_extension('tests.extension.mockextensions.mockext_py')

    # Toggle each extension module with a JSON config file
    # at the sys-prefix config dir.
    toggle_server_extension_python(
        'tests.extension.mockextensions.mockext_sys',
        enabled=True,
        sys_prefix=True
    )
    toggle_server_extension_python(
        'tests.extension.mockextensions.mockext_user',
        enabled=True,
        user=True
    )

    # Write this configuration in two places, sys-prefix and user.
    # sys-prefix supercedes users, so the extension should be disabled
    # when these two configs merge.
    toggle_server_extension_python(
        'tests.extension.mockextensions.mockext_both',
        enabled=True,
        user=True
    )
    toggle_server_extension_python(
        'tests.extension.mockextensions.mockext_both',
        enabled=False,
        sys_prefix=True
    )

    arg = "--ServerApp.jpserver_extensions={{'{mockext_py}': True}}".format(
        mockext_py='tests.extension.mockextensions.mockext_py'
    )

    # Enable the last extension, mockext_py, using the CLI interface.
    app = configurable_serverapp(
        config_dir=str(env_config_path),
        argv=[arg]
    )
    # Verify that extensions are enabled and merged properly.
    extensions = app.jpserver_extensions
    assert extensions['tests.extension.mockextensions.mockext_user']
    assert extensions['tests.extension.mockextensions.mockext_sys']
    assert extensions['tests.extension.mockextensions.mockext_py']
    # Merging should causes this extension to be disabled.
    assert not extensions['tests.extension.mockextensions.mockext_both']


def test_load_ordered(configurable_serverapp):
    app = configurable_serverapp(
        jpserver_extensions=OrderedDict([
            ('tests.extension.mockextensions.mock2', True),
            ('tests.extension.mockextensions.mock1', True)
        ])
    )
    assert app.mockII is True, "Mock II should have been loaded"
    assert app.mockI is True, "Mock I should have been loaded"
    assert app.mock_shared == 'II', "Mock II should be loaded after Mock I"

