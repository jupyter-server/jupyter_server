import json
from io import StringIO
from logging import StreamHandler
from typing import Any

import pytest
from traitlets.config import Config

from jupyter_server.serverapp import ServerApp

from .mockextensions.app import MockExtensionApp


@pytest.fixture
def jp_server_config(jp_template_dir):
    config = {
        "ServerApp": {
            "jpserver_extensions": {"tests.extension.mockextensions": True},
        },
        "MockExtensionApp": {
            "template_paths": [str(jp_template_dir)],
            "log_level": "DEBUG",
        },
    }
    return config


@pytest.fixture
def mock_extension(extension_manager):
    name = "tests.extension.mockextensions"
    pkg = extension_manager.extensions[name]
    point = pkg.extension_points["mockextension"]
    app = point.app
    return app


def test_initialize(jp_serverapp, jp_template_dir, mock_extension):
    # Check that settings and handlers were added to the mock extension.
    assert isinstance(mock_extension.serverapp, ServerApp)
    assert len(mock_extension.handlers) > 0
    assert mock_extension.loaded
    assert mock_extension.template_paths == [str(jp_template_dir)]


@pytest.mark.parametrize(
    "trait_name, trait_value, jp_argv",
    (
        [
            "mock_trait",
            "test mock trait",
            ["--MockExtensionApp.mock_trait=test mock trait"],
        ],
    ),
)
def test_instance_creation_with_argv(
    trait_name,
    trait_value,
    jp_argv,
    mock_extension,
):
    assert getattr(mock_extension, trait_name) == trait_value


def test_extensionapp_load_config_file(
    config_file,
    jp_serverapp,
    mock_extension,
):
    # Assert default config_file_paths is the same in the app and extension.
    assert mock_extension.config_file_paths == jp_serverapp.config_file_paths
    assert mock_extension.config_dir == jp_serverapp.config_dir
    assert mock_extension.config_file_name == "jupyter_mockextension_config"
    # Assert that the trait is updated by config file
    assert mock_extension.mock_trait == "config from file"


def test_extensionapp_no_parent():
    # make sure we can load config files, even when serverapp is not passed
    # relevant for e.g. shortcuts to config-loading
    app = MockExtensionApp()
    assert isinstance(app.config_file_paths, list)
    assert app.serverapp is not None


OPEN_BROWSER_COMBINATIONS: Any = (
    (True, {}),
    (True, {"ServerApp": {"open_browser": True}}),
    (False, {"ServerApp": {"open_browser": False}}),
    (True, {"MockExtensionApp": {"open_browser": True}}),
    (False, {"MockExtensionApp": {"open_browser": False}}),
    (
        True,
        {
            "ServerApp": {"open_browser": True},
            "MockExtensionApp": {"open_browser": True},
        },
    ),
    (
        False,
        {
            "ServerApp": {"open_browser": True},
            "MockExtensionApp": {"open_browser": False},
        },
    ),
    (
        True,
        {
            "ServerApp": {"open_browser": False},
            "MockExtensionApp": {"open_browser": True},
        },
    ),
    (
        False,
        {
            "ServerApp": {"open_browser": False},
            "MockExtensionApp": {"open_browser": False},
        },
    ),
)


@pytest.mark.parametrize("expected_value, config", OPEN_BROWSER_COMBINATIONS)
async def test_browser_open(monkeypatch, jp_environ, config, expected_value):
    serverapp = MockExtensionApp.initialize_server(config=Config(config))
    assert serverapp.open_browser == expected_value


async def test_load_parallel_extensions(monkeypatch, jp_environ):
    serverapp = MockExtensionApp.initialize_server()
    exts = serverapp.extension_manager.extensions
    assert "tests.extension.mockextensions.mock1" in exts
    assert "tests.extension.mockextensions" in exts

    exts = serverapp.jpserver_extensions
    assert exts["tests.extension.mockextensions.mock1"]
    assert exts["tests.extension.mockextensions"]


async def test_stop_extension(jp_serverapp, caplog):
    """Test the stop_extension method.

    This should be fired by ServerApp.cleanup_extensions.
    """
    calls = 0

    # load extensions (make sure we only have the one extension loaded
    # as well as
    jp_serverapp.extension_manager.load_all_extensions()
    extension_name = "tests.extension.mockextensions"
    apps = set(jp_serverapp.extension_manager.extension_apps)
    assert apps == {"jupyter_server_terminals", extension_name}

    # add a stop_extension method for the extension app
    async def _stop(*args):
        nonlocal calls
        calls += 1

    for apps in jp_serverapp.extension_manager.extension_apps.values():
        for app in apps:
            if app:
                app.stop_extension = _stop

    # call cleanup_extensions, check the logging is correct
    caplog.clear()
    await jp_serverapp.cleanup_extensions()
    assert {msg for *_, msg in caplog.record_tuples} == {
        "Shutting down 2 extensions",
        "jupyter_server_terminals | extension app 'jupyter_server_terminals' stopping",
        f"{extension_name} | extension app 'mockextension' stopping",
        "jupyter_server_terminals | extension app 'jupyter_server_terminals' stopped",
        f"{extension_name} | extension app 'mockextension' stopped",
    }

    # check the shutdown method was called twice
    assert calls == 2


async def test_events(jp_serverapp, jp_fetch):
    stream = StringIO()
    handler = StreamHandler(stream)
    jp_serverapp.event_logger.register_handler(handler)

    await jp_fetch("mock")

    handler.flush()
    output = json.loads(stream.getvalue())
    # Clear the sink.
    stream.truncate(0)
    stream.seek(0)
    assert output["msg"] == "Hello, world!"
