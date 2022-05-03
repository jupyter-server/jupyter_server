import json
import os
from pathlib import Path

import pytest
from nbformat import writes
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook, new_output
from tornado.httpclient import HTTPClientError

from .utils import expected_http_error


@pytest.fixture(
    params=[
        [False, ["å b"]],
        [False, ["å b", "ç. d"]],
        [True, [".å b"]],
        [True, ["å b", ".ç d"]],
    ]
)
def maybe_hidden(request):
    return request.param


async def fetch_expect_200(jp_fetch, *path_parts):
    r = await jp_fetch("files", *path_parts, method="GET")
    assert r.body.decode() == path_parts[-1], (path_parts, r.body)


async def fetch_expect_404(jp_fetch, *path_parts):
    with pytest.raises(HTTPClientError) as e:
        await jp_fetch("files", *path_parts, method="GET")
    assert expected_http_error(e, 404), [path_parts, e]


async def test_hidden_files(jp_fetch, jp_serverapp, jp_root_dir, maybe_hidden):
    is_hidden, path_parts = maybe_hidden
    path = Path(jp_root_dir, *path_parts)
    path.mkdir(parents=True, exist_ok=True)

    foos = ["foo", ".foo"]
    for foo in foos:
        (path / foo).write_text(foo)

    if is_hidden:
        for foo in foos:
            await fetch_expect_404(jp_fetch, *path_parts, foo)
    else:
        await fetch_expect_404(jp_fetch, *path_parts, ".foo")
        await fetch_expect_200(jp_fetch, *path_parts, "foo")

    jp_serverapp.contents_manager.allow_hidden = True

    for foo in foos:
        await fetch_expect_200(jp_fetch, *path_parts, foo)


async def test_contents_manager(jp_fetch, jp_serverapp, jp_root_dir):
    """make sure ContentsManager returns right files (ipynb, bin, txt).
    Also test save file hooks."""
    nb = new_notebook(
        cells=[
            new_markdown_cell("Created by test ³"),
            new_code_cell(
                "print(2*6)",
                outputs=[
                    new_output("stream", text="12"),
                ],
            ),
        ]
    )
    jp_root_dir.joinpath("testnb.ipynb").write_text(writes(nb, version=4), encoding="utf-8")
    jp_root_dir.joinpath("test.bin").write_bytes(b"\xff" + os.urandom(5))
    jp_root_dir.joinpath("test.txt").write_text("foobar")

    r = await jp_fetch("files/testnb.ipynb", method="GET")
    assert r.code == 200
    assert "print(2*6)" in r.body.decode("utf-8")

    r = await jp_fetch("files/test.bin", method="GET")
    assert r.code == 200
    assert r.headers["content-type"] == "application/octet-stream"
    assert r.body[:1] == b"\xff"
    assert len(r.body) == 6

    r = await jp_fetch("files/test.txt", method="GET")
    assert r.code == 200
    assert r.headers["content-type"] == "text/plain; charset=UTF-8"
    assert r.body.decode() == "foobar"


async def test_save_hooks(jp_fetch, jp_serverapp):
    # define a first pre-save hook that will change the content of the file before saving
    def pre_save_hook1(model, **kwargs):
        model["content"] += " was modified"

    # define a second pre-save hook that will change the content of the file before saving
    def pre_save_hook2(model, **kwargs):
        model["content"] += " twice!"

    # define a first post-save hook that will change the 'last_modified' date
    def post_save_hook1(model, **kwargs):
        model["last_modified"] = "yesterday"

    # define a second post-save hook that will change the 'last_modified' date
    def post_save_hook2(model, **kwargs):
        model["last_modified"] += " or tomorrow!"

    # register the pre-save hooks
    jp_serverapp.contents_manager.register_pre_save_hook(pre_save_hook1)
    jp_serverapp.contents_manager.register_pre_save_hook(pre_save_hook2)

    # register the post-save hooks
    jp_serverapp.contents_manager.register_post_save_hook(post_save_hook1)
    jp_serverapp.contents_manager.register_post_save_hook(post_save_hook2)

    # send a request to save a file, with an original content
    # the 'last_modified' returned model field should have been modified by post_save_hook1 then post_save_hook2
    r = await jp_fetch(
        "api/contents/test.txt",
        method="PUT",
        body=json.dumps(
            {"format": "text", "path": "test.txt", "type": "file", "content": "original content"}
        ),
    )
    assert json.loads(r.body.decode())["last_modified"] == "yesterday or tomorrow!"

    # read the file back
    # the original content should have been modified by pre_save_hook1 then pre_save_hook2
    r = await jp_fetch("files/test.txt", method="GET")
    assert r.body.decode() == "original content was modified twice!"


async def test_download(jp_fetch, jp_serverapp, jp_root_dir):
    text = "hello"
    jp_root_dir.joinpath("test.txt").write_text(text)

    r = await jp_fetch("files", "test.txt", method="GET")
    disposition = r.headers.get("Content-Disposition", "")
    assert "attachment" not in disposition

    r = await jp_fetch("files", "test.txt", method="GET", params={"download": True})
    disposition = r.headers.get("Content-Disposition", "")
    assert "attachment" in disposition
    assert "filename*=utf-8''test.txt" in disposition


async def test_old_files_redirect(jp_fetch, jp_serverapp, jp_root_dir):
    """pre-2.0 'files/' prefixed links are properly redirected"""
    jp_root_dir.joinpath("files").mkdir(parents=True, exist_ok=True)
    jp_root_dir.joinpath("sub", "files").mkdir(parents=True, exist_ok=True)

    for prefix in ("", "sub"):
        jp_root_dir.joinpath(prefix, "files", "f1.txt").write_text(prefix + "/files/f1")
        jp_root_dir.joinpath(prefix, "files", "f2.txt").write_text(prefix + "/files/f2")
        jp_root_dir.joinpath(prefix, "f2.txt").write_text(prefix + "/f2")
        jp_root_dir.joinpath(prefix, "f3.txt").write_text(prefix + "/f3")

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
