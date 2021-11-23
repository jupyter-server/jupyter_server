import json
import os
import shutil
import time

import pytest
import tornado
from jupyter_client.ioloop import AsyncIOLoopKernelManager
from nbformat import writes
from nbformat.v4 import new_notebook
from tornado.httpclient import HTTPClientError
from traitlets import default

from ...utils import expected_http_error
from jupyter_server.services.kernels.kernelmanager import AsyncMappingKernelManager
from jupyter_server.utils import url_path_join


j = lambda r: json.loads(r.body.decode())


class NewPortsKernelManager(AsyncIOLoopKernelManager):
    @default("cache_ports")
    def _default_cache_ports(self) -> bool:
        return False

    async def restart_kernel(self, now: bool = False, newports: bool = True, **kw) -> None:
        self.log.debug(f"DEBUG**** calling super().restart_kernel with newports={newports}")
        return await super().restart_kernel(now=now, newports=newports, **kw)


class NewPortsMappingKernelManager(AsyncMappingKernelManager):
    @default("kernel_manager_class")
    def _default_kernel_manager_class(self):
        self.log.debug("NewPortsMappingKernelManager in _default_kernel_manager_class!")
        return "jupyter_server.tests.services.sessions.test_api.NewPortsKernelManager"


@pytest.fixture(
    params=["MappingKernelManager", "AsyncMappingKernelManager", "NewPortsMappingKernelManager"]
)
def jp_argv(request):
    if request.param == "NewPortsMappingKernelManager":
        extra = []
        if hasattr(AsyncMappingKernelManager, "use_pending_kernels"):
            extra = ["--AsyncMappingKernelManager.use_pending_kernels=True"]
        return [
            "--ServerApp.kernel_manager_class=jupyter_server.tests.services.sessions.test_api."
            + request.param
        ] + extra
    return [
        "--ServerApp.kernel_manager_class=jupyter_server.services.kernels.kernelmanager."
        + request.param
    ]


class SessionClient:
    def __init__(self, fetch_callable):
        self.jp_fetch = fetch_callable

    async def _req(self, *args, method, body=None):
        if body is not None:
            body = json.dumps(body)

        r = await self.jp_fetch(
            "api", "sessions", *args, method=method, body=body, allow_nonstandard_methods=True
        )
        return r

    async def list(self):
        return await self._req(method="GET")

    async def get(self, id):
        return await self._req(id, method="GET")

    async def create(self, path, type="notebook", kernel_name=None, kernel_id=None):
        body = {"path": path, "type": type, "kernel": {"name": kernel_name, "id": kernel_id}}
        return await self._req(method="POST", body=body)

    def create_deprecated(self, path):
        body = {"notebook": {"path": path}, "kernel": {"name": "python", "id": "foo"}}
        return self._req(method="POST", body=body)

    def modify_path(self, id, path):
        body = {"path": path}
        return self._req(id, method="PATCH", body=body)

    def modify_path_deprecated(self, id, path):
        body = {"notebook": {"path": path}}
        return self._req(id, method="PATCH", body=body)

    def modify_type(self, id, type):
        body = {"type": type}
        return self._req(id, method="PATCH", body=body)

    def modify_kernel_name(self, id, kernel_name):
        body = {"kernel": {"name": kernel_name}}
        return self._req(id, method="PATCH", body=body)

    def modify_kernel_id(self, id, kernel_id):
        # Also send a dummy name to show that id takes precedence.
        body = {"kernel": {"id": kernel_id, "name": "foo"}}
        return self._req(id, method="PATCH", body=body)

    async def delete(self, id):
        return await self._req(id, method="DELETE")

    async def cleanup(self):
        resp = await self.list()
        sessions = j(resp)
        for session in sessions:
            await self.delete(session["id"])
        time.sleep(0.1)


@pytest.fixture
def session_client(jp_root_dir, jp_fetch):
    subdir = jp_root_dir.joinpath("foo")
    subdir.mkdir()

    # Write a notebook to subdir.
    nb = new_notebook()
    nb_str = writes(nb, version=4)
    nbpath = subdir.joinpath("nb1.ipynb")
    nbpath.write_text(nb_str, encoding="utf-8")

    # Yield a session client
    client = SessionClient(jp_fetch)
    yield client

    # Remove subdir
    shutil.rmtree(str(subdir), ignore_errors=True)


def assert_kernel_equality(actual, expected):
    """Compares kernel models after taking into account that execution_states
    may differ from 'starting' to 'idle'.  The 'actual' argument is the
    current state (which may have an 'idle' status) while the 'expected'
    argument is the previous state (which may have a 'starting' status).
    """
    actual.pop("execution_state", None)
    actual.pop("last_activity", None)
    expected.pop("execution_state", None)
    expected.pop("last_activity", None)
    assert actual == expected


def assert_session_equality(actual, expected):
    """Compares session models.  `actual` is the most current session,
    while `expected` is the target of the comparison.  This order
    matters when comparing the kernel sub-models.
    """
    assert actual["id"] == expected["id"]
    assert actual["path"] == expected["path"]
    assert actual["type"] == expected["type"]
    assert_kernel_equality(actual["kernel"], expected["kernel"])


async def test_create(session_client, jp_base_url, jp_cleanup_subprocesses, jp_serverapp):
    # Make sure no sessions exist.
    resp = await session_client.list()
    sessions = j(resp)
    assert len(sessions) == 0

    # Create a session.
    resp = await session_client.create("foo/nb1.ipynb")
    assert resp.code == 201
    new_session = j(resp)
    assert "id" in new_session
    assert new_session["path"] == "foo/nb1.ipynb"
    assert new_session["type"] == "notebook"
    assert resp.headers["Location"] == url_path_join(
        jp_base_url, "/api/sessions/", new_session["id"]
    )

    # Make sure kernel is in expected state
    kid = new_session["kernel"]["id"]
    kernel = jp_serverapp.kernel_manager.get_kernel(kid)

    if hasattr(kernel, "ready") and os.name != "nt":
        km = jp_serverapp.kernel_manager
        if isinstance(km, AsyncMappingKernelManager):
            assert kernel.ready.done() == (not km.use_pending_kernels)
        else:
            assert kernel.ready.done()

    # Check that the new session appears in list.
    resp = await session_client.list()
    sessions = j(resp)
    assert len(sessions) == 1
    assert_session_equality(sessions[0], new_session)

    # Retrieve that session.
    sid = new_session["id"]
    resp = await session_client.get(sid)
    got = j(resp)
    assert_session_equality(got, new_session)

    # Need to find a better solution to this.
    await session_client.cleanup()
    await jp_cleanup_subprocesses()


async def test_create_bad(
    session_client, jp_base_url, jp_cleanup_subprocesses, jp_serverapp, jp_kernelspecs
):
    if getattr(jp_serverapp.kernel_manager, "use_pending_kernels", False):
        return

    # Make sure no sessions exist.
    jp_serverapp.kernel_manager.default_kernel_name = "bad"
    resp = await session_client.list()
    sessions = j(resp)
    assert len(sessions) == 0

    # Create a session.
    with pytest.raises(HTTPClientError):
        await session_client.create("foo/nb1.ipynb")

    # Need to find a better solution to this.
    await session_client.cleanup()
    await jp_cleanup_subprocesses()


async def test_create_bad_pending(
    session_client, jp_base_url, jp_ws_fetch, jp_cleanup_subprocesses, jp_serverapp, jp_kernelspecs
):
    if not getattr(jp_serverapp.kernel_manager, "use_pending_kernels", False):
        return

    # Make sure no sessions exist.
    jp_serverapp.kernel_manager.default_kernel_name = "bad"
    resp = await session_client.list()
    sessions = j(resp)
    assert len(sessions) == 0

    # Create a session.
    resp = await session_client.create("foo/nb1.ipynb")
    assert resp.code == 201

    # Open a websocket connection.
    kid = j(resp)["kernel"]["id"]
    with pytest.raises(HTTPClientError):
        await jp_ws_fetch("api", "kernels", kid, "channels")

    # Get the updated kernel state
    resp = await session_client.list()
    session = j(resp)[0]
    assert session["kernel"]["execution_state"] == "dead"
    if os.name != "nt":
        assert "non_existent_path" in session["kernel"]["reason"]

    # Need to find a better solution to this.
    await session_client.cleanup()
    await jp_cleanup_subprocesses()


async def test_create_file_session(session_client, jp_cleanup_subprocesses, jp_serverapp):
    resp = await session_client.create("foo/nb1.py", type="file")
    assert resp.code == 201
    newsession = j(resp)
    assert newsession["path"] == "foo/nb1.py"
    assert newsession["type"] == "file"
    await session_client.cleanup()
    await jp_cleanup_subprocesses()


async def test_create_console_session(session_client, jp_cleanup_subprocesses, jp_serverapp):
    resp = await session_client.create("foo/abc123", type="console")
    assert resp.code == 201
    newsession = j(resp)
    assert newsession["path"] == "foo/abc123"
    assert newsession["type"] == "console"
    # Need to find a better solution to this.
    await session_client.cleanup()
    await jp_cleanup_subprocesses()


async def test_create_deprecated(session_client, jp_cleanup_subprocesses, jp_serverapp):
    resp = await session_client.create_deprecated("foo/nb1.ipynb")
    assert resp.code == 201
    newsession = j(resp)
    assert newsession["path"] == "foo/nb1.ipynb"
    assert newsession["type"] == "notebook"
    assert newsession["notebook"]["path"] == "foo/nb1.ipynb"
    # Need to find a better solution to this.
    await session_client.cleanup()
    await jp_cleanup_subprocesses()


async def test_create_with_kernel_id(
    session_client, jp_fetch, jp_base_url, jp_cleanup_subprocesses, jp_serverapp
):
    # create a new kernel
    resp = await jp_fetch("api/kernels", method="POST", allow_nonstandard_methods=True)
    kernel = j(resp)

    resp = await session_client.create("foo/nb1.ipynb", kernel_id=kernel["id"])
    assert resp.code == 201
    new_session = j(resp)
    assert "id" in new_session
    assert new_session["path"] == "foo/nb1.ipynb"
    assert new_session["kernel"]["id"] == kernel["id"]
    assert resp.headers["Location"] == url_path_join(
        jp_base_url, "/api/sessions/{0}".format(new_session["id"])
    )

    resp = await session_client.list()
    sessions = j(resp)
    assert len(sessions) == 1
    assert_session_equality(sessions[0], new_session)

    # Retrieve it
    sid = new_session["id"]
    resp = await session_client.get(sid)
    got = j(resp)
    assert_session_equality(got, new_session)
    # Need to find a better solution to this.
    await session_client.cleanup()
    await jp_cleanup_subprocesses()


async def test_create_with_bad_kernel_id(session_client, jp_cleanup_subprocesses, jp_serverapp):
    resp = await session_client.create("foo/nb1.py", type="file")
    assert resp.code == 201
    newsession = j(resp)
    # TODO
    assert newsession["path"] == "foo/nb1.py"
    assert newsession["type"] == "file"
    await session_client.cleanup()
    await jp_cleanup_subprocesses()


async def test_delete(session_client, jp_cleanup_subprocesses, jp_serverapp):
    resp = await session_client.create("foo/nb1.ipynb")
    newsession = j(resp)
    sid = newsession["id"]

    resp = await session_client.delete(sid)
    assert resp.code == 204

    resp = await session_client.list()
    sessions = j(resp)
    assert sessions == []

    with pytest.raises(tornado.httpclient.HTTPClientError) as e:
        await session_client.get(sid)
    assert expected_http_error(e, 404)
    # Need to find a better solution to this.
    await session_client.cleanup()
    await jp_cleanup_subprocesses()


async def test_modify_path(session_client, jp_cleanup_subprocesses, jp_serverapp):
    resp = await session_client.create("foo/nb1.ipynb")
    newsession = j(resp)
    sid = newsession["id"]

    resp = await session_client.modify_path(sid, "nb2.ipynb")
    changed = j(resp)
    assert changed["id"] == sid
    assert changed["path"] == "nb2.ipynb"
    # Need to find a better solution to this.
    await session_client.cleanup()
    await jp_cleanup_subprocesses()


async def test_modify_path_deprecated(session_client, jp_cleanup_subprocesses, jp_serverapp):
    resp = await session_client.create("foo/nb1.ipynb")
    newsession = j(resp)
    sid = newsession["id"]

    resp = await session_client.modify_path_deprecated(sid, "nb2.ipynb")
    changed = j(resp)
    assert changed["id"] == sid
    assert changed["notebook"]["path"] == "nb2.ipynb"
    # Need to find a better solution to this.
    await session_client.cleanup()
    await jp_cleanup_subprocesses()


async def test_modify_type(session_client, jp_cleanup_subprocesses, jp_serverapp):
    resp = await session_client.create("foo/nb1.ipynb")
    newsession = j(resp)
    sid = newsession["id"]

    resp = await session_client.modify_type(sid, "console")
    changed = j(resp)
    assert changed["id"] == sid
    assert changed["type"] == "console"
    # Need to find a better solution to this.
    await session_client.cleanup()
    await jp_cleanup_subprocesses()


async def test_modify_kernel_name(session_client, jp_fetch, jp_cleanup_subprocesses, jp_serverapp):
    resp = await session_client.create("foo/nb1.ipynb")
    before = j(resp)
    sid = before["id"]

    resp = await session_client.modify_kernel_name(sid, before["kernel"]["name"])
    after = j(resp)
    assert after["id"] == sid
    assert after["path"] == before["path"]
    assert after["type"] == before["type"]
    assert after["kernel"]["id"] != before["kernel"]["id"]

    # check kernel list, to be sure previous kernel was cleaned up
    resp = await jp_fetch("api/kernels", method="GET")
    kernel_list = j(resp)
    after["kernel"].pop("last_activity")
    [k.pop("last_activity") for k in kernel_list]
    if not getattr(jp_serverapp.kernel_manager, "use_pending_kernels", False):
        assert kernel_list == [after["kernel"]]

    # Need to find a better solution to this.
    await session_client.cleanup()
    await jp_cleanup_subprocesses()


async def test_modify_kernel_id(session_client, jp_fetch, jp_cleanup_subprocesses, jp_serverapp):
    resp = await session_client.create("foo/nb1.ipynb")
    before = j(resp)
    sid = before["id"]

    # create a new kernel
    resp = await jp_fetch("api/kernels", method="POST", allow_nonstandard_methods=True)
    kernel = j(resp)

    # Attach our session to the existing kernel
    resp = await session_client.modify_kernel_id(sid, kernel["id"])
    after = j(resp)
    assert after["id"] == sid
    assert after["path"] == before["path"]
    assert after["type"] == before["type"]
    assert after["kernel"]["id"] != before["kernel"]["id"]
    assert after["kernel"]["id"] == kernel["id"]

    # check kernel list, to be sure previous kernel was cleaned up
    resp = await jp_fetch("api/kernels", method="GET")
    kernel_list = j(resp)

    kernel.pop("last_activity")
    [k.pop("last_activity") for k in kernel_list]
    if not getattr(jp_serverapp.kernel_manager, "use_pending_kernels", False):
        assert kernel_list == [kernel]

    # Need to find a better solution to this.
    await session_client.cleanup()
    await jp_cleanup_subprocesses()


async def test_restart_kernel(
    session_client, jp_base_url, jp_fetch, jp_ws_fetch, jp_cleanup_subprocesses
):
    # Create a session.
    resp = await session_client.create("foo/nb1.ipynb")
    assert resp.code == 201
    new_session = j(resp)
    assert "id" in new_session
    assert new_session["path"] == "foo/nb1.ipynb"
    assert new_session["type"] == "notebook"
    assert resp.headers["Location"] == url_path_join(
        jp_base_url, "/api/sessions/", new_session["id"]
    )

    kid = new_session["kernel"]["id"]

    # Get kernel info
    r = await jp_fetch("api", "kernels", kid, method="GET")
    model = json.loads(r.body.decode())
    assert model["connections"] == 0

    # Open a websocket connection.
    ws = await jp_ws_fetch("api", "kernels", kid, "channels")

    # Test that it was opened.
    r = await jp_fetch("api", "kernels", kid, method="GET")
    model = json.loads(r.body.decode())
    assert model["connections"] == 1

    # Restart kernel
    r = await jp_fetch(
        "api", "kernels", kid, "restart", method="POST", allow_nonstandard_methods=True
    )
    restarted_kernel = json.loads(r.body.decode())
    assert restarted_kernel["id"] == kid

    # Close/open websocket
    ws.close()
    # give it some time to close on the other side:
    for i in range(10):
        r = await jp_fetch("api", "kernels", kid, method="GET")
        model = json.loads(r.body.decode())
        if model["connections"] > 0:
            time.sleep(0.1)
        else:
            break

    r = await jp_fetch("api", "kernels", kid, method="GET")
    model = json.loads(r.body.decode())
    assert model["connections"] == 0

    # Open a websocket connection.
    await jp_ws_fetch("api", "kernels", kid, "channels")

    r = await jp_fetch("api", "kernels", kid, method="GET")
    model = json.loads(r.body.decode())
    assert model["connections"] == 1

    # Need to find a better solution to this.
    await session_client.cleanup()
    await jp_cleanup_subprocesses()
