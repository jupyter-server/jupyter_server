import asyncio
import datetime
import json
import os
import platform
import uuid
import warnings

import jupyter_client
import pytest
from tornado.httpclient import HTTPClientError
from traitlets.config import Config

POLL_TIMEOUT = 10
POLL_INTERVAL = 1


async def test_execution_state(jp_fetch, jp_ws_fetch):
    r = await jp_fetch("api", "kernels", method="POST", allow_nonstandard_methods=True)
    kernel = json.loads(r.body.decode())
    kid = kernel["id"]

    # Open a websocket connection.
    ws = await jp_ws_fetch("api", "kernels", kid, "channels")
    await poll_for_execution_state(kid, "idle", jp_fetch)

    session_id = uuid.uuid1().hex
    message_id = uuid.uuid1().hex
    await ws.write_message(
        json.dumps(
            {
                "channel": "shell",
                "header": {
                    "date": datetime.datetime.now(tz=datetime.UTC).isoformat(),
                    "session": session_id,
                    "msg_id": message_id,
                    "msg_type": "execute_request",
                    "username": "",
                    "version": "5.2",
                },
                "parent_header": {},
                "metadata": {},
                "content": {
                    "code": f"import time\ntime.sleep({POLL_TIMEOUT-1})",
                    "silent": False,
                    "allow_stdin": False,
                    "stop_on_error": True,
                },
                "buffers": [],
            }
        )
    )
    await poll_for_execution_state(kid, "busy", jp_fetch)

    message_id_2 = uuid.uuid1().hex
    await ws.write_message(
        json.dumps(
            {
                "channel": "shell",
                "header": {
                    "date": datetime.datetime.now(tz=datetime.UTC).isoformat(),
                    "session": session_id,
                    "msg_id": message_id_2,
                    "msg_type": "execute_request",
                    "username": "",
                    "version": "5.2",
                },
                "parent_header": {},
                "metadata": {},
                "content": {
                    "code": "pass",
                    "silent": False,
                    "allow_stdin": False,
                    "stop_on_error": True,
                },
                "buffers": [],
            }
        )
    )
    await get_idle_reply(kid, message_id_2, ws)
    es = await get_execution_state(kid, jp_fetch)

    # Verify that the overall kernel status is still "busy" even though one
    # "idle" response was already seen for the second execute request.
    assert es == "busy"

    await poll_for_execution_state(kid, "idle", jp_fetch)
    ws.close()


async def get_execution_state(kid, jp_fetch):
    r = await jp_fetch("api", "kernels", kid, method="GET")
    model = json.loads(r.body.decode())
    return model["execution_state"]


async def poll_for_execution_state(kid, target_state, jp_fetch):
    for _ in range(int(POLL_TIMEOUT / POLL_INTERVAL)):
        es = await get_execution_state(kid, jp_fetch)
        if es == target_state:
            return True
        else:
            await asyncio.sleep(POLL_INTERVAL)
    raise AssertionError(f"Timed out waiting for kernel execution state {target_state}")


async def get_idle_reply(kid, parent_message_id, ws):
    while True:
        resp = await ws.read_message()
        resp_json = json.loads(resp)
        parent_message = resp_json.get("parent_header", {}).get("msg_id", None)
        if parent_message != parent_message_id:
            continue

        response_type = resp_json.get("header", {}).get("msg_type", None)
        if response_type != "status":
            continue

        execution_state = resp_json.get("content", {}).get("execution_state", "")
        if execution_state == "idle":
            return
