"""A mock extension named `mock1` for testing purposes."""

# by the test functions.
import asyncio


def _jupyter_server_extension_paths():
    return [{"module": "tests.extension.mockextensions.mock1"}]


def _load_jupyter_server_extension(serverapp):
    serverapp.mockI = True
    serverapp.mock_shared = "I"


async def _start_jupyter_server_extension(serverapp):
    await asyncio.sleep(0.1)
    serverapp.mock1_started = True
