import pytest

from jupyter_server.utils import url_path_join


async def test_get_spec(fetch):
    response = await fetch(
        'api', 'spec.yaml',
        method='GET'
    )
    assert response.code == 200



