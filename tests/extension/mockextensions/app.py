from traitlets import Unicode, List

from jupyter_server.base.handlers import JupyterHandler
from jupyter_server.extension.application import (
    ExtensionApp,
    ExtensionAppJinjaMixin
)
from jupyter_server.extension.handler import (
    ExtensionHandlerMixin,
    ExtensionHandlerJinjaMixin
)


class MockExtensionHandler(ExtensionHandlerMixin, JupyterHandler):

    def get(self):
        self.finish(self.config.mock_trait)


class MockExtensionTemplateHandler(
    ExtensionHandlerJinjaMixin,
    ExtensionHandlerMixin,
    JupyterHandler
):

    def get(self):
        self.write(self.render_template("index.html"))


class MockExtensionApp(ExtensionAppJinjaMixin, ExtensionApp):

    name = 'mockextension'
    template_paths = List().tag(config=True)
    mock_trait = Unicode('mock trait', config=True)
    loaded = False

    def initialize_handlers(self):
        self.handlers.append(('/mock', MockExtensionHandler))
        self.handlers.append(('/mock_template', MockExtensionTemplateHandler))
        self.loaded = True