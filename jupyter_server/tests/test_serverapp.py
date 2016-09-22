"""Test ServerApp"""


import logging
import os
import re
from tempfile import NamedTemporaryFile

import nose.tools as nt

from traitlets.tests.utils import check_help_all_output

from jupyter_core.application import NoStart
from ipython_genutils.tempdir import TemporaryDirectory
from traitlets import TraitError
from jupyter_server import serverapp, __version__
ServerApp = serverapp.ServerApp


def test_help_output():
    """jupyter server --help-all works"""
    check_help_all_output('jupyter_server')

def test_server_info_file():
    td = TemporaryDirectory()
    serverapp = ServerApp(runtime_dir=td.name, log=logging.getLogger())
    def get_servers():
        return list(serverapp.list_running_servers(serverapp.runtime_dir))
    serverapp.initialize(argv=[])
    serverapp.write_server_info_file()
    servers = get_servers()
    nt.assert_equal(len(servers), 1)
    nt.assert_equal(servers[0]['port'], serverapp.port)
    nt.assert_equal(servers[0]['url'], serverapp.connection_url)
    serverapp.remove_server_info_file()
    nt.assert_equal(get_servers(), [])

    # The ENOENT error should be silenced.
    serverapp.remove_server_info_file()

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
