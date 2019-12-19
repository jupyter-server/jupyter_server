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
    extension_name = "mockextension"
    mock_trait = Unicode("mock trait", config=True)

    loaded = False

    def initialize_handlers(self):
        self.handlers.append(("/mock", MockExtensionHandler))
        self.loaded = True

    @staticmethod
    def _jupyter_server_extension_paths():
        return [{"module": "_mockdestination/index"}]


@pytest.fixture
def extension_environ(env_config_path, monkeypatch):
    monkeypatch.setattr(serverextension, "ENV_CONFIG_PATH", [str(env_config_path)])
    monkeypatch.setattr(serverextension, "ENV_CONFIG_PATH", [str(env_config_path)])


@pytest.fixture
def config_file(config_dir):
    f = config_dir.joinpath("jupyter_mockextension_config.py")
    f.write_text("c.MockExtensionApp.mock_trait ='config from file'")
    return f


@pytest.fixture
def extended_serverapp(serverapp):
    m = MockExtensionApp()
    m.initialize(serverapp)
    return m


@pytest.fixture
def inject_mock_extension(environ, extension_environ):
    def ext(modulename="mockextension"):
        sys.modules[modulename] = e = MockExtensionApp()
        return e

    return ext
