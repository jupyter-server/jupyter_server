"""The Jupyter Server"""
import os
import pathlib

DEFAULT_STATIC_FILES_PATH = os.path.join(os.path.dirname(__file__), "static")
DEFAULT_TEMPLATE_PATH_LIST = [
    os.path.dirname(__file__),
    os.path.join(os.path.dirname(__file__), "templates"),
]

DEFAULT_JUPYTER_SERVER_PORT = 8888
JUPYTER_SERVER_EVENTS_URI = "https://events.jupyter.org/jupyter_server"
DEFAULT_EVENTS_SCHEMA_PATH = pathlib.Path(__file__).parent / "event_schemas"

del os

from ._version import __version__, version_info  # noqa
from .base.call_context import CallContext  # noqa


def _cleanup():
    pass
