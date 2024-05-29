"""Extension entry point."""

from .application import SimpleApp11


def _jupyter_server_extension_points():
    return [{"module": "simple_ext11.application", "app": SimpleApp11}]


_jupyter_server_extension_paths = _jupyter_server_extension_points
