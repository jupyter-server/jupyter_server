"""Add deprecation warning here.
"""
from jupyter_server.services.kernels.connection.base import (
    deserialize_binary_message,
    deserialize_msg_from_ws_v1,
    serialize_binary_message,
    serialize_msg_to_ws_v1,
)
from jupyter_server.services.kernels.websocket import WebSocketMixin
