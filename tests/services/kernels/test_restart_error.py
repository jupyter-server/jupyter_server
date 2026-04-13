"""Tests for kernel restart error handling in KernelActionHandler.

These tests verify that when a kernel restart fails, the error response
uses Tornado's standard write_error() pipeline (via web.HTTPError) rather
than manually constructing a JSON response. This ensures:
- Consistent JSON error format with Content-Type header
- Proper error structure matching other API endpoints
- Standard logging through the write_error() path
"""

import json

import pytest
from tornado.httpclient import HTTPClientError


@pytest.fixture()
def jp_server_config(jp_server_config):
    return {"KernelManager": {"shutdown_wait_time": 0}}


async def test_restart_success(jp_fetch):
    """Verify normal restart returns 200 with kernel model."""
    r = await jp_fetch("api", "kernels", method="POST", body="{}")
    kernel = json.loads(r.body.decode())
    kernel_id = kernel["id"]

    r = await jp_fetch(
        "api",
        "kernels",
        kernel_id,
        "restart",
        method="POST",
        allow_nonstandard_methods=True,
    )
    assert r.code == 200
    model = json.loads(r.body.decode())
    assert model["id"] == kernel_id


async def test_restart_failure_returns_500_json(jp_fetch, jp_serverapp):
    """When restart_kernel raises, the handler should return a proper
    JSON error response via write_error(), not a manually constructed one."""
    r = await jp_fetch("api", "kernels", method="POST", body="{}")
    kernel = json.loads(r.body.decode())
    kernel_id = kernel["id"]

    # Make restart_kernel fail
    km = jp_serverapp.kernel_manager
    original_restart = km.restart_kernel

    async def failing_restart(*args, **kwargs):
        raise RuntimeError("kernel process died")

    km.restart_kernel = failing_restart
    try:
        with pytest.raises(HTTPClientError) as exc_info:
            await jp_fetch(
                "api",
                "kernels",
                kernel_id,
                "restart",
                method="POST",
                allow_nonstandard_methods=True,
            )

        response = exc_info.value.response
        assert response.code == 500

        # Verify it's a proper JSON response from write_error()
        assert "application/json" in response.headers.get("Content-Type", "")

        body = json.loads(response.body.decode())
        assert "message" in body
        assert "Exception restarting kernel" in body["message"]
        # write_error() includes "reason" field; the old manual write didn't
        assert "reason" in body
    finally:
        km.restart_kernel = original_restart


async def test_interrupt_unaffected(jp_fetch):
    """Verify interrupt still works normally (returns 204)."""
    r = await jp_fetch("api", "kernels", method="POST", body="{}")
    kernel = json.loads(r.body.decode())
    kernel_id = kernel["id"]

    r = await jp_fetch(
        "api",
        "kernels",
        kernel_id,
        "interrupt",
        method="POST",
        allow_nonstandard_methods=True,
    )
    assert r.code == 204
