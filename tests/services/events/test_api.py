import io
import json
import logging
import pathlib

import pytest
import tornado
from jupyter_telemetry.eventlog import _skip_message
from pythonjsonlogger import jsonlogger

from tests.utils import expected_http_error


@pytest.fixture
def eventbus_sink(jp_serverapp):
    event_bus = jp_serverapp.event_bus
    # Register the event schema defined in this directory.
    schema_file = pathlib.Path(__file__).parent / "mock_event.yaml"
    event_bus.register_schema_file(schema_file)
    event_bus.allowed_schemas = ["event.mock.jupyter.org/message"]

    sink = io.StringIO()
    formatter = jsonlogger.JsonFormatter(json_serializer=_skip_message)
    handler = logging.StreamHandler(sink)
    handler.setFormatter(formatter)
    event_bus.handlers = [handler]
    event_bus.log.addHandler(handler)

    return event_bus, sink


@pytest.fixture
def event_bus(eventbus_sink):
    event_bus, sink = eventbus_sink
    return event_bus


async def test_subscribe_websocket(jp_ws_fetch, event_bus):
    ws = await jp_ws_fetch("/api/events/subscribe")

    event_bus.record_event(
        schema_name="event.mock.jupyter.org/message",
        version=1,
        event={"event_message": "Hello, world!"},
    )
    message = await ws.read_message()
    event_data = json.loads(message)
    ws.close()

    assert event_data.get("event_message") == "Hello, world!"


payload_1 = """\
{
    "schema_name": "event.mock.jupyter.org/message",
    "version": 1,
    "event": {
        "event_message": "Hello, world!"
    },
    "timestamp": "2022-05-26T12:50:00+06:00Z"
}
"""

payload_2 = """\
{
    "schema_name": "event.mock.jupyter.org/message",
    "version": 1,
    "event": {
        "event_message": "Hello, world!"
    }
}
"""


@pytest.mark.parametrize("payload", [payload_1, payload_2])
async def test_post_event(jp_fetch, eventbus_sink, payload):
    event_bus, sink = eventbus_sink

    r = await jp_fetch("api", "events", method="POST", body=payload)
    assert r.code == 204

    output = sink.getvalue()
    assert output
    input = json.loads(payload)
    data = json.loads(output)
    assert input["event"]["event_message"] == data["event_message"]
    assert data["__timestamp__"]
    if "timestamp" in input:
        assert input["timestamp"] == data["__timestamp__"]


payload_3 = """\
{
    "schema_name": "event.mock.jupyter.org/message",
    "event": {
        "event_message": "Hello, world!"
    }
}
"""

payload_4 = """\
{
    "version": 1,
    "event": {
        "event_message": "Hello, world!"
    }
}
"""

payload_5 = """\
{
    "schema_name": "event.mock.jupyter.org/message",
    "version": 1
}
"""

payload_6 = """\
{
    "schema_name": "event.mock.jupyter.org/message",
    "version": 1,
    "event": {
        "event_message": "Hello, world!"
    },
    "timestamp": "2022-05-26 12:50:00"
}
"""


@pytest.mark.parametrize("payload", [payload_3, payload_4, payload_5, payload_6])
async def test_post_event_400(jp_fetch, event_bus, payload):
    with pytest.raises(tornado.httpclient.HTTPClientError) as e:
        await jp_fetch("api", "events", method="POST", body=payload)

    expected_http_error(e, 400)


payload_7 = """\
{
    "schema_name": "event.mock.jupyter.org/message",
    "version": 1,
    "event": {
        "message": "Hello, world!"
    }
}
"""

payload_8 = """\
{
    "schema_name": "event.mock.jupyter.org/message",
    "version": 2,
    "event": {
        "message": "Hello, world!"
    }
}
"""


@pytest.mark.parametrize("payload", [payload_7, payload_8])
async def test_post_event_500(jp_fetch, event_bus, payload):
    with pytest.raises(tornado.httpclient.HTTPClientError) as e:
        await jp_fetch("api", "events", method="POST", body=payload)

    expected_http_error(e, 500)
