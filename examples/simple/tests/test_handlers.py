import pytest


@pytest.fixture
def jp_server_config(jp_template_dir):
    return {
        "ServerApp": {"jpserver_extensions": {"simple_ext1": True}},
    }


async def test_handler_default(jp_fetch):
    r = await jp_fetch("simple_ext1/default", method="GET")
    assert r.code == 200
    assert r.body.decode().index("Hello Simple 1 - I am the default...") > -1


async def test_handler_template(jp_fetch):
    path = "/custom/path"
    r = await jp_fetch(f"simple_ext1/template1/{path}", method="GET")
    assert r.code == 200
    assert r.body.decode().index(f"Path: {path}") > -1


async def test_handler_typescript(jp_fetch):
    r = await jp_fetch("simple_ext1/typescript", method="GET")
    assert r.code == 200


async def test_handler_error(jp_fetch):
    r = await jp_fetch("simple_ext1/nope", method="GET")
    assert r.body.decode().index("400 : Bad Request") > -1
