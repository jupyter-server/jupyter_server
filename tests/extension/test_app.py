import pytest

from jupyter_server.serverapp import ServerApp
from jupyter_server.extension.application import ExtensionApp

from .conftest import MockExtension


def test_instance_creation():
    mock_extension = MockExtension()
    assert mock_extension.static_paths == []
    assert mock_extension.template_paths == []
    assert mock_extension.settings == {}
    assert mock_extension.handlers == [] 


def test_initialize(serverapp):
    mock_extension = MockExtension()
    mock_extension.initialize(serverapp)
    # Check that settings and handlers were added to the mock extension.
    assert isinstance(mock_extension.serverapp, ServerApp)
    assert len(mock_extension.settings) > 0
    assert len(mock_extension.handlers) > 0


traits = [
    ('static_paths', ['test']),
    ('template_paths', ['test']),
    ('custom_display_url', '/test_custom_url'),
    ('default_url', '/test_url')
]


@pytest.mark.parametrize(
    'trait_name,trait_value',
    traits
)
def test_instance_creation_with_instance_args(trait_name, trait_value):
    kwarg = {}
    kwarg.setdefault(trait_name, trait_value)
    mock_extension = MockExtension(**kwarg)
    assert getattr(mock_extension, trait_name) == trait_value


@pytest.mark.parametrize(
    'trait_name,trait_value',
    traits
)
def test_instance_creation_with_argv(serverapp, trait_name, trait_value):
    kwarg = {}
    kwarg.setdefault(trait_name, trait_value)

    argv = [
        '--MockExtension.{name}={value}'.format(name=trait_name, value=trait_value)
    ]

    mock_extension = MockExtension()
    mock_extension.initialize(serverapp, argv=argv)
    assert getattr(mock_extension, trait_name) == trait_value
