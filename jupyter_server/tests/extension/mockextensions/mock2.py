"""A mock extension named `mock2` for testing purposes.
"""


# by the test functions.
def _jupyter_server_extension_paths():
    return [
        {
            'module': 'jupyter_server.tests.extension.mockextensions.mock2'
        }
    ]


def _load_jupyter_server_extension(serverapp):
    serverapp.mockII = True
    serverapp.mock_shared = 'II'
