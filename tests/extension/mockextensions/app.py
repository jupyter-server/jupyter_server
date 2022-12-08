import os

from jupyter_events import EventLogger
from jupyter_events.schema_registry import SchemaRegistryException
from traitlets import List, Unicode

from jupyter_server.base.handlers import JupyterHandler
from jupyter_server.extension.application import ExtensionApp, ExtensionAppJinjaMixin
from jupyter_server.extension.handler import ExtensionHandlerJinjaMixin, ExtensionHandlerMixin

STATIC_PATH = os.path.join(os.path.dirname(__file__), "static")

EVENT_SCHEMA = """\
$id: https://events.jupyter.org/mockapp/v1/test
version: 1
properties:
  msg:
    type: string
required:
- msg
"""


# Function that makes these extensions discoverable
# by the test functions.
def _jupyter_server_extension_points():
    return [{"module": __name__, "app": MockExtensionApp}]


class MockExtensionHandler(ExtensionHandlerMixin, JupyterHandler):
    def get(self):
        self.event_logger.emit(
            schema_id="https://events.jupyter.org/mockapp/v1/test", data={"msg": "Hello, world!"}
        )
        self.finish(self.config.mock_trait)


class MockExtensionTemplateHandler(
    ExtensionHandlerJinjaMixin, ExtensionHandlerMixin, JupyterHandler
):
    def get(self):
        self.write(self.render_template("index.html"))


class MockExtensionApp(ExtensionAppJinjaMixin, ExtensionApp):

    name = "mockextension"
    template_paths = List().tag(config=True)
    static_paths = [STATIC_PATH]
    mock_trait = Unicode("mock trait", config=True)
    loaded = False

    serverapp_config = {"jpserver_extensions": {"tests.extension.mockextensions.mock1": True}}

    @staticmethod
    def get_extension_package():
        return "tests.extension.mockextensions"

    def initialize_settings(self):
        # Only add this event if it hasn't already been added.
        # Log the error if it fails, but don't crash the app.
        try:
            elogger: EventLogger = self.serverapp.event_logger
            elogger.register_event_schema(EVENT_SCHEMA)
        except SchemaRegistryException as err:
            self.log.error(err)
            pass

    def initialize_handlers(self):
        self.handlers.append(("/mock", MockExtensionHandler))
        self.handlers.append(("/mock_template", MockExtensionTemplateHandler))
        self.loaded = True


if __name__ == "__main__":
    MockExtensionApp.launch_instance()
