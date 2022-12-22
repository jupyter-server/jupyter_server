"""The extension entry point."""
from .application import SimpleApp2


def _jupyter_server_extension_paths():
    return [
        {"module": "simple_ext2.application", "app": SimpleApp2},
    ]
