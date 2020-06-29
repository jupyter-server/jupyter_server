import os
import io
import zipfile
import tarfile
import pathlib
import shutil
import pytest
import tornado

from .utils import expected_http_error

from nbformat import writes
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell, new_output


async def test_hidden_files(fetch, serverapp, root_dir):
    not_hidden = [
        u"å b",
        u"å b/ç. d",
    ]
    hidden = [
        u".å b",
        u"å b/.ç d",
    ]
    dirs = not_hidden + hidden

    for d in dirs:
        path = root_dir / d.replace("/", os.sep)
        path.mkdir(parents=True, exist_ok=True)
        path.joinpath("foo").write_text("foo")
        path.joinpath(".foo").write_text(".foo")

    for d in not_hidden:
        path = root_dir / d.replace("/", os.sep)

        r = await fetch("files", d, "foo", method="GET")
        assert r.body.decode() == "foo"

        with pytest.raises(tornado.httpclient.HTTPClientError) as e:
            r = await fetch("files", d, ".foo", method="GET")
        assert expected_http_error(e, 404)

    for d in hidden:
        path = root_dir / d.replace("/", os.sep)
        for foo in ("foo", ".foo"):
            with pytest.raises(tornado.httpclient.HTTPClientError) as e:
                r = await fetch("files", d, foo, method="GET")
            assert expected_http_error(e, 404)

    serverapp.contents_manager.allow_hidden = True

    for d in not_hidden:
        path = root_dir / d.replace("/", os.sep)

        r = await fetch("files", d, "foo", method="GET")
        assert r.body.decode() == "foo"

        r = await fetch("files", d, ".foo", method="GET")
        assert r.body.decode() == ".foo"

        for d in hidden:
            path = root_dir / d.replace("/", os.sep)

            for foo in ("foo", ".foo"):
                r = await fetch("files", d, foo, method="GET")
                assert r.body.decode() == foo


async def test_contents_manager(fetch, serverapp, root_dir):
    "make sure ContentsManager returns right files (ipynb, bin, txt)."
    nb = new_notebook(
        cells=[
            new_markdown_cell(u"Created by test ³"),
            new_code_cell("print(2*6)", outputs=[new_output("stream", text="12"),]),
        ]
    )
    root_dir.joinpath("testnb.ipynb").write_text(
        writes(nb, version=4), encoding="utf-8"
    )
    root_dir.joinpath("test.bin").write_bytes(b"\xff" + os.urandom(5))
    root_dir.joinpath("test.txt").write_text("foobar")

    r = await fetch("files/testnb.ipynb", method="GET")
    assert r.code == 200
    assert "print(2*6)" in r.body.decode("utf-8")

    r = await fetch("files/test.bin", method="GET")
    assert r.code == 200
    assert r.headers["content-type"] == "application/octet-stream"
    assert r.body[:1] == b"\xff"
    assert len(r.body) == 6

    r = await fetch("files/test.txt", method="GET")
    assert r.code == 200
    assert r.headers["content-type"] == "text/plain; charset=UTF-8"
    assert r.body.decode() == "foobar"


async def test_download(fetch, serverapp, root_dir):
    text = "hello"
    root_dir.joinpath("test.txt").write_text(text)

    r = await fetch("files", "test.txt", method="GET")
    disposition = r.headers.get("Content-Disposition", "")
    assert "attachment" not in disposition

    r = await fetch("files", "test.txt", method="GET", params={"download": True})
    disposition = r.headers.get("Content-Disposition", "")
    assert "attachment" in disposition
    assert "filename*=utf-8''test.txt" in disposition


async def test_old_files_redirect(fetch, serverapp, root_dir):
    """pre-2.0 'files/' prefixed links are properly redirected"""
    root_dir.joinpath("files").mkdir(parents=True, exist_ok=True)
    root_dir.joinpath("sub", "files").mkdir(parents=True, exist_ok=True)

    for prefix in ("", "sub"):
        root_dir.joinpath(prefix, "files", "f1.txt").write_text(prefix + "/files/f1")
        root_dir.joinpath(prefix, "files", "f2.txt").write_text(prefix + "/files/f2")
        root_dir.joinpath(prefix, "f2.txt").write_text(prefix + "/f2")
        root_dir.joinpath(prefix, "f3.txt").write_text(prefix + "/f3")

    # These depend on the tree handlers
    #
    # def test_download(self):
    #     rootdir = self.root_dir

    #     text = 'hello'
    #     with open(pjoin(rootdir, 'test.txt'), 'w') as f:
    #         f.write(text)

    #     r = self.request('GET', 'files/test.txt')
    #     disposition = r.headers.get('Content-Disposition', '')
    #     self.assertNotIn('attachment', disposition)

    #     r = self.request('GET', 'files/test.txt?download=1')
    #     disposition = r.headers.get('Content-Disposition', '')
    #     self.assertIn('attachment', disposition)
    #     self.assertIn("filename*=utf-8''test.txt", disposition)


async def test_download_directory(fetch, serverapp, root_dir):
    # Create a dummy directory.
    root_dir = pathlib.Path(root_dir)
    archive_dir_path = root_dir / "download-archive-dir"
    archive_dir_path.mkdir()
    with open(archive_dir_path / "test1.txt", "w") as f:
        f.write("hello1")
    with open(archive_dir_path / "test2.txt", "w") as f:
        f.write("hello2")
    with open(archive_dir_path / "test3.md", "w") as f:
        f.write("hello3")

    # Try to download the created folder.
    file_lists = {
        "download-archive-dir/test2.txt",
        "download-archive-dir/test1.txt",
        "download-archive-dir/test3.md",
    }

    archive_formats = {
        "zip": "r",
        "tgz": "r|gz",
        "tar.gz": "r|gz",
        "tbz": "r|bz2",
        "tbz2": "r|bz2",
        "tar.bz": "r|bz2",
        "tar.bz2": "r|bz2",
        "txz": "r|xz",
        "tar.xz": "r|xz",
    }

    archive_token = 59487596

    for archive_format, mode in archive_formats.items():
        params = dict(archiveToken=archive_token, archiveFormat=archive_format)
        dir_path = str(archive_dir_path.relative_to(root_dir))
        r = await fetch("directories", dir_path, method="GET", params=params)
        assert r.code == 200
        assert r.headers.get("content-type") == "application/octet-stream"
        assert r.headers.get("cache-control") == "no-cache"
        if archive_format == "zip":
            with zipfile.ZipFile(io.BytesIO(r.body), mode=mode) as zf:
                assert set(zf.namelist()) == file_lists
        else:
            with tarfile.open(fileobj=io.BytesIO(r.body), mode=mode) as tf:
                assert set(map(lambda m: m.name, tf.getmembers())) == file_lists


async def test_extract_directory(fetch, serverapp, root_dir):

    format_mode = {
        "zip": "w",
        "tgz": "w|gz",
        "tar.gz": "w|gz",
        "tbz": "w|bz2",
        "tbz2": "w|bz2",
        "tar.bz": "w|bz2",
        "tar.bz2": "w|bz2",
        "txz": "w|xz",
        "tar.xz": "w|xz",
    }

    for archive_format, mode in format_mode.items():

        # Create a dummy directory.
        root_dir = pathlib.Path(root_dir)
        archive_dir_path = root_dir / "extract-archive-dir"
        archive_dir_path.mkdir()
        with open(archive_dir_path / "extract-test1.txt", "w") as f:
            f.write("hello1")
        with open(archive_dir_path / "extract-test2.txt", "w") as f:
            f.write("hello2")
        with open(archive_dir_path / "extract-test3.md", "w") as f:
            f.write("hello3")

        # Make an archive
        archive_path = archive_dir_path.with_suffix("." + archive_format)
        if archive_format == "zip":
            with zipfile.ZipFile(archive_path, mode=mode) as writer:
                for file_path in archive_dir_path.rglob("*"):
                    if file_path.is_file():
                        writer.write(file_path, file_path.relative_to(root_dir))
        else:
            with tarfile.open(str(archive_path), mode=mode) as writer:
                for file_path in archive_dir_path.rglob("*"):
                    if file_path.is_file():
                        writer.add(str(file_path), str(file_path.relative_to(root_dir)))

        # Remove the directory
        shutil.rmtree(archive_dir_path)

        # REST call to extract the archive
        relative_archive_path = str(archive_path.relative_to(root_dir))
        print(archive_path)
        r = await fetch("extract-directories", relative_archive_path, method="GET")

        assert r.code == 200
        assert archive_dir_path.is_dir()

        n_files = len(list(archive_dir_path.glob("*")))
        assert n_files == 3

        # Remove the directory after extraction
        shutil.rmtree(archive_dir_path)
