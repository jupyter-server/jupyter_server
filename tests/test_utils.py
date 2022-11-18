import os
import socket
import subprocess
import sys
import uuid
import warnings
from pathlib import Path
from unittest.mock import patch

import pytest
from traitlets.tests.utils import check_help_all_output

from jupyter_server.utils import (
    check_pid,
    check_version,
    is_namespace_package,
    path2url,
    run_sync_in_loop,
    samefile_simple,
    to_api_path,
    unix_socket_in_use,
    url2path,
    url_escape,
    url_unescape,
)


def test_help_output():
    check_help_all_output("jupyter_server")


@pytest.mark.parametrize(
    "unescaped,escaped",
    [
        ("/this is a test/for spaces/", "/this%20is%20a%20test/for%20spaces/"),
        ("notebook with space.ipynb", "notebook%20with%20space.ipynb"),
        (
            "/path with a/notebook and space.ipynb",
            "/path%20with%20a/notebook%20and%20space.ipynb",
        ),
        (
            "/ !@$#%^&* / test %^ notebook @#$ name.ipynb",
            "/%20%21%40%24%23%25%5E%26%2A%20/%20test%20%25%5E%20notebook%20%40%23%24%20name.ipynb",
        ),
    ],
)
def test_url_escaping(unescaped, escaped):
    # Test escaping.
    path = url_escape(unescaped)
    assert path == escaped
    # Test unescaping.
    path = url_unescape(escaped)
    assert path == unescaped


@pytest.mark.parametrize(
    "name, expected",
    [
        # returns True if it is a namespace package
        ("test_namespace", True),
        # returns False if it isn't a namespace package
        ("sys", False),
        ("jupyter_server", False),
        # returns None if it isn't importable
        ("not_a_python_namespace", None),
    ],
)
def test_is_namespace_package(monkeypatch, name, expected):
    monkeypatch.syspath_prepend(Path(__file__).parent / "namespace-package-test")

    assert is_namespace_package(name) is expected


def test_is_namespace_package_no_spec():
    with patch("importlib.util.find_spec") as mocked_spec:
        mocked_spec.side_effect = ValueError()

        assert is_namespace_package("dummy") is None
        mocked_spec.assert_called_once_with("dummy")


@pytest.mark.skipif(os.name == "nt", reason="Paths are annoying on Windows")
def test_path_utils(tmp_path):
    path = str(tmp_path)
    assert os.path.basename(path2url(path)) == os.path.basename(path)

    url = path2url(path)
    assert path.endswith(url2path(url))

    assert samefile_simple(path, path)

    assert to_api_path(path, os.path.dirname(path)) == os.path.basename(path)


def test_check_version():
    assert check_version("1.0.2", "1.0.1")
    assert not check_version("1.0.0", "1.0.1")
    assert check_version(1.0, "1.0.1")


def test_check_pid():
    proc = subprocess.Popen([sys.executable])
    proc.kill()
    proc.wait()
    check_pid(proc.pid)


async def test_run_sync_in_loop():
    async def foo():
        pass

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        await run_sync_in_loop(foo())


@pytest.mark.skipif(os.name != "posix", reason="Requires unix sockets")
def test_unix_socket_in_use(tmp_path):
    root_tmp_dir = Path("/tmp").resolve()
    server_address = os.path.join(root_tmp_dir, uuid.uuid4().hex)
    if os.path.exists(server_address):
        os.remove(server_address)
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.bind(server_address)
    sock.listen(0)
    assert unix_socket_in_use(server_address)
    sock.close()
