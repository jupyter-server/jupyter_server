import pytest

from traitlets.config import Config
from jupyter_server.services.contents.checkpoints import AsyncCheckpoints
from jupyter_server.services.contents.filecheckpoints import GenericFileCheckpoints
from jupyter_server.services.contents.manager import AsyncContentsManager


@pytest.fixture
def jp_server_config():
    return {'FileContentsManager': {'checkpoints_class': GenericFileCheckpoints}}


def test_config_did_something(jp_serverapp):
    assert isinstance(jp_serverapp.contents_manager.checkpoints, GenericFileCheckpoints)


async def test_async_contents_manager(jp_configurable_serverapp):
    config = {'ContentsManager': {'checkpoints_class': AsyncCheckpoints}}
    argv = ['--ServerApp.contents_manager_class=jupyter_server.services.contents.manager.AsyncContentsManager']
    app = jp_configurable_serverapp(config=config, argv=argv)
    assert isinstance(app.contents_manager, AsyncContentsManager)

