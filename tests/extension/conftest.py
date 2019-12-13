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
def extended_serverapp(serverapp):
    m = MockExtension()
    m.initialize(serverapp)
    return m