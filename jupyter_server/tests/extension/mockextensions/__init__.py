"""A mock extension module with a list of extensions
to load in various tests.
"""
from .app import MockExtensionApp


# Function that makes these extensions discoverable
# by the test functions.
def _jupyter_server_extension_points():
    return [
        {"module": "jupyter_server.tests.extension.mockextensions.app", "app": MockExtensionApp},
        {"module": "jupyter_server.tests.extension.mockextensions.mock1"},
        {"module": "jupyter_server.tests.extension.mockextensions.mock2"},
        {"module": "jupyter_server.tests.extension.mockextensions.mock3"},
    ]
