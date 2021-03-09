import pytest
from traitlets.config import Config
from jupyter_server.serverapp import ServerApp
from .mockextensions.app import MockExtensionApp


@pytest.fixture
def jp_server_config(jp_template_dir):
    config = {
        "ServerApp": {
            "jpserver_extensions": {
                "jupyter_server.tests.extension.mockextensions": True
            },
        },
        "MockExtensionApp": {
            "template_paths": [
                str(jp_template_dir)
            ],
            "log_level": 'DEBUG'
        }
    }
    return config


@pytest.fixture
def mock_extension(extension_manager):
    name = "jupyter_server.tests.extension.mockextensions"
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
    'trait_name, trait_value, jp_argv',
    (
        [
            'mock_trait',
            'test mock trait',
            ['--MockExtensionApp.mock_trait=test mock trait']
        ],
    )
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
    assert mock_extension.config_file_name == 'jupyter_mockextension_config'
    # Assert that the trait is updated by config file
    assert mock_extension.mock_trait == 'config from file'


OPEN_BROWSER_COMBINATIONS = (
    (True, {}),
    (True, {'ServerApp': {'open_browser': True}}),
    (False, {'ServerApp': {'open_browser': False}}),
    (True, {'MockExtensionApp': {'open_browser': True}}),
    (False, {'MockExtensionApp': {'open_browser': False}}),
    (True, {'ServerApp': {'open_browser': True}, 'MockExtensionApp': {'open_browser': True}}),
    (False, {'ServerApp': {'open_browser': True}, 'MockExtensionApp': {'open_browser': False}}),
    (True, {'ServerApp': {'open_browser': False}, 'MockExtensionApp': {'open_browser': True}}),
    (False, {'ServerApp': {'open_browser': False}, 'MockExtensionApp': {'open_browser': False}}),
)

@pytest.mark.parametrize(
    'expected_value, config', OPEN_BROWSER_COMBINATIONS
)
def test_browser_open(monkeypatch, jp_environ, config, expected_value):
    serverapp = MockExtensionApp.initialize_server(config=Config(config))
    assert serverapp.open_browser == expected_value
