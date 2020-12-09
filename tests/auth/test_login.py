"""Tests for login redirects"""

from functools import partial
from urllib.parse import urlencode

import pytest
from tornado.httpclient import HTTPClientError
from tornado.httputil import url_concat, parse_cookie

from jupyter_server.utils import url_path_join


# override default config to ensure a non-empty base url is used
@pytest.fixture
def jp_base_url():
    return "/a%40b/"


@pytest.fixture
def jp_server_config(jp_base_url):
    return {
        "ServerApp": {
            "base_url": jp_base_url,
        },
    }


async def _login(jp_serverapp, http_server_client, jp_base_url, next):
    # first: request login page with no creds
    login_url = url_path_join(jp_base_url, "login")
    first = await http_server_client.fetch(login_url)
    cookie_header = first.headers["Set-Cookie"]
    cookies = parse_cookie(cookie_header)

    # second, submit login form with credentials
    try:
        resp = await http_server_client.fetch(
            url_concat(login_url, {"next": next}),
            method="POST",
            body=urlencode(
                {
                    "password": jp_serverapp.token,
                    "_xsrf": cookies.get("_xsrf", ""),
                }
            ),
            headers={"Cookie": cookie_header},
            follow_redirects=False,
        )
    except HTTPClientError as e:
        if e.code != 302:
            raise
        return e.response.headers["Location"]
    else:
        assert resp.code == 302, "Should have returned a redirect!"


@pytest.fixture
def login(jp_serverapp, http_server_client, jp_base_url):
    """Fixture to return a function to login to a Jupyter server

    by submitting the login page form
    """
    yield partial(_login, jp_serverapp, http_server_client, jp_base_url)


@pytest.mark.parametrize(
    "bad_next",
    (
        r"\\tree",
        "//some-host",
        "//host{base_url}tree",
        "https://google.com",
        "/absolute/not/base_url",
    ),
)
async def test_next_bad(login, jp_base_url, bad_next):
    bad_next = bad_next.format(base_url=jp_base_url)
    url = await login(bad_next)
    assert url == jp_base_url


@pytest.mark.parametrize(
    "next_path",
    (
        "tree/",
        "//{base_url}tree",
        "notebooks/notebook.ipynb",
        "tree//something",
    ),
)
async def test_next_ok(login, jp_base_url, next_path):
    next_path = next_path.format(base_url=jp_base_url)
    expected = jp_base_url + next_path
    actual = await login(next=expected)
    assert actual == expected
