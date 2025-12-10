import json

import pytest

from jupyter_server.services.contents.filemanager import (
    AsyncFileContentsManager,
)


class NoHashFileManager(AsyncFileContentsManager):
    """FileManager prior to 2.11 that introduce the ability to request file hash."""

    def _base_model(self, path):
        """Drop new attributes from model."""
        model = super()._base_model(path)

        del model["hash"]
        del model["hash_algorithm"]

        return model

    async def get(self, path, content=True, type=None, format=None):
        """Get without the new `require_hash` argument"""
        model = await super().get(path, content=content, type=type, format=format)
        return model


@pytest.fixture
def jp_server_config(jp_server_config):
    jp_server_config["ServerApp"]["contents_manager_class"] = NoHashFileManager
    return jp_server_config


async def test_manager_no_hash_support(tmp_path, jp_root_dir, jp_fetch):
    # Create some content
    path = "dummy.txt"
    (jp_root_dir / path).write_text("blablabla", encoding="utf-8")

    response = await jp_fetch("api", "contents", path, method="GET", params=dict(hash="1"))

    model = json.loads(response.body)

    assert "hash" not in model
    assert "hash_algorithm" not in model
