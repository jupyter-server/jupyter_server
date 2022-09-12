import io
import json
import logging
import pathlib

import pytest
import tornado

from tests.utils import expected_http_error


@pytest.fixture
def event_logger_sink(jp_serverapp):
    event_logger = jp_serverapp.event_logger
    # Register the event schema defined in this directory.
    schema_file = pathlib.Path(__file__).parent / "mock_event.yaml"
    event_logger.register_event_schema(schema_file)
    sink = io.StringIO()
    handler = logging.StreamHandler(sink)
    event_logger.register_handler(handler)
    return event_logger, sink


@pytest.fixture
def event_logger(event_logger_sink):
    event_logger, sink = event_logger_sink
    return event_logger


async def test_subscribe_websocket(event_logger, jp_ws_fetch):
    ws = await jp_ws_fetch("/api/events/subscribe")

    event_logger.emit(
        schema_id="http://event.mock.jupyter.org/message",
        data={"event_message": "Hello, world!"},
    )
    # await event_logger.gather_listeners()
    message = await ws.read_message()
    event_data = json.loads(message)
    ws.close()

    assert event_data.get("event_message") == "Hello, world!"


payload_1 = """\
{
    "schema_id": "http://event.mock.jupyter.org/message",
    "version": 1,
    "data": {
        "event_message": "Hello, world!"
    },
    "timestamp": "2022-05-26T12:50:00+06:00Z"
}
"""

payload_2 = """\
{
    "schema_id": "http://event.mock.jupyter.org/message",
    "version": 1,
    "data": {
        "event_message": "Hello, world!"
    }
}
"""


@pytest.mark.parametrize("payload", [payload_1, payload_2])
async def test_post_event(jp_fetch, event_logger_sink, payload):
    event_logger, sink = event_logger_sink

    r = await jp_fetch("api", "events", method="POST", body=payload)
    assert r.code == 204

    output = sink.getvalue()
    assert output
    input = json.loads(payload)
    data = json.loads(output)
    assert input["data"]["event_message"] == data["event_message"]
    assert data["__timestamp__"]
    if "timestamp" in input:
        assert input["timestamp"] == data["__timestamp__"]


payload_3 = """\
{
    "schema_id": "http://event.mock.jupyter.org/message",
    "data": {
        "event_message": "Hello, world!"
    }
}
"""

payload_4 = """\
{
    "version": 1,
    "data": {
        "event_message": "Hello, world!"
    }
}
"""

payload_5 = """\
{
    "schema_id": "http://event.mock.jupyter.org/message",
    "version": 1
}
"""

payload_6 = """\
{
    "schema_id": "event.mock.jupyter.org/message",
    "version": 1,
    "data": {
        "event_message": "Hello, world!"
    },
    "timestamp": "2022-05-26 12:50:00"
}
"""


@pytest.mark.parametrize("payload", [payload_3, payload_4, payload_5, payload_6])
async def test_post_event_400(jp_fetch, event_logger, payload):
    with pytest.raises(tornado.httpclient.HTTPClientError) as e:
        await jp_fetch("api", "events", method="POST", body=payload)

    expected_http_error(e, 400)


payload_7 = """\
{
    "schema_id": "http://event.mock.jupyter.org/message",
    "version": 1,
    "data": {
        "message": "Hello, world!"
    }
}
"""

payload_8 = """\
{
    "schema_id": "http://event.mock.jupyter.org/message",
    "version": 2,
    "data": {
        "message": "Hello, world!"
    }
}
"""


@pytest.mark.parametrize("payload", [payload_7, payload_8])
async def test_post_event_500(jp_fetch, event_logger, payload):
    with pytest.raises(tornado.httpclient.HTTPClientError) as e:
        await jp_fetch("api", "events", method="POST", body=payload)

    expected_http_error(e, 500)
