"""Tests for login redirects"""
import json
from functools import partial
from urllib.parse import urlencode

import pytest
from tornado.httpclient import HTTPClientError
from tornado.httputil import parse_cookie, url_concat

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


async def _login(
    jp_serverapp,
    http_server_client,
    jp_base_url,
    login_headers,
    next="/",
    password=None,
    new_password=None,
):
    # first: request login page with no creds
    login_url = url_path_join(jp_base_url, "login")
    first = await http_server_client.fetch(login_url)
    cookie_header = first.headers["Set-Cookie"]
    cookies = parse_cookie(cookie_header)
    form = {"_xsrf": cookies.get("_xsrf")}
    if password is None:
        password = jp_serverapp.identity_provider.token
    if password:
        form["password"] = password
    if new_password:
        form["new_password"] = new_password

    # second, submit login form with credentials
    try:
        resp = await http_server_client.fetch(
            url_concat(login_url, {"next": next}),
            method="POST",
            body=urlencode(form),
            headers={"Cookie": cookie_header},
            follow_redirects=False,
        )
    except HTTPClientError as e:
        if e.code != 302:
            raise
        assert e.response is not None
        resp = e.response
    else:
        assert resp.code == 302, "Should have returned a redirect!"
    return resp


@pytest.fixture
def login_headers():
    """Extra headers to pass to login

    Fixture so it can be overridden
    """
    return {}


@pytest.fixture
def login(jp_serverapp, http_server_client, jp_base_url, login_headers):
    """Fixture to return a function to login to a Jupyter server

    by submitting the login page form
    """
    yield partial(_login, jp_serverapp, http_server_client, jp_base_url, login_headers)


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
    resp = await login(bad_next)
    url = resp.headers["Location"]
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
    resp = await login(next=expected)
    actual = resp.headers["Location"]
    assert actual == expected


async def test_login_cookie(login, jp_serverapp, jp_fetch, login_headers):
    resp = await login()
    assert "Set-Cookie" in resp.headers
    cookie = resp.headers["Set-Cookie"]
    headers = {"Cookie": cookie}
    headers.update(login_headers)
    id_resp = await jp_fetch("/api/me", headers=headers)
    assert id_resp.code == 200
    model = json.loads(id_resp.body.decode("utf8"))
    assert model["identity"]["username"]
    with pytest.raises(HTTPClientError) as exc:
        resp = await login(password="incorrect")
    assert exc.value.code == 401


@pytest.mark.parametrize("allow_password_change", [True, False])
async def test_change_password(login, jp_serverapp, jp_base_url, jp_fetch, allow_password_change):
    new_password = "super-new-pass"
    jp_serverapp.identity_provider.allow_password_change = allow_password_change
    resp = await login(new_password=new_password)

    # second request
    if allow_password_change:
        resp = await login(password=new_password)
        assert resp.code == 302
    else:
        with pytest.raises(HTTPClientError) as exc_info:
            resp = await login(password=new_password)
        assert exc_info.value.code == 401


async def test_logout(jp_serverapp, login, http_server_client, jp_base_url):
    jp_serverapp.identity_provider.cookie_name = "test-cookie"
    expected = jp_base_url
    resp = await login(next=jp_base_url)
    cookie_header = resp.headers["Set-Cookie"]
    cookies = parse_cookie(cookie_header)
    assert cookies.get("test-cookie")

    resp = await http_server_client.fetch(jp_base_url + "logout", headers={"Cookie": cookie_header})
    assert resp.code == 200
    cookie_header = resp.headers["Set-Cookie"]
    cookies = parse_cookie(cookie_header)
    assert cookies.get("test-cookie") == ""
    assert "Successfully logged out" in resp.body.decode("utf8")


async def test_token_cookie_user_id(jp_serverapp, jp_fetch):
    token = jp_serverapp.identity_provider.token

    # first request with token, sets cookie with user-id
    resp = await jp_fetch("/")
    assert resp.code == 200
    set_cookie = resp.headers["set-cookie"]
    headers = {"Cookie": set_cookie}

    # subsequent requests with cookie and no token
    # receive same user-id
    resp = await jp_fetch("/api/me", headers=headers)
    user_id = json.loads(resp.body.decode("utf8"))
    resp = await jp_fetch("/api/me", headers=headers)
    user_id2 = json.loads(resp.body.decode("utf8"))
    assert user_id["identity"] == user_id2["identity"]

    # new request, just token -> new user_id
    resp = await jp_fetch("/api/me")
    user_id3 = json.loads(resp.body.decode("utf8"))
    assert user_id["identity"] != user_id3["identity"]
