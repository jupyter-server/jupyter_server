import json
import pathlib

import pytest


@pytest.fixture
def event_bus(jp_serverapp):
    event_bus = jp_serverapp.event_bus
    # Register the event schema defined in this directory.
    schema_file = pathlib.Path(__file__).parent / "mock_event.yaml"
    event_bus.register_schema_file(schema_file)
    #
    event_bus.allowed_schemas = ["event.mock.jupyter.org/message"]
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
