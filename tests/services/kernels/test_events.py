import pytest
from jupyter_client.manager import AsyncKernelManager
from tornado import web

from jupyter_server.services.kernels.kernelmanager import ServerKernelManager

pytest_plugins = ["jupyter_events.pytest_plugin"]


@pytest.mark.parametrize("action", ["start", "restart", "interrupt", "shutdown"])
async def test_kernel_action_success_event(
    monkeypatch, action, jp_read_emitted_events, jp_event_handler
):
    manager = ServerKernelManager()
    manager.event_logger.register_handler(jp_event_handler)

    async def mock_method(self, *args, **kwargs):
        self.kernel_id = "x-x-x-x-x"

    monkeypatch.setattr(AsyncKernelManager, f"{action}_kernel", mock_method)

    await getattr(manager, f"{action}_kernel")()

    output = jp_read_emitted_events()[0]
    assert "action" in output and output["action"] == action
    assert "msg" in output
    assert "kernel_id" in output
    assert "status" in output and output["status"] == "success"


@pytest.mark.parametrize("action", ["start", "restart", "interrupt", "shutdown"])
async def test_kernel_action_failed_event(
    monkeypatch, action, jp_read_emitted_events, jp_event_handler
):
    manager = ServerKernelManager()
    manager.event_logger.register_handler(jp_event_handler)

    async def mock_method(self, *args, **kwargs):
        self.kernel_id = "x-x-x-x-x"
        raise Exception

    monkeypatch.setattr(AsyncKernelManager, f"{action}_kernel", mock_method)

    with pytest.raises(Exception):  # noqa: B017
        await getattr(manager, f"{action}_kernel")()

    output = jp_read_emitted_events()[0]
    assert "action" in output and output["action"] == action
    assert "msg" in output
    assert "kernel_id" in output
    assert "status" in output and output["status"] == "error"


@pytest.mark.parametrize("action", ["start", "restart", "interrupt", "shutdown"])
async def test_kernel_action_http_error_event(
    monkeypatch, action, jp_read_emitted_events, jp_event_handler
):
    manager = ServerKernelManager()
    manager.event_logger.register_handler(jp_event_handler)

    log_message = "This http request failed."

    async def mock_method(self, *args, **kwargs):
        self.kernel_id = "x-x-x-x-x"
        raise web.HTTPError(status_code=500, log_message=log_message)

    monkeypatch.setattr(AsyncKernelManager, f"{action}_kernel", mock_method)

    with pytest.raises(web.HTTPError):
        await getattr(manager, f"{action}_kernel")()

    output = jp_read_emitted_events()[0]
    assert "action" in output and output["action"] == action
    assert "msg" in output and output["msg"] == log_message
    assert "kernel_id" in output
    assert "status" in output and output["status"] == "error"
    assert "status_code" in output and output["status_code"] == 500
