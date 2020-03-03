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


def test_enable(inject_mock_extension):
    inject_mock_extension()
    toggle_server_extension_python('mockextension', True)
    config = get_config()
    assert config['mockextension']


def test_disable(inject_mock_extension):
    inject_mock_extension()
    toggle_server_extension_python('mockextension', True)
    toggle_server_extension_python('mockextension', False)

    config = get_config()
    assert not config['mockextension']


def test_merge_config(
    env_config_path,
    inject_mock_extension,
    configurable_serverapp
    ):
    # enabled at sys level
    inject_mock_extension('mockext_sys')
    validate_server_extension('mockext_sys')
    # enabled at sys, disabled at user
    inject_mock_extension('mockext_both')
    validate_server_extension('mockext_both')
    # enabled at user
    inject_mock_extension('mockext_user')
    validate_server_extension('mockext_user')
    # enabled at Python
    inject_mock_extension('mockext_py')
    validate_server_extension('mockext_py')

    # Toggle each extension module with a JSON config file
    # at the sys-prefix config dir.
    toggle_server_extension_python('mockext_sys', enabled=True, sys_prefix=True)
    toggle_server_extension_python('mockext_user', enabled=True, user=True)

    # Write this configuration in two places, sys-prefix and user.
    # sys-prefix supercedes users, so the extension should be disabled
    # when these two configs merge.
    toggle_server_extension_python('mockext_both', enabled=True, user=True)
    toggle_server_extension_python('mockext_both', enabled=False, sys_prefix=True)

    # Enable the last extension, mockext_py, using the CLI interface.
    app = configurable_serverapp(
        config_dir=str(env_config_path),
        argv=['--ServerApp.jpserver_extensions={"mockext_py":True}']
    )
    # Verify that extensions are enabled and merged properly.
    extensions = app.jpserver_extensions
    assert extensions['mockext_user']
    assert extensions['mockext_sys']
    assert extensions['mockext_py']
    # Merging should causes this extension to be disabled.
    assert not extensions['mockext_both']


@pytest.fixture
def ordered_server_extensions():
    mockextension1 = SimpleNamespace()
    mockextension2 = SimpleNamespace()

    def load_jupyter_server_extension(obj):
        obj.mockI = True
        obj.mock_shared = 'I'

    mockextension1.load_jupyter_server_extension = load_jupyter_server_extension

    def load_jupyter_server_extension(obj):
        obj.mockII = True
        obj.mock_shared = 'II'

    mockextension2.load_jupyter_server_extension = load_jupyter_server_extension

    sys.modules['mockextension2'] = mockextension2
    sys.modules['mockextension1'] = mockextension1


def test_load_ordered(ordered_server_extensions):
    app = ServerApp()
    app.jpserver_extensions = OrderedDict([('mockextension2',True),('mockextension1',True)])

    app.init_server_extensions()

    assert app.mockII is True, "Mock II should have been loaded"
    assert app.mockI is True, "Mock I should have been loaded"
    assert app.mock_shared == 'II', "Mock II should be loaded after Mock I"

