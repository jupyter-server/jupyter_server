import sys
import pytest
from traitlets import Unicode


from jupyter_core import paths
from jupyter_server.extension import serverextension
from jupyter_server.extension.serverextension import _get_config_dir
from jupyter_server.extension.application import ExtensionApp
from jupyter_server.extension.handler import ExtensionHandler

# ----------------- Mock Extension App ----------------------

class MockExtensionHandler(ExtensionHandler):

    def get(self):
        self.finish(self.config.mock_trait)


class MockExtensionApp(ExtensionApp):
    extension_name = 'mockextension'
    mock_trait = Unicode('mock trait', config=True)

    loaded = False

    def initialize_handlers(self):
        self.handlers.append(('/mock', MockExtensionHandler))
        self.loaded = True

    @staticmethod
    def _jupyter_server_extension_paths():
        return [{
            'module': '_mockdestination/index'
        }]

@pytest.fixture
def make_mock_extension_app(template_dir):
    def _make_mock_extension_app(**kwargs):
        kwargs.setdefault('template_paths', [str(template_dir)])
        return MockExtensionApp(**kwargs)

    return _make_mock_extension_app


@pytest.fixture
def config_file(config_dir):
    """"""
    f = config_dir.joinpath("jupyter_mockextension_config.py")
    f.write_text("c.MockExtensionApp.mock_trait ='config from file'")
    return f


@pytest.fixture
def extended_serverapp(serverapp, make_mock_extension_app):
    """"""
    m = make_mock_extension_app()
    m.initialize(serverapp)
    return m


@pytest.fixture
def inject_mock_extension(environ, extension_environ, make_mock_extension_app):
    """Fixture that can be used to inject a mock Jupyter Server extension into the tests namespace.

        Usage: inject_mock_extension({'extension_name': ExtensionClass})
    """
    def ext(modulename="mockextension"):
        sys.modules[modulename] = e = make_mock_extension_app()
        return e

    return ext
