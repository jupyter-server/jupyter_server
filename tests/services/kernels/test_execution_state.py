import asyncio
import datetime
import json
import os
import platform
import time
import uuid
import warnings

import jupyter_client
import pytest
from flaky import flaky
from tornado.httpclient import HTTPClientError
from traitlets.config import Config

MAX_POLL_ATTEMPTS = 10
POLL_INTERVAL = 1
MINIMUM_CONSISTENT_COUNT = 4


@flaky
async def test_execution_state(jp_fetch, jp_ws_fetch):
    r = await jp_fetch("api", "kernels", method="POST", allow_nonstandard_methods=True)
    kernel = json.loads(r.body.decode())
    kid = kernel["id"]

    # Open a websocket connection.
    ws = await jp_ws_fetch("api", "kernels", kid, "channels")
    session_id = uuid.uuid1().hex
    message_id = uuid.uuid1().hex
    await ws.write_message(
        json.dumps(
            {
                "channel": "shell",
                "header": {
                    "date": datetime.datetime.now(tz=datetime.timezone.utc).isoformat(),
                    "session": session_id,
                    "msg_id": message_id,
                    "msg_type": "execute_request",
                    "username": "",
                    "version": "5.2",
                },
                "parent_header": {},
                "metadata": {},
                "content": {
                    "code": "while True:\n\tpass",
                    "silent": False,
                    "allow_stdin": False,
                    "stop_on_error": True,
                },
                "buffers": [],
            }
        )
    )
    await poll_for_parent_message_status(kid, message_id, "busy", ws)
    es = await get_execution_state(kid, jp_fetch)
    assert es == "busy"

    message_id_2 = uuid.uuid1().hex
    await ws.write_message(
        json.dumps(
            {
                "channel": "control",
                "header": {
                    "date": datetime.datetime.now(tz=datetime.timezone.utc).isoformat(),
                    "session": session_id,
                    "msg_id": message_id_2,
                    "msg_type": "debug_request",
                    "username": "",
                    "version": "5.2",
                },
                "parent_header": {},
                "metadata": {},
                "content": {
                    "type": "request",
                    "command": "debugInfo",
                },
                "buffers": [],
            }
        )
    )
    await poll_for_parent_message_status(kid, message_id_2, "idle", ws)
    es = await get_execution_state(kid, jp_fetch)

    # Verify that the overall kernel status is still "busy" even though one
    # "idle" response was already seen for the second execute request.
    assert es == "busy"

    await jp_fetch(
        "api",
        "kernels",
        kid,
        "interrupt",
        method="POST",
        allow_nonstandard_methods=True,
    )

    await poll_for_parent_message_status(kid, message_id, "idle", ws)
    es = await get_execution_state(kid, jp_fetch)
    assert es == "idle"
    ws.close()


async def get_execution_state(kid, jp_fetch):
    # There is an inherent race condition when getting the kernel execution status
    # where we might fetch the status right before an expected state change occurs.
    #
    # To work-around this, we don't return the status until we've been able to fetch
    # it twice in a row and get the same result both times.
    last_execution_states = []

    for _ in range(MAX_POLL_ATTEMPTS):
        r = await jp_fetch("api", "kernels", kid, method="GET")
        model = json.loads(r.body.decode())
        execution_state = model["execution_state"]
        last_execution_states.append(execution_state)
        consistent_count = 0
        last_execution_state = None
        for es in last_execution_states:
            if es != last_execution_state:
                consistent_count = 0
                last_execution_state = es
            consistent_count += 1
            if consistent_count >= MINIMUM_CONSISTENT_COUNT:
                return es
        time.sleep(POLL_INTERVAL)

    raise AssertionError("failed to get a consistent execution state")


async def poll_for_parent_message_status(kid, parent_message_id, target_status, ws):
    while True:
        resp = await ws.read_message()
        resp_json = json.loads(resp)
        print(resp_json)
        parent_message = resp_json.get("parent_header", {}).get("msg_id", None)
        if parent_message != parent_message_id:
            continue

        response_type = resp_json.get("header", {}).get("msg_type", None)
        if response_type != "status":
            continue

        execution_state = resp_json.get("content", {}).get("execution_state", "")
        if execution_state == target_status:
            return
