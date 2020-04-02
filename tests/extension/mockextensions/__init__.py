"""A mock extension module with a list of extensions
to load in various tests.
"""
from .app import MockExtensionApp


# Function that makes these extensions discoverable
# by the test functions.
def _jupyter_server_extension_paths():
    return [
        {
            'module': 'mockextension',
            'app': MockExtensionApp
        },
        {
            'module': 'mock1'
        },
        {
            'module': 'mock2'
        },
        {
            'module': 'mock3'
        }
    ]
