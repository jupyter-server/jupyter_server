import pytest


@pytest.fixture
def jp_server_config(jp_template_dir):
    return {
        "ServerApp": {"jpserver_extensions": {"tests.extension.mockextensions": True}},
        "MockExtensionApp": {"template_paths": [str(jp_template_dir)]},
    }


async def test_handler(jp_fetch):
    r = await jp_fetch("mock", method="GET")
    assert r.code == 200
    assert r.body.decode() == "mock trait"


async def test_handler_template(jp_fetch, mock_template):
    r = await jp_fetch("mock_template", method="GET")
    assert r.code == 200


@pytest.mark.parametrize(
    "jp_server_config",
    [
        {
            "ServerApp": {
                "allow_unauthenticated_access": False,
                "jpserver_extensions": {"tests.extension.mockextensions": True},
            }
        }
    ],
)
async def test_handler_gets_blocked(jp_fetch, jp_server_config):
    # should redirect to login page if authorization token is missing
    r = await jp_fetch(
        "mock",
        method="GET",
        headers={"Authorization": ""},
        follow_redirects=False,
        raise_error=False,
    )
    assert r.code == 302
    assert "/login" in r.headers["Location"]
    # should still work if authorization token is present
    r = await jp_fetch("mock", method="GET")
    assert r.code == 200


def test_serverapp_warns_of_unauthenticated_handler(jp_configurable_serverapp):
    # should warn about the handler missing decorator when unauthenticated access forbidden
    expected_warning = "Extension endpoints without @allow_unauthenticated, @ws_authenticated, nor @web.authenticated:"
    with pytest.warns(RuntimeWarning, match=expected_warning) as record:
        jp_configurable_serverapp(allow_unauthenticated_access=False)
    assert any(
        "GET of MockExtensionTemplateHandler registered for /a%40b/mock_template"
        in r.message.args[0]
        for r in record
    )


@pytest.mark.parametrize(
    "jp_server_config",
    [
        {
            "ServerApp": {"jpserver_extensions": {"tests.extension.mockextensions": True}},
            "MockExtensionApp": {
                # Change a trait in the MockExtensionApp using
                # the following config value.
                "mock_trait": "test mock trait"
            },
        }
    ],
)
async def test_handler_setting(jp_fetch, jp_server_config):
    # Test that the extension trait was picked up by the webapp.
    r = await jp_fetch("mock", method="GET")
    assert r.code == 200
    assert r.body.decode() == "test mock trait"


@pytest.mark.parametrize("jp_argv", (["--MockExtensionApp.mock_trait=test mock trait"],))
async def test_handler_argv(jp_fetch, jp_argv):
    # Test that the extension trait was picked up by the webapp.
    r = await jp_fetch("mock", method="GET")
    assert r.code == 200
    assert r.body.decode() == "test mock trait"


@pytest.mark.parametrize(
    "jp_server_config,jp_base_url",
    [
        (
            {
                "ServerApp": {
                    "jpserver_extensions": {"tests.extension.mockextensions": True},
                    # Move extension handlers behind a url prefix
                    "base_url": "test_prefix",
                },
                "MockExtensionApp": {
                    # Change a trait in the MockExtensionApp using
                    # the following config value.
                    "mock_trait": "test mock trait"
                },
            },
            "/test_prefix/",
        )
    ],
)
async def test_base_url(jp_fetch, jp_server_config, jp_base_url):
    # Test that the extension's handlers were properly prefixed
    r = await jp_fetch("mock", method="GET")
    assert r.code == 200
    assert r.body.decode() == "test mock trait"

    # Test that the static namespace was prefixed by base_url
    r = await jp_fetch("static", "mockextension", "mock.txt", method="GET")
    assert r.code == 200
    body = r.body.decode()
    assert "mock static content" in body
