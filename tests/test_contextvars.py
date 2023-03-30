import asyncio
import time

from jupyter_server.auth.utils import get_anonymous_username
from jupyter_server.base.handlers import CURRENT_JUPYTER_HANDLER, JupyterHandler
from jupyter_server.services.kernels.kernelmanager import AsyncMappingKernelManager


async def test_jupyter_handler_contextvar(jp_fetch, monkeypatch):
    # Create some mock kernel Ids
    kernel1 = "x-x-x-x-x"
    kernel2 = "y-y-y-y-y"

    # We'll use this dictionary to track the current user within each request.
    context_tracker = {
        kernel1: {"started": "no user yet", "ended": "still no user", "user": None},
        kernel2: {"started": "no user yet", "ended": "still no user", "user": None},
    }

    # Monkeypatch the get_current_user method in Tornado's
    # request handler to return a random user name for
    # each request
    async def get_current_user(self):
        return get_anonymous_username()

    monkeypatch.setattr(JupyterHandler, "get_current_user", get_current_user)

    # Monkeypatch the kernel_model method to show that
    # the current context variable is truly local and
    # not contaminated by other asynchronous parallel requests.
    def kernel_model(self, kernel_id):
        # Get the Jupyter Handler from the current context.
        current: JupyterHandler = CURRENT_JUPYTER_HANDLER.get()
        # Get the current user
        context_tracker[kernel_id]["user"] = current.current_user
        context_tracker[kernel_id]["started"] = current.current_user
        time.sleep(2.0)
        # Track the current user a few seconds later. We'll
        # verify that this user was unaffected by other parallel
        # requests.
        context_tracker[kernel_id]["ended"] = current.current_user
        return {"id": kernel_id, "name": "blah"}

    monkeypatch.setattr(AsyncMappingKernelManager, "kernel_model", kernel_model)

    # Make two requests in parallel.
    await asyncio.gather(jp_fetch("api", "kernels", kernel1), jp_fetch("api", "kernels", kernel2))

    # Assert that the two requests had different users
    assert context_tracker[kernel1]["user"] != context_tracker[kernel2]["user"]
    # Assert that the first request started+ended with the same user
    assert context_tracker[kernel1]["started"] == context_tracker[kernel1]["ended"]
    # Assert that the second request started+ended with the same user
    assert context_tracker[kernel2]["started"] == context_tracker[kernel2]["ended"]
