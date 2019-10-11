from .application import SimpleServer

EXTENSION_NAME = "simple_ext"

def _jupyter_server_extension_paths():
    return [{"module": EXTENSION_NAME}]

load_jupyter_server_extension = SimpleServer.load_jupyter_server_extension
