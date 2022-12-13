from .mock_extension import _load_jupyter_server_extension  # noqa: F401

# Function that makes these extensions discoverable
# by the test functions.


def _jupyter_server_extension_points():
    return [
        {"module": "tests.services.events.mockextension"},
    ]
