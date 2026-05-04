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
    filefind,
    is_namespace_package,
    origin_matches_pat,
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
    assert check_version(1.0, "1.0.1")  # type:ignore[arg-type]


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


@pytest.mark.parametrize(
    "filename, result",
    [
        ("/foo", OSError),
        ("../c/in-c", OSError),
        ("in-a", "a/in-a"),
        ("in-b", "b/in-b"),
        ("in-both", "a/in-both"),
        (r"\in-a", OSError),
        ("not-found", OSError),
    ],
)
def test_filefind(tmp_path, filename, result):
    a = tmp_path / "a"
    a.mkdir()
    b = tmp_path / "b"
    b.mkdir()
    c = tmp_path / "c"
    c.mkdir()
    for parent in (a, b):
        with parent.joinpath("in-both").open("w"):
            pass
    with a.joinpath("in-a").open("w"):
        pass
    with b.joinpath("in-b").open("w"):
        pass
    with c.joinpath("in-c").open("w"):
        pass

    if isinstance(result, str):
        found = filefind(filename, [str(a), str(b)])
        found_relative = Path(found).relative_to(tmp_path)
        assert str(found_relative).replace(os.sep, "/") == result
    else:
        with pytest.raises(result):
            filefind(filename, [str(a), str(b)])


TRUSTED_PAT = r"https://trusted\.example\.com"


@pytest.mark.parametrize(
    "origin",
    [
        "https://trusted.example.com",
        # pattern is the full origin string
    ],
)
def test_origin_matches_pat_accepts_exact(origin):
    assert origin_matches_pat(TRUSTED_PAT, origin) is True


@pytest.mark.parametrize(
    "origin",
    [
        # suffix-bypass: pre-CVE-2026-40110 prefix matching would have allowed these
        "https://trusted.example.com.evil.com",
        "https://trusted.example.comedy",
        "https://trusted.example.com:9999",
        "https://trusted.example.com/path",
        # newline injection — must not be allowed via $-anchor or otherwise
        "https://trusted.example.com\nhttps://evil.com",
    ],
)
def test_origin_matches_pat_rejects_full_match_failures(origin):
    # These all match `re.match` (prefix) but NOT `re.fullmatch`, so the helper
    # warns and returns False.
    with pytest.warns(UserWarning, match="only matched the request origin as a prefix"):
        assert origin_matches_pat(TRUSTED_PAT, origin) is False


@pytest.mark.parametrize(
    "origin",
    [
        "http://trusted.example.com",
        "https://other.example.com",
        "https://trusted.example.co",
        "",
    ],
)
def test_origin_matches_pat_rejects_non_match(origin):
    # No prefix match either, so no warning.
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        assert origin_matches_pat(TRUSTED_PAT, origin) is False


def test_origin_matches_pat_empty_pattern_rejects_all():
    # Empty pattern must never allow any origin (empty-string regex would otherwise
    # fullmatch only the empty string, but the early-return guard makes this explicit).
    assert origin_matches_pat("", "") is False
    assert origin_matches_pat("", "https://anything") is False


def test_origin_matches_pat_respects_user_anchors():
    # Patterns that already include ^ and $ should still work (fullmatch is idempotent
    # with explicit anchors).
    assert origin_matches_pat(r"^https://trusted\.example\.com$", "https://trusted.example.com")
    assert not origin_matches_pat(
        r"^https://trusted\.example\.com$", "https://trusted.example.com.evil"
    )


def test_origin_matches_pat_alternation():
    pat = r"https://a\.com|https://b\.com"
    assert origin_matches_pat(pat, "https://a.com") is True
    assert origin_matches_pat(pat, "https://b.com") is True
    # alternation must not be exploitable as a prefix:
    with pytest.warns(UserWarning, match="only matched the request origin as a prefix"):
        assert origin_matches_pat(pat, "https://a.comevil") is False


def test_origin_matches_pat_unescaped_dot_is_a_footgun():
    # Documented footgun: an operator who forgets to escape `.` writes a regex that
    # treats it as a wildcard. The helper has no way to detect this — it is the
    # caller's responsibility to escape literal characters in `allow_origin_pat`.
    # This test pins the current behavior so a future change that auto-escapes or
    # warns about unescaped dots is a deliberate, reviewed decision.
    bad_pattern = r"https://trusted.example.com"  # dots NOT escaped
    assert origin_matches_pat(bad_pattern, "https://trustedxexamplexcom") is True
    assert origin_matches_pat(bad_pattern, "https://trusted-example-com") is True
