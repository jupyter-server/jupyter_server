import pytest
from jupyter_core.utils import ensure_async
from nbformat import from_dict
from nbformat.v4 import new_markdown_cell

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
