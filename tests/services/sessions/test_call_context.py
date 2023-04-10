import asyncio
import time

from jupyter_server.auth.utils import get_anonymous_username
from jupyter_server.base.handlers import JupyterHandler
from jupyter_server.services.kernels.kernelmanager import AsyncMappingKernelManager
from jupyter_server.services.sessions.call_context import CallContext


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

    # Monkeypatch an async method in the mapping kernel manager.
    # We chose a method that takes the kernel_id as as required
    # first argument to ensure the kernel_id is correct in the
    # current context.
    async def shutdown_kernel(self, kernel_id, *args, **kwargs):
        # Get the Jupyter Handler from the current context.
        current: JupyterHandler = CallContext.get(CallContext.JUPYTER_HANDLER)
        # Get the current user
        context_tracker[kernel_id]["user"] = current.current_user
        context_tracker[kernel_id]["started"] = current.current_user
        await asyncio.sleep(1.0)
        # Track the current user a few seconds later. We'll
        # verify that this user was unaffected by other parallel
        # requests.
        context_tracker[kernel_id]["ended"] = current.current_user

    monkeypatch.setattr(AsyncMappingKernelManager, "shutdown_kernel", shutdown_kernel)

    # Make two requests in parallel.
    await asyncio.gather(
        jp_fetch("api", "kernels", kernel1, method="DELETE"),
        jp_fetch("api", "kernels", kernel2, method="DELETE"),
    )

    # Assert that the two requests had different users
    assert context_tracker[kernel1]["user"] != context_tracker[kernel2]["user"]
    # Assert that the first request started+ended with the same user
    assert context_tracker[kernel1]["started"] == context_tracker[kernel1]["ended"]
    # Assert that the second request started+ended with the same user
    assert context_tracker[kernel2]["started"] == context_tracker[kernel2]["ended"]


async def test_context_variable_names():
    CallContext.set("foo", "bar")
    CallContext.set("foo2", "bar2")
    names = CallContext.context_variable_names()
    assert len(names) == 2
    assert set(names) == {"foo", "foo2"}


async def test_same_context_operations():
    CallContext.set("foo", "bar")
    CallContext.set("foo2", "bar2")

    foo = CallContext.get("foo")
    assert foo == "bar"

    CallContext.set("foo", "bar2")
    assert CallContext.get("foo") == CallContext.get("foo2")


async def test_multi_context_operations():
    async def context1():
        """The "slower" context.  This ensures that, following the sleep, the
        context variable set prior to the sleep is still the expected value.
        If contexts are not managed properly, we should find that context2() has
        corrupted context1().
        """
        CallContext.set("foo", "bar1")
        await asyncio.sleep(1.0)
        assert CallContext.get("foo") == "bar1"
        context1_names = CallContext.context_variable_names()
        assert len(context1_names) == 1

    async def context2():
        """The "faster" context.  This ensures that CallContext reflects the
        appropriate values of THIS context.
        """
        CallContext.set("foo", "bar2")
        assert CallContext.get("foo") == "bar2"
        CallContext.set("foo2", "bar2")
        context2_names = CallContext.context_variable_names()
        assert len(context2_names) == 2

    await asyncio.gather(context1(), context2())

    # Assert that THIS context doesn't have any variables defined.
    names = CallContext.context_variable_names()
    assert len(names) == 0
