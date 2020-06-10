import pytest
from jupyter_server.extension.utils import list_extensions_from_configd


@pytest.fixture
def config_path(tmp_path):
    root = tmp_path.joinpath('config')
    root.mkdir()
    return root

@pytest.fixture
def configd(config_path):
    configd = config_path.joinpath('jupyter_server_config.d')
    configd.mkdir()
    return configd


ext1_json_config = """\
{
    "ServerApp": {
        "jpserver_extensions": {
            "ext1_config": true
        }
    }
}
"""


@pytest.fixture
def ext1_config(configd):
    config = configd.joinpath("ext1_config.json")
    config.write_text(ext1_json_config)


ext2_py_config = """\
c.ServerApp.jpserver_extensions = {
    "ext2_config": True
}
"""


@pytest.fixture
def ext2_config(configd):
    config = configd.joinpath("ext2_config.py")
    config.write_text(ext2_py_config)


def test_list_extension_from_configd(config_path, ext1_config, ext2_config):
    extensions = list_extensions_from_configd(
        config_paths=[config_path]
    )
    assert "ext2_config" in extensions
    assert "ext1_config" in extensions
    assert extensions["ext2_config"]
    assert extensions["ext1_config"]
