import os
import shlex
import stat
import subprocess
import sys
import time

import pytest

from jupyter_server.serverapp import (
    JupyterServerListApp,
    JupyterServerStopApp,
    list_running_servers,
    shutdown_server,
)
from jupyter_server.utils import urlencode_unix_socket, urlencode_unix_socket_path

# Skip this module if on Windows. Unix sockets are not available on Windows.
pytestmark = pytest.mark.skipif(
    sys.platform.startswith("win"), reason="Unix sockets are not available on Windows."
)


def _check_output(cmd, *args, **kwargs):
    if isinstance(cmd, str):
        cmd = shlex.split(cmd)
    kwargs.setdefault("stderr", subprocess.STDOUT)
    output = subprocess.check_output(cmd, *args, **kwargs)
    if not isinstance(output, str):
        output = output.decode("utf-8")
    return output


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

    assert encoded_sock_path in _check_output("jupyter-server list")

    # Ensure umask is properly applied.
    assert stat.S_IMODE(os.lstat(jp_unix_socket_file).st_mode) == 0o700

    try:
        _check_output("jupyter-server stop")
    except subprocess.CalledProcessError as e:
        assert "There is currently no server running on" in e.output.decode()
    else:
        raise AssertionError("expected stop command to fail due to target mis-match")

    assert encoded_sock_path in _check_output("jupyter-server list")

    # Fake out stopping the server.
    app = JupyterServerStopApp(sock=str(jp_unix_socket_file))
    app.initialize([])
    app.shutdown_server = lambda _: True  # type:ignore
    app._maybe_remove_unix_socket = lambda _: _  # type: ignore
    app.start()

    _check_output(["jupyter-server", "stop", jp_unix_socket_file])

    assert encoded_sock_path not in _check_output(["jupyter-server", "list"])

    _cleanup_process(p)


@pytest.mark.integration_test
def test_sock_server_validate_sockmode_type():
    try:
        _check_output(["jupyter-server", "--sock=/tmp/nonexistent", "--sock-mode=badbadbad"])
    except subprocess.CalledProcessError as e:
        assert "badbadbad" in e.output.decode()
    else:
        raise AssertionError("expected execution to fail due to validation of --sock-mode param")


@pytest.mark.integration_test
def test_sock_server_validate_sockmode_accessible():
    try:
        _check_output(
            ["jupyter-server", "--sock=/tmp/nonexistent", "--sock-mode=0444"],
        )
    except subprocess.CalledProcessError as e:
        assert "0444" in e.output.decode()
    else:
        raise AssertionError("expected execution to fail due to validation of --sock-mode param")


def _ensure_stopped(check_msg="There are no running servers"):
    try:
        _check_output(["jupyter-server", "stop"])
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
    assert shutdown_msg in _check_output(["jupyter-server", "stop"])

    _ensure_stopped("There is currently no server running on 8888")

    assert MSG_TMPL.format(jp_unix_socket_file) in _check_output(
        ["jupyter-server", "stop", jp_unix_socket_file]
    )

    assert MSG_TMPL.format(TEST_PORT) in _check_output(["jupyter-server", "stop", TEST_PORT])

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
        _check_output(cmd)
    except subprocess.CalledProcessError as cpe:
        assert check_msg in cpe.output.decode()
    except Exception as ex:
        raise AssertionError(f"expected 'already in use' error, got '{ex}'!") from ex
    else:
        raise AssertionError("expected 'already in use' error, got success instead!")

    # Stop the background server, ensure it's stopped and wait on the process to exit.
    subprocess.check_call(["jupyter-server", "stop", sock])

    _ensure_stopped()

    _cleanup_process(p1)


@pytest.mark.integration_test
def test_shutdown_server(jp_environ):
    # Start a server in another process
    # Stop that server
    import subprocess

    from jupyter_client.connect import LocalPortCache

    port = LocalPortCache().find_available_port("localhost")
    p = subprocess.Popen(["jupyter-server", f"--port={port}"])
    servers = []
    while 1:
        servers = list(list_running_servers())
        if len(servers):
            break
        time.sleep(0.1)
    while 1:
        try:
            shutdown_server(servers[0])
            break
        except ConnectionRefusedError:
            time.sleep(0.1)
    _cleanup_process(p)


@pytest.mark.integration_test
def test_jupyter_server_apps(jp_environ):

    # Start a server in another process
    # Stop that server
    import subprocess

    from jupyter_client.connect import LocalPortCache

    port = LocalPortCache().find_available_port("localhost")
    p = subprocess.Popen(["jupyter-server", f"--port={port}"])
    servers = []
    while 1:
        servers = list(list_running_servers())
        if len(servers):
            break
        time.sleep(0.1)

    app = JupyterServerListApp()
    app.initialize([])
    app.jsonlist = True
    app.start()
    app.jsonlist = False
    app.json = True
    app.start()
    app.json = False
    app.start()

    stop_app = JupyterServerStopApp()
    stop_app.initialize([])
    stop_app.port = port
    while 1:
        try:
            stop_app.start()
            break
        except ConnectionRefusedError:
            time.sleep(0.1)
    _cleanup_process(p)
