import json
import logging
import pathlib
from contextlib import nullcontext

import pytest
import tornado

from tests.utils import expected_http_error


@pytest.fixture
def event_bus(jp_serverapp):
    event_bus = jp_serverapp.event_bus
    # Register the event schema defined in this directory.
    schema_file = pathlib.Path(__file__).parent / "mock_event.yaml"
    event_bus.register_schema_file(schema_file)
    #
    event_bus.allowed_schemas = ["event.mock.jupyter.org/message"]
    event_bus.handlers = [logging.NullHandler()]
    return event_bus


async def test_subscribe_websocket(jp_ws_fetch, event_bus):
    # Open a websocket connection.
    ws = await jp_ws_fetch("/api/events/subscribe")

    event_bus.record_event(
        schema_name="event.mock.jupyter.org/message",
        version=1,
        event={"event_message": "Hello, world!"},
    )
    message = await ws.read_message()
    event_data = json.loads(message)
    # Close websocket
    ws.close()

    assert event_data.get("event_message") == "Hello, world!"


payload_1 = """\
{
    "schema_name": "event.mock.jupyter.com/message",
    "version": 1,
    "event": {
        "event_message": "Hello, world!"
    }
}
"""

payload_2 = """\
{
    "schema_name": "event.mock.jupyter.com/message",
    "event": {
        "event_message": "Hello, world!"
    }
}
"""

payload_3 = """\
{
    "version": 1,
    "event": {
        "event_message": "Hello, world!"
    }
}
"""

payload_4 = """\
{
    "schema_name": "event.mock.jupyter.com/message",
    "version": 1
}
"""


async def test_post_event(jp_fetch, event_bus):
    r = await jp_fetch("api", "events", method="POST", body=payload_1)
    assert r.code == 204


@pytest.mark.parametrize("payload", [payload_2, payload_3, payload_4])
async def test_post_event_400(jp_fetch, event_bus, payload):
    with pytest.raises(tornado.httpclient.HTTPClientError) as e:
        await jp_fetch("api", "events", method="POST", body=payload)

    expected_http_error(e, 400)


payload_5 = """\
{
    "schema_name": "event.mock.jupyter.com/message",
    "version": 1,
    "event": {
        "message": "Hello, world!"
    }
}
"""

payload_6 = """\
{
    "schema_name": "event.mock.jupyter.com/message",
    "version": 2,
    "event": {
        "message": "Hello, world!"
    }
}
"""


@pytest.mark.parametrize("payload", [payload_5, payload_6])
async def test_post_event_500(jp_fetch, event_bus, payload):
    with pytest.raises(tornado.httpclient.HTTPClientError) as e:
        await jp_fetch("api", "events", method="POST", body=payload)

    expected_http_error(e, 500)
