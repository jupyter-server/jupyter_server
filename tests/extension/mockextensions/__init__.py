"""A mock extension module with a list of extensions
to load in various tests.
"""
from .app import MockExtensionApp


# Function that makes these extensions discoverable
# by the test functions.
def _jupyter_server_extension_points():
    return [
        {
            'module': 'tests.extension.mockextensions.app',
            'app': MockExtensionApp
        },
        {
            'module': 'tests.extension.mockextensions.mock1'
        },
        {
            'module': 'tests.extension.mockextensions.mock2'
        },
        {
            'module': 'tests.extension.mockextensions.mock3'
        }
    ]
