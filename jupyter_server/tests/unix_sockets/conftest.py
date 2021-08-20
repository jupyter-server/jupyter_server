import os
import pathlib

import pytest

from jupyter_server import DEFAULT_JUPYTER_SERVER_PORT


@pytest.fixture
def jp_process_id():
    """Choose a random unused process ID."""
    return os.getpid()


@pytest.fixture
def jp_unix_socket_file(jp_process_id):
    """Define a temporary socket connection"""
    # Rely on `/tmp` to avoid any Linux socket length max buffer
    # issues. Key on PID for process-wise concurrency.
    tmp_path = pathlib.Path("/tmp")
    filename = "jupyter_server.{}.sock".format(jp_process_id)
    jp_unix_socket_file = tmp_path.joinpath(filename)
    yield str(jp_unix_socket_file)
    # Clean up the file after the test runs.
    if jp_unix_socket_file.exists():
        jp_unix_socket_file.unlink()


@pytest.fixture
def jp_http_port():
    """Set the port to the default value, since sock
    and port cannot both be configured at the same time.
    """
    return DEFAULT_JUPYTER_SERVER_PORT
