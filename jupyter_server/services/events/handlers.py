import logging

import tornado.web
import tornado.websocket
from jupyter_telemetry.eventlog import _skip_message
from pythonjsonlogger import jsonlogger

from jupyter_server.base.handlers import JupyterHandler


class TornadoWebSocketLoggingHandler(logging.Handler):
    """Logging handler that routes records to a Tornado websocket."""

    def __init__(self, websocket):
        super().__init__()
        self.websocket = websocket

    def emit(self, record):
        """Emit the message across the websocket"""
        self.websocket.write_message(record.msg)


class SubscribeWebsocket(
    JupyterHandler,
    tornado.websocket.WebSocketHandler,
):
    @property
    def event_bus(self):
        return self.settings["event_bus"]

    def open(self):
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
