import re

import pytest
import tornado

from jupyter_server.base.handlers import path_regex
from jupyter_server.utils import url_path_join

# build regexps that tornado uses:
path_pat = re.compile("^" + "/x%s" % path_regex + "$")


def test_path_regex():
    for path in (
        "/x",
        "/x/",
        "/x/foo",
        "/x/foo.ipynb",
        "/x/foo/bar",
        "/x/foo/bar.txt",
    ):
        assert re.match(path_pat, path)


def test_path_regex_bad():
    for path in (
        "/xfoo",
        "/xfoo/",
        "/xfoo/bar",
        "/xfoo/bar/",
        "/x/foo/bar/",
        "/x//foo",
        "/y",
        "/y/x/foo",
    ):
        assert re.match(path_pat, path) is None


@pytest.mark.parametrize(
    "uri,expected",
    [
        ("/notebooks/mynotebook/", "/notebooks/mynotebook"),
        ("////foo///", "/foo"),
        ("//example.com/", "/example.com"),
        ("/has/param/?hasparam=true", "/has/param?hasparam=true"),
    ],
)
async def test_trailing_slash(
    jp_ensure_app_fixture, uri, expected, http_server_client, jp_auth_header, jp_base_url
):
    # http_server_client raises an exception when follow_redirects=False
    with pytest.raises(tornado.httpclient.HTTPClientError) as err:
        await http_server_client.fetch(
            url_path_join(jp_base_url, uri),
            headers=jp_auth_header,
            request_timeout=20,
            follow_redirects=False,
        )
    # Capture the response from the raised exception value.
    response = err.value.response
    assert response.code == 302
    assert "Location" in response.headers
    assert response.headers["Location"] == url_path_join(jp_base_url, expected)
