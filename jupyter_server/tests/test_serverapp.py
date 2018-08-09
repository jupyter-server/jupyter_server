"""Test ServerApp"""

import getpass
import logging
import os
import re
from tempfile import NamedTemporaryFile

from unittest.mock import patch
import pytest

from tempfile import TemporaryDirectory

from traitlets.tests.utils import check_help_all_output
from traitlets import TraitError

from jupyter_core.application import NoStart
from jupyter_server import serverapp, __version__
from jupyter_server.auth.security import passwd_check

ServerApp = serverapp.ServerApp


def test_help_output():
    """jupyter server --help-all works"""
    check_help_all_output('jupyter_server')


def test_server_info_file():
    td = TemporaryDirectory()
    svapp = ServerApp(runtime_dir=td.name, log=logging.getLogger())

    def get_servers():
        return list(serverapp.list_running_servers(svapp.runtime_dir))

    svapp.initialize(argv=[])
    svapp.write_server_info_file()
    servers = get_servers()
    assert len(servers) == 1
    assert servers[0]['port'] == svapp.port
    assert servers[0]['url'] == svapp.connection_url
    svapp.remove_server_info_file()
    assert get_servers() == []

    # The ENOENT error should be silenced.
    svapp.remove_server_info_file()


def test_root_dir():
    with TemporaryDirectory() as td:
        app = ServerApp(root_dir=td)
        assert app.root_dir == td


def test_no_create_root_dir():
    with TemporaryDirectory() as td:
        rootdir = os.path.join(td, 'notebooks')
        app = ServerApp()
        with pytest.raises(TraitError):
            app.root_dir = rootdir


def test_missing_root_dir():
    with TemporaryDirectory() as td:
        rootdir = os.path.join(td, 'root', 'dir', 'is', 'missing')
        app = ServerApp()
        with pytest.raises(TraitError):
            app.root_dir = rootdir


def test_invalid_root_dir():
    with NamedTemporaryFile() as tf:
        app = ServerApp()
        with pytest.raises(TraitError):
            app.root_dir = tf


def test_root_dir_with_slash():
    with TemporaryDirectory(suffix="_slash" + os.sep) as td:
        app = ServerApp(root_dir=td)
        assert not app.root_dir.endswith(os.sep)


def test_root_dir_root():
    root = os.path.abspath(os.sep)  # gets the right value on Windows, Posix
    app = ServerApp(root_dir=root)
    assert app.root_dir == root


def test_generate_config():
    with TemporaryDirectory() as td:
        app = ServerApp(config_dir=td)
        app.initialize(['--generate-config', '--allow-root'])
        with pytest.raises(NoStart):
            app.start()
        assert os.path.exists(os.path.join(td, 'jupyter_server_config.py'))


# test if the version testin function works
def test_pep440_version():

    for version in [
        '4.1.0.b1',
        '4.1.b1',
        '4.2',
        'X.y.z',
        '1.2.3.dev1.post2',
        ]:
        def loc():
            with pytest.raises(ValueError):
                raise_on_bad_version(version)
        yield loc


pep440re = re.compile('^(\d+)\.(\d+)\.(\d+((a|b|rc)\d+)?)(\.post\d+)?(\.dev\d*)?$')


def raise_on_bad_version(version):
    if not pep440re.match(version):
        raise ValueError("Versions String does apparently not match Pep 440 specification, "
                         "which might lead to sdist and wheel being seen as 2 different release. "
                         "E.g: do not use dots for beta/alpha/rc markers.")


def test_current_version():
    raise_on_bad_version(__version__)


def test_server_password():
    password = 'secret'
    with TemporaryDirectory() as td:
        with patch.dict('os.environ', {
            'JUPYTER_CONFIG_DIR': td,
        }), patch.object(getpass, 'getpass', return_value=password):
            app = serverapp.JupyterPasswordApp(log_level=logging.ERROR)
            app.initialize([])
            app.start()
            sv = ServerApp()
            sv.load_config_file()
            assert sv.password != ''
            passwd_check(sv.password, password)


class TestingStopApp(serverapp.JupyterServerStopApp):
    """For testing the logic of JupyterServerStopApp."""

    def __init__(self, **kwargs):
        super(TestingStopApp, self).__init__(**kwargs)
        self.servers_shut_down = []

    def shutdown_server(self, server):
        self.servers_shut_down.append(server)
        return True


def test_server_stop():
    def list_running_servers(runtime_dir):
        for port in range(100, 110):
            yield {
                'pid': 1000 + port,
                'port': port,
                'base_url': '/',
                'hostname': 'localhost',
                'root_dir': '/',
                'secure': False,
                'token': '',
                'password': False,
                'url': 'http://localhost:%i' % port,
            }

    mock_servers = patch('jupyter_server.serverapp.list_running_servers', list_running_servers)

    # test stop with a match
    with mock_servers:
        app = TestingStopApp()
        app.initialize(['105'])
        app.start()
    assert len(app.servers_shut_down) == 1
    assert app.servers_shut_down[0]['port'] == 105

    # test no match
    with mock_servers, patch('os.kill'):
        app = TestingStopApp()
        app.initialize(['999'])
        with pytest.raises(SystemExit) as exc:
            app.start()
        assert exc.value.code == 1
    assert len(app.servers_shut_down) == 0
