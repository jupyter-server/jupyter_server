import sys
import pytest
from collections import OrderedDict

from types import SimpleNamespace

from traitlets.tests.utils import check_help_all_output

from .conftest import mkdir

from jupyter_core import paths
from jupyter_server.serverapp import ServerApp
from jupyter_server import extensions, extensions_base
from jupyter_server.extensions import toggle_serverextension_python, _get_config_dir
from jupyter_server.config_manager import BaseJSONConfigManager


def test_help_output():
    check_help_all_output('jupyter_server.extensions')
    check_help_all_output('jupyter_server.extensions', ['enable'])
    check_help_all_output('jupyter_server.extensions', ['disable'])
    check_help_all_output('jupyter_server.extensions', ['install'])
    check_help_all_output('jupyter_server.extensions', ['uninstall'])


outer_file = __file__


@pytest.fixture
def environ(
    monkeypatch,
    tmp_path,
    data_dir,
    config_dir,
    ):
    system_data_dir = tmp_path / 'system_data'
    system_config_dir = tmp_path / 'system_config'
    system_path = [str(system_data_dir)]
    system_config_path = [str(system_config_dir)] 

    # Set global environments variable
    monkeypatch.setenv('JUPYTER_CONFIG_DIR', str(config_dir))
    monkeypatch.setenv('JUPYTER_DATA_DIR', str(data_dir))

    # Set paths for each extension.
    for mod in (paths,):
        monkeypatch.setattr(mod, 'SYSTEM_JUPYTER_PATH', system_path)
        monkeypatch.setattr(mod, 'ENV_JUPYTER_PATH', [])
    for mod in (paths, extensions_base):
        monkeypatch.setattr(mod, 'SYSTEM_CONFIG_PATH', system_config_path)
        monkeypatch.setattr(mod, 'ENV_CONFIG_PATH', [])

    assert paths.jupyter_config_path() == [str(config_dir)] + system_config_path
    assert extensions_base._get_config_dir(user=False) == str(system_config_dir)
    assert paths.jupyter_path() == [str(data_dir)] + system_path


class MockExtensionModule(object):
    __file__ = outer_file

    @staticmethod
    def _jupyter_server_extension_paths():
        return [{
            'module': '_mockdestination/index'
        }]

    loaded = False

    def load_jupyter_server_extension(self, app):
        self.loaded = True


def get_config(user=True):
    cm = BaseJSONConfigManager(config_dir=_get_config_dir(user))
    data = cm.get("jupyter_server_config")
    return data.get("ServerApp", {}).get("jpserver_extensions", {})


@pytest.fixture
def inject_mock_extension(environ):
    def ext(modulename='mockextension'):
        sys.modules[modulename] = e = MockExtensionModule()
        return e
    return ext


def test_enable(inject_mock_extension):
    inject_mock_extension()
    toggle_serverextension_python('mockextension', True)
    config = get_config()
    assert config['mockextension']


def test_disable(inject_mock_extension):
    inject_mock_extension()
    toggle_serverextension_python('mockextension', True)
    toggle_serverextension_python('mockextension', False)

    config = get_config()
    assert not config['mockextension']


def test_merge_config(inject_mock_extension):
    # enabled at sys level
    mock_sys = inject_mock_extension('mockext_sys')
    # enabled at sys, disabled at user
    mock_both = inject_mock_extension('mockext_both')
    # enabled at user
    mock_user = inject_mock_extension('mockext_user')
    # enabled at Python
    mock_py = inject_mock_extension('mockext_py')

    toggle_serverextension_python('mockext_sys', enabled=True, user=False)
    toggle_serverextension_python('mockext_user', enabled=True, user=True)
    toggle_serverextension_python('mockext_both', enabled=True, user=False)
    toggle_serverextension_python('mockext_both', enabled=False, user=True)

    app = ServerApp(jpserver_extensions={'mockext_py': True})
    app.init_server_extension_config()
    app.init_server_extensions()

    assert mock_user.loaded
    assert mock_sys.loaded
    assert mock_py.loaded
    assert not mock_both.loaded


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
