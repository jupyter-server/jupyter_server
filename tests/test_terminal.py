import asyncio
import json
import os
import shlex
import shutil
import sys

import pytest
from tornado.httpclient import HTTPClientError
from traitlets.config import Config

from jupyter_server._tz import isoformat


@pytest.fixture
def terminal_path(tmp_path):
    subdir = tmp_path.joinpath("terminal_path")
    subdir.mkdir()

    yield subdir

    shutil.rmtree(str(subdir), ignore_errors=True)


@pytest.fixture
def terminal_root_dir(jp_root_dir):
    subdir = jp_root_dir.joinpath("terminal_path")
    subdir.mkdir()

    yield subdir

    shutil.rmtree(str(subdir), ignore_errors=True)


CULL_TIMEOUT = 10
CULL_INTERVAL = 3


@pytest.fixture
def jp_server_config():
    return Config(
        {
            "ServerApp": {
                "TerminalManager": {
                    "cull_inactive_timeout": CULL_TIMEOUT,
                    "cull_interval": CULL_INTERVAL,
                }
            }
        }
    )


@pytest.fixture
def jp_argv():
    """Allows tests to setup specific argv values."""
    return ["--ServerApp.jpserver_extensions", "jupyter_server_terminals=True"]


async def test_no_terminals(jp_fetch):
    resp_list = await jp_fetch(
        "api",
        "terminals",
        method="GET",
        allow_nonstandard_methods=True,
    )

    data = json.loads(resp_list.body.decode())

    assert len(data) == 0


async def test_terminal_create(jp_fetch, jp_serverapp):
    resp = await jp_fetch(
        "api",
        "terminals",
        method="POST",
        allow_nonstandard_methods=True,
    )
    term = json.loads(resp.body.decode())
    assert term["name"] == "1"

    resp_list = await jp_fetch(
        "api",
        "terminals",
        method="GET",
        allow_nonstandard_methods=True,
    )

    data = json.loads(resp_list.body.decode())

    assert len(data) == 1
    assert data[0]["name"] == term["name"]


async def test_terminal_create_with_kwargs(jp_fetch, jp_ws_fetch, terminal_path):
    resp_create = await jp_fetch(
        "api",
        "terminals",
        method="POST",
        body=json.dumps({"cwd": str(terminal_path)}),
        allow_nonstandard_methods=True,
    )

    data = json.loads(resp_create.body.decode())
    term_name = data["name"]

    resp_get = await jp_fetch(
        "api",
        "terminals",
        term_name,
        method="GET",
        allow_nonstandard_methods=True,
    )

    data = json.loads(resp_get.body.decode())

    assert data["name"] == term_name


async def test_terminal_create_with_cwd(jp_fetch, jp_ws_fetch, terminal_path, jp_serverapp):
    resp = await jp_fetch(
        "api",
        "terminals",
        method="POST",
        body=json.dumps({"cwd": str(terminal_path)}),
        allow_nonstandard_methods=True,
    )

    data = json.loads(resp.body.decode())
    term_name = data["name"]

    ws = await jp_ws_fetch("terminals", "websocket", term_name)

    ws.write_message(json.dumps(["stdin", "pwd\r\n"]))

    message_stdout = ""
    while True:
        try:
            message = await asyncio.wait_for(ws.read_message(), timeout=5.0)
        except asyncio.TimeoutError:
            break

        message = json.loads(message)

        if message[0] == "stdout":
            message_stdout += message[1]

    ws.close()

    assert os.path.basename(terminal_path) in message_stdout

    resp = await jp_fetch("api", "status")
    data = json.loads(resp.body.decode())
    assert data["last_activity"] == isoformat(
        jp_serverapp.web_app.settings["terminal_last_activity"]
    )


@pytest.mark.skip(reason="Not yet working")
async def test_terminal_create_with_relative_cwd(
    jp_fetch, jp_ws_fetch, jp_root_dir, terminal_root_dir
):
    resp = await jp_fetch(
        "api",
        "terminals",
        method="POST",
        body=json.dumps({"cwd": str(terminal_root_dir.relative_to(jp_root_dir))}),
        allow_nonstandard_methods=True,
    )

    data = json.loads(resp.body.decode())
    term_name = data["name"]

    ws = await jp_ws_fetch("terminals", "websocket", term_name)

    ws.write_message(json.dumps(["stdin", "pwd\r\n"]))

    message_stdout = ""
    while True:
        try:
            message = await asyncio.wait_for(ws.read_message(), timeout=5.0)
        except asyncio.TimeoutError:
            break

        message = json.loads(message)

        if message[0] == "stdout":
            message_stdout += message[1]

    ws.close()

    expected = terminal_root_dir.name if sys.platform == "win32" else str(terminal_root_dir)
    assert expected in message_stdout


@pytest.mark.skip(reason="Not yet working")
async def test_terminal_create_with_bad_cwd(jp_fetch, jp_ws_fetch):
    non_existing_path = "/tmp/path/to/nowhere"
    resp = await jp_fetch(
        "api",
        "terminals",
        method="POST",
        body=json.dumps({"cwd": non_existing_path}),
        allow_nonstandard_methods=True,
    )

    data = json.loads(resp.body.decode())
    term_name = data["name"]

    ws = await jp_ws_fetch("terminals", "websocket", term_name)

    ws.write_message(json.dumps(["stdin", "pwd\r\n"]))

    message_stdout = ""
    while True:
        try:
            message = await asyncio.wait_for(ws.read_message(), timeout=5.0)
        except asyncio.TimeoutError:
            break

        message = json.loads(message)

        if message[0] == "stdout":
            message_stdout += message[1]

    ws.close()

    assert non_existing_path not in message_stdout


def test_culling_config(jp_server_config, jp_configurable_serverapp):
    app = jp_configurable_serverapp()
    terminal_mgr_config = app.config.ServerApp.TerminalManager
    assert terminal_mgr_config.cull_inactive_timeout == CULL_TIMEOUT
    assert terminal_mgr_config.cull_interval == CULL_INTERVAL
    app = jp_configurable_serverapp()
    terminal_mgr_settings = app.web_app.settings["terminal_manager"]
    assert terminal_mgr_settings.cull_inactive_timeout == CULL_TIMEOUT
    assert terminal_mgr_settings.cull_interval == CULL_INTERVAL


async def test_culling(jp_server_config, jp_fetch):
    # POST request
    resp = await jp_fetch(
        "api",
        "terminals",
        method="POST",
        allow_nonstandard_methods=True,
    )
    term = json.loads(resp.body.decode())
    term_1 = term["name"]
    last_activity = term["last_activity"]

    culled = False
    for _ in range(CULL_TIMEOUT + CULL_INTERVAL):
        try:
            resp = await jp_fetch(
                "api",
                "terminals",
                term_1,
                method="GET",
                allow_nonstandard_methods=True,
            )
        except HTTPClientError as e:
            assert e.code == 404
            culled = True
            break
        else:
            await asyncio.sleep(1)

    assert culled


@pytest.mark.parametrize(
    "terminado_settings,expected_shell,min_traitlets",
    [
        ("shell_command=\"['/path/to/shell', '-l']\"", ["/path/to/shell", "-l"], "5.4"),
        ('shell_command="/string/path/to/shell -l"', ["/string/path/to/shell", "-l"], "5.1"),
    ],
)
def test_shell_command_override(
    terminado_settings, expected_shell, min_traitlets, jp_configurable_serverapp
):
    pytest.importorskip("traitlets", minversion=min_traitlets)
    argv = shlex.split(f"--ServerApp.terminado_settings={terminado_settings}")
    app = jp_configurable_serverapp(argv=argv)
    assert app.web_app.settings["terminal_manager"].shell_command == expected_shell
