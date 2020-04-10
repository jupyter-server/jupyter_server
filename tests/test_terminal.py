# Only Run tests on MacOS and Linux
import shutil
import pytest
import json
import asyncio
import sys

# Skip this whole module on Windows. The terminal API leads
# to timeouts on Windows CI.
if sys.platform.startswith('win'):
    pytest.skip("Terminal API tests time out on Windows.", allow_module_level=True)


@pytest.fixture
def terminal_path(tmp_path):
    subdir = tmp_path.joinpath('terminal_path')
    subdir.mkdir()

    yield subdir

    shutil.rmtree(str(subdir), ignore_errors=True)


async def test_terminal_create(fetch):
    await fetch(
        'api', 'terminals',
        method='POST',
        allow_nonstandard_methods=True,
    )

    resp_list = await fetch(
        'api', 'terminals',
        method='GET',
        allow_nonstandard_methods=True,
    )

    data = json.loads(resp_list.body.decode())

    assert len(data) == 1


async def test_terminal_create_with_kwargs(fetch, ws_fetch, terminal_path):
    resp_create = await fetch(
        'api', 'terminals',
        method='POST',
        body=json.dumps({'cwd': str(terminal_path)}),
        allow_nonstandard_methods=True,
    )

    data = json.loads(resp_create.body.decode())
    term_name = data['name']

    resp_get = await fetch(
        'api', 'terminals', term_name,
        method='GET',
        allow_nonstandard_methods=True,
    )

    data = json.loads(resp_get.body.decode())

    assert data['name'] == term_name


async def test_terminal_create_with_cwd(fetch, ws_fetch, terminal_path):
    resp = await fetch(
        'api', 'terminals',
        method='POST',
        body=json.dumps({'cwd': str(terminal_path)}),
        allow_nonstandard_methods=True,
    )

    data = json.loads(resp.body.decode())
    term_name = data['name']

    ws = await ws_fetch(
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
