import getpass
import logging
import os
import pathlib
import warnings
from unittest.mock import patch

import pytest
from jupyter_core.application import NoStart
from traitlets import TraitError
from traitlets.config import Config
from traitlets.tests.utils import check_help_all_output

from jupyter_server.auth.security import passwd_check
from jupyter_server.serverapp import (
    JupyterPasswordApp,
    ServerApp,
    ServerWebApplication,
    list_running_servers,
    random_ports,
)
from jupyter_server.services.contents.filemanager import (
    AsyncFileContentsManager,
    FileContentsManager,
)
from jupyter_server.utils import pathname2url, urljoin


@pytest.fixture(params=[FileContentsManager, AsyncFileContentsManager])
def jp_file_contents_manager_class(request, tmp_path):
    return request.param


def test_help_output():
    """jupyter server --help-all works"""
    check_help_all_output("jupyter_server")


def test_server_info_file(tmp_path, jp_configurable_serverapp):
    app = jp_configurable_serverapp(log=logging.getLogger())

    app.write_server_info_file()
    servers = list(list_running_servers(app.runtime_dir))

    assert len(servers) == 1
    sinfo = servers[0]

    assert sinfo["port"] == app.port
    assert sinfo["url"] == app.connection_url
    assert sinfo["version"] == app.version

    app.remove_server_info_file()

    assert list(list_running_servers(app.runtime_dir)) == []
    app.remove_server_info_file


def test_root_dir(tmp_path, jp_configurable_serverapp):
    app = jp_configurable_serverapp(root_dir=str(tmp_path))
    assert app.root_dir == str(tmp_path)


# Build a list of invalid paths
@pytest.fixture(params=[("notebooks",), ("root", "dir", "is", "missing"), ("test.txt",)])
def invalid_root_dir(tmp_path, request):
    path = tmp_path.joinpath(*request.param)
    # If the path is a file, create it.
    if os.path.splitext(str(path))[1] != "":
        path.write_text("")
    return str(path)


def test_invalid_root_dir(invalid_root_dir, jp_configurable_serverapp):
    app = jp_configurable_serverapp()
    with pytest.raises(TraitError):
        app.root_dir = invalid_root_dir


@pytest.fixture(params=[("/",), ("first-level",), ("first-level", "second-level")])
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
    if root_dir != "/":
        root_dir = valid_root_dir.rstrip("/")
    assert app.root_dir == root_dir


async def test_generate_config(tmp_path, jp_configurable_serverapp):
    app = jp_configurable_serverapp(config_dir=str(tmp_path))
    app.initialize(["--generate-config", "--allow-root"])
    with pytest.raises(NoStart):
        app.start()
    assert tmp_path.joinpath("jupyter_server_config.py").exists()


def test_server_password(tmp_path, jp_configurable_serverapp):
    password = "secret"
    with patch.dict("os.environ", {"JUPYTER_CONFIG_DIR": str(tmp_path)}), patch.object(
        getpass, "getpass", return_value=password
    ):
        app = JupyterPasswordApp(log_level=logging.ERROR)
        app.initialize([])
        app.start()
        sv = jp_configurable_serverapp()
        sv.load_config_file()
        assert sv.identity_provider.hashed_password != ""
        passwd_check(sv.identity_provider.hashed_password, password)


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
        if rawpath.startswith("/jp_root_dir"):
            path = jp_root_dir.joinpath(*path.parts[2:])
        elif rawpath.startswith("/tmp_path"):
            path = tmp_path.joinpath(*path.parts[2:])
        return pathlib.Path(path)

    return _inner


@pytest.mark.parametrize(
    "root_dir,file_to_run,expected_output",
    [
        (None, "notebook.ipynb", "notebook.ipynb"),
        (None, "/tmp_path/path/to/notebook.ipynb", "notebook.ipynb"),
        ("/jp_root_dir", "/tmp_path/path/to/notebook.ipynb", SystemExit),
        ("/tmp_path", "/tmp_path/path/to/notebook.ipynb", "path/to/notebook.ipynb"),
        ("/jp_root_dir", "notebook.ipynb", "notebook.ipynb"),
        ("/jp_root_dir", "path/to/notebook.ipynb", "path/to/notebook.ipynb"),
    ],
)
def test_resolve_file_to_run_and_root_dir(prefix_path, root_dir, file_to_run, expected_output):
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


# Test the URLs returned by ServerApp. The `<generated>` piece
# in urls shown below will be replaced with the token
# generated by the ServerApp on instance creation.
@pytest.mark.parametrize(
    "config,public_url,local_url,connection_url",
    [
        # Token is hidden when configured.
        (
            {"token": "test"},
            "http://localhost:8888/?token=...",
            "http://127.0.0.1:8888/?token=...",
            "http://localhost:8888/",
        ),
        # Verify port number has changed
        (
            {"port": 9999},
            "http://localhost:9999/?token=<generated>",
            "http://127.0.0.1:9999/?token=<generated>",
            "http://localhost:9999/",
        ),
        (
            {"ip": "1.1.1.1"},
            "http://1.1.1.1:8888/?token=<generated>",
            "http://127.0.0.1:8888/?token=<generated>",
            "http://1.1.1.1:8888/",
        ),
        # Verify that HTTPS is returned when certfile is given
        (
            {"certfile": "/path/to/dummy/file"},
            "https://localhost:8888/?token=<generated>",
            "https://127.0.0.1:8888/?token=<generated>",
            "https://localhost:8888/",
        ),
        # Verify changed port and a custom display URL
        (
            {"port": 9999, "custom_display_url": "http://test.org"},
            "http://test.org/?token=<generated>",
            "http://127.0.0.1:9999/?token=<generated>",
            "http://localhost:9999/",
        ),
        (
            {"base_url": "/", "default_url": "/test/"},
            "http://localhost:8888/test/?token=<generated>",
            "http://127.0.0.1:8888/test/?token=<generated>",
            "http://localhost:8888/",
        ),
        # Verify unix socket URLs are handled properly
        (
            {"sock": "/tmp/jp-test.sock"},
            "http+unix://%2Ftmp%2Fjp-test.sock/?token=<generated>",
            "http+unix://%2Ftmp%2Fjp-test.sock/?token=<generated>",
            "http+unix://%2Ftmp%2Fjp-test.sock/",
        ),
        (
            {"base_url": "/", "default_url": "/test/", "sock": "/tmp/jp-test.sock"},
            "http+unix://%2Ftmp%2Fjp-test.sock/test/?token=<generated>",
            "http+unix://%2Ftmp%2Fjp-test.sock/test/?token=<generated>",
            "http+unix://%2Ftmp%2Fjp-test.sock/",
        ),
        (
            {"ip": ""},
            "http://localhost:8888/?token=<generated>",
            "http://127.0.0.1:8888/?token=<generated>",
            "http://localhost:8888/",
        ),
    ],
)
def test_urls(config, public_url, local_url, connection_url):
    # Verify we're working with a clean instance.
    ServerApp.clear_instance()
    serverapp = ServerApp.instance(**config)
    serverapp.init_configurables()
    token = serverapp.identity_provider.token
    # If a token is generated (not set by config), update
    # expected_url with token.
    if serverapp.identity_provider.token_generated:
        public_url = public_url.replace("<generated>", token)
        local_url = local_url.replace("<generated>", token)
        connection_url = connection_url.replace("<generated>", token)
    assert serverapp.public_url == public_url
    assert serverapp.local_url == local_url
    assert serverapp.connection_url == connection_url
    # Cleanup singleton after test.
    ServerApp.clear_instance()


# Preferred dir tests
# ----------------------------------------------------------------------------
@pytest.mark.filterwarnings("ignore::FutureWarning")
def test_valid_preferred_dir(tmp_path, jp_configurable_serverapp):
    path = str(tmp_path)
    app = jp_configurable_serverapp(root_dir=path, preferred_dir=path)
    assert app.root_dir == path
    assert app.preferred_dir == path
    assert app.root_dir == app.preferred_dir
    assert app.contents_manager.root_dir == path
    assert app.contents_manager.preferred_dir == ""


@pytest.mark.filterwarnings("ignore::FutureWarning")
def test_valid_preferred_dir_is_root_subdir(tmp_path, jp_configurable_serverapp):
    path = str(tmp_path)
    path_subdir = str(tmp_path / "subdir")
    os.makedirs(path_subdir, exist_ok=True)
    app = jp_configurable_serverapp(root_dir=path, preferred_dir=path_subdir)
    assert app.root_dir == path
    assert app.preferred_dir == path_subdir
    assert app.preferred_dir.startswith(app.root_dir)
    assert app.contents_manager.preferred_dir == "subdir"


def test_valid_preferred_dir_does_not_exist(tmp_path, jp_configurable_serverapp):
    path = str(tmp_path)
    path_subdir = str(tmp_path / "subdir")
    with pytest.raises(TraitError) as error:
        jp_configurable_serverapp(root_dir=path, preferred_dir=path_subdir)

    assert "No such preferred dir:" in str(error)


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_preferred_dir_validation_sync_regression(
    tmp_path, jp_configurable_serverapp, jp_file_contents_manager_class
):
    path = str(tmp_path)
    path_subdir = str(tmp_path / "subdir")
    os.makedirs(path_subdir, exist_ok=True)
    app = jp_configurable_serverapp(
        root_dir=path,
        contents_manager_class=jp_file_contents_manager_class,
    )
    app.contents_manager.preferred_dir = path_subdir
    assert app.preferred_dir == path_subdir
    assert app.preferred_dir.startswith(app.root_dir)
    assert app.contents_manager.preferred_dir == "subdir"


# This tests some deprecated behavior as well
@pytest.mark.filterwarnings("ignore::FutureWarning")
@pytest.mark.parametrize(
    "root_dir_loc,preferred_dir_loc,config_target",
    [
        ("cli", "cli", "ServerApp"),
        ("cli", "cli", "FileContentsManager"),
        ("cli", "config", "ServerApp"),
        ("cli", "config", "FileContentsManager"),
        ("cli", "default", "ServerApp"),
        ("cli", "default", "FileContentsManager"),
        ("config", "cli", "ServerApp"),
        ("config", "cli", "FileContentsManager"),
        ("config", "config", "ServerApp"),
        ("config", "config", "FileContentsManager"),
        ("config", "default", "ServerApp"),
        ("config", "default", "FileContentsManager"),
        ("default", "cli", "ServerApp"),
        ("default", "cli", "FileContentsManager"),
        ("default", "config", "ServerApp"),
        ("default", "config", "FileContentsManager"),
        ("default", "default", "ServerApp"),
        ("default", "default", "FileContentsManager"),
    ],
)
def test_preferred_dir_validation(
    root_dir_loc,
    preferred_dir_loc,
    config_target,
    tmp_path,
    jp_config_dir,
    jp_configurable_serverapp,
):
    expected_root_dir = str(tmp_path)

    os_preferred_dir = str(tmp_path / "subdir")
    os.makedirs(os_preferred_dir, exist_ok=True)
    config_preferred_dir = os_preferred_dir if config_target == "ServerApp" else "subdir"
    config_preferred_dir = config_preferred_dir + "/"  # add trailing slash to ensure it is removed
    expected_preferred_dir = "subdir"

    argv = []
    kwargs = {"root_dir": None}

    config_lines = []
    config_file = None
    if root_dir_loc == "config" or preferred_dir_loc == "config":
        config_file = jp_config_dir.joinpath("jupyter_server_config.py")

    if root_dir_loc == "cli":
        argv.append(f"--{config_target}.root_dir={expected_root_dir}")
    if root_dir_loc == "config":
        config_lines.append(f'c.{config_target}.root_dir = r"{expected_root_dir}"')
    if root_dir_loc == "default":
        expected_root_dir = os.getcwd()

    if preferred_dir_loc == "cli":
        argv.append(f"--{config_target}.preferred_dir={config_preferred_dir}")
    if preferred_dir_loc == "config":
        config_lines.append(f'c.{config_target}.preferred_dir = r"{config_preferred_dir}"')
    if preferred_dir_loc == "default":
        expected_preferred_dir = ""

    if config_file is not None:
        config_file.write_text("\n".join(config_lines))

    if argv:
        kwargs["argv"] = argv  # type:ignore

    if root_dir_loc == "default" and preferred_dir_loc != "default":  # error expected
        with pytest.raises(SystemExit):
            jp_configurable_serverapp(**kwargs)
    else:
        app = jp_configurable_serverapp(**kwargs)
        assert app.contents_manager.root_dir == expected_root_dir
        assert app.contents_manager.preferred_dir == expected_preferred_dir
        assert ".." not in expected_preferred_dir


def test_invalid_preferred_dir_does_not_exist(tmp_path, jp_configurable_serverapp):
    path = str(tmp_path)
    path_subdir = str(tmp_path / "subdir")
    with pytest.raises(TraitError) as error:
        app = jp_configurable_serverapp(root_dir=path, preferred_dir=path_subdir)

    assert "No such preferred dir:" in str(error)


def test_invalid_preferred_dir_does_not_exist_set(tmp_path, jp_configurable_serverapp):
    path = str(tmp_path)
    path_subdir = str(tmp_path / "subdir")

    app = jp_configurable_serverapp(root_dir=path)
    with pytest.raises(TraitError) as error:
        app.preferred_dir = path_subdir

    assert "No such preferred dir:" in str(error)


@pytest.mark.filterwarnings("ignore::FutureWarning")
def test_invalid_preferred_dir_not_root_subdir(tmp_path, jp_configurable_serverapp):
    path = str(tmp_path / "subdir")
    os.makedirs(path, exist_ok=True)
    not_subdir_path = str(tmp_path)

    with pytest.raises(SystemExit):
        jp_configurable_serverapp(root_dir=path, preferred_dir=not_subdir_path)


async def test_invalid_preferred_dir_not_root_subdir_set(tmp_path, jp_configurable_serverapp):
    path = str(tmp_path / "subdir")
    os.makedirs(path, exist_ok=True)
    not_subdir_path = os.path.relpath(tmp_path, path)

    app = jp_configurable_serverapp(root_dir=path)
    with pytest.raises(TraitError) as error:
        app.contents_manager.preferred_dir = not_subdir_path

    assert "is outside root contents directory" in str(error.value)


async def test_absolute_preferred_dir_not_root_subdir_set(tmp_path, jp_configurable_serverapp):
    path = str(tmp_path / "subdir")
    os.makedirs(path, exist_ok=True)
    not_subdir_path = str(tmp_path)

    app = jp_configurable_serverapp(root_dir=path)

    with pytest.raises(TraitError) as error:
        app.contents_manager.preferred_dir = not_subdir_path

    if os.name == "nt":
        assert "is not a relative API path" in str(error.value)
    else:
        assert "Preferred directory not found" in str(error.value)


def test_random_ports():
    ports = list(random_ports(500, 50))
    assert len(ports) == 50


def test_server_web_application(jp_serverapp):
    server: ServerApp = jp_serverapp
    server.default_url = "/foo"
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        app = ServerWebApplication(
            server,
            [],
            server.kernel_manager,
            server.contents_manager,
            server.session_manager,
            server.kernel_manager,
            server.config_manager,
            server.event_logger,
            ["jupyter_server.gateway.handlers"],
            server.log,
            server.base_url,
            server.default_url,
            {},
            {},
        )
    app.init_handlers([], app.settings)


def test_misc(jp_serverapp, tmp_path):
    app: ServerApp = jp_serverapp
    assert app.terminals_enabled is True
    app.extra_args = [str(tmp_path)]
    app.parse_command_line([])


def test_deprecated_props(jp_serverapp, tmp_path):
    app: ServerApp = jp_serverapp
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        app.cookie_options = dict(foo=1)
        app.get_secure_cookie_kwargs = dict(bar=1)
        app.notebook_dir = str(tmp_path)
        app.server_extensions = dict(foo=True)
        app.kernel_ws_protocol = "foo"
        app.limit_rate = True
        app.iopub_msg_rate_limit = 10
        app.iopub_data_rate_limit = 10
        app.rate_limit_window = 10
    with pytest.raises(SystemExit):
        app.pylab = "foo"


def test_signals(jp_serverapp):
    app: ServerApp = jp_serverapp
    app.answer_yes = True
    app._restore_sigint_handler()
    app._handle_sigint(None, None)
    app._confirm_exit()
    app._signal_info(None, None)


async def test_shutdown_no_activity(jp_serverapp):
    app: ServerApp = jp_serverapp
    app.extension_manager.extensions = {}
    app.exit = lambda _: None  # type:ignore
    app.shutdown_no_activity()
    app.shutdown_no_activity_timeout = 1
    app.init_shutdown_no_activity()


def test_running_server_info(jp_serverapp):
    app: ServerApp = jp_serverapp
    app.running_server_info(True)


@pytest.mark.parametrize("should_exist", [True, False])
def test_browser_open_files(jp_configurable_serverapp, should_exist, caplog):
    app = jp_configurable_serverapp(no_browser_open_file=not should_exist)
    assert os.path.exists(app.browser_open_file) == should_exist
    url = urljoin("file:", pathname2url(app.browser_open_file))
    url_messages = [rec.message for rec in caplog.records if url in rec.message]
    assert url_messages if should_exist else not url_messages


def test_deprecated_notebook_dir_priority(jp_configurable_serverapp, tmp_path):
    notebook_dir = tmp_path / "notebook"
    notebook_dir.mkdir()
    cli_dir = tmp_path / "cli"
    cli_dir.mkdir()

    app = jp_configurable_serverapp(argv=[str(cli_dir)], root_dir=None)
    assert app._root_dir_set

    # simulate delayed loading of notebook_dir config
    # this should _not_ take priority over an explicitly set root_dir
    # as done by notebook_shim
    cfg = Config()
    cfg.ServerApp.notebook_dir = str(notebook_dir)
    app.update_config(cfg)
    assert app.root_dir == str(cli_dir)
