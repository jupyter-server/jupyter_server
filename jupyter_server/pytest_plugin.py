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
from jupyter_server.extension import serverextension
from jupyter_server.serverapp import ServerApp
from jupyter_server.utils import url_path_join
from jupyter_server.services.contents.filemanager import FileContentsManager

import nbformat

# This shouldn't be needed anymore, since pytest_tornasync is found in entrypoints
pytest_plugins = "pytest_tornasync"

# NOTE: This is a temporary fix for Windows 3.8
# We have to override the io_loop fixture with an
# asyncio patch. This will probably be removed in
# the future.

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


server_config = pytest.fixture(lambda: {})
home_dir = pytest.fixture(lambda tmp_path: mkdir(tmp_path, "home"))
data_dir = pytest.fixture(lambda tmp_path: mkdir(tmp_path, "data"))
config_dir = pytest.fixture(lambda tmp_path: mkdir(tmp_path, "config"))
runtime_dir = pytest.fixture(lambda tmp_path: mkdir(tmp_path, "runtime"))
root_dir = pytest.fixture(lambda tmp_path: mkdir(tmp_path, "root_dir"))
template_dir = pytest.fixture(lambda tmp_path: mkdir(tmp_path, "templates"))
system_jupyter_path = pytest.fixture(
    lambda tmp_path: mkdir(tmp_path, "share", "jupyter")
)
env_jupyter_path = pytest.fixture(
    lambda tmp_path: mkdir(tmp_path, "env", "share", "jupyter")
)
system_config_path = pytest.fixture(lambda tmp_path: mkdir(tmp_path, "etc", "jupyter"))
env_config_path = pytest.fixture(
    lambda tmp_path: mkdir(tmp_path, "env", "etc", "jupyter")
)
some_resource = u"The very model of a modern major general"
sample_kernel_json = {
    'argv':['cat', '{connection_file}'],
    'display_name': 'Test kernel',
}
argv = pytest.fixture(lambda: [])


@pytest.fixture
def environ(
    monkeypatch,
    tmp_path,
    home_dir,
    data_dir,
    config_dir,
    runtime_dir,
    root_dir,
    system_jupyter_path,
    system_config_path,
    env_jupyter_path,
    env_config_path,
):
    monkeypatch.setenv("HOME", str(home_dir))
    monkeypatch.setenv("PYTHONPATH", os.pathsep.join(sys.path))
    # monkeypatch.setenv("JUPYTER_NO_CONFIG", "1")
    monkeypatch.setenv("JUPYTER_CONFIG_DIR", str(config_dir))
    monkeypatch.setenv("JUPYTER_DATA_DIR", str(data_dir))
    monkeypatch.setenv("JUPYTER_RUNTIME_DIR", str(runtime_dir))
    monkeypatch.setattr(
        jupyter_core.paths, "SYSTEM_JUPYTER_PATH", [str(system_jupyter_path)]
    )
    monkeypatch.setattr(jupyter_core.paths, "ENV_JUPYTER_PATH", [str(env_jupyter_path)])
    monkeypatch.setattr(
        jupyter_core.paths, "SYSTEM_CONFIG_PATH", [str(system_config_path)]
    )
    monkeypatch.setattr(jupyter_core.paths, "ENV_CONFIG_PATH", [str(env_config_path)])


@pytest.fixture
def extension_environ(env_config_path, monkeypatch):
    """Monkeypatch a Jupyter Extension's config path into each test's environment variable"""
    monkeypatch.setattr(serverextension, "ENV_CONFIG_PATH", [str(env_config_path)])


@pytest.fixture(scope='function')
def configurable_serverapp(
    environ,
    server_config,
    argv,
    http_port,
    tmp_path,
    root_dir,
    io_loop,
):
    ServerApp.clear_instance()

    def _configurable_serverapp(
        config=server_config,
        argv=argv,
        environ=environ,
        http_port=http_port,
        tmp_path=tmp_path,
        root_dir=root_dir,
        **kwargs
    ):
        c = Config(config)
        c.NotebookNotary.db_file = ":memory:"
        token = hexlify(os.urandom(4)).decode("ascii")
        url_prefix = "/"
        app = ServerApp.instance(
            # Set the log level to debug for testing purposes
            log_level='DEBUG',
            port=http_port,
            port_retries=0,
            open_browser=False,
            root_dir=str(root_dir),
            base_url=url_prefix,
            config=c,
            allow_root=True,
            token=token,
            **kwargs
        )

        app.init_signal = lambda: None
        app.log.propagate = True
        app.log.handlers = []
        # Initialize app without httpserver
        app.initialize(argv=argv, new_httpserver=False)
        app.log.propagate = True
        app.log.handlers = []
        # Start app without ioloop
        app.start_app()
        return app

    return _configurable_serverapp


@pytest.fixture(scope="function")
def serverapp(server_config, argv, configurable_serverapp):
    app = configurable_serverapp(config=server_config, argv=argv)
    yield app
    app.remove_server_info_file()
    app.remove_browser_open_file()
    app.cleanup_kernels()


@pytest.fixture
def app(serverapp):
    """app fixture is needed by pytest_tornasync plugin"""
    return serverapp.web_app


@pytest.fixture
def auth_header(serverapp):
    return {"Authorization": "token {token}".format(token=serverapp.token)}


@pytest.fixture
def http_port(http_server_port):
    return http_server_port[-1]


@pytest.fixture
def base_url():
    return "/"


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
        return http_server_client.fetch(
            url, headers=headers, request_timeout=20, **kwargs
        )
    return client_fetch


@pytest.fixture
def ws_fetch(auth_header, http_port):
    """websocket fetch fixture that handles auth, base_url, and path"""
    def client_fetch(*parts, headers={}, params={}, **kwargs):
        # Handle URL strings
        path = url_escape(url_path_join(*parts), plus=False)
        urlparts = urllib.parse.urlparse('ws://localhost:{}'.format(http_port))
        urlparts = urlparts._replace(
            path=path,
            query=urllib.parse.urlencode(params)
        )
        url = urlparts.geturl()
        # Add auth keys to header
        headers.update(auth_header)
        # Make request.
        req = tornado.httpclient.HTTPRequest(
            url,
            headers=auth_header,
            connect_timeout=120
        )
        return tornado.websocket.websocket_connect(req)
    return client_fetch


@pytest.fixture
def kernelspecs(data_dir):
    spec_names = ['sample', 'sample 2']
    for name in spec_names:
        sample_kernel_dir = data_dir.joinpath('kernels', name)
        sample_kernel_dir.mkdir(parents=True)
        # Create kernel json file
        sample_kernel_file = sample_kernel_dir.joinpath('kernel.json')
        sample_kernel_file.write_text(json.dumps(sample_kernel_json))
        # Create resources text
        sample_kernel_resources = sample_kernel_dir.joinpath('resource.txt')
        sample_kernel_resources.write_text(some_resource)


@pytest.fixture(params=[True, False])
def contents_manager(request, tmp_path):
    return FileContentsManager(root_dir=str(tmp_path), use_atomic_writing=request.param)


@pytest.fixture
def create_notebook(root_dir):
    """Create a notebook in the test's home directory."""
    def inner(nbpath):
        nbpath = root_dir.joinpath(nbpath)
        # Check that the notebook has the correct file extension.
        if nbpath.suffix != '.ipynb':
            raise Exception("File extension for notebook must be .ipynb")
        # If the notebook path has a parent directory, make sure it's created.
        parent = nbpath.parent
        parent.mkdir(parents=True, exist_ok=True)
        # Create a notebook string and write to file.
        nb = nbformat.v4.new_notebook()
        nbtext = nbformat.writes(nb, version=4)
        nbpath.write_text(nbtext)
    return inner
