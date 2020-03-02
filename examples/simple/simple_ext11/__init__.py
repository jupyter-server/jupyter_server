from .application import SimpleApp1

def _jupyter_server_extension_paths():
    return [
        {'module': 'simple_ext1'}
    ]

load_jupyter_server_extension = SimpleApp1.load_jupyter_server_extension
