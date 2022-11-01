import warnings

import pytest

from jupyter_server.services.contents.checkpoints import AsyncCheckpoints
from jupyter_server.services.contents.filecheckpoints import (
    AsyncGenericFileCheckpoints,
    GenericFileCheckpoints,
)
from jupyter_server.services.contents.manager import AsyncContentsManager


@pytest.fixture(autouse=True)
def suppress_deprecation_warnings():
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message="ContentsManager will become an alias",
            category=DeprecationWarning,
        )
        warnings.filterwarnings(
            "ignore",
            message="Checkpoints will become an alias",
            category=DeprecationWarning,
        )
        yield


@pytest.fixture(params=[AsyncGenericFileCheckpoints, GenericFileCheckpoints])
def jp_server_config(request):
    return {"AsyncFileContentsManager": {"checkpoints_class": request.param}}


def test_config_did_something(jp_server_config, jp_serverapp):
    assert isinstance(
        jp_serverapp.contents_manager.checkpoints,
        jp_server_config["AsyncFileContentsManager"]["checkpoints_class"],
    )


def example_pre_save_hook():
    pass


def example_post_save_hook():
    pass


@pytest.mark.parametrize(
    "jp_server_config",
    [
        {
            "AsyncContentsManager": {
                "pre_save_hook": "tests.services.contents.test_config.example_pre_save_hook",
                "post_save_hook": "tests.services.contents.test_config.example_post_save_hook",
            },
        }
    ],
)
def test_pre_post_save_hook_config(jp_serverapp, jp_server_config):
    assert jp_serverapp.contents_manager.pre_save_hook.__name__ == "example_pre_save_hook"
    assert jp_serverapp.contents_manager.post_save_hook.__name__ == "example_post_save_hook"


def test_async_contents_manager(jp_configurable_serverapp):
    config = {"ContentsManager": {"checkpoints_class": AsyncCheckpoints}}
    argv = [
        "--ServerApp.contents_manager_class=jupyter_server.services.contents.manager.AsyncContentsManager"
    ]
    app = jp_configurable_serverapp(config=config, argv=argv)
    assert isinstance(app.contents_manager, AsyncContentsManager)
