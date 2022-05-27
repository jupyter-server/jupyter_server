import pytest
import tornado

from jupyter_server.services.contents.largefilemanager import (
    AsyncLargeFileManager,
    LargeFileManager,
)
from jupyter_server.utils import ensure_async

from ...utils import expected_http_error


@pytest.fixture(params=[LargeFileManager, AsyncLargeFileManager])
def jp_large_contents_manager(request, tmp_path):
    """Returns a LargeFileManager instance."""
    file_manager = request.param
    return file_manager(root_dir=str(tmp_path))


async def test_save(jp_large_contents_manager):
    cm = jp_large_contents_manager
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


@pytest.mark.parametrize(
    "model,err_message",
    [
        (
            {"name": "test", "path": "test", "chunk": 1},
            "HTTP 400: Bad Request (No file type provided)",
        ),
        (
            {"name": "test", "path": "test", "chunk": 1, "type": "notebook"},
            'HTTP 400: Bad Request (File type "notebook" is not supported for large file transfer)',
        ),
        (
            {"name": "test", "path": "test", "chunk": 1, "type": "file"},
            "HTTP 400: Bad Request (No file content provided)",
        ),
        (
            {
                "name": "test",
                "path": "test",
                "chunk": 2,
                "type": "file",
                "content": "test",
                "format": "json",
            },
            "HTTP 400: Bad Request (Must specify format of file contents as 'text' or 'base64')",
        ),
    ],
)
async def test_bad_save(jp_large_contents_manager, model, err_message):
    with pytest.raises(tornado.web.HTTPError) as e:
        await ensure_async(jp_large_contents_manager.save(model, model["path"]))
    assert expected_http_error(e, 400, expected_message=err_message)


async def test_saving_different_chunks(jp_large_contents_manager):
    cm = jp_large_contents_manager
    model = {
        "name": "test",
        "path": "test",
        "type": "file",
        "content": "test==",
        "format": "text",
    }
    name = model["name"]
    path = model["path"]
    await ensure_async(cm.save(model, path))

    for chunk in (1, 2, -1):
        for fm in ("text", "base64"):
            full_model = await ensure_async(cm.get(path))
            full_model["chunk"] = chunk
            full_model["format"] = fm
            model_res = await ensure_async(cm.save(full_model, path))
            assert isinstance(model_res, dict)
            assert "name" in model_res
            assert "path" in model_res
            assert "chunk" not in model_res
            assert model_res["name"] == name
            assert model_res["path"] == path


async def test_save_in_subdirectory(jp_large_contents_manager, tmp_path):
    cm = jp_large_contents_manager
    sub_dir = tmp_path / "foo"
    sub_dir.mkdir()
    model = await ensure_async(cm.new_untitled(path="/foo/", type="notebook"))
    path = model["path"]
    model = await ensure_async(cm.get(path))

    # Change the name in the model for rename
    model = await ensure_async(cm.save(model, path))
    assert isinstance(model, dict)
    assert "name" in model
    assert "path" in model
    assert model["name"] == "Untitled.ipynb"
    assert model["path"] == "foo/Untitled.ipynb"
