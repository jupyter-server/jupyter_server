import os
import getpass
import pathlib
import pytest
import logging
from unittest.mock import patch

from traitlets import TraitError
from traitlets.tests.utils import check_help_all_output
from jupyter_core.application import NoStart

from jupyter_server.serverapp import (
    ServerApp,
    list_running_servers,
    JupyterPasswordApp,
    JupyterServerStopApp
)
from jupyter_server.auth.security import passwd_check


def test_help_output():
    """jupyter server --help-all works"""
    check_help_all_output('jupyter_server')


def test_server_info_file(tmp_path, jp_configurable_serverapp):
    app = jp_configurable_serverapp(log=logging.getLogger())

    app.write_server_info_file()
    servers = list(list_running_servers(app.runtime_dir))

    assert len(servers) == 1
    sinfo = servers[0]

    assert sinfo['port'] == app.port
    assert sinfo['url'] == app.connection_url
    assert sinfo['version'] == app.version

    app.remove_server_info_file()

    assert list(list_running_servers(app.runtime_dir)) == []
    app.remove_server_info_file


def test_root_dir(tmp_path, jp_configurable_serverapp):
    app = jp_configurable_serverapp(root_dir=str(tmp_path))
    assert app.root_dir == str(tmp_path)


# Build a list of invalid paths
@pytest.fixture(
    params=[
        ('notebooks',),
        ('root', 'dir', 'is', 'missing'),
        ('test.txt',)
    ]
)
def invalid_root_dir(tmp_path, request):
    path = tmp_path.joinpath(*request.param)
    # If the path is a file, create it.
    if os.path.splitext(str(path))[1] != '':
        path.write_text('')
    return str(path)


def test_invalid_root_dir(invalid_root_dir, jp_configurable_serverapp):
    app = jp_configurable_serverapp()
    with pytest.raises(TraitError):
        app.root_dir = invalid_root_dir

@pytest.fixture(
    params=[
        ('/',),
        ('first-level',),
        ('first-level', 'second-level')
    ]
)
def valid_root_dir(tmp_path, request):
    path = tmp_path.joinpath(*request.param)
    if not path.exists():
        # Create path in temporary directory
        path.mkdir(parents=True)
    return str(path)

def test_valid_root_dir(valid_root_dir, jp_configurable_serverapp):
    app = jp_configurable_serverapp(root_dir=valid_root_dir)
    root_dir = valid_root_dir
    # If nested path, the last slash should
    # be stripped by the root_dir trait.
    if root_dir != '/':
        root_dir = valid_root_dir.rstrip('/')
    assert app.root_dir == root_dir


def test_generate_config(tmp_path, jp_configurable_serverapp):
    app = jp_configurable_serverapp(config_dir=str(tmp_path))
    app.initialize(['--generate-config', '--allow-root'])
    with pytest.raises(NoStart):
        app.start()
    assert tmp_path.joinpath('jupyter_server_config.py').exists()


def test_server_password(tmp_path, jp_configurable_serverapp):
    password = 'secret'
    with patch.dict(
        'os.environ', {'JUPYTER_CONFIG_DIR': str(tmp_path)}
        ), patch.object(getpass, 'getpass', return_value=password):
        app = JupyterPasswordApp(log_level=logging.ERROR)
        app.initialize([])
        app.start()
        sv = jp_configurable_serverapp()
        sv.load_config_file()
        assert sv.password != ''
        passwd_check(sv.password, password)


def test_list_running_servers(jp_serverapp, jp_web_app):
    servers = list(list_running_servers(jp_serverapp.runtime_dir))
    assert len(servers) >= 1


@pytest.fixture
def prefix_path(jp_root_dir, tmp_path):
    """If a given path is prefixed with the literal
    strings `/jp_root_dir` or `/tmp_path`, replace those
    strings with these fixtures.

    Returns a pathlib Path object.
    """
    def _inner(rawpath):
        path = pathlib.PurePosixPath(rawpath)
        if rawpath.startswith('/jp_root_dir'):
            path = jp_root_dir.joinpath(*path.parts[2:])
        elif rawpath.startswith('/tmp_path'):
            path = tmp_path.joinpath(*path.parts[2:])
        return pathlib.Path(path)
    return _inner


@pytest.mark.parametrize(
    "root_dir,file_to_run,expected_output",
    [
        (
            None,
            'notebook.ipynb',
            'notebook.ipynb'
        ),
        (
            None,
            '/tmp_path/path/to/notebook.ipynb',
            'notebook.ipynb'
        ),
        (
            '/jp_root_dir',
            '/tmp_path/path/to/notebook.ipynb',
            SystemExit
        ),
        (
            '/tmp_path',
            '/tmp_path/path/to/notebook.ipynb',
            'path/to/notebook.ipynb'
        ),
        (
            '/jp_root_dir',
            'notebook.ipynb',
            'notebook.ipynb'
        ),
        (
            '/jp_root_dir',
            'path/to/notebook.ipynb',
            'path/to/notebook.ipynb'
        ),
    ]
)
def test_resolve_file_to_run_and_root_dir(
    prefix_path,
    root_dir,
    file_to_run,
    expected_output
):
    # Verify that the Singleton instance is cleared before the test runs.
    ServerApp.clear_instance()

    # Setup the file_to_run path, in case the server checks
    # if the directory exists before initializing the server.
    file_to_run = prefix_path(file_to_run)
    if file_to_run.is_absolute():
        file_to_run.parent.mkdir(parents=True, exist_ok=True)
    kwargs = {"file_to_run": str(file_to_run)}

    # Setup the root_dir path, in case the server checks
    # if the directory exists before initializing the server.
    if root_dir:
        root_dir = prefix_path(root_dir)
        if root_dir.is_absolute():
            root_dir.parent.mkdir(parents=True, exist_ok=True)
        kwargs["root_dir"] = str(root_dir)

    # Create the notebook in the given location
    serverapp = ServerApp.instance(**kwargs)

    if expected_output is SystemExit:
        with pytest.raises(SystemExit):
            serverapp._resolve_file_to_run_and_root_dir()
    else:
        relpath = serverapp._resolve_file_to_run_and_root_dir()
        assert relpath == str(pathlib.Path(expected_output))

    # Clear the singleton instance after each run.
    ServerApp.clear_instance()
