# Function that makes these extensions discoverable
# by the test functions.
def _jupyter_server_extension_points():
    return [
        {"module": "tests.events.mock_extension"},
    ]
