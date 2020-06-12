import pytest
from jupyter_server.serverapp import ServerApp


@pytest.fixture
def server_config(request, template_dir):
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
    return extension_manager.paths["mockextension"].app


def test_initialize(mock_extension, template_dir):
    # Check that settings and handlers were added to the mock extension.
    assert isinstance(mock_extension.serverapp, ServerApp)
    assert len(mock_extension.handlers) > 0
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
    serverapp,
    trait_name,
    trait_value,
    extension_manager
):
    extension = extension_manager.paths['mockextension'].app
    assert getattr(extension, trait_name) == trait_value


def test_extensionapp_load_config_file(
    extension_environ,
    config_file,
    extension_manager,
    serverapp,
):
    extension = extension_manager.paths['mockextension'].app
    # Assert default config_file_paths is the same in the app and extension.
    assert extension.config_file_paths == serverapp.config_file_paths
    assert extension.config_dir == serverapp.config_dir
    assert extension.config_file_name == 'jupyter_mockextension_config'
    # Assert that the trait is updated by config file
    assert extension.mock_trait == 'config from file'
