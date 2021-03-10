# Only Run tests on MacOS and Linux
import shutil
import pytest
import json
import asyncio
import sys

from tornado.httpclient import HTTPClientError
from traitlets.config import Config

# Skip this whole module on Windows. The terminal API leads
# to timeouts on Windows CI.
if sys.platform.startswith('win'):
    pytest.skip("Terminal API tests time out on Windows.", allow_module_level=True)


# Kill all running terminals after each test to avoid cross-test issues
# with still running terminals.
@pytest.fixture
def kill_all(jp_serverapp):
    async def _():
        await jp_serverapp.web_app.settings["terminal_manager"].kill_all()
    return _


@pytest.fixture
def terminal_path(tmp_path):
    subdir = tmp_path.joinpath('terminal_path')
    subdir.mkdir()

    yield subdir

    shutil.rmtree(str(subdir), ignore_errors=True)


CULL_TIMEOUT = 2
CULL_INTERVAL = 3


@pytest.fixture
def jp_server_config():
    return Config({
        'ServerApp': {
            'TerminalManager': {
                'cull_inactive_timeout': CULL_TIMEOUT,
                'cull_interval': CULL_INTERVAL
            }
        }
    })


async def test_no_terminals(jp_fetch):
    resp_list = await jp_fetch(
        'api', 'terminals',
        method='GET',
        allow_nonstandard_methods=True,
    )

    data = json.loads(resp_list.body.decode())

    assert len(data) == 0


async def test_terminal_create(jp_fetch, kill_all):
    resp = await jp_fetch(
        'api', 'terminals',
        method='POST',
        allow_nonstandard_methods=True,
    )
    term = json.loads(resp.body.decode())
    assert term['name'] == "1"

    resp_list = await jp_fetch(
        'api', 'terminals',
        method='GET',
        allow_nonstandard_methods=True,
    )

    data = json.loads(resp_list.body.decode())

    assert len(data) == 1
    assert data[0] == term
    await kill_all()


async def test_terminal_create_with_kwargs(jp_fetch, jp_ws_fetch, terminal_path, kill_all):
    resp_create = await jp_fetch(
        'api', 'terminals',
        method='POST',
        body=json.dumps({'cwd': str(terminal_path)}),
        allow_nonstandard_methods=True,
    )

    data = json.loads(resp_create.body.decode())
    term_name = data['name']

    resp_get = await jp_fetch(
        'api', 'terminals', term_name,
        method='GET',
        allow_nonstandard_methods=True,
    )

    data = json.loads(resp_get.body.decode())

    assert data['name'] == term_name
    await kill_all()


async def test_terminal_create_with_cwd(jp_fetch, jp_ws_fetch, terminal_path):
    resp = await jp_fetch(
        'api', 'terminals',
        method='POST',
        body=json.dumps({'cwd': str(terminal_path)}),
        allow_nonstandard_methods=True,
    )

    data = json.loads(resp.body.decode())
    term_name = data['name']

    ws = await jp_ws_fetch(
        'terminals', 'websocket', term_name
    )

    ws.write_message(json.dumps(['stdin', 'pwd\r\n']))

    message_stdout = ''
    while True:
        try:
            message = await asyncio.wait_for(ws.read_message(), timeout=1.0)
        except asyncio.TimeoutError:
            break

        message = json.loads(message)

        if message[0] == 'stdout':
            message_stdout += message[1]

    ws.close()

    assert str(terminal_path) in message_stdout


async def test_culling_config(jp_server_config, jp_configurable_serverapp):
    terminal_mgr_config = jp_configurable_serverapp().config.ServerApp.TerminalManager
    assert terminal_mgr_config.cull_inactive_timeout == CULL_TIMEOUT
    assert terminal_mgr_config.cull_interval == CULL_INTERVAL
    terminal_mgr_settings = jp_configurable_serverapp().web_app.settings['terminal_manager']
    assert terminal_mgr_settings.cull_inactive_timeout == CULL_TIMEOUT
    assert terminal_mgr_settings.cull_interval == CULL_INTERVAL


async def test_culling(jp_server_config, jp_fetch):
    # POST request
    resp = await jp_fetch(
        'api', 'terminals',
        method='POST',
        allow_nonstandard_methods=True,
    )
    term = json.loads(resp.body.decode())
    term_1 = term['name']
    last_activity = term['last_activity']

    culled = False
    for i in range(10):  # Culling should occur in a few seconds
        try:
            resp = await jp_fetch(
                'api', 'terminals', term_1,
                method='GET',
                allow_nonstandard_methods=True,
            )
        except HTTPClientError as e:
            assert e.code == 404
            culled = True
            break
        else:
            await asyncio.sleep(1)

    assert culled
