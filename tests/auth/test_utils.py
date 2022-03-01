import pytest

from jupyter_server.auth.utils import match_url_to_resource


@pytest.mark.parametrize(
    "url,expected_resource",
    [
        ("/api/kernels", "kernels"),
        ("/api/kernelspecs", "kernelspecs"),
        ("/api/contents", "contents"),
        ("/api/sessions", "sessions"),
        ("/api/terminals", "terminals"),
        ("/api/nbconvert", "nbconvert"),
        ("/api/config/x", "config"),
        ("/api/shutdown", "server"),
        ("/nbconvert/py", "nbconvert"),
    ],
)
def test_match_url_to_resource(url, expected_resource):
    resource = match_url_to_resource(url)
    assert resource == expected_resource


@pytest.mark.parametrize(
    "url",
    [
        "/made/up/url",
        # Misspell.
        "/api/kernel",
        # Not a resource
        "/tree",
    ],
)
def test_bad_match_url_to_resource(url):
    resource = match_url_to_resource(url)
    assert resource is None
