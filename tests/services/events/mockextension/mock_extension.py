import pathlib

from jupyter_server.base.handlers import JupyterHandler
from jupyter_server.utils import url_path_join


class MockEventHandler(JupyterHandler):
    def get(self):
        # Emit an event.
        self.event_bus.record_event(
            schema_name="event.mockextension.jupyter.org/message",
            version=1,
            event={"event_message": "Hello world, from mock extension!"},
        )


def _load_jupyter_server_extension(serverapp):
    # Register a schema with the EventBus
    schema_file = pathlib.Path(__file__).parent / "mock_extension_event.yaml"
    serverapp.event_bus.register_schema_file(schema_file)
    serverapp.web_app.add_handlers(
        ".*$", [(url_path_join(serverapp.base_url, "/mock/event"), MockEventHandler)]
    )
