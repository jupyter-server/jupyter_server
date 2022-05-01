"""A Websocket Handler for emitting Jupyter server events.

.. versionadded:: 2.0
"""
import logging

from jupyter_telemetry.eventlog import _skip_message
from pythonjsonlogger import jsonlogger
from tornado import web, websocket

from jupyter_server.base.handlers import JupyterHandler

AUTH_RESOURCE = "events"


class TornadoWebSocketLoggingHandler(logging.Handler):
    """Python logging handler that routes records to a Tornado websocket."""

    def __init__(self, websocket):
        super().__init__()
        self.websocket = websocket

    def emit(self, record):
        """Emit the message across the websocket"""
        self.websocket.write_message(record.msg)


class SubscribeWebsocket(
    JupyterHandler,
    websocket.WebSocketHandler,
):
    """Websocket Handler for listening to eve"""

    auth_resource = AUTH_RESOURCE

    def pre_get(self):
        """Handles authentication/authorization when
        attempting to subscribe to events emitted by
        Jupyter Server's eventbus.
        """
        # authenticate the request before opening the websocket
        user = self.current_user
        if user is None:
            self.log.warning("Couldn't authenticate WebSocket connection")
            raise web.HTTPError(403)

        # authorize the user.
        if not self.authorizer.is_authorized(self, user, "execute", "events"):
            raise web.HTTPError(403)

    async def get(self, *args, **kwargs):
        self.pre_get()
        res = super().get(*args, **kwargs)
        await res

    @property
    def event_bus(self):
        """Jupyter Server's event bus that emits structured event data."""
        return self.settings["event_bus"]

    def open(self):
        """Routes events that are emitted by Jupyter Server's
        EventBus to a WebSocket client in the browser.
        """
        self.logging_handler = TornadoWebSocketLoggingHandler(self)
        # Add a JSON formatter to the handler.
        formatter = jsonlogger.JsonFormatter(json_serializer=_skip_message)
        self.logging_handler.setFormatter(formatter)
        # To do: add an eventlog.add_handler method to jupyter_telemetry.
        self.event_bus.log.addHandler(self.logging_handler)
        self.event_bus.handlers.append(self.logging_handler)

    def on_close(self):
        self.event_bus.log.removeHandler(self.logging_handler)


default_handlers = [
    (r"/api/events/subscribe", SubscribeWebsocket),
]
