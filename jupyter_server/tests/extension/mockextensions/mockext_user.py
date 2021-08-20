"""A mock extension named `mockext_user` for testing purposes.
"""
# Function that makes these extensions discoverable
# by the test functions.
def _jupyter_server_extension_paths():
    return [{"module": "jupyter_server.tests.extension.mockextensions.mockext_user"}]


def _load_jupyter_server_extension(serverapp):
    pass
