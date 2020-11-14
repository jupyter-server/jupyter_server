import pytest


@pytest.fixture
def jp_server_config(jp_template_dir):
    return {
            "ServerApp": {
                "jpserver_extensions": {
                    "simple_ext1": True
                }
            },
        }


async def test_handler_default(jp_fetch):
    r = await jp_fetch(
        'simple_ext1/default',
        method='GET'
    )
    assert r.code == 200
    print(r.body.decode())
    assert r.body.decode().index('Hello Simple 1 - I am the default...') > -1


async def test_handler_template(jp_fetch):
    r = await jp_fetch(
        'simple_ext1/template1/test',
        method='GET'
    )
    assert r.code == 200
