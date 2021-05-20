import sys
import pytest

# Skip this module if on Windows. Unix sockets are not available on Windows.
pytestmark = pytest.mark.skipif(
    sys.platform.startswith('win'),
    reason="Unix sockets are not available on Windows."
)

import os
import urllib
import pathlib

if not sys.platform.startswith('win'):
    from tornado.netutil import bind_unix_socket

from tornado.escape import url_escape

import jupyter_server.serverapp
from jupyter_server import DEFAULT_JUPYTER_SERVER_PORT
from jupyter_server.utils import (
    url_path_join,
    urlencode_unix_socket,
    async_fetch,
)


@pytest.fixture
def jp_server_config(jp_unix_socket_file):
    """Configure the serverapp fixture with the unix socket."""
    return {
        "ServerApp": {
            "sock" : jp_unix_socket_file,
            "allow_remote_access": True
        }
    }


@pytest.fixture
def http_server_port(jp_unix_socket_file, jp_process_id):
    """Unix socket and process ID used by tornado's HTTP Server.

    Overrides the http_server_port fixture from pytest-tornasync and replaces
    it with a tuple: (unix socket, process id)
    """
    return (bind_unix_socket(jp_unix_socket_file), jp_process_id)


@pytest.fixture
def jp_unix_socket_fetch(jp_unix_socket_file, jp_auth_header, jp_base_url, http_server, io_loop):
    """A fetch fixture for Jupyter Server tests that use the unix_serverapp fixture"""
    async def client(*parts, headers={}, params={}, **kwargs):
        # Handle URL strings
        host_url = urlencode_unix_socket(jp_unix_socket_file)
        path_url = url_path_join(jp_base_url, *parts)
        params_url = urllib.parse.urlencode(params)
        url = url_path_join(host_url, path_url+ "?" + params_url)
        r = await async_fetch(url, headers=headers, io_loop=io_loop, **kwargs)
        return r
    return client


async def test_get_spec(jp_unix_socket_fetch):
    # Handle URL strings
    parts = ["api", "spec.yaml"]

    # Make request and verify it succeeds.'
    response = await jp_unix_socket_fetch(*parts)
    assert response.code == 200
    assert response.body != None


async def test_list_running_servers(jp_unix_socket_file, http_server):
    """Test that a server running on unix sockets is discovered by the server list"""
    servers = list(jupyter_server.serverapp.list_running_servers())
    assert len(servers) >= 1
    assert jp_unix_socket_file in {info['sock'] for info in servers}
