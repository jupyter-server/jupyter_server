import pytest

from traitlets.config import Config
from jupyter_server.services.contents.filecheckpoints import GenericFileCheckpoints


@pytest.fixture
def server_config():
    return {'FileContentsManager': {'checkpoints_class': GenericFileCheckpoints}}


def test_config_did_something(serverapp):
    assert isinstance(serverapp.contents_manager.checkpoints, GenericFileCheckpoints)