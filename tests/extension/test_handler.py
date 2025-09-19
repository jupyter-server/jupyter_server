from html.parser import HTMLParser

import pytest
from tornado.httpclient import HTTPClientError


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


class StylesheetFinder(HTMLParser):
    """Minimal HTML parser to find iframe.src attr"""

    def __init__(self):
        super().__init__()
        self.stylesheets = []
        self.body_chunks = []
        self.in_head = False
        self.in_body = False
        self.in_script = False

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag == "head":
            self.in_head = True
        elif tag == "body":
            self.in_body = True
        elif tag == "script":
            self.in_script = True
        elif self.in_head and tag.lower() == "link":
            attr_dict = dict(attrs)
            if attr_dict.get("rel", "").lower() == "stylesheet":
                self.stylesheets.append(attr_dict["href"])

    def handle_endtag(self, tag):
        if tag == "head":
            self.in_head = False
        if tag == "body":
            self.in_body = False
        if tag == "script":
            self.in_script = False

    def handle_data(self, data):
        if self.in_body and not self.in_script:
            data = data.strip()
            if data:
                self.body_chunks.append(data)


def find_stylesheets_body(html):
    """Find the href= attr of stylesheets

    and body text of an HTML document

    stylesheets are used to test static_url prefix
    """
    finder = StylesheetFinder()
    finder.feed(html)
    return (finder.stylesheets, "\n".join(finder.body_chunks))


@pytest.mark.parametrize("error_url", ["mock_error_template", "mock_error_notemplate"])
async def test_error_render(jp_fetch, jp_serverapp, jp_base_url, error_url):
    with pytest.raises(HTTPClientError) as e:
        await jp_fetch(error_url, method="GET")
    r = e.value.response
    assert r.code == 418
    assert r.headers["Content-Type"] == "text/html"
    html = r.body.decode("utf8")
    stylesheets, body = find_stylesheets_body(html)
    static_prefix = f"{jp_base_url}static/"
    assert stylesheets
    assert all(stylesheet.startswith(static_prefix) for stylesheet in stylesheets)
    assert str(r.code) in body
