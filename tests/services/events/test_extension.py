import json

import pytest


@pytest.fixture
def jp_server_config():
    config = {
        "ServerApp": {
            "jpserver_extensions": {"tests.services.events.mockextension": True},
        },
        "EventBus": {"allowed_schemas": ["http://event.mockextension.jupyter.org/message"]},
    }
    return config


async def test_subscribe_websocket(jp_ws_fetch, jp_fetch):
    # Open an event listener websocket
    ws = await jp_ws_fetch("/api/events/subscribe")

    # Hit the extension endpoint that emits an event
    await jp_fetch("/mock/event")

    # Check the event listener for a message
    message = await ws.read_message()
    event_data = json.loads(message)

    # Close websocket
    ws.close()

    # Verify that an event message was received.
    assert event_data.get("event_message") == "Hello world, from mock extension!"
