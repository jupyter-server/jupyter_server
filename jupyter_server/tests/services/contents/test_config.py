import pytest

from jupyter_server.services.contents.checkpoints import AsyncCheckpoints
from jupyter_server.services.contents.filecheckpoints import AsyncGenericFileCheckpoints
from jupyter_server.services.contents.filecheckpoints import GenericFileCheckpoints
from jupyter_server.services.contents.manager import AsyncContentsManager


@pytest.fixture(params=[AsyncGenericFileCheckpoints, GenericFileCheckpoints])
def jp_server_config(request):
    return {"FileContentsManager": {"checkpoints_class": request.param}}


def test_config_did_something(jp_server_config, jp_serverapp):
    assert isinstance(
        jp_serverapp.contents_manager.checkpoints,
        jp_server_config["FileContentsManager"]["checkpoints_class"],
    )


async def test_async_contents_manager(jp_configurable_serverapp):
    config = {"ContentsManager": {"checkpoints_class": AsyncCheckpoints}}
    argv = [
        "--ServerApp.contents_manager_class=jupyter_server.services.contents.manager.AsyncContentsManager"
    ]
    app = jp_configurable_serverapp(config=config, argv=argv)
    assert isinstance(app.contents_manager, AsyncContentsManager)
