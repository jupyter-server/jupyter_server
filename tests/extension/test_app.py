import pytest
from jupyter_server.serverapp import ServerApp


@pytest.fixture
def server_config(template_dir):
    config = {
        "ServerApp": {
            "jpserver_extensions": {
                "tests.extension.mockextensions": True
            },
        },
        "MockExtensionApp": {
            "template_paths": [
                str(template_dir)
            ],
            "log_level": 'DEBUG'
        }
    }
    return config


@pytest.fixture
def mock_extension(extension_manager):
    name = "tests.extension.mockextensions"
    pkg = extension_manager.extensions[name]
    point = pkg.extension_points["mockextension"]
    app = point.app
    return app


def test_initialize(serverapp, template_dir, mock_extension):
    # Check that settings and handlers were added to the mock extension.
    assert isinstance(mock_extension.serverapp, ServerApp)
    assert len(mock_extension.handlers) > 0
    assert mock_extension.loaded
    assert mock_extension.template_paths == [str(template_dir)]


@pytest.mark.parametrize(
    'trait_name, trait_value, argv',
    (
        [
            'mock_trait',
            'test mock trait',
            ['--MockExtensionApp.mock_trait="test mock trait"']
        ],
    )
)
def test_instance_creation_with_argv(
    trait_name,
    trait_value,
    mock_extension,
):
    assert getattr(mock_extension, trait_name) == trait_value


def test_extensionapp_load_config_file(
    config_file,
    serverapp,
    mock_extension,
):
    # Assert default config_file_paths is the same in the app and extension.
    assert mock_extension.config_file_paths == serverapp.config_file_paths
    assert mock_extension.config_dir == serverapp.config_dir
    assert mock_extension.config_file_name == 'jupyter_mockextension_config'
    # Assert that the trait is updated by config file
    assert mock_extension.mock_trait == 'config from file'
