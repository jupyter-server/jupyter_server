"""A Websocket Handler for emitting Jupyter server events.

.. versionadded:: 2.0
"""
import logging
from datetime import datetime

from jupyter_telemetry.eventlog import _skip_message
from pythonjsonlogger import jsonlogger
from tornado import web, websocket

from jupyter_server.auth import authorized
from jupyter_server.base.handlers import JupyterHandler

from ...base.handlers import APIHandler

AUTH_RESOURCE = "events"


class WebSocketLoggingHandler(logging.Handler):
    """Python logging handler that routes records to a Tornado websocket."""

    def __init__(self, websocket, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.websocket = websocket

    def emit(self, record):
        """Emit the message across the websocket"""
        self.websocket.write_message(record.msg)


class SubscribeWebsocket(
    JupyterHandler,
    websocket.WebSocketHandler,
):
    """Websocket handler for subscribing to events"""

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

    def open(self):
        """Routes events that are emitted by Jupyter Server's
        EventBus to a WebSocket client in the browser.
        """
        self.logging_handler = WebSocketLoggingHandler(self)
        # Add a JSON formatter to the handler.
        formatter = jsonlogger.JsonFormatter(json_serializer=_skip_message)
        self.logging_handler.setFormatter(formatter)
        # To do: add an eventlog.add_handler method to jupyter_telemetry.
        self.event_bus.log.addHandler(self.logging_handler)
        self.event_bus.handlers.append(self.logging_handler)

    def on_close(self):
        self.event_bus.log.removeHandler(self.logging_handler)
        self.event_bus.handlers.remove(self.logging_handler)


class EventHandler(APIHandler):
    """REST api handler for events"""

    auth_resource = AUTH_RESOURCE

    @web.authenticated
    @authorized
    async def post(self):
        payload = self.get_json_body()
        if payload is None:
            raise web.HTTPError(400, "No JSON data provided")

        try:
            if "timestamp" in payload:
                timestamp = datetime.strptime(payload["timestamp"], "%Y-%m-%d %H:%M:%S.%f %z")
            else:
                timestamp = None

            if "schema_name" not in payload:
                raise web.HTTPError(400, f"'schema_name' missing in JSON data")

            if "version" not in payload:
                raise web.HTTPError(400, f"'version' missing in JSON data")

            if "event" not in payload:
                raise web.HTTPError(400, f"'event' missing in JSON data")

            self.event_bus.record_event(
                schema_name=payload["schema_name"],
                version=payload["version"],
                event=payload["event"],
                timestamp_override=timestamp,
            )
            self.set_status(204)
            self.finish()
        except Exception as e:
            raise web.HTTPError(500, str(e)) from e


default_handlers = [
    (r"/api/events", EventHandler),
    (r"/api/events/subscribe", SubscribeWebsocket),
]
