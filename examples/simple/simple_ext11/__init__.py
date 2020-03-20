from .application import SimpleApp11

def _jupyter_server_extension_paths():
    return [
        {
            'module': 'simple_ext11',
            'app': SimpleApp11
        }
    ]

load_jupyter_server_extension = SimpleApp11.load_jupyter_server_extension
