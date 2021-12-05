import asyncio
import json
import os
import platform
import shutil

import pytest
from traitlets.config import Config


@pytest.fixture
def terminal_path(tmp_path):
    subdir = tmp_path.joinpath("terminal_path")
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
                "terminal_manager_class": "jupyter_server.terminal.StatefulTerminalManager",
            }
        }
    )


@pytest.mark.skipif(platform.system().lower() != "linux", reason="Only available on Linux")
async def test_set_idle(jp_fetch, jp_ws_fetch, jp_cleanup_subprocesses, jp_serverapp):
    # disable man sudo_root
    os.system(f"touch {os.path.expanduser('~/.sudo_as_admin_successful')}")

    resp = await jp_fetch(
        "api",
        "terminals",
        method="POST",
        allow_nonstandard_methods=True,
    )
    term = json.loads(resp.body.decode())
    term_1 = term["name"]
    ws = await jp_ws_fetch("terminals", "websocket", term_1)
    setup = ["set_size", 0, 0, 80, 32]
    await ws.write_message(json.dumps(setup))
    while True:
        try:
            await asyncio.wait_for(ws.read_message(), timeout=1)
        except asyncio.TimeoutError:
            break
    sleep_2_msg = ["stdin", "python -c 'import time;time.sleep(2)'\r\n"]
    await ws.write_message(json.dumps(sleep_2_msg))
    await asyncio.sleep(1)
    assert (
        jp_serverapp.web_app.settings["terminal_manager"].terminals[term_1].execution_state
        == "busy"
    )
    await asyncio.sleep(2)
    message_stdout = ""
    while True:
        try:
            message = await asyncio.wait_for(ws.read_message(), timeout=5.0)
        except asyncio.TimeoutError:
            break

        message = json.loads(message)

        if message[0] == "stdout":
            message_stdout += message[1]
    print(message_stdout)
    assert (
        jp_serverapp.web_app.settings["terminal_manager"].terminals[term_1].execution_state
        == "idle"
    )
    await jp_cleanup_subprocesses()


@pytest.mark.skipif(platform.system().lower() != "linux", reason="Only available on Linux")
async def test_set_idle_disconnect(jp_fetch, jp_ws_fetch, jp_cleanup_subprocesses, jp_serverapp):
    # disable man sudo_root
    os.system(f"touch {os.path.expanduser('~/.sudo_as_admin_successful')}")

    resp = await jp_fetch(
        "api",
        "terminals",
        method="POST",
        allow_nonstandard_methods=True,
    )
    term = json.loads(resp.body.decode())
    term_1 = term["name"]
    ws = await jp_ws_fetch("terminals", "websocket", term_1)
    setup = ["set_size", 0, 0, 80, 32]
    await ws.write_message(json.dumps(setup))
    while True:
        try:
            await asyncio.wait_for(ws.read_message(), timeout=1)
        except asyncio.TimeoutError:
            break
    sleep_2_msg = ["stdin", "python -c 'import time;time.sleep(2)'\r\n"]
    await ws.write_message(json.dumps(sleep_2_msg))
    ws.close()
    await asyncio.sleep(1)
    assert (
        jp_serverapp.web_app.settings["terminal_manager"].terminals[term_1].execution_state
        == "busy"
    )
    await asyncio.sleep(2)
    assert not jp_serverapp.web_app.settings["terminal_manager"].terminals[term_1].clients
    assert (
        jp_serverapp.web_app.settings["terminal_manager"].terminals[term_1].execution_state
        == "idle"
    )
    await jp_cleanup_subprocesses()
