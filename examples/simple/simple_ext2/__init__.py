from .application import SimpleApp2

def _jupyter_server_extension_paths():
    return [
        {'module': 'simple_ext2'},
    ]

load_jupyter_server_extension = SimpleApp2.load_jupyter_server_extension
