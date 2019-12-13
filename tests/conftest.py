import os
import sys
import json
import pytest
import asyncio
from binascii import hexlify

import urllib.parse
import tornado
from tornado.escape import url_escape

from traitlets.config import Config

import jupyter_core.paths
from jupyter_server.serverapp import ServerApp
from jupyter_server.utils import url_path_join


pytest_plugins = ("pytest_tornasync")


# NOTE: This is a temporary fix for Windows 3.8
# We have to override the io_loop fixture with an 
# asyncio patch. This will probably be removed in 
# the future.                   
if sys.platform.startswith("win") and sys.version_info >= (3, 8):

    @pytest.fixture
    def asyncio_patch():
        ServerApp()._init_asyncio_patch()

    @pytest.fixture
    def io_loop(asyncio_patch):
        loop = tornado.ioloop.IOLoop()
        loop.make_current()
        yield loop
        loop.clear_current()
        loop.close(all_fds=True)


def mkdir(tmp_path, *parts):
    path = tmp_path.joinpath(*parts)
    if not path.exists():
        path.mkdir(parents=True)
    return path


def expected_http_error(error, expected_code, expected_message=None):
    """Check that the error matches the expected output error."""
    e = error.value
    if isinstance(e, tornado.web.HTTPError):
        if expected_code != e.status_code:
            return False
        if expected_message is not None and expected_message != str(e):
            return False
        return True
    elif any([
        isinstance(e, tornado.httpclient.HTTPClientError), 
        isinstance(e, tornado.httpclient.HTTPError)
    ]):
        if expected_code != e.code:
            return False
        if expected_message:
            message = json.loads(e.response.body.decode())['message']
            if expected_message != message:
                return False
        return True


config = pytest.fixture(lambda: {})
home_dir = pytest.fixture(lambda tmp_path: mkdir(tmp_path, 'home'))
data_dir = pytest.fixture(lambda tmp_path: mkdir(tmp_path, 'data'))
config_dir = pytest.fixture(lambda tmp_path: mkdir(tmp_path, 'config'))
runtime_dir = pytest.fixture(lambda tmp_path: mkdir(tmp_path, 'runtime'))
root_dir = pytest.fixture(lambda tmp_path: mkdir(tmp_path, 'root_dir'))
argv = pytest.fixture(lambda: [])

@pytest.fixture
def environ(
    monkeypatch,
    tmp_path,
    home_dir,
    data_dir,
    config_dir,
    runtime_dir,
    root_dir
    ):
    monkeypatch.setenv('HOME', str(home_dir))
    monkeypatch.setenv('PYTHONPATH', os.pathsep.join(sys.path))
    monkeypatch.setenv('JUPYTER_NO_CONFIG', '1')
    monkeypatch.setenv('JUPYTER_CONFIG_DIR', str(config_dir))
    monkeypatch.setenv('JUPYTER_DATA_DIR', str(data_dir))
    monkeypatch.setenv('JUPYTER_RUNTIME_DIR', str(runtime_dir))
    monkeypatch.setattr(jupyter_core.paths, 'SYSTEM_JUPYTER_PATH', [str(mkdir(tmp_path, 'share', 'jupyter'))])
    monkeypatch.setattr(jupyter_core.paths, 'ENV_JUPYTER_PATH', [str(mkdir(tmp_path, 'env', 'share', 'jupyter'))])
    monkeypatch.setattr(jupyter_core.paths, 'SYSTEM_CONFIG_PATH', [str(mkdir(tmp_path, 'etc', 'jupyter'))])
    monkeypatch.setattr(jupyter_core.paths, 'ENV_CONFIG_PATH', [str(mkdir(tmp_path, 'env', 'etc', 'jupyter'))])


@pytest.fixture
def configurable_serverapp(    
    environ,
    http_port, 
    tmp_path, 
    home_dir,
    data_dir,
    config_dir,
    runtime_dir,
    root_dir
    ):

    def serverapp(
        config={}, 
        argv=[], 
        environ=environ,
        http_port=http_port, 
        tmp_path=tmp_path, 
        home_dir=home_dir,
        data_dir=data_dir,
        config_dir=config_dir,
        runtime_dir=runtime_dir,
        root_dir=root_dir,
        **kwargs):
        c = Config(config)
        c.NotebookNotary.db_file = ':memory:'
        token = hexlify(os.urandom(4)).decode('ascii')
        url_prefix = '/'
        app = ServerApp.instance(
            port=http_port,
            port_retries=0,
            open_browser=False,
            config_dir=str(config_dir),
            data_dir=str(data_dir),
            runtime_dir=str(runtime_dir),
            root_dir=str(root_dir),
            base_url=url_prefix,
            config=c,
            allow_root=True,
            token=token,
            **kwargs
        )
        app.init_signal = lambda : None
        app.log.propagate = True
        app.log.handlers = []
        # Initialize app without httpserver
        app.initialize(argv=argv, new_httpserver=False)
        app.log.propagate = True
        app.log.handlers = []
        # Start app without ioloop
        app.start_app()
        return app

    yield serverapp
    ServerApp.clear_instance()


@pytest.fixture
def serverapp(configurable_serverapp, config, argv):
    app = configurable_serverapp(config=config, argv=argv)
    yield app
    app.remove_server_info_file()
    app.remove_browser_open_file()
    app.cleanup_kernels()


@pytest.fixture
def app(serverapp):
    return serverapp.web_app


@pytest.fixture
def auth_header(serverapp):
    return {'Authorization': 'token {token}'.format(token=serverapp.token)}


@pytest.fixture
def http_port(http_server_port):
    return http_server_port[-1]


@pytest.fixture
def base_url(http_server_port):
    return '/'


@pytest.fixture
def fetch(http_server_client, auth_header, base_url):
    """fetch fixture that handles auth, base_url, and path"""
    def client_fetch(*parts, headers={}, params={}, **kwargs):
        # Handle URL strings
        path_url = url_escape(url_path_join(base_url, *parts), plus=False)
        params_url = urllib.parse.urlencode(params)
        url = path_url + "?" + params_url
        # Add auth keys to header
        headers.update(auth_header)
        # Make request.
        return http_server_client.fetch(url, headers=headers, request_timeout=20, **kwargs)
    return client_fetch