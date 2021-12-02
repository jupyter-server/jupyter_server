import json
import pathlib
import sys
from base64 import decodebytes
from base64 import encodebytes
from unicodedata import normalize

import pytest
import tornado
from nbformat import from_dict
from nbformat import writes
from nbformat.v4 import new_markdown_cell
from nbformat.v4 import new_notebook

from ...utils import expected_http_error
from jupyter_server.utils import url_path_join


def notebooks_only(dir_model):
    return [nb for nb in dir_model["content"] if nb["type"] == "notebook"]


def dirs_only(dir_model):
    return [x for x in dir_model["content"] if x["type"] == "directory"]


dirs = [
    ("", "inroot"),
    ("Directory with spaces in", "inspace"),
    (u"unicodé", "innonascii"),
    ("foo", "a"),
    ("foo", "b"),
    ("foo", "name with spaces"),
    ("foo", u"unicodé"),
    ("foo/bar", "baz"),
    ("ordering", "A"),
    ("ordering", "b"),
    ("ordering", "C"),
    (u"å b", u"ç d"),
]


@pytest.fixture(params=["FileContentsManager", "AsyncFileContentsManager"])
def jp_argv(request):
    return [
        "--ServerApp.contents_manager_class=jupyter_server.services.contents.filemanager."
        + request.param
    ]


@pytest.fixture
def contents_dir(tmp_path, jp_serverapp):
    return tmp_path / jp_serverapp.root_dir


@pytest.fixture
def contents(contents_dir):
    # Create files in temporary directory
    paths = {
        "notebooks": [],
        "textfiles": [],
        "blobs": [],
    }
    for d, name in dirs:
        p = contents_dir / d
        p.mkdir(parents=True, exist_ok=True)

        # Create a notebook
        nb = writes(new_notebook(), version=4)
        nbname = p.joinpath("{}.ipynb".format(name))
        nbname.write_text(nb, encoding="utf-8")
        paths["notebooks"].append(nbname.relative_to(contents_dir))

        # Create a text file
        txt = "{} text file".format(name)
        txtname = p.joinpath("{}.txt".format(name))
        txtname.write_text(txt, encoding="utf-8")
        paths["textfiles"].append(txtname.relative_to(contents_dir))

        # Create a random blob
        blob = name.encode("utf-8") + b"\xFF"
        blobname = p.joinpath("{}.blob".format(name))
        blobname.write_bytes(blob)
        paths["blobs"].append(blobname.relative_to(contents_dir))
    paths["all"] = list(paths.values())
    return paths


@pytest.fixture
def folders():
    return list(set(item[0] for item in dirs))


@pytest.mark.parametrize("path,name", dirs)
async def test_list_notebooks(jp_fetch, contents, path, name):
    response = await jp_fetch(
        "api",
        "contents",
        path,
        method="GET",
    )
    data = json.loads(response.body.decode())
    nbs = notebooks_only(data)
    assert len(nbs) > 0
    assert name + ".ipynb" in [normalize("NFC", n["name"]) for n in nbs]
    assert url_path_join(path, name + ".ipynb") in [normalize("NFC", n["path"]) for n in nbs]


@pytest.mark.parametrize("path,name", dirs)
async def test_get_dir_no_contents(jp_fetch, contents, path, name):
    response = await jp_fetch(
        "api",
        "contents",
        path,
        method="GET",
        params=dict(
            content="0",
        ),
    )
    model = json.loads(response.body.decode())
    assert model["path"] == path
    assert model["type"] == "directory"
    assert "content" in model
    assert model["content"] is None


async def test_list_nonexistant_dir(jp_fetch, contents):
    with pytest.raises(tornado.httpclient.HTTPClientError):
        await jp_fetch(
            "api",
            "contents",
            "nonexistant",
            method="GET",
        )


@pytest.mark.parametrize("path,name", dirs)
async def test_get_nb_contents(jp_fetch, contents, path, name):
    nbname = name + ".ipynb"
    nbpath = (path + "/" + nbname).lstrip("/")
    r = await jp_fetch("api", "contents", nbpath, method="GET", params=dict(content="1"))
    model = json.loads(r.body.decode())
    assert model["name"] == nbname
    assert model["path"] == nbpath
    assert model["type"] == "notebook"
    assert "content" in model
    assert model["format"] == "json"
    assert "metadata" in model["content"]
    assert isinstance(model["content"]["metadata"], dict)


@pytest.mark.parametrize("path,name", dirs)
async def test_get_nb_no_contents(jp_fetch, contents, path, name):
    nbname = name + ".ipynb"
    nbpath = (path + "/" + nbname).lstrip("/")
    r = await jp_fetch("api", "contents", nbpath, method="GET", params=dict(content="0"))
    model = json.loads(r.body.decode())
    assert model["name"] == nbname
    assert model["path"] == nbpath
    assert model["type"] == "notebook"
    assert "content" in model
    assert model["content"] is None


async def test_get_nb_invalid(contents_dir, jp_fetch, contents):
    nb = {
        "nbformat": 4,
        "metadata": {},
        "cells": [
            {
                "cell_type": "wrong",
                "metadata": {},
            }
        ],
    }
    nbpath = u"å b/Validate tést.ipynb"
    (contents_dir / nbpath).write_text(json.dumps(nb))
    r = await jp_fetch(
        "api",
        "contents",
        nbpath,
        method="GET",
    )
    model = json.loads(r.body.decode())
    assert model["path"] == nbpath
    assert model["type"] == "notebook"
    assert "content" in model
    assert "message" in model
    assert "validation failed" in model["message"].lower()


async def test_get_contents_no_such_file(jp_fetch):
    with pytest.raises(tornado.httpclient.HTTPClientError) as e:
        await jp_fetch(
            "api",
            "contents",
            "foo/q.ipynb",
            method="GET",
        )
    assert e.value.code == 404


@pytest.mark.parametrize("path,name", dirs)
async def test_get_text_file_contents(jp_fetch, contents, path, name):
    txtname = name + ".txt"
    txtpath = (path + "/" + txtname).lstrip("/")
    r = await jp_fetch("api", "contents", txtpath, method="GET", params=dict(content="1"))
    model = json.loads(r.body.decode())
    assert model["name"] == txtname
    assert model["path"] == txtpath
    assert "content" in model
    assert model["format"] == "text"
    assert model["type"] == "file"
    assert model["content"] == "{} text file".format(name)

    with pytest.raises(tornado.httpclient.HTTPClientError) as e:
        await jp_fetch(
            "api",
            "contents",
            "foo/q.txt",
            method="GET",
        )
    assert expected_http_error(e, 404)

    with pytest.raises(tornado.httpclient.HTTPClientError) as e:
        await jp_fetch(
            "api",
            "contents",
            "foo/bar/baz.blob",
            method="GET",
            params=dict(type="file", format="text"),
        )
    assert expected_http_error(e, 400)


@pytest.mark.parametrize("path,name", dirs)
async def test_get_binary_file_contents(jp_fetch, contents, path, name):
    blobname = name + ".blob"
    blobpath = (path + "/" + blobname).lstrip("/")
    r = await jp_fetch("api", "contents", blobpath, method="GET", params=dict(content="1"))
    model = json.loads(r.body.decode())
    assert model["name"] == blobname
    assert model["path"] == blobpath
    assert "content" in model
    assert model["format"] == "base64"
    assert model["type"] == "file"
    data_out = decodebytes(model["content"].encode("ascii"))
    data_in = name.encode("utf-8") + b"\xFF"
    assert data_in == data_out

    with pytest.raises(tornado.httpclient.HTTPClientError) as e:
        await jp_fetch(
            "api",
            "contents",
            "foo/q.txt",
            method="GET",
        )
    assert expected_http_error(e, 404)


async def test_get_bad_type(jp_fetch, contents):
    with pytest.raises(tornado.httpclient.HTTPClientError) as e:
        path = "unicodé"
        type = "file"
        await jp_fetch(
            "api",
            "contents",
            path,
            method="GET",
            params=dict(type=type),  # This should be a directory, and thus throw and error
        )
    assert expected_http_error(e, 400, "%s is a directory, not a %s" % (path, type))

    with pytest.raises(tornado.httpclient.HTTPClientError) as e:
        path = "unicodé/innonascii.ipynb"
        type = "directory"
        await jp_fetch(
            "api",
            "contents",
            path,
            method="GET",
            params=dict(type=type),  # This should be a file, and thus throw and error
        )
    assert expected_http_error(e, 400, "%s is not a directory" % path)


@pytest.fixture
def _check_created(jp_base_url):
    def _inner(r, contents_dir, path, name, type="notebook"):
        fpath = path + "/" + name
        assert r.code == 201
        location = jp_base_url + "api/contents/" + tornado.escape.url_escape(fpath, plus=False)
        assert r.headers["Location"] == location
        model = json.loads(r.body.decode())
        assert model["name"] == name
        assert model["path"] == fpath
        assert model["type"] == type
        path = contents_dir + "/" + fpath
        if type == "directory":
            assert pathlib.Path(path).is_dir()
        else:
            assert pathlib.Path(path).is_file()

    return _inner


async def test_create_untitled(jp_fetch, contents, contents_dir, _check_created):
    path = "å b"
    name = "Untitled.ipynb"
    r = await jp_fetch("api", "contents", path, method="POST", body=json.dumps({"ext": ".ipynb"}))
    _check_created(r, str(contents_dir), path, name, type="notebook")

    name = "Untitled1.ipynb"
    r = await jp_fetch("api", "contents", path, method="POST", body=json.dumps({"ext": ".ipynb"}))
    _check_created(r, str(contents_dir), path, name, type="notebook")

    path = "foo/bar"
    name = "Untitled.ipynb"
    r = await jp_fetch("api", "contents", path, method="POST", body=json.dumps({"ext": ".ipynb"}))
    _check_created(r, str(contents_dir), path, name, type="notebook")


async def test_create_untitled_txt(jp_fetch, contents, contents_dir, _check_created):
    name = "untitled.txt"
    path = "foo/bar"
    r = await jp_fetch("api", "contents", path, method="POST", body=json.dumps({"ext": ".txt"}))
    _check_created(r, str(contents_dir), path, name, type="file")

    r = await jp_fetch("api", "contents", path, name, method="GET")
    model = json.loads(r.body.decode())
    assert model["type"] == "file"
    assert model["format"] == "text"
    assert model["content"] == ""


async def test_upload(jp_fetch, contents, contents_dir, _check_created):
    nb = new_notebook()
    nbmodel = {"content": nb, "type": "notebook"}
    path = "å b"
    name = "Upload tést.ipynb"
    r = await jp_fetch("api", "contents", path, name, method="PUT", body=json.dumps(nbmodel))
    _check_created(r, str(contents_dir), path, name)


async def test_mkdir_untitled(jp_fetch, contents, contents_dir, _check_created):
    name = "Untitled Folder"
    path = "å b"
    r = await jp_fetch(
        "api", "contents", path, method="POST", body=json.dumps({"type": "directory"})
    )
    _check_created(r, str(contents_dir), path, name, type="directory")

    name = "Untitled Folder 1"
    r = await jp_fetch(
        "api", "contents", path, method="POST", body=json.dumps({"type": "directory"})
    )
    _check_created(r, str(contents_dir), path, name, type="directory")

    name = "Untitled Folder"
    path = "foo/bar"
    r = await jp_fetch(
        "api", "contents", path, method="POST", body=json.dumps({"type": "directory"})
    )
    _check_created(r, str(contents_dir), path, name, type="directory")


async def test_mkdir(jp_fetch, contents, contents_dir, _check_created):
    name = "New ∂ir"
    path = "å b"
    r = await jp_fetch(
        "api", "contents", path, name, method="PUT", body=json.dumps({"type": "directory"})
    )
    _check_created(r, str(contents_dir), path, name, type="directory")


async def test_mkdir_hidden_400(jp_fetch):
    with pytest.raises(tornado.httpclient.HTTPClientError) as e:
        await jp_fetch(
            "api", "contents", "å b/.hidden", method="PUT", body=json.dumps({"type": "directory"})
        )
    assert expected_http_error(e, 400)


async def test_upload_txt(jp_fetch, contents, contents_dir, _check_created):
    body = "ünicode téxt"
    model = {
        "content": body,
        "format": "text",
        "type": "file",
    }
    path = "å b"
    name = "Upload tést.txt"
    await jp_fetch("api", "contents", path, name, method="PUT", body=json.dumps(model))

    # check roundtrip
    r = await jp_fetch("api", "contents", path, name, method="GET")
    model = json.loads(r.body.decode())
    assert model["type"] == "file"
    assert model["format"] == "text"
    assert model["path"] == path + "/" + name
    assert model["content"] == body


async def test_upload_b64(jp_fetch, contents, contents_dir, _check_created):
    body = b"\xFFblob"
    b64body = encodebytes(body).decode("ascii")
    model = {
        "content": b64body,
        "format": "base64",
        "type": "file",
    }
    path = "å b"
    name = "Upload tést.blob"
    await jp_fetch("api", "contents", path, name, method="PUT", body=json.dumps(model))
    # check roundtrip
    r = await jp_fetch("api", "contents", path, name, method="GET")
    model = json.loads(r.body.decode())
    assert model["type"] == "file"
    assert model["path"] == path + "/" + name
    assert model["format"] == "base64"
    decoded = decodebytes(model["content"].encode("ascii"))
    assert decoded == body


async def test_copy(jp_fetch, contents, contents_dir, _check_created):
    path = "å b"
    name = "ç d.ipynb"
    copy = "ç d-Copy1.ipynb"
    r = await jp_fetch(
        "api", "contents", path, method="POST", body=json.dumps({"copy_from": path + "/" + name})
    )
    _check_created(r, str(contents_dir), path, copy, type="notebook")

    # Copy the same file name
    copy2 = "ç d-Copy2.ipynb"
    r = await jp_fetch(
        "api", "contents", path, method="POST", body=json.dumps({"copy_from": path + "/" + name})
    )
    _check_created(r, str(contents_dir), path, copy2, type="notebook")

    # copy a copy.
    copy3 = "ç d-Copy3.ipynb"
    r = await jp_fetch(
        "api", "contents", path, method="POST", body=json.dumps({"copy_from": path + "/" + copy2})
    )
    _check_created(r, str(contents_dir), path, copy3, type="notebook")


async def test_copy_path(jp_fetch, contents, contents_dir, _check_created):
    path1 = "foo"
    path2 = "å b"
    name = "a.ipynb"
    copy = "a-Copy1.ipynb"
    r = await jp_fetch(
        "api", "contents", path2, method="POST", body=json.dumps({"copy_from": path1 + "/" + name})
    )
    _check_created(r, str(contents_dir), path2, name, type="notebook")

    r = await jp_fetch(
        "api", "contents", path2, method="POST", body=json.dumps({"copy_from": path1 + "/" + name})
    )
    _check_created(r, str(contents_dir), path2, copy, type="notebook")


async def test_copy_put_400(jp_fetch, contents, contents_dir, _check_created):
    with pytest.raises(tornado.httpclient.HTTPClientError) as e:
        await jp_fetch(
            "api",
            "contents",
            "å b/cøpy.ipynb",
            method="PUT",
            body=json.dumps({"copy_from": "å b/ç d.ipynb"}),
        )
    assert expected_http_error(e, 400)


async def test_copy_dir_400(jp_fetch, contents, contents_dir, _check_created):
    with pytest.raises(tornado.httpclient.HTTPClientError) as e:
        await jp_fetch(
            "api", "contents", "foo", method="POST", body=json.dumps({"copy_from": "å b"})
        )
    assert expected_http_error(e, 400)


@pytest.mark.parametrize("path,name", dirs)
async def test_delete(jp_fetch, contents, contents_dir, path, name, _check_created):
    nbname = name + ".ipynb"
    nbpath = (path + "/" + nbname).lstrip("/")
    r = await jp_fetch(
        "api",
        "contents",
        nbpath,
        method="DELETE",
    )
    assert r.code == 204


async def test_delete_dirs(jp_fetch, contents, folders):
    # Iterate over folders
    for name in sorted(folders + ["/"], key=len, reverse=True):
        r = await jp_fetch("api", "contents", name, method="GET")
        # Get JSON blobs for each content.
        listing = json.loads(r.body.decode())["content"]
        # Delete all content
        for model in listing:
            await jp_fetch("api", "contents", model["path"], method="DELETE")
    # Make sure all content has been deleted.
    r = await jp_fetch("api", "contents", method="GET")
    model = json.loads(r.body.decode())
    assert model["content"] == []


@pytest.mark.skipif(sys.platform == "win32", reason="Disabled deleting non-empty dirs on Windows")
async def test_delete_non_empty_dir(jp_fetch, contents):
    # Delete a folder
    await jp_fetch("api", "contents", "å b", method="DELETE")
    # Check that the folder was been deleted.
    with pytest.raises(tornado.httpclient.HTTPClientError) as e:
        await jp_fetch("api", "contents", "å b", method="GET")
    assert expected_http_error(e, 404)


async def test_rename(jp_fetch, jp_base_url, contents, contents_dir):
    path = "foo"
    name = "a.ipynb"
    new_name = "z.ipynb"
    # Rename the file
    r = await jp_fetch(
        "api",
        "contents",
        path,
        name,
        method="PATCH",
        body=json.dumps({"path": path + "/" + new_name}),
    )
    fpath = path + "/" + new_name
    assert r.code == 200
    location = url_path_join(jp_base_url, "api/contents/", fpath)
    assert r.headers["Location"] == location
    model = json.loads(r.body.decode())
    assert model["name"] == new_name
    assert model["path"] == fpath
    fpath = str(contents_dir / fpath)
    assert pathlib.Path(fpath).is_file()

    # Check that the files have changed
    r = await jp_fetch("api", "contents", path, method="GET")
    listing = json.loads(r.body.decode())
    nbnames = [name["name"] for name in listing["content"]]
    assert "z.ipynb" in nbnames
    assert "a.ipynb" not in nbnames


async def test_checkpoints_follow_file(jp_fetch, contents):
    path = "foo"
    name = "a.ipynb"

    # Read initial file.
    r = await jp_fetch("api", "contents", path, name, method="GET")
    model = json.loads(r.body.decode())

    # Create a checkpoint of initial state
    r = await jp_fetch(
        "api", "contents", path, name, "checkpoints", method="POST", allow_nonstandard_methods=True
    )
    cp1 = json.loads(r.body.decode())

    # Modify file and save.
    nbcontent = model["content"]
    nb = from_dict(nbcontent)
    hcell = new_markdown_cell("Created by test")
    nb.cells.append(hcell)
    nbmodel = {"content": nb, "type": "notebook"}
    await jp_fetch("api", "contents", path, name, method="PUT", body=json.dumps(nbmodel))

    # List checkpoints
    r = await jp_fetch(
        "api",
        "contents",
        path,
        name,
        "checkpoints",
        method="GET",
    )
    cps = json.loads(r.body.decode())
    assert cps == [cp1]

    r = await jp_fetch("api", "contents", path, name, method="GET")
    model = json.loads(r.body.decode())
    nbcontent = model["content"]
    nb = from_dict(nbcontent)
    assert nb.cells[0].source == "Created by test"


async def test_rename_existing(jp_fetch, contents):
    with pytest.raises(tornado.httpclient.HTTPClientError) as e:
        path = "foo"
        name = "a.ipynb"
        new_name = "b.ipynb"
        # Rename the file
        await jp_fetch(
            "api",
            "contents",
            path,
            name,
            method="PATCH",
            body=json.dumps({"path": path + "/" + new_name}),
        )
    assert expected_http_error(e, 409)


async def test_save(jp_fetch, contents):
    r = await jp_fetch("api", "contents", "foo/a.ipynb", method="GET")
    model = json.loads(r.body.decode())
    nbmodel = model["content"]
    nb = from_dict(nbmodel)
    nb.cells.append(new_markdown_cell("Created by test ³"))
    nbmodel = {"content": nb, "type": "notebook"}
    await jp_fetch("api", "contents", "foo/a.ipynb", method="PUT", body=json.dumps(nbmodel))
    # Round trip.
    r = await jp_fetch("api", "contents", "foo/a.ipynb", method="GET")
    model = json.loads(r.body.decode())
    newnb = from_dict(model["content"])
    assert newnb.cells[0].source == "Created by test ³"


async def test_checkpoints(jp_fetch, contents):
    path = "foo/a.ipynb"
    resp = await jp_fetch("api", "contents", path, method="GET")
    model = json.loads(resp.body.decode())
    r = await jp_fetch(
        "api", "contents", path, "checkpoints", method="POST", allow_nonstandard_methods=True
    )
    assert r.code == 201
    cp1 = json.loads(r.body.decode())
    assert set(cp1) == {"id", "last_modified"}
    assert r.headers["Location"].split("/")[-1] == cp1["id"]

    # Modify it.
    nbcontent = model["content"]
    nb = from_dict(nbcontent)
    hcell = new_markdown_cell("Created by test")
    nb.cells.append(hcell)

    # Save it.
    nbmodel = {"content": nb, "type": "notebook"}
    await jp_fetch("api", "contents", path, method="PUT", body=json.dumps(nbmodel))

    # List checkpoints
    r = await jp_fetch("api", "contents", path, "checkpoints", method="GET")
    cps = json.loads(r.body.decode())
    assert cps == [cp1]

    r = await jp_fetch("api", "contents", path, method="GET")
    nbcontent = json.loads(r.body.decode())["content"]
    nb = from_dict(nbcontent)
    assert nb.cells[0].source == "Created by test"

    # Restore Checkpoint cp1
    r = await jp_fetch(
        "api",
        "contents",
        path,
        "checkpoints",
        cp1["id"],
        method="POST",
        allow_nonstandard_methods=True,
    )
    assert r.code == 204

    r = await jp_fetch("api", "contents", path, method="GET")
    nbcontent = json.loads(r.body.decode())["content"]
    nb = from_dict(nbcontent)
    assert nb.cells == []

    # Delete cp1
    r = await jp_fetch("api", "contents", path, "checkpoints", cp1["id"], method="DELETE")
    assert r.code == 204

    r = await jp_fetch("api", "contents", path, "checkpoints", method="GET")
    cps = json.loads(r.body.decode())
    assert cps == []


async def test_file_checkpoints(jp_fetch, contents):
    path = "foo/a.txt"
    resp = await jp_fetch("api", "contents", path, method="GET")
    orig_content = json.loads(resp.body.decode())["content"]
    r = await jp_fetch(
        "api", "contents", path, "checkpoints", method="POST", allow_nonstandard_methods=True
    )
    assert r.code == 201
    cp1 = json.loads(r.body.decode())
    assert set(cp1) == {"id", "last_modified"}
    assert r.headers["Location"].split("/")[-1] == cp1["id"]

    # Modify it.
    new_content = orig_content + "\nsecond line"
    model = {
        "content": new_content,
        "type": "file",
        "format": "text",
    }

    # Save it.
    await jp_fetch("api", "contents", path, method="PUT", body=json.dumps(model))

    # List checkpoints
    r = await jp_fetch("api", "contents", path, "checkpoints", method="GET")
    cps = json.loads(r.body.decode())
    assert cps == [cp1]

    r = await jp_fetch("api", "contents", path, method="GET")
    content = json.loads(r.body.decode())["content"]
    assert content == new_content

    # Restore Checkpoint cp1
    r = await jp_fetch(
        "api",
        "contents",
        path,
        "checkpoints",
        cp1["id"],
        method="POST",
        allow_nonstandard_methods=True,
    )
    assert r.code == 204

    r = await jp_fetch("api", "contents", path, method="GET")
    restored_content = json.loads(r.body.decode())["content"]
    assert restored_content == orig_content

    # Delete cp1
    r = await jp_fetch("api", "contents", path, "checkpoints", cp1["id"], method="DELETE")
    assert r.code == 204

    r = await jp_fetch("api", "contents", path, "checkpoints", method="GET")
    cps = json.loads(r.body.decode())
    assert cps == []


async def test_trust(jp_fetch, contents):
    # It should be able to trust a notebook that exists
    for path in contents["notebooks"]:
        r = await jp_fetch(
            "api", "contents", str(path), "trust", method="POST", allow_nonstandard_methods=True
        )
        assert r.code == 201
