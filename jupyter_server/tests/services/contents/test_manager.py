import os
import sys
import time
from itertools import combinations

import pytest
from nbformat import v4 as nbformat
from tornado.web import HTTPError
from traitlets import TraitError

from ...utils import expected_http_error
from jupyter_server.services.contents.filemanager import AsyncFileContentsManager
from jupyter_server.services.contents.filemanager import FileContentsManager
from jupyter_server.utils import ensure_async


@pytest.fixture(
    params=[
        (FileContentsManager, True),
        (FileContentsManager, False),
        (AsyncFileContentsManager, True),
        (AsyncFileContentsManager, False),
    ]
)
def jp_contents_manager(request, tmp_path):
    contents_manager, use_atomic_writing = request.param
    return contents_manager(root_dir=str(tmp_path), use_atomic_writing=use_atomic_writing)


@pytest.fixture(params=[FileContentsManager, AsyncFileContentsManager])
def jp_file_contents_manager_class(request, tmp_path):
    return request.param


# -------------- Functions ----------------------------


def _make_dir(jp_contents_manager, api_path):
    """
    Make a directory.
    """
    os_path = jp_contents_manager._get_os_path(api_path)
    try:
        os.makedirs(os_path)
    except OSError:
        print("Directory already exists: %r" % os_path)


def symlink(jp_contents_manager, src, dst):
    """Make a symlink to src from dst

    src and dst are api_paths
    """
    src_os_path = jp_contents_manager._get_os_path(src)
    dst_os_path = jp_contents_manager._get_os_path(dst)
    print(src_os_path, dst_os_path, os.path.isfile(src_os_path))
    os.symlink(src_os_path, dst_os_path)


def add_code_cell(notebook):
    output = nbformat.new_output("display_data", {"application/javascript": "alert('hi');"})
    cell = nbformat.new_code_cell("print('hi')", outputs=[output])
    notebook.cells.append(cell)


async def new_notebook(jp_contents_manager):
    cm = jp_contents_manager
    model = await ensure_async(cm.new_untitled(type="notebook"))
    name = model["name"]
    path = model["path"]

    full_model = await ensure_async(cm.get(path))
    nb = full_model["content"]
    nb["metadata"]["counter"] = int(1e6 * time.time())
    add_code_cell(nb)

    await ensure_async(cm.save(full_model, path))
    return nb, name, path


async def make_populated_dir(jp_contents_manager, api_path):
    cm = jp_contents_manager
    _make_dir(cm, api_path)
    await ensure_async(cm.new(path="/".join([api_path, "nb.ipynb"])))
    await ensure_async(cm.new(path="/".join([api_path, "file.txt"])))


async def check_populated_dir_files(jp_contents_manager, api_path):
    dir_model = await ensure_async(jp_contents_manager.get(api_path))

    assert dir_model["path"] == api_path
    assert dir_model["type"] == "directory"

    for entry in dir_model["content"]:
        if entry["type"] == "directory":
            continue
        elif entry["type"] == "file":
            assert entry["name"] == "file.txt"
            complete_path = "/".join([api_path, "file.txt"])
            assert entry["path"] == complete_path
        elif entry["type"] == "notebook":
            assert entry["name"] == "nb.ipynb"
            complete_path = "/".join([api_path, "nb.ipynb"])
            assert entry["path"] == complete_path


# ----------------- Tests ----------------------------------


def test_root_dir(jp_file_contents_manager_class, tmp_path):
    fm = jp_file_contents_manager_class(root_dir=str(tmp_path))
    assert fm.root_dir == str(tmp_path)


def test_missing_root_dir(jp_file_contents_manager_class, tmp_path):
    root = tmp_path / "notebook" / "dir" / "is" / "missing"
    with pytest.raises(TraitError):
        jp_file_contents_manager_class(root_dir=str(root))


def test_invalid_root_dir(jp_file_contents_manager_class, tmp_path):
    temp_file = tmp_path / "file.txt"
    temp_file.write_text("")
    with pytest.raises(TraitError):
        jp_file_contents_manager_class(root_dir=str(temp_file))


def test_get_os_path(jp_file_contents_manager_class, tmp_path):
    fm = jp_file_contents_manager_class(root_dir=str(tmp_path))
    path = fm._get_os_path("/path/to/notebook/test.ipynb")
    rel_path_list = "/path/to/notebook/test.ipynb".split("/")
    fs_path = os.path.join(fm.root_dir, *rel_path_list)
    assert path == fs_path

    fm = jp_file_contents_manager_class(root_dir=str(tmp_path))
    path = fm._get_os_path("test.ipynb")
    fs_path = os.path.join(fm.root_dir, "test.ipynb")
    assert path == fs_path

    fm = jp_file_contents_manager_class(root_dir=str(tmp_path))
    path = fm._get_os_path("////test.ipynb")
    fs_path = os.path.join(fm.root_dir, "test.ipynb")
    assert path == fs_path


def test_checkpoint_subdir(jp_file_contents_manager_class, tmp_path):
    subd = "sub ∂ir"
    cp_name = "test-cp.ipynb"
    fm = jp_file_contents_manager_class(root_dir=str(tmp_path))
    tmp_path.joinpath(subd).mkdir()
    cpm = fm.checkpoints
    cp_dir = cpm.checkpoint_path("cp", "test.ipynb")
    cp_subdir = cpm.checkpoint_path("cp", "/%s/test.ipynb" % subd)
    assert cp_dir != cp_subdir
    assert cp_dir == os.path.join(str(tmp_path), cpm.checkpoint_dir, cp_name)


async def test_bad_symlink(jp_file_contents_manager_class, tmp_path):
    td = str(tmp_path)

    cm = jp_file_contents_manager_class(root_dir=td)
    path = "test bad symlink"
    _make_dir(cm, path)

    file_model = await ensure_async(cm.new_untitled(path=path, ext=".txt"))

    # create a broken symlink
    symlink(cm, "target", "%s/%s" % (path, "bad symlink"))
    model = await ensure_async(cm.get(path))

    contents = {content["name"]: content for content in model["content"]}
    assert "untitled.txt" in contents
    assert contents["untitled.txt"] == file_model
    assert "bad symlink" in contents


@pytest.mark.skipif(sys.platform.startswith("win"), reason="Windows doesn't detect symlink loops")
async def test_recursive_symlink(jp_file_contents_manager_class, tmp_path):
    td = str(tmp_path)

    cm = jp_file_contents_manager_class(root_dir=td)
    path = "test recursive symlink"
    _make_dir(cm, path)

    file_model = await ensure_async(cm.new_untitled(path=path, ext=".txt"))

    # create recursive symlink
    symlink(cm, "%s/%s" % (path, "recursive"), "%s/%s" % (path, "recursive"))
    model = await ensure_async(cm.get(path))

    contents = {content["name"]: content for content in model["content"]}
    assert "untitled.txt" in contents
    assert contents["untitled.txt"] == file_model
    # recursive symlinks should not be shown in the contents manager
    assert "recursive" not in contents


async def test_good_symlink(jp_file_contents_manager_class, tmp_path):
    td = str(tmp_path)
    cm = jp_file_contents_manager_class(root_dir=td)
    parent = "test good symlink"
    name = "good symlink"
    path = "{0}/{1}".format(parent, name)
    _make_dir(cm, parent)

    file_model = await ensure_async(cm.new(path=parent + "/zfoo.txt"))

    # create a good symlink
    symlink(cm, file_model["path"], path)
    symlink_model = await ensure_async(cm.get(path, content=False))
    dir_model = await ensure_async(cm.get(parent))
    assert sorted(dir_model["content"], key=lambda x: x["name"]) == [symlink_model, file_model]


@pytest.mark.skipif(sys.platform.startswith("win"), reason="Can't test permissions on Windows")
async def test_403(jp_file_contents_manager_class, tmp_path):
    if hasattr(os, "getuid"):
        if os.getuid() == 0:
            raise pytest.skip("Can't test permissions as root")

    td = str(tmp_path)
    cm = jp_file_contents_manager_class(root_dir=td)
    model = await ensure_async(cm.new_untitled(type="file"))
    os_path = cm._get_os_path(model["path"])

    os.chmod(os_path, 0o400)
    try:
        with cm.open(os_path, "w") as f:
            f.write(u"don't care")
    except HTTPError as e:
        assert e.status_code == 403


async def test_escape_root(jp_file_contents_manager_class, tmp_path):
    td = str(tmp_path)
    cm = jp_file_contents_manager_class(root_dir=td)
    # make foo, bar next to root
    with open(os.path.join(cm.root_dir, "..", "foo"), "w") as f:
        f.write("foo")
    with open(os.path.join(cm.root_dir, "..", "bar"), "w") as f:
        f.write("bar")

    with pytest.raises(HTTPError) as e:
        await ensure_async(cm.get(".."))
    expected_http_error(e, 404)

    with pytest.raises(HTTPError) as e:
        await ensure_async(cm.get("foo/../../../bar"))
    expected_http_error(e, 404)

    with pytest.raises(HTTPError) as e:
        await ensure_async(cm.delete("../foo"))
    expected_http_error(e, 404)

    with pytest.raises(HTTPError) as e:
        await ensure_async(cm.rename("../foo", "../bar"))
    expected_http_error(e, 404)

    with pytest.raises(HTTPError) as e:
        await ensure_async(
            cm.save(
                model={
                    "type": "file",
                    "content": u"",
                    "format": "text",
                },
                path="../foo",
            )
        )
    expected_http_error(e, 404)


async def test_new_untitled(jp_contents_manager):
    cm = jp_contents_manager
    # Test in root directory
    model = await ensure_async(cm.new_untitled(type="notebook"))
    assert isinstance(model, dict)
    assert "name" in model
    assert "path" in model
    assert "type" in model
    assert model["type"] == "notebook"
    assert model["name"] == "Untitled.ipynb"
    assert model["path"] == "Untitled.ipynb"

    # Test in sub-directory
    model = await ensure_async(cm.new_untitled(type="directory"))
    assert isinstance(model, dict)
    assert "name" in model
    assert "path" in model
    assert "type" in model
    assert model["type"] == "directory"
    assert model["name"] == "Untitled Folder"
    assert model["path"] == "Untitled Folder"
    sub_dir = model["path"]

    model = await ensure_async(cm.new_untitled(path=sub_dir))
    assert isinstance(model, dict)
    assert "name" in model
    assert "path" in model
    assert "type" in model
    assert model["type"] == "file"
    assert model["name"] == "untitled"
    assert model["path"] == "%s/untitled" % sub_dir

    # Test with a compound extension
    model = await ensure_async(cm.new_untitled(path=sub_dir, ext=".foo.bar"))
    assert model["name"] == "untitled.foo.bar"
    model = await ensure_async(cm.new_untitled(path=sub_dir, ext=".foo.bar"))
    assert model["name"] == "untitled1.foo.bar"


async def test_modified_date(jp_contents_manager):
    cm = jp_contents_manager
    # Create a new notebook.
    nb, name, path = await new_notebook(cm)
    model = await ensure_async(cm.get(path))

    # Add a cell and save.
    add_code_cell(model["content"])
    await ensure_async(cm.save(model, path))

    # Reload notebook and verify that last_modified incremented.
    saved = await ensure_async(cm.get(path))
    assert saved["last_modified"] >= model["last_modified"]

    # Move the notebook and verify that last_modified stayed the same.
    # (The frontend fires a warning if last_modified increases on the
    # renamed file.)
    new_path = "renamed.ipynb"
    await ensure_async(cm.rename(path, new_path))
    renamed = await ensure_async(cm.get(new_path))
    assert renamed["last_modified"] >= saved["last_modified"]


async def test_get(jp_contents_manager):
    cm = jp_contents_manager
    # Create a notebook
    model = await ensure_async(cm.new_untitled(type="notebook"))
    name = model["name"]
    path = model["path"]

    # Check that we 'get' on the notebook we just created
    model2 = await ensure_async(cm.get(path))
    assert isinstance(model2, dict)
    assert "name" in model2
    assert "path" in model2
    assert model["name"] == name
    assert model["path"] == path

    nb_as_file = await ensure_async(cm.get(path, content=True, type="file"))
    assert nb_as_file["path"] == path
    assert nb_as_file["type"] == "file"
    assert nb_as_file["format"] == "text"
    assert not isinstance(nb_as_file["content"], dict)

    nb_as_bin_file = await ensure_async(cm.get(path, content=True, type="file", format="base64"))
    assert nb_as_bin_file["format"] == "base64"

    # Test in sub-directory
    sub_dir = "/foo/"
    _make_dir(cm, "foo")
    await ensure_async(cm.new_untitled(path=sub_dir, ext=".ipynb"))
    model2 = await ensure_async(cm.get(sub_dir + name))
    assert isinstance(model2, dict)
    assert "name" in model2
    assert "path" in model2
    assert "content" in model2
    assert model2["name"] == "Untitled.ipynb"
    assert model2["path"] == "{0}/{1}".format(sub_dir.strip("/"), name)

    # Test with a regular file.
    file_model_path = (await ensure_async(cm.new_untitled(path=sub_dir, ext=".txt")))["path"]
    file_model = await ensure_async(cm.get(file_model_path))
    expected_model = {
        "content": u"",
        "format": u"text",
        "mimetype": u"text/plain",
        "name": u"untitled.txt",
        "path": u"foo/untitled.txt",
        "type": u"file",
        "writable": True,
    }
    # Assert expected model is in file_model
    for key, value in expected_model.items():
        assert file_model[key] == value
    assert "created" in file_model
    assert "last_modified" in file_model

    # Create a sub-sub directory to test getting directory contents with a
    # subdir.
    _make_dir(cm, "foo/bar")
    dirmodel = await ensure_async(cm.get("foo"))
    assert dirmodel["type"] == "directory"
    assert isinstance(dirmodel["content"], list)
    assert len(dirmodel["content"]) == 3
    assert dirmodel["path"] == "foo"
    assert dirmodel["name"] == "foo"

    # Directory contents should match the contents of each individual entry
    # when requested with content=False.
    model2_no_content = await ensure_async(cm.get(sub_dir + name, content=False))
    file_model_no_content = await ensure_async(cm.get(u"foo/untitled.txt", content=False))
    sub_sub_dir_no_content = await ensure_async(cm.get("foo/bar", content=False))
    assert sub_sub_dir_no_content["path"] == "foo/bar"
    assert sub_sub_dir_no_content["name"] == "bar"

    for entry in dirmodel["content"]:
        # Order isn't guaranteed by the spec, so this is a hacky way of
        # verifying that all entries are matched.
        if entry["path"] == sub_sub_dir_no_content["path"]:
            assert entry == sub_sub_dir_no_content
        elif entry["path"] == model2_no_content["path"]:
            assert entry == model2_no_content
        elif entry["path"] == file_model_no_content["path"]:
            assert entry == file_model_no_content
        else:
            assert False, "Unexpected directory entry: %s" % entry()

    with pytest.raises(HTTPError):
        await ensure_async(cm.get("foo", type="file"))


async def test_update(jp_contents_manager):
    cm = jp_contents_manager
    # Create a notebook.
    model = await ensure_async(cm.new_untitled(type="notebook"))
    name = model["name"]
    path = model["path"]

    # Change the name in the model for rename
    model["path"] = "test.ipynb"
    model = await ensure_async(cm.update(model, path))
    assert isinstance(model, dict)
    assert "name" in model
    assert "path" in model
    assert model["name"] == "test.ipynb"

    # Make sure the old name is gone
    with pytest.raises(HTTPError):
        await ensure_async(cm.get(path))

    # Test in sub-directory
    # Create a directory and notebook in that directory
    sub_dir = "/foo/"
    _make_dir(cm, "foo")
    model = await ensure_async(cm.new_untitled(path=sub_dir, type="notebook"))
    path = model["path"]

    # Change the name in the model for rename
    d = path.rsplit("/", 1)[0]
    new_path = model["path"] = d + "/test_in_sub.ipynb"
    model = await ensure_async(cm.update(model, path))
    assert isinstance(model, dict)
    assert "name" in model
    assert "path" in model
    assert model["name"] == "test_in_sub.ipynb"
    assert model["path"] == new_path

    # Make sure the old name is gone
    with pytest.raises(HTTPError):
        await ensure_async(cm.get(path))


async def test_save(jp_contents_manager):
    cm = jp_contents_manager
    # Create a notebook
    model = await ensure_async(cm.new_untitled(type="notebook"))
    name = model["name"]
    path = model["path"]

    # Get the model with 'content'
    full_model = await ensure_async(cm.get(path))

    # Save the notebook
    model = await ensure_async(cm.save(full_model, path))
    assert isinstance(model, dict)
    assert "name" in model
    assert "path" in model
    assert model["name"] == name
    assert model["path"] == path

    # Test in sub-directory
    # Create a directory and notebook in that directory
    sub_dir = "/foo/"
    _make_dir(cm, "foo")
    model = await ensure_async(cm.new_untitled(path=sub_dir, type="notebook"))
    path = model["path"]
    model = await ensure_async(cm.get(path))

    # Change the name in the model for rename
    model = await ensure_async(cm.save(model, path))
    assert isinstance(model, dict)
    assert "name" in model
    assert "path" in model
    assert model["name"] == "Untitled.ipynb"
    assert model["path"] == "foo/Untitled.ipynb"


async def test_delete(jp_contents_manager):
    cm = jp_contents_manager
    # Create a notebook
    nb, name, path = await new_notebook(cm)

    # Delete the notebook
    await ensure_async(cm.delete(path))

    # Check that deleting a non-existent path raises an error.
    with pytest.raises(HTTPError):
        await ensure_async(cm.delete(path))

    # Check that a 'get' on the deleted notebook raises and error
    with pytest.raises(HTTPError):
        await ensure_async(cm.get(path))


@pytest.mark.parametrize(
    "delete_to_trash, always_delete, error",
    (
        [True, True, False],
        # on linux test folder may not be on home folder drive
        # => if this is the case, _check_trash will be False
        [True, False, None],
        [False, True, False],
        [False, False, True],
    ),
)
async def test_delete_non_empty_folder(delete_to_trash, always_delete, error, jp_contents_manager):
    cm = jp_contents_manager
    cm.delete_to_trash = delete_to_trash
    cm.always_delete_dir = always_delete

    dir = "to_delete"

    await make_populated_dir(cm, dir)
    await check_populated_dir_files(cm, dir)

    if error is None:
        error = False
        if sys.platform == "win32":
            error = True
        elif sys.platform == "linux":
            file_dev = os.stat(cm.root_dir).st_dev
            home_dev = os.stat(os.path.expanduser("~")).st_dev
            error = file_dev != home_dev

    if error:
        with pytest.raises(
            HTTPError,
            match=r"HTTP 400: Bad Request \(Directory .*?to_delete not empty\)",
        ):
            await ensure_async(cm.delete_file(dir))
    else:
        await ensure_async(cm.delete_file(dir))
        assert await ensure_async(cm.dir_exists(dir)) == False


async def test_rename(jp_contents_manager):
    cm = jp_contents_manager
    # Create a new notebook
    nb, name, path = await new_notebook(cm)

    # Rename the notebook
    await ensure_async(cm.rename(path, "changed_path"))

    # Attempting to get the notebook under the old name raises an error
    with pytest.raises(HTTPError):
        await ensure_async(cm.get(path))
    # Fetching the notebook under the new name is successful
    assert isinstance(await ensure_async(cm.get("changed_path")), dict)

    # Ported tests on nested directory renaming from pgcontents
    all_dirs = ["foo", "bar", "foo/bar", "foo/bar/foo", "foo/bar/foo/bar"]
    unchanged_dirs = all_dirs[:2]
    changed_dirs = all_dirs[2:]

    for _dir in all_dirs:
        await make_populated_dir(cm, _dir)
        await check_populated_dir_files(cm, _dir)

    # Renaming to an existing directory should fail
    for src, dest in combinations(all_dirs, 2):
        with pytest.raises(HTTPError) as e:
            await ensure_async(cm.rename(src, dest))
        assert expected_http_error(e, 409)

    # Creating a notebook in a non_existant directory should fail
    with pytest.raises(HTTPError) as e:
        await ensure_async(cm.new_untitled("foo/bar_diff", ext=".ipynb"))
    assert expected_http_error(e, 404)

    await ensure_async(cm.rename("foo/bar", "foo/bar_diff"))

    # Assert that unchanged directories remain so
    for unchanged in unchanged_dirs:
        await check_populated_dir_files(cm, unchanged)

    # Assert changed directories can no longer be accessed under old names
    for changed_dirname in changed_dirs:
        with pytest.raises(HTTPError) as e:
            await ensure_async(cm.get(changed_dirname))
        assert expected_http_error(e, 404)
        new_dirname = changed_dirname.replace("foo/bar", "foo/bar_diff", 1)
        await check_populated_dir_files(cm, new_dirname)

    # Created a notebook in the renamed directory should work
    await ensure_async(cm.new_untitled("foo/bar_diff", ext=".ipynb"))


async def test_delete_root(jp_contents_manager):
    cm = jp_contents_manager
    with pytest.raises(HTTPError) as e:
        await ensure_async(cm.delete(""))
    assert expected_http_error(e, 400)


async def test_copy(jp_contents_manager):
    cm = jp_contents_manager
    parent = u"å b"
    name = u"nb √.ipynb"
    path = u"{0}/{1}".format(parent, name)
    _make_dir(cm, parent)

    orig = await ensure_async(cm.new(path=path))
    # copy with unspecified name
    copy = await ensure_async(cm.copy(path))
    assert copy["name"] == orig["name"].replace(".ipynb", "-Copy1.ipynb")

    # copy with specified name
    copy2 = await ensure_async(cm.copy(path, u"å b/copy 2.ipynb"))
    assert copy2["name"] == u"copy 2.ipynb"
    assert copy2["path"] == u"å b/copy 2.ipynb"
    # copy with specified path
    copy2 = await ensure_async(cm.copy(path, u"/"))
    assert copy2["name"] == name
    assert copy2["path"] == name


async def test_mark_trusted_cells(jp_contents_manager):
    cm = jp_contents_manager
    nb, name, path = await new_notebook(cm)

    cm.mark_trusted_cells(nb, path)
    for cell in nb.cells:
        if cell.cell_type == "code":
            assert not cell.metadata.trusted

    await ensure_async(cm.trust_notebook(path))
    nb = (await ensure_async(cm.get(path)))["content"]
    for cell in nb.cells:
        if cell.cell_type == "code":
            assert cell.metadata.trusted


async def test_check_and_sign(jp_contents_manager):
    cm = jp_contents_manager
    nb, name, path = await new_notebook(cm)

    cm.mark_trusted_cells(nb, path)
    cm.check_and_sign(nb, path)
    assert not cm.notary.check_signature(nb)

    await ensure_async(cm.trust_notebook(path))
    nb = (await ensure_async(cm.get(path)))["content"]
    cm.mark_trusted_cells(nb, path)
    cm.check_and_sign(nb, path)
    assert cm.notary.check_signature(nb)
