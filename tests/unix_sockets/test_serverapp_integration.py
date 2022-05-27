import stat
import sys

import pytest

# Skip this module if on Windows. Unix sockets are not available on Windows.
pytestmark = pytest.mark.skipif(
    sys.platform.startswith("win"), reason="Unix sockets are not available on Windows."
)

import os
import subprocess
import time

from jupyter_server.utils import urlencode_unix_socket, urlencode_unix_socket_path


def _cleanup_process(proc):
    proc.wait()
    # Make sure all the fds get closed.
    for attr in ["stdout", "stderr", "stdin"]:
        fid = getattr(proc, attr)
        if fid:
            fid.close()


@pytest.mark.integration_test
def test_shutdown_sock_server_integration(jp_unix_socket_file):
    url = urlencode_unix_socket(jp_unix_socket_file).encode()
    encoded_sock_path = urlencode_unix_socket_path(jp_unix_socket_file)
    p = subprocess.Popen(
        ["jupyter-server", "--sock=%s" % jp_unix_socket_file, "--sock-mode=0700"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    complete = False
    assert p.stderr is not None
    for line in iter(p.stderr.readline, b""):
        if url in line:
            complete = True
            break

    assert complete, "did not find socket URL in stdout when launching notebook"

    socket_path = encoded_sock_path.encode()
    assert socket_path in subprocess.check_output(["jupyter-server", "list"])

    # Ensure umask is properly applied.
    assert stat.S_IMODE(os.lstat(jp_unix_socket_file).st_mode) == 0o700

    try:
        subprocess.check_output(["jupyter-server", "stop"], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        assert "There is currently no server running on" in e.output.decode()
    else:
        raise AssertionError("expected stop command to fail due to target mis-match")

    assert encoded_sock_path.encode() in subprocess.check_output(["jupyter-server", "list"])

    subprocess.check_output(["jupyter-server", "stop", jp_unix_socket_file])

    assert encoded_sock_path.encode() not in subprocess.check_output(["jupyter-server", "list"])

    _cleanup_process(p)


@pytest.mark.integration_test
def test_sock_server_validate_sockmode_type():
    try:
        subprocess.check_output(
            ["jupyter-server", "--sock=/tmp/nonexistent", "--sock-mode=badbadbad"],
            stderr=subprocess.STDOUT,
        )
    except subprocess.CalledProcessError as e:
        assert "badbadbad" in e.output.decode()
    else:
        raise AssertionError("expected execution to fail due to validation of --sock-mode param")


@pytest.mark.integration_test
def test_sock_server_validate_sockmode_accessible():
    try:
        subprocess.check_output(
            ["jupyter-server", "--sock=/tmp/nonexistent", "--sock-mode=0444"],
            stderr=subprocess.STDOUT,
        )
    except subprocess.CalledProcessError as e:
        assert "0444" in e.output.decode()
    else:
        raise AssertionError("expected execution to fail due to validation of --sock-mode param")


def _ensure_stopped(check_msg="There are no running servers"):
    try:
        subprocess.check_output(["jupyter-server", "stop"], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        assert check_msg in e.output.decode()
    else:
        raise AssertionError("expected all servers to be stopped")


@pytest.mark.integration_test
def test_stop_multi_integration(jp_unix_socket_file, jp_http_port):
    """Tests lifecycle behavior for mixed-mode server types w/ default ports.

    Mostly suitable for local dev testing due to reliance on default port binding.
    """
    TEST_PORT = "9797"
    MSG_TMPL = "Shutting down server on {}..."

    _ensure_stopped()

    # Default port.
    p1 = subprocess.Popen(["jupyter-server", "--no-browser"])

    # Unix socket.
    p2 = subprocess.Popen(["jupyter-server", "--sock=%s" % jp_unix_socket_file])

    # Specified port
    p3 = subprocess.Popen(["jupyter-server", "--no-browser", "--port=%s" % TEST_PORT])

    time.sleep(3)

    shutdown_msg = MSG_TMPL.format(jp_http_port)
    assert shutdown_msg in subprocess.check_output(["jupyter-server", "stop"]).decode()

    _ensure_stopped("There is currently no server running on 8888")

    assert (
        MSG_TMPL.format(jp_unix_socket_file)
        in subprocess.check_output(["jupyter-server", "stop", jp_unix_socket_file]).decode()
    )

    assert (
        MSG_TMPL.format(TEST_PORT)
        in subprocess.check_output(["jupyter-server", "stop", TEST_PORT]).decode()
    )

    _ensure_stopped()

    [_cleanup_process(p) for p in [p1, p2, p3]]


@pytest.mark.integration_test
def test_launch_socket_collision(jp_unix_socket_file):
    """Tests UNIX socket in-use detection for lifecycle correctness."""
    sock = jp_unix_socket_file
    check_msg = "socket %s is already in use" % sock

    _ensure_stopped()

    # Start a server.
    cmd = ["jupyter-server", "--sock=%s" % sock]
    p1 = subprocess.Popen(cmd)
    time.sleep(3)

    # Try to start a server bound to the same UNIX socket.
    try:
        subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as cpe:
        assert check_msg in cpe.output.decode()
    except Exception as ex:
        raise AssertionError(f"expected 'already in use' error, got '{ex}'!")
    else:
        raise AssertionError("expected 'already in use' error, got success instead!")

    # Stop the background server, ensure it's stopped and wait on the process to exit.
    subprocess.check_call(["jupyter-server", "stop", sock])

    _ensure_stopped()

    _cleanup_process(p1)
