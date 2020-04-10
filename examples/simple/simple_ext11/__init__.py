from .application import SimpleApp11


def _jupyter_server_extension_paths():
    return [
        {
            'module': 'simple_ext11.application',
            'app': SimpleApp11
        }
    ]