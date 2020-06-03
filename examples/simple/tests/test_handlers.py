import pytest


@pytest.fixture
def server_config(template_dir):
    return {
            "ServerApp": {
                "jpserver_extensions": {
                    "simple_ext1": True
                }
            },
        }


async def test_handler_default(fetch):
    r = await fetch(
        'simple_ext1/default',
        method='GET'
    )
    assert r.code == 200
    print(r.body.decode())
    assert r.body.decode().index('Hello Simple 1 - I am the default...') > -1


async def test_handler_template(fetch):
    r = await fetch(
        'simple_ext1/template1/test',
        method='GET'
    )
    assert r.code == 200
