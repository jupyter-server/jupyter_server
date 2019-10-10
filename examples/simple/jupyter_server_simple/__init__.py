from .application import ServerSimple

EXTENSION_NAME = "server_simple"

def _jupyter_server_extension_paths():
    return [{"module": EXTENSION_NAME}]

load_jupyter_server_extension = ServerSimple.load_jupyter_server_extension
