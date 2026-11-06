import os
import stat
import sys
import tempfile

import pytest
from jupyter_core.utils import ensure_async
from nbformat import from_dict
from nbformat.v4 import new_markdown_cell
from tornado.web import HTTPError

from jupyter_server.services.contents.filecheckpoints import (
    AsyncFileCheckpoints,
    AsyncGenericFileCheckpoints,
    FileCheckpoints,
    GenericFileCheckpoints,
)
from jupyter_server.services.contents.largefilemanager import (
    AsyncLargeFileManager,
    LargeFileManager,
)

param_pairs = [
    (LargeFileManager, FileCheckpoints),
    (LargeFileManager, GenericFileCheckpoints),
    (AsyncLargeFileManager, AsyncFileCheckpoints),
    (AsyncLargeFileManager, AsyncGenericFileCheckpoints),
]


@pytest.fixture(params=param_pairs)
def contents_manager(request, contents):
    """Returns a LargeFileManager instance."""
    file_manager, checkpoints_class = request.param
    root_dir = str(contents["contents_dir"])
    return file_manager(root_dir=root_dir, checkpoints_class=checkpoints_class)


async def test_checkpoints_follow_file(contents_manager):
    cm: LargeFileManager = contents_manager
    path = "foo/a.ipynb"

    # Read initial file.
    model = await ensure_async(cm.get(path))

    # Create a checkpoint of initial state
    cp1 = await ensure_async(cm.create_checkpoint(path))

    # Modify file and save.
    nbcontent = model["content"]
    nb = from_dict(nbcontent)
    hcell = new_markdown_cell("Created by test")
    nb.cells.append(hcell)
    nbmodel = {"content": nb, "type": "notebook"}
    await ensure_async(cm.save(nbmodel, path))

    # List checkpoints
    cps = await ensure_async(cm.list_checkpoints(path))
    assert cps == [cp1]

    model = await ensure_async(cm.get(path))
    nbcontent = model["content"]
    nb = from_dict(nbcontent)
    assert nb.cells[0].source == "Created by test"


async def test_nb_checkpoints(contents_manager):
    cm: LargeFileManager = contents_manager
    path = "foo/a.ipynb"
    model = await ensure_async(cm.get(path))
    cp1 = await ensure_async(cm.create_checkpoint(path))
    assert set(cp1) == {"id", "last_modified"}

    # Modify it.
    nbcontent = model["content"]
    nb = from_dict(nbcontent)
    hcell = new_markdown_cell("Created by test")
    nb.cells.append(hcell)

    # Save it.
    nbmodel = {"content": nb, "type": "notebook"}
    await ensure_async(cm.save(nbmodel, path))

    # List checkpoints
    cps = await ensure_async(cm.list_checkpoints(path))
    assert cps == [cp1]

    nbcontent = await ensure_async(cm.get(path))
    nb = from_dict(nbcontent["content"])
    assert nb.cells[0].source == "Created by test"

    # Restore Checkpoint cp1
    await ensure_async(cm.restore_checkpoint(cp1["id"], path))

    nbcontent = await ensure_async(cm.get(path))
    nb = from_dict(nbcontent["content"])
    assert nb.cells == []

    # Delete cp1
    await ensure_async(cm.delete_checkpoint(cp1["id"], path))

    cps = await ensure_async(cm.list_checkpoints(path))
    assert cps == []


async def test_file_checkpoints(contents_manager):
    cm: LargeFileManager = contents_manager
    path = "foo/a.txt"
    model = await ensure_async(cm.get(path))
    orig_content = model["content"]

    cp1 = await ensure_async(cm.create_checkpoint(path))
    assert set(cp1) == {"id", "last_modified"}

    # Modify and save it.
    model["content"] = new_content = orig_content + "\nsecond line"
    await ensure_async(cm.save(model, path))

    # List checkpoints
    cps = await ensure_async(cm.list_checkpoints(path))
    assert cps == [cp1]

    model = await ensure_async(cm.get(path))
    assert model["content"] == new_content

    # Restore Checkpoint cp1
    await ensure_async(cm.restore_checkpoint(cp1["id"], path))

    restored_content = await ensure_async(cm.get(path))
    assert restored_content["content"] == orig_content

    # Delete cp1
    await ensure_async(cm.delete_checkpoint(cp1["id"], path))

    cps = await ensure_async(cm.list_checkpoints(path))
    assert cps == []


@pytest.mark.skipif(sys.platform.startswith("win"), reason="requires POSIX directory perms")
async def test_checkpoints_in_readonly_dir_use_private_temp_dir(
    contents_manager, tmp_path, monkeypatch
):
    cm: LargeFileManager = contents_manager
    shared_tmp = tmp_path / "shared_tmp"
    shared_tmp.mkdir()
    monkeypatch.setattr(tempfile, "tempdir", str(shared_tmp))

    # another local user staged the old fixed location with a symlink
    staged = shared_tmp / "jupyter_checkpoints" / "foo"
    staged.mkdir(parents=True)
    target = tmp_path / "target"
    target.write_text("untouched")
    (staged / "a-checkpoint.ipynb").symlink_to(target)

    readonly = cm._get_os_path("foo")
    os.chmod(readonly, 0o500)
    try:
        cp = await ensure_async(cm.create_checkpoint("foo/a.ipynb"))
        assert await ensure_async(cm.list_checkpoints("foo/a.ipynb")) == [cp]
    finally:
        os.chmod(readonly, 0o700)

    assert target.read_text() == "untouched"
    cp_root = shared_tmp / f"jupyter_checkpoints-{os.getuid()}"
    assert stat.S_IMODE(cp_root.stat().st_mode) == 0o700
    assert (cp_root / "foo" / "a-checkpoint.ipynb").is_file()


@pytest.mark.skipif(sys.platform.startswith("win"), reason="requires POSIX directory perms")
async def test_checkpoints_refuse_non_private_temp_dir(contents_manager, tmp_path, monkeypatch):
    cm: LargeFileManager = contents_manager
    shared_tmp = tmp_path / "shared_tmp"
    shared_tmp.mkdir()
    monkeypatch.setattr(tempfile, "tempdir", str(shared_tmp))

    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    os.chmod(elsewhere, 0o777)
    (shared_tmp / f"jupyter_checkpoints-{os.getuid()}").symlink_to(elsewhere)

    readonly = cm._get_os_path("foo")
    os.chmod(readonly, 0o500)
    try:
        with pytest.raises(HTTPError) as e:
            await ensure_async(cm.create_checkpoint("foo/a.ipynb"))
    finally:
        os.chmod(readonly, 0o700)
    assert e.value.status_code == 403
    assert list(elsewhere.iterdir()) == []
