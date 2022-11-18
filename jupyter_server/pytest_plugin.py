# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
import asyncio
import importlib
import io
import json
import logging
import os
import shutil
import sys
import urllib.parse
from binascii import hexlify
from contextlib import closing

import jupyter_core.paths
import nbformat
import pytest
import tornado
import tornado.testing
from pytest_tornasync.plugin import AsyncHTTPServerClient
from tornado.escape import url_escape
from tornado.httpclient import HTTPClientError
from tornado.websocket import WebSocketHandler
from traitlets.config import Config, re

from jupyter_server.auth import Authorizer
from jupyter_server.extension import serverextension
from jupyter_server.serverapp import JUPYTER_SERVICE_HANDLERS, ServerApp
from jupyter_server.services.contents.filemanager import AsyncFileContentsManager
from jupyter_server.services.contents.largefilemanager import AsyncLargeFileManager
from jupyter_server.utils import url_path_join

# List of dependencies needed for this plugin.
pytest_plugins = [
    "pytest_tornasync",
    # Once the chunk below moves to Jupyter Core, we'll uncomment
    # This plugin and use the fixtures directly from Jupyter Core.
    # "jupyter_core.pytest_plugin"
]


if os.name == "nt":
    asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy()  # type:ignore[attr-defined]
    )


# ============ Move to Jupyter Core =============

# Once the chunk below moves to Jupyter Core
# use the fixtures directly from Jupyter Core.


def mkdir(tmp_path, *parts):
    path = tmp_path.joinpath(*parts)
    if not path.exists():
        path.mkdir(parents=True)
    return path


@pytest.fixture
def jp_home_dir(tmp_path):
    """Provides a temporary HOME directory value."""
    return mkdir(tmp_path, "home")


@pytest.fixture
def jp_data_dir(tmp_path):
    """Provides a temporary Jupyter data dir directory value."""
    return mkdir(tmp_path, "data")


@pytest.fixture
def jp_config_dir(tmp_path):
    """Provides a temporary Jupyter config dir directory value."""
    return mkdir(tmp_path, "config")


@pytest.fixture
def jp_runtime_dir(tmp_path):
    """Provides a temporary Jupyter runtime dir directory value."""
    return mkdir(tmp_path, "runtime")


@pytest.fixture
def jp_system_jupyter_path(tmp_path):
    """Provides a temporary Jupyter system path value."""
    return mkdir(tmp_path, "share", "jupyter")


@pytest.fixture
def jp_env_jupyter_path(tmp_path):
    """Provides a temporary Jupyter env system path value."""
    return mkdir(tmp_path, "env", "share", "jupyter")


@pytest.fixture
def jp_system_config_path(tmp_path):
    """Provides a temporary Jupyter config path value."""
    return mkdir(tmp_path, "etc", "jupyter")


@pytest.fixture
def jp_env_config_path(tmp_path):
    """Provides a temporary Jupyter env config path value."""
    return mkdir(tmp_path, "env", "etc", "jupyter")


@pytest.fixture
def jp_environ(
    monkeypatch,
    tmp_path,
    jp_home_dir,
    jp_data_dir,
    jp_config_dir,
    jp_runtime_dir,
    jp_system_jupyter_path,
    jp_system_config_path,
    jp_env_jupyter_path,
    jp_env_config_path,
):
    """Configures a temporary environment based on Jupyter-specific environment variables."""
    monkeypatch.setenv("HOME", str(jp_home_dir))
    monkeypatch.setenv("PYTHONPATH", os.pathsep.join(sys.path))
    # monkeypatch.setenv("JUPYTER_NO_CONFIG", "1")
    monkeypatch.setenv("JUPYTER_CONFIG_DIR", str(jp_config_dir))
    monkeypatch.setenv("JUPYTER_DATA_DIR", str(jp_data_dir))
    monkeypatch.setenv("JUPYTER_RUNTIME_DIR", str(jp_runtime_dir))
    monkeypatch.setattr(jupyter_core.paths, "SYSTEM_JUPYTER_PATH", [str(jp_system_jupyter_path)])
    monkeypatch.setattr(jupyter_core.paths, "ENV_JUPYTER_PATH", [str(jp_env_jupyter_path)])
    monkeypatch.setattr(jupyter_core.paths, "SYSTEM_CONFIG_PATH", [str(jp_system_config_path)])
    monkeypatch.setattr(jupyter_core.paths, "ENV_CONFIG_PATH", [str(jp_env_config_path)])


# ================= End: Move to Jupyter core ================


@pytest.fixture
def asyncio_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def io_loop(asyncio_loop):
    async def get_tornado_loop():
        return tornado.ioloop.IOLoop.current()

    return asyncio_loop.run_until_complete(get_tornado_loop())


@pytest.fixture
def http_server_client(http_server, io_loop):
    """
    Create an asynchronous HTTP client that can fetch from `http_server`.
    """

    async def get_client():
        return AsyncHTTPServerClient(http_server=http_server)

    client = io_loop.run_sync(get_client)
    with closing(client) as context:
        yield context


@pytest.fixture
def http_server(io_loop, http_server_port, jp_web_app):
    """Start a tornado HTTP server that listens on all available interfaces."""

    async def get_server():
        server = tornado.httpserver.HTTPServer(jp_web_app)
        server.add_socket(http_server_port[0])
        return server

    server = io_loop.run_sync(get_server)
    yield server
    server.stop()

    if hasattr(server, "close_all_connections"):
        io_loop.run_sync(server.close_all_connections)

    http_server_port[0].close()


@pytest.fixture
def jp_server_config():
    """Allows tests to setup their specific configuration values."""
    return Config(
        {
            "jpserver_extensions": {"jupyter_server_terminals": True},
        }
    )


@pytest.fixture
def jp_root_dir(tmp_path):
    """Provides a temporary Jupyter root directory value."""
    return mkdir(tmp_path, "root_dir")


@pytest.fixture
def jp_template_dir(tmp_path):
    """Provides a temporary Jupyter templates directory value."""
    return mkdir(tmp_path, "templates")


@pytest.fixture
def jp_argv():
    """Allows tests to setup specific argv values."""
    return []


@pytest.fixture
def jp_extension_environ(jp_env_config_path, monkeypatch):
    """Monkeypatch a Jupyter Extension's config path into each test's environment variable"""
    monkeypatch.setattr(serverextension, "ENV_CONFIG_PATH", [str(jp_env_config_path)])


@pytest.fixture
def jp_http_port(http_server_port):
    """Returns the port value from the http_server_port fixture."""
    yield http_server_port[-1]
    http_server_port[0].close()


@pytest.fixture
def jp_nbconvert_templates(jp_data_dir):
    """Setups up a temporary directory consisting of the nbconvert templates."""

    # Get path to nbconvert template directory *before*
    # monkeypatching the paths env variable via the jp_environ fixture.
    possible_paths = jupyter_core.paths.jupyter_path("nbconvert", "templates")
    nbconvert_path = None
    for path in possible_paths:
        if os.path.exists(path):
            nbconvert_path = path
            break

    nbconvert_target = jp_data_dir / "nbconvert" / "templates"

    # copy nbconvert templates to new tmp data_dir.
    if nbconvert_path:
        shutil.copytree(nbconvert_path, str(nbconvert_target))


@pytest.fixture
def jp_logging_stream():
    """StringIO stream intended to be used by the core
    Jupyter ServerApp logger's default StreamHandler. This
    helps avoid collision with stdout which is hijacked
    by Pytest.
    """
    logging_stream = io.StringIO()
    yield logging_stream
    output = logging_stream.getvalue()
    # If output exists, print it.
    if output:
        print(output)
    return output


@pytest.fixture(scope="function")
def jp_configurable_serverapp(
    jp_nbconvert_templates,  # this fixture must preceed jp_environ
    jp_environ,
    jp_server_config,
    jp_argv,
    jp_http_port,
    jp_base_url,
    tmp_path,
    jp_root_dir,
    jp_logging_stream,
    asyncio_loop,
):
    """Starts a Jupyter Server instance based on
    the provided configuration values.

    The fixture is a factory; it can be called like
    a function inside a unit test. Here's a basic
    example of how use this fixture:

    .. code-block:: python

        def my_test(jp_configurable_serverapp):

            app = jp_configurable_serverapp(...)
            ...
    """
    ServerApp.clear_instance()

    # Inject jupyter_server_terminals into config unless it was
    # explicitly put in config.
    serverapp_config = jp_server_config.setdefault("ServerApp", {})
    exts = serverapp_config.setdefault("jpserver_extensions", {})
    if "jupyter_server_terminals" not in exts:
        exts["jupyter_server_terminals"] = True

    def _configurable_serverapp(
        config=jp_server_config,
        base_url=jp_base_url,
        argv=jp_argv,
        environ=jp_environ,
        http_port=jp_http_port,
        tmp_path=tmp_path,
        root_dir=jp_root_dir,
        **kwargs,
    ):
        c = Config(config)
        c.NotebookNotary.db_file = ":memory:"
        if "token" not in c.ServerApp and not c.IdentityProvider.token:
            token = hexlify(os.urandom(4)).decode("ascii")
            c.IdentityProvider.token = token

        # Allow tests to configure root_dir via a file, argv, or its
        # default (cwd) by specifying a value of None.
        if root_dir is not None:
            kwargs["root_dir"] = str(root_dir)

        app = ServerApp.instance(
            # Set the log level to debug for testing purposes
            log_level="DEBUG",
            port=http_port,
            port_retries=0,
            open_browser=False,
            base_url=base_url,
            config=c,
            allow_root=True,
            **kwargs,
        )

        app.init_signal = lambda: None
        app.log.propagate = True
        app.log.handlers = []
        # Initialize app without httpserver
        if asyncio_loop.is_running():
            app.initialize(argv=argv, new_httpserver=False)
        else:

            async def initialize_app():
                app.initialize(argv=argv, new_httpserver=False)

            asyncio_loop.run_until_complete(initialize_app())
        # Reroute all logging StreamHandlers away from stdin/stdout since pytest hijacks
        # these streams and closes them at unfortunate times.
        stream_handlers = [h for h in app.log.handlers if isinstance(h, logging.StreamHandler)]
        for handler in stream_handlers:
            handler.setStream(jp_logging_stream)
        app.log.propagate = True
        app.log.handlers = []
        app.start_app()
        return app

    return _configurable_serverapp


@pytest.fixture(scope="function")
def jp_serverapp(jp_server_config, jp_argv, jp_configurable_serverapp):
    """Starts a Jupyter Server instance based on the established configuration values."""
    return jp_configurable_serverapp(config=jp_server_config, argv=jp_argv)


@pytest.fixture
def jp_web_app(jp_serverapp):
    """app fixture is needed by pytest_tornasync plugin"""
    return jp_serverapp.web_app


@pytest.fixture
def jp_auth_header(jp_serverapp):
    """Configures an authorization header using the token from the serverapp fixture."""
    return {"Authorization": f"token {jp_serverapp.identity_provider.token}"}


@pytest.fixture
def jp_base_url():
    """Returns the base url to use for the test."""
    return "/a%40b/"


@pytest.fixture
def jp_fetch(jp_serverapp, http_server_client, jp_auth_header, jp_base_url):
    """Sends an (asynchronous) HTTP request to a test server.

    The fixture is a factory; it can be called like
    a function inside a unit test. Here's a basic
    example of how use this fixture:

    .. code-block:: python

        async def my_test(jp_fetch):

            response = await jp_fetch("api", "spec.yaml")
            ...
    """

    def client_fetch(*parts, headers=None, params=None, **kwargs):
        if not headers:
            headers = {}
        if not params:
            params = {}
        # Handle URL strings
        path_url = url_escape(url_path_join(*parts), plus=False)
        base_path_url = url_path_join(jp_base_url, path_url)
        params_url = urllib.parse.urlencode(params)
        url = base_path_url + "?" + params_url
        # Add auth keys to header, if not overridden
        for key, value in jp_auth_header.items():
            headers.setdefault(key, value)
        # Make request.
        return http_server_client.fetch(url, headers=headers, request_timeout=20, **kwargs)

    return client_fetch


@pytest.fixture
def jp_ws_fetch(jp_serverapp, http_server_client, jp_auth_header, jp_http_port, jp_base_url):
    """Sends a websocket request to a test server.

    The fixture is a factory; it can be called like
    a function inside a unit test. Here's a basic
    example of how use this fixture:

    .. code-block:: python

        async def my_test(jp_fetch, jp_ws_fetch):
            # Start a kernel
            r = await jp_fetch(
                'api', 'kernels',
                method='POST',
                body=json.dumps({
                    'name': "python3"
                })
            )
            kid = json.loads(r.body.decode())['id']

            # Open a websocket connection.
            ws = await jp_ws_fetch(
                'api', 'kernels', kid, 'channels'
            )
            ...
    """

    def client_fetch(*parts, headers=None, params=None, **kwargs):
        if not headers:
            headers = {}
        if not params:
            params = {}
        # Handle URL strings
        path_url = url_escape(url_path_join(*parts), plus=False)
        base_path_url = url_path_join(jp_base_url, path_url)
        urlparts = urllib.parse.urlparse(f"ws://localhost:{jp_http_port}")
        urlparts = urlparts._replace(path=base_path_url, query=urllib.parse.urlencode(params))
        url = urlparts.geturl()
        # Add auth keys to header
        headers.update(jp_auth_header)
        # Make request.
        req = tornado.httpclient.HTTPRequest(url, headers=headers, connect_timeout=120)
        return tornado.websocket.websocket_connect(req)

    return client_fetch


some_resource = "The very model of a modern major general"
sample_kernel_json = {
    "argv": ["cat", "{connection_file}"],
    "display_name": "Test kernel",
}


@pytest.fixture
def jp_kernelspecs(jp_data_dir):
    """Configures some sample kernelspecs in the Jupyter data directory."""
    spec_names = ["sample", "sample2", "bad"]
    for name in spec_names:
        sample_kernel_dir = jp_data_dir.joinpath("kernels", name)
        sample_kernel_dir.mkdir(parents=True)
        # Create kernel json file
        sample_kernel_file = sample_kernel_dir.joinpath("kernel.json")
        kernel_json = sample_kernel_json.copy()
        if name == "bad":
            kernel_json["argv"] = ["non_existent_path"]
        sample_kernel_file.write_text(json.dumps(kernel_json))
        # Create resources text
        sample_kernel_resources = sample_kernel_dir.joinpath("resource.txt")
        sample_kernel_resources.write_text(some_resource)


@pytest.fixture(params=[True, False])
def jp_contents_manager(request, tmp_path):
    """Returns an AsyncFileContentsManager instance based on the use_atomic_writing parameter value."""
    return AsyncFileContentsManager(root_dir=str(tmp_path), use_atomic_writing=request.param)


@pytest.fixture
def jp_large_contents_manager(tmp_path):
    """Returns an AsyncLargeFileManager instance."""
    return AsyncLargeFileManager(root_dir=str(tmp_path))


@pytest.fixture
def jp_create_notebook(jp_root_dir):
    """Creates a notebook in the test's home directory."""

    def inner(nbpath):
        nbpath = jp_root_dir.joinpath(nbpath)
        # Check that the notebook has the correct file extension.
        if nbpath.suffix != ".ipynb":
            raise Exception("File extension for notebook must be .ipynb")
        # If the notebook path has a parent directory, make sure it's created.
        parent = nbpath.parent
        parent.mkdir(parents=True, exist_ok=True)
        # Create a notebook string and write to file.
        nb = nbformat.v4.new_notebook()
        nbtext = nbformat.writes(nb, version=4)
        nbpath.write_text(nbtext)

    return inner


@pytest.fixture(autouse=True)
def jp_server_cleanup(asyncio_loop):
    yield
    app: ServerApp = ServerApp.instance()
    asyncio_loop.run_until_complete(app._cleanup())
    ServerApp.clear_instance()


@pytest.fixture
def send_request(jp_fetch, jp_ws_fetch):
    """Send to Jupyter Server and return response code."""

    async def _(url, **fetch_kwargs):
        if url.endswith("channels") or "/websocket/" in url:
            fetch = jp_ws_fetch
        else:
            fetch = jp_fetch

        try:
            r = await fetch(url, **fetch_kwargs, allow_nonstandard_methods=True)
            code = r.code
        except HTTPClientError as err:
            code = err.code
        else:
            if fetch is jp_ws_fetch:
                r.close()

        return code

    return _


@pytest.fixture
def jp_server_auth_core_resources():
    modules = []
    for mod_name in JUPYTER_SERVICE_HANDLERS.values():
        if mod_name:
            modules.extend(mod_name)
    resource_map = {}
    for handler_module in modules:
        mod = importlib.import_module(handler_module)
        name = mod.AUTH_RESOURCE
        for handler in mod.default_handlers:
            url_regex = handler[0]
            resource_map[url_regex] = name
    return resource_map


@pytest.fixture
def jp_server_auth_resources(jp_server_auth_core_resources):
    return jp_server_auth_core_resources


@pytest.fixture
def jp_server_authorizer(jp_server_auth_resources):
    class _(Authorizer):

        # Set these class attributes from within a test
        # to verify that they match the arguments passed
        # by the REST API.
        permissions: dict = {}

        HTTP_METHOD_TO_AUTH_ACTION = {
            "GET": "read",
            "HEAD": "read",
            "OPTIONS": "read",
            "POST": "write",
            "PUT": "write",
            "PATCH": "write",
            "DELETE": "write",
            "WEBSOCKET": "execute",
        }

        def match_url_to_resource(self, url, regex_mapping=None):
            """Finds the JupyterHandler regex pattern that would
            match the given URL and returns the resource name (str)
            of that handler.

            e.g.
            /api/contents/... returns "contents"
            """
            if not regex_mapping:
                regex_mapping = jp_server_auth_resources
            for regex, auth_resource in regex_mapping.items():
                pattern = re.compile(regex)
                if pattern.fullmatch(url):
                    return auth_resource

        def normalize_url(self, path):
            """Drop the base URL and make sure path leads with a /"""
            base_url = self.parent.base_url
            # Remove base_url
            if path.startswith(base_url):
                path = path[len(base_url) :]
            # Make sure path starts with /
            if not path.startswith("/"):
                path = "/" + path
            return path

        def is_authorized(self, handler, user, action, resource):
            # Parse Request
            if isinstance(handler, WebSocketHandler):
                method = "WEBSOCKET"
            else:
                method = handler.request.method
            url = self.normalize_url(handler.request.path)

            # Map request parts to expected action and resource.
            expected_action = self.HTTP_METHOD_TO_AUTH_ACTION[method]
            expected_resource = self.match_url_to_resource(url)

            # Assert that authorization layer returns the
            # correct action + resource.
            assert action == expected_action
            assert resource == expected_resource

            # Now, actually apply the authorization layer.
            return all(
                [
                    action in self.permissions.get("actions", []),
                    resource in self.permissions.get("resources", []),
                ]
            )

    return _
