import json
import pathlib

import pytest


@pytest.fixture
def event_bus(jp_serverapp):
    event_bus = jp_serverapp.event_bus
    event_bus.allowed_schemas = ["event.mockextension.jupyter.com/message"]
    return event_bus


async def test_subscribe_websocket(jp_ws_fetch, jp_fetch, event_bus):
    # Open a websocket connection.
    ws = await jp_ws_fetch("/api/events/subscribe")

    await jp_fetch("/mock/event")
    message = await ws.read_message()
    event_data = json.loads(message)
    # Close websocket
    ws.close()

    assert event_data.get("event_message") == "Hello world, from mock extension!"
