import json
import pytest

from jupyter_server.utils import url_path_join


async def test_create_retrieve_config(fetch):
    sample = {'foo': 'bar', 'baz': 73}
    response = await fetch(
        'api', 'config', 'example',
        method='PUT',
        body=json.dumps(sample)
    )
    assert response.code == 204

    response2 = await fetch(
        'api', 'config', 'example',
        method='GET',
    )
    assert response2.code == 200
    assert json.loads(response2.body.decode()) == sample


async def test_modify(fetch):
    sample = {
        'foo': 'bar', 
        'baz': 73,
        'sub': {'a': 6, 'b': 7}, 
        'sub2': {'c': 8}
    }

    modified_sample = {
        'foo': None,  # should delete foo
        'baz': 75,
        'wib': [1,2,3],
        'sub': {'a': 8, 'b': None, 'd': 9},
        'sub2': {'c': None}  # should delete sub2
    }

    diff = {
        'baz': 75, 
        'wib': [1,2,3],
        'sub': {'a': 8, 'd': 9}
    }

    await fetch(
        'api', 'config', 'example',
        method='PUT',
        body=json.dumps(sample)
    )

    response2 = await fetch(
        'api', 'config', 'example',
        method='PATCH',
        body=json.dumps(modified_sample)
    )

    assert response2.code == 200
    assert json.loads(response2.body.decode()) == diff
    

async def test_get_unknown(fetch):
    response = await fetch(
        'api', 'config', 'nonexistant',
        method='GET',
    )
    assert response.code == 200
    assert json.loads(response.body.decode()) == {}