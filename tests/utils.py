import json
from typing import NewType

from tornado.httpclient import HTTPClientError
from tornado.web import HTTPError

some_resource = "The very model of a modern major general"

sample_kernel_json = {
    "argv": ["cat", "{connection_file}"],
    "display_name": "Test kernel",
}

ApiPath = NewType("ApiPath", str)


def mkdir(tmp_path, *parts):
    path = tmp_path.joinpath(*parts)
    if not path.exists():
        path.mkdir(parents=True)
    return path


def expected_http_error(error, expected_code, expected_message=None):
    """Check that the error matches the expected output error."""
    e = error.value
    if isinstance(e, HTTPError):
        if expected_code != e.status_code:
            return False
        if expected_message is not None and expected_message != str(e):
            return False
        return True
    elif any(
        [
            isinstance(e, HTTPClientError),
            isinstance(e, HTTPError),
        ]
    ):
        if expected_code != e.code:
            return False
        if expected_message:
            message = json.loads(e.response.body.decode())["message"]
            if expected_message != message:
                return False
        return True
