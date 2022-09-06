import pytest


@pytest.fixture
def jp_server_auth_resources(jp_server_auth_core_resources):
    for url_regex in [
        "/simple_ext1/default",
    ]:
        jp_server_auth_core_resources[url_regex] = "simple_ext1:default"
    return jp_server_auth_core_resources


@pytest.fixture
def jp_server_config(jp_template_dir, jp_server_authorizer):
    return {
        "ServerApp": {
            "jpserver_extensions": {"simple_ext1": True},
            "authorizer_class": jp_server_authorizer,
        },
    }


async def test_handler_default(jp_fetch, jp_serverapp):
    jp_serverapp.authorizer.permissions = {
        "actions": ["read"],
        "resources": [
            "simple_ext1:default",
        ],
    }
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
