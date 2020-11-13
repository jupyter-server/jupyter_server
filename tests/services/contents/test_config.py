import pytest

from traitlets.config import Config
from jupyter_server.services.contents.filecheckpoints import GenericFileCheckpoints


@pytest.fixture
def jp_server_config():
    return {'FileContentsManager': {'checkpoints_class': GenericFileCheckpoints}}


def test_config_did_something(jp_serverapp):
    assert isinstance(jp_serverapp.contents_manager.checkpoints, GenericFileCheckpoints)