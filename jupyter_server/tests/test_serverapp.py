"""Test ServerApp"""

import getpass
import logging
import os
import re
import signal
from subprocess import Popen, PIPE, STDOUT
import sys
from tempfile import NamedTemporaryFile

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch # py2

import nose.tools as nt

from ipython_genutils.tempdir import TemporaryDirectory

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
    nt.assert_equal(len(servers), 1)
    nt.assert_equal(servers[0]['port'], svapp.port)
    nt.assert_equal(servers[0]['url'], svapp.connection_url)
    svapp.remove_server_info_file()
    nt.assert_equal(get_servers(), [])

    # The ENOENT error should be silenced.
    svapp.remove_server_info_file()

def test_root_dir():
    with TemporaryDirectory() as td:
        app = ServerApp(root_dir=td)
        nt.assert_equal(app.root_dir, td)

def test_no_create_root_dir():
    with TemporaryDirectory() as td:
        rootdir = os.path.join(td, 'notebooks')
        app = ServerApp()
        with nt.assert_raises(TraitError):
            app.root_dir = rootdir

def test_missing_root_dir():
    with TemporaryDirectory() as td:
        rootdir = os.path.join(td, 'root', 'dir', 'is', 'missing')
        app = ServerApp()
        with nt.assert_raises(TraitError):
            app.root_dir = rootdir

def test_invalid_root_dir():
    with NamedTemporaryFile() as tf:
        app = ServerApp()
        with nt.assert_raises(TraitError):
            app.root_dir = tf

def test_root_dir_with_slash():
    with TemporaryDirectory(suffix="_slash" + os.sep) as td:
        app = ServerApp(root_dir=td)
        nt.assert_false(app.root_dir.endswith(os.sep))

def test_root_dir_root():
    root = os.path.abspath(os.sep) # gets the right value on Windows, Posix
    app = ServerApp(root_dir=root)
    nt.assert_equal(app.root_dir, root)

def test_generate_config():
    with TemporaryDirectory() as td:
        app = ServerApp(config_dir=td)
        app.initialize(['--generate-config', '--allow-root'])
        with nt.assert_raises(NoStart):
            app.start()
        assert os.path.exists(os.path.join(td, 'jupyter_server_config.py'))

#test if the version testin function works
def test_pep440_version():

    for version in [
        '4.1.0.b1',
        '4.1.b1',
        '4.2',
        'X.y.z',
        '1.2.3.dev1.post2',
        ]:
        def loc():
            with nt.assert_raises(ValueError):
                raise_on_bad_version(version)
        yield loc

    for version in [
        '4.1.1',
        '4.2.1b3',
        ]:

        yield (raise_on_bad_version, version)

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
            nt.assert_not_equal(sv.password, '')
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
    nt.assert_equal(len(app.servers_shut_down), 1)
    nt.assert_equal(app.servers_shut_down[0]['port'], 105)

    # test no match
    with mock_servers, patch('os.kill') as os_kill:
        app = TestingStopApp()
        app.initialize(['999'])
        with nt.assert_raises(SystemExit) as exc:
            app.start()
        nt.assert_equal(exc.exception.code, 1)
    nt.assert_equal(len(app.servers_shut_down), 0)
