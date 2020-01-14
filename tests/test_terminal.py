import shutil
import pytest
import json
import asyncio
import sys


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
        # body=body,
        allow_nonstandard_methods=True,
    )

    resp_list = await fetch(
        'api', 'terminals',
        method='GET',
        # body=body,
        allow_nonstandard_methods=True,
    )

    data = json.loads(resp_list.body.decode())

    assert len(data) == 1


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

    if sys.platform != "win32":
        ws.write_message(json.dumps(['stdin', 'echo %cd%\r\n']))
    else:
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
