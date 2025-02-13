from __future__ import annotations

import os

from jupyter_events import EventLogger
from jupyter_events.schema_registry import SchemaRegistryException
from tornado import web
from traitlets import Bool, List, Unicode

from jupyter_server.base.handlers import JupyterHandler
from jupyter_server.extension.application import ExtensionApp, ExtensionAppJinjaMixin
from jupyter_server.extension.handler import ExtensionHandlerJinjaMixin, ExtensionHandlerMixin

STATIC_PATH = os.path.join(os.path.dirname(__file__), "static")

EVENT_SCHEMA = """\
$id: https://events.jupyter.org/mockapp/v1/test
version: '1'
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


class MockExtensionErrorHandler(ExtensionHandlerMixin, JupyterHandler):
    def get(self):
        raise web.HTTPError(418)


class MockExtensionApp(ExtensionAppJinjaMixin, ExtensionApp):
    name = "mockextension"
    template_paths: List[str] = List().tag(config=True)  # type:ignore[assignment]
    static_paths = [STATIC_PATH]  # type:ignore[assignment]
    mock_trait = Unicode("mock trait", config=True)
    loaded = False
    started = Bool(False)

    serverapp_config = {
        "jpserver_extensions": {
            "tests.extension.mockextensions.mock1": True,
            "tests.extension.mockextensions.app.mockextension_notemplate": True,
        }
    }

    async def _start_jupyter_server_extension(self, serverapp):
        self.started = True

    @staticmethod
    def get_extension_package():
        return "tests.extension.mockextensions"

    def initialize_settings(self):
        # Only add this event if it hasn't already been added.
        # Log the error if it fails, but don't crash the app.
        try:
            elogger: EventLogger = self.serverapp.event_logger  # type:ignore[union-attr, assignment]
            elogger.register_event_schema(EVENT_SCHEMA)
        except SchemaRegistryException as err:
            self.log.error(err)

    def initialize_handlers(self):
        self.handlers.append(("/mock", MockExtensionHandler))
        self.handlers.append(("/mock_template", MockExtensionTemplateHandler))
        self.handlers.append(("/mock_error_template", MockExtensionErrorHandler))
        self.loaded = True


class MockExtensionNoTemplateApp(ExtensionApp):
    name = "mockextension_notemplate"
    loaded = False

    @staticmethod
    def get_extension_package():
        return "tests.extension.mockextensions"

    def initialize_handlers(self):
        self.handlers.append(("/mock_error_notemplate", MockExtensionErrorHandler))
        self.loaded = True

    async def _start_jupyter_server_extension(self, serverapp):
        self.started = True


if __name__ == "__main__":
    MockExtensionApp.launch_instance()
