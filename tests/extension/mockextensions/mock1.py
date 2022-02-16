"""A mock extension named `mock1` for testing purposes.
"""
# by the test functions.
def _jupyter_server_extension_paths():
    return [{"module": "jupyter_server.tests.extension.mockextensions.mock1"}]


def _load_jupyter_server_extension(serverapp):
    serverapp.mockI = True
    serverapp.mock_shared = "I"
