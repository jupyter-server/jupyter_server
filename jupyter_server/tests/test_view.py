"""test view handler"""
from html.parser import HTMLParser

import pytest
import tornado

from .utils import expected_http_error
from jupyter_server.utils import url_path_join


class IFrameSrcFinder(HTMLParser):
    """Minimal HTML parser to find iframe.src attr"""

    def __init__(self):
        super().__init__()
        self.iframe_src = None

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "iframe":
            for attr, value in attrs:
                if attr.lower() == "src":
                    self.iframe_src = value
                    return


def find_iframe_src(html):
    """Find the src= attr of an iframe on the page

    Assumes only one iframe
    """
    finder = IFrameSrcFinder()
    finder.feed(html)
    return finder.iframe_src


@pytest.mark.parametrize(
    "exists, name",
    [
        (False, "nosuchfile.html"),
        (False, "nosuchfile.bin"),
        (True, "exists.html"),
        (True, "exists.bin"),
    ],
)
async def test_view(jp_fetch, jp_serverapp, jp_root_dir, exists, name):
    """Test /view/$path for a few cases"""
    if exists:
        jp_root_dir.joinpath(name).write_text(name)

    if not exists:
        with pytest.raises(tornado.httpclient.HTTPClientError) as e:
            await jp_fetch("view", name, method="GET")
        assert expected_http_error(e, 404), [name, e]
    else:
        r = await jp_fetch("view", name, method="GET")
        assert r.code == 200
        assert r.headers["content-type"] == "text/html; charset=UTF-8"
        html = r.body.decode()
        src = find_iframe_src(html)
        assert src == url_path_join(jp_serverapp.base_url, f"/files/{name}")
