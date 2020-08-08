"""A mock extension named `mockext_py` for testing purposes.
"""


# Function that makes these extensions discoverable
# by the test functions.
def _jupyter_server_extension_paths():
    return [
        {
            'module': 'tests.extension.mockextensions.mockext_py'
        }
    ]


def _load_jupyter_server_extension(serverapp):
    pass