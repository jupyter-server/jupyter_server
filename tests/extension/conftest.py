import pytest
from traitlets import Unicode

from jupyter_server.extension.application import ExtensionApp
from jupyter_server.extension.handler import ExtensionHandler

# --------------- Build a mock extension --------------

class MockExtensionHandler(ExtensionHandler):

    def get(self):
        self.finish(self.config.mock_trait)


class MockExtension(ExtensionApp):
    extension_name = 'mock'
    mock_trait = Unicode('mock trait', config=True)

    def initialize_handlers(self):
        self.handlers.append(('/mock', MockExtensionHandler))


@pytest.fixture
def config_file(config_dir):
    f = config_dir.joinpath('jupyter_mock_config.py')
    f.write_text("c.MockExtension.mock_trait ='config from file'")
    return f


@pytest.fixture
def extended_serverapp(serverapp):
    m = MockExtension()
    m.initialize(serverapp)
    return m