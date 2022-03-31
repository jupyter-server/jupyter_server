import os
import stat
import sys

import pytest

from jupyter_server.services.contents.fileio import atomic_writing

umask = 0


def test_atomic_writing(tmp_path):
    class CustomExc(Exception):
        pass

    f1 = tmp_path / "penguin"
    f1.write_text("Before")

    if os.name != "nt":
        os.chmod(str(f1), 0o701)
        orig_mode = stat.S_IMODE(os.stat(str(f1)).st_mode)

    f2 = tmp_path / "flamingo"
    try:
        os.symlink(str(f1), str(f2))
        have_symlink = True
    except (AttributeError, NotImplementedError, OSError):
        # AttributeError: Python doesn't support it
        # NotImplementedError: The system doesn't support it
        # OSError: The user lacks the privilege (Windows)
        have_symlink = False

    with pytest.raises(CustomExc):
        with atomic_writing(str(f1)) as f:
            f.write("Failing write")
            raise CustomExc

    with open(str(f1)) as f:
        assert f.read() == "Before"

    with atomic_writing(str(f1)) as f:
        f.write("Overwritten")

    with open(str(f1)) as f:
        assert f.read() == "Overwritten"

    if os.name != "nt":
        mode = stat.S_IMODE(os.stat(str(f1)).st_mode)
        assert mode == orig_mode

    if have_symlink:
        # Check that writing over a file preserves a symlink
        with atomic_writing(str(f2)) as f:
            f.write("written from symlink")

        with open(str(f1)) as f:
            assert f.read() == "written from symlink"


@pytest.fixture
def handle_umask():
    global umask
    umask = os.umask(0)
    os.umask(umask)
    yield
    os.umask(umask)


@pytest.mark.skipif(sys.platform.startswith("win"), reason="Windows")
def test_atomic_writing_umask(handle_umask, tmp_path):

    os.umask(0o022)
    f1 = str(tmp_path / "1")
    with atomic_writing(f1) as f:
        f.write("1")
    mode = stat.S_IMODE(os.stat(f1).st_mode)
    assert mode == 0o644

    os.umask(0o057)
    f2 = str(tmp_path / "2")

    with atomic_writing(f2) as f:
        f.write("2")

    mode = stat.S_IMODE(os.stat(f2).st_mode)
    assert mode == 0o620


def test_atomic_writing_newlines(tmp_path):
    path = str(tmp_path / "testfile")

    lf = "a\nb\nc\n"
    plat = lf.replace("\n", os.linesep)
    crlf = lf.replace("\n", "\r\n")

    # test default
    with open(path, "w") as f:
        f.write(lf)
    with open(path, newline="") as f:
        read = f.read()
    assert read == plat

    # test newline=LF
    with open(path, "w", newline="\n") as f:
        f.write(lf)
    with open(path, newline="") as f:
        read = f.read()
    assert read == lf

    # test newline=CRLF
    with atomic_writing(str(path), newline="\r\n") as f:
        f.write(lf)
    with open(path, newline="") as f:
        read = f.read()
    assert read == crlf

    # test newline=no convert
    text = "crlf\r\ncr\rlf\n"
    with atomic_writing(str(path), newline="") as f:
        f.write(text)
    with open(path, newline="") as f:
        read = f.read()
    assert read == text
