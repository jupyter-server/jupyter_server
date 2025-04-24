import json
import logging
import os
import stat
import sys

import pytest
from nbformat import validate
from nbformat.v4 import new_notebook
from tornado.web import HTTPError

from jupyter_server.services.contents.fileio import (
    AsyncFileManagerMixin,
    FileManagerMixin,
    atomic_writing,
    path_to_intermediate,
    path_to_invalid,
)

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

    with pytest.raises(CustomExc), atomic_writing(str(f1)) as f:
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


def test_path_to_invalid(tmpdir):
    assert path_to_invalid(tmpdir) == str(tmpdir) + ".invalid"


@pytest.mark.skipif(sys.platform.startswith("win"), reason="requires POSIX directory perms")
def test_atomic_writing_in_readonly_dir(tmp_path):
    # Setup: non-writable dir but a writable file inside
    nonw = tmp_path / "nonwritable"
    nonw.mkdir()
    f = nonw / "file.txt"
    f.write_text("original content")
    os.chmod(str(nonw), 0o500)
    os.chmod(str(f), 0o700)

    # direct write fallback succeeds
    with atomic_writing(str(f)) as ff:
        ff.write("new content")
    assert f.read_text() == "new content"

    # dir perms unchanged
    mode = stat.S_IMODE(os.stat(str(nonw)).st_mode)
    assert mode == 0o500


@pytest.mark.skipif(os.name == "nt", reason="test fails on Windows")
def test_file_manager_mixin(tmp_path):
    mixin = FileManagerMixin()
    mixin.log = logging.getLogger()
    bad_content = tmp_path / "bad_content.ipynb"
    bad_content.write_text("{}", "utf8")
    # Same as `echo -n {} | sha256sum`
    assert mixin._get_hash(bad_content.read_bytes()) == {
        "hash": "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a",
        "hash_algorithm": "sha256",
    }
    with pytest.raises(HTTPError):
        mixin._read_notebook(bad_content)
    other = path_to_intermediate(bad_content)
    with open(other, "w") as fid:
        json.dump(new_notebook(), fid)
    mixin.use_atomic_writing = True
    nb = mixin._read_notebook(bad_content)
    validate(nb)

    with pytest.raises(HTTPError):
        mixin._read_file(tmp_path, "text")

    with pytest.raises(HTTPError):
        mixin._save_file(tmp_path / "foo", "foo", "bar")


@pytest.mark.skipif(os.name == "nt", reason="test fails on Windows")
async def test_async_file_manager_mixin(tmpdir):
    mixin = AsyncFileManagerMixin()
    mixin.log = logging.getLogger()
    bad_content = tmpdir / "bad_content.ipynb"
    bad_content.write_text("{}", "utf8")
    with pytest.raises(HTTPError):
        await mixin._read_notebook(bad_content)
    other = path_to_intermediate(bad_content)
    with open(other, "w") as fid:
        json.dump(new_notebook(), fid)
    mixin.use_atomic_writing = True
    nb, bcontent = await mixin._read_notebook(bad_content, raw=True)
    # Same as `echo -n {} | sha256sum`
    assert mixin._get_hash(bcontent) == {
        "hash": "4747f9680816e352a697d0fb69d82334457cdd1e46f053e800859833d3e6003e",
        "hash_algorithm": "sha256",
    }
    validate(nb)

    with pytest.raises(HTTPError):
        await mixin._read_file(tmpdir, "text")

    with pytest.raises(HTTPError):
        await mixin._save_file(tmpdir / "foo", "foo", "bar")


async def test_AsyncFileManagerMixin_read_notebook_no_raw(tmpdir):
    mixin = AsyncFileManagerMixin()
    mixin.log = logging.getLogger()
    bad_content = tmpdir / "bad_content.ipynb"
    bad_content.write_text("{}", "utf8")

    other = path_to_intermediate(bad_content)
    with open(other, "w") as fid:
        json.dump(new_notebook(), fid)
    mixin.use_atomic_writing = True
    answer = await mixin._read_notebook(bad_content)

    assert not isinstance(answer, tuple)


async def test_AsyncFileManagerMixin_read_file_no_raw(tmpdir):
    mixin = AsyncFileManagerMixin()
    mixin.log = logging.getLogger()
    file_path = tmpdir / "bad_content.text"
    file_path.write_text("blablabla", "utf8")

    mixin.use_atomic_writing = True
    answer = await mixin._read_file(file_path, "text")

    assert len(answer) == 2
