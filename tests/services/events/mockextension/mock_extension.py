import pathlib

from jupyter_server.base.handlers import JupyterHandler
from jupyter_server.utils import url_path_join


class MockEventHandler(JupyterHandler):
    def get(self):
        # Emit an event.
        self.event_logger.emit(
            schema_id="http://event.mockextension.jupyter.org/message",
            data={"event_message": "Hello world, from mock extension!"},
        )


def _load_jupyter_server_extension(serverapp):
    # Register a schema with the EventBus
    schema_file = pathlib.Path(__file__).parent / "mock_extension_event.yaml"
    serverapp.event_logger.register_event_schema(schema_file)
    serverapp.web_app.add_handlers(
        ".*$", [(url_path_join(serverapp.base_url, "/mock/event"), MockEventHandler)]
    )
