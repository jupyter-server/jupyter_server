import asyncio

import pytest
from tornado import web
from traitlets import TraitError

from jupyter_server._tz import isoformat, utcnow
from jupyter_server.services.contents.manager import ContentsManager
from jupyter_server.services.kernels.kernelmanager import MappingKernelManager
from jupyter_server.services.sessions.sessionmanager import (
    KernelSessionRecord,
    KernelSessionRecordConflict,
    KernelSessionRecordList,
    SessionManager,
)


class DummyKernel:
    execution_state: str
    last_activity: str

    def __init__(self, kernel_name="python"):
        self.kernel_name = kernel_name


dummy_date = utcnow()
dummy_date_s = isoformat(dummy_date)


class MockMKM(MappingKernelManager):
    """MappingKernelManager interface that doesn't start kernels, for testing"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id_letters = iter("ABCDEFGHIJK")

    def _new_id(self):
        return next(self.id_letters)

    async def start_kernel(self, kernel_id=None, path=None, kernel_name="python", **kwargs):
        kernel_id = kernel_id or self._new_id()
        k = self._kernels[kernel_id] = DummyKernel(kernel_name=kernel_name)
        self._kernel_connections[kernel_id] = 0
        k.last_activity = dummy_date
        k.execution_state = "idle"
        return kernel_id

    async def shutdown_kernel(self, kernel_id, now=False):
        del self._kernels[kernel_id]


class SlowStartingKernelsMKM(MockMKM):
    async def start_kernel(self, kernel_id=None, path=None, kernel_name="python", **kwargs):
        await asyncio.sleep(1.0)
        return await super().start_kernel(
            kernel_id=kernel_id, path=path, kernel_name=kernel_name, **kwargs
        )

    async def shutdown_kernel(self, kernel_id, now=False):
        await asyncio.sleep(1.0)
        await super().shutdown_kernel(kernel_id, now=now)


@pytest.fixture
def session_manager():
    return SessionManager(kernel_manager=MockMKM(), contents_manager=ContentsManager())


def test_kernel_record_equals():
    record1 = KernelSessionRecord(session_id="session1")
    record2 = KernelSessionRecord(session_id="session1", kernel_id="kernel1")
    record3 = KernelSessionRecord(session_id="session2", kernel_id="kernel1")
    record4 = KernelSessionRecord(session_id="session1", kernel_id="kernel2")

    assert record1 == record2
    assert record2 == record3
    assert record3 != record4
    assert record1 != record3
    assert record3 != record4

    with pytest.raises(KernelSessionRecordConflict):
        assert record2 == record4


def test_kernel_record_update():
    record1 = KernelSessionRecord(session_id="session1")
    record2 = KernelSessionRecord(session_id="session1", kernel_id="kernel1")
    record1.update(record2)
    assert record1.kernel_id == "kernel1"

    record1 = KernelSessionRecord(session_id="session1")
    record2 = KernelSessionRecord(kernel_id="kernel1")
    record1.update(record2)
    assert record1.kernel_id == "kernel1"

    record1 = KernelSessionRecord(kernel_id="kernel1")
    record2 = KernelSessionRecord(session_id="session1")
    record1.update(record2)
    assert record1.session_id == "session1"

    record1 = KernelSessionRecord(kernel_id="kernel1")
    record2 = KernelSessionRecord(session_id="session1", kernel_id="kernel1")
    record1.update(record2)
    assert record1.session_id == "session1"

    record1 = KernelSessionRecord(kernel_id="kernel1")
    record2 = KernelSessionRecord(session_id="session1", kernel_id="kernel2")
    with pytest.raises(KernelSessionRecordConflict):
        record1.update(record2)

    record1 = KernelSessionRecord(kernel_id="kernel1", session_id="session1")
    record2 = KernelSessionRecord(kernel_id="kernel2")
    with pytest.raises(KernelSessionRecordConflict):
        record1.update(record2)

    record1 = KernelSessionRecord(kernel_id="kernel1", session_id="session1")
    record2 = KernelSessionRecord(kernel_id="kernel2", session_id="session1")
    with pytest.raises(KernelSessionRecordConflict):
        record1.update(record2)

    record1 = KernelSessionRecord(session_id="session1", kernel_id="kernel1")
    record2 = KernelSessionRecord(session_id="session2", kernel_id="kernel1")
    record1.update(record2)
    assert record1.session_id == "session2"


def test_kernel_record_list():
    records = KernelSessionRecordList()
    r = KernelSessionRecord(kernel_id="kernel1")
    records.update(r)
    assert r in records
    assert "kernel1" in records
    assert len(records) == 1

    # Test .get()
    r_ = records.get(r)
    assert r == r_
    r_ = records.get(r.kernel_id or "")
    assert r == r_

    with pytest.raises(ValueError):
        records.get("badkernel")

    r_update = KernelSessionRecord(kernel_id="kernel1", session_id="session1")
    records.update(r_update)
    assert len(records) == 1
    assert "session1" in records

    r2 = KernelSessionRecord(kernel_id="kernel2")
    records.update(r2)
    assert r2 in records
    assert len(records) == 2

    records.remove(r2)
    assert r2 not in records
    assert len(records) == 1


async def create_multiple_sessions(session_manager, *kwargs_list):
    sessions = []
    for kwargs in kwargs_list:
        kwargs.setdefault("type", "notebook")
        session = await session_manager.create_session(**kwargs)
        sessions.append(session)
    return sessions


async def test_get_session(session_manager):
    session = await session_manager.create_session(
        path="/path/to/test.ipynb", kernel_name="bar", type="notebook"
    )
    session_id = session["id"]
    model = await session_manager.get_session(session_id=session_id)
    expected = {
        "id": session_id,
        "path": "/path/to/test.ipynb",
        "notebook": {"path": "/path/to/test.ipynb", "name": None},
        "type": "notebook",
        "name": None,
        "kernel": {
            "id": "A",
            "name": "bar",
            "connections": 0,
            "last_activity": dummy_date_s,
            "execution_state": "idle",
        },
    }
    assert model == expected


async def test_bad_get_session(session_manager):
    session = await session_manager.create_session(
        path="/path/to/test.ipynb", kernel_name="foo", type="notebook"
    )
    with pytest.raises(TypeError):
        await session_manager.get_session(bad_id=session["id"])


async def test_get_session_dead_kernel(session_manager):
    session = await session_manager.create_session(
        path="/path/to/1/test1.ipynb", kernel_name="python", type="notebook"
    )
    # Kill the kernel
    await session_manager.kernel_manager.shutdown_kernel(session["kernel"]["id"])
    with pytest.raises(web.HTTPError):
        await session_manager.get_session(session_id=session["id"])
    # no session left
    listed = await session_manager.list_sessions()
    assert listed == []


async def test_list_session(session_manager):
    sessions = await create_multiple_sessions(
        session_manager,
        dict(path="/path/to/1/test1.ipynb", kernel_name="python"),
        dict(path="/path/to/2/test2.py", type="file", kernel_name="python"),
        dict(path="/path/to/3", name="foo", type="console", kernel_name="python"),
    )
    sessions = await session_manager.list_sessions()
    expected = [
        {
            "id": sessions[0]["id"],
            "path": "/path/to/1/test1.ipynb",
            "type": "notebook",
            "notebook": {"path": "/path/to/1/test1.ipynb", "name": None},
            "name": None,
            "kernel": {
                "id": "A",
                "name": "python",
                "connections": 0,
                "last_activity": dummy_date_s,
                "execution_state": "idle",
            },
        },
        {
            "id": sessions[1]["id"],
            "path": "/path/to/2/test2.py",
            "type": "file",
            "name": None,
            "kernel": {
                "id": "B",
                "name": "python",
                "connections": 0,
                "last_activity": dummy_date_s,
                "execution_state": "idle",
            },
        },
        {
            "id": sessions[2]["id"],
            "path": "/path/to/3",
            "type": "console",
            "name": "foo",
            "kernel": {
                "id": "C",
                "name": "python",
                "connections": 0,
                "last_activity": dummy_date_s,
                "execution_state": "idle",
            },
        },
    ]
    assert sessions == expected


async def test_list_sessions_dead_kernel(session_manager):
    sessions = await create_multiple_sessions(
        session_manager,
        dict(path="/path/to/1/test1.ipynb", kernel_name="python"),
        dict(path="/path/to/2/test2.ipynb", kernel_name="python"),
    )
    # kill one of the kernels
    await session_manager.kernel_manager.shutdown_kernel(sessions[0]["kernel"]["id"])
    listed = await session_manager.list_sessions()
    expected = [
        {
            "id": sessions[1]["id"],
            "path": "/path/to/2/test2.ipynb",
            "type": "notebook",
            "name": None,
            "notebook": {"path": "/path/to/2/test2.ipynb", "name": None},
            "kernel": {
                "id": "B",
                "name": "python",
                "connections": 0,
                "last_activity": dummy_date_s,
                "execution_state": "idle",
            },
        }
    ]
    assert listed == expected


async def test_update_session(session_manager):
    session = await session_manager.create_session(
        path="/path/to/test.ipynb", kernel_name="julia", type="notebook"
    )
    session_id = session["id"]
    await session_manager.update_session(session_id, path="/path/to/new_name.ipynb")
    model = await session_manager.get_session(session_id=session_id)
    expected = {
        "id": session_id,
        "path": "/path/to/new_name.ipynb",
        "type": "notebook",
        "name": None,
        "notebook": {"path": "/path/to/new_name.ipynb", "name": None},
        "kernel": {
            "id": "A",
            "name": "julia",
            "connections": 0,
            "last_activity": dummy_date_s,
            "execution_state": "idle",
        },
    }
    assert model == expected


async def test_bad_update_session(session_manager):
    # try to update a session with a bad keyword ~ raise error
    session = await session_manager.create_session(
        path="/path/to/test.ipynb", kernel_name="ir", type="notegbook"
    )
    session_id = session["id"]
    with pytest.raises(TypeError):
        await session_manager.update_session(
            session_id=session_id, bad_kw="test.ipynb"
        )  # Bad keyword


async def test_delete_session(session_manager):
    sessions = await create_multiple_sessions(
        session_manager,
        dict(path="/path/to/1/test1.ipynb", kernel_name="python"),
        dict(path="/path/to/2/test2.ipynb", kernel_name="python"),
        dict(path="/path/to/3", name="foo", type="console", kernel_name="python"),
    )
    await session_manager.delete_session(sessions[1]["id"])
    new_sessions = await session_manager.list_sessions()
    expected = [
        {
            "id": sessions[0]["id"],
            "path": "/path/to/1/test1.ipynb",
            "type": "notebook",
            "name": None,
            "notebook": {"path": "/path/to/1/test1.ipynb", "name": None},
            "kernel": {
                "id": "A",
                "name": "python",
                "connections": 0,
                "last_activity": dummy_date_s,
                "execution_state": "idle",
            },
        },
        {
            "id": sessions[2]["id"],
            "type": "console",
            "path": "/path/to/3",
            "name": "foo",
            "kernel": {
                "id": "C",
                "name": "python",
                "connections": 0,
                "last_activity": dummy_date_s,
                "execution_state": "idle",
            },
        },
    ]
    assert new_sessions == expected


async def test_bad_delete_session(session_manager):
    # try to delete a session that doesn't exist ~ raise error
    await session_manager.create_session(
        path="/path/to/test.ipynb", kernel_name="python", type="notebook"
    )
    with pytest.raises(TypeError):
        await session_manager.delete_session(bad_kwarg="23424")  # Bad keyword
    with pytest.raises(web.HTTPError):
        await session_manager.delete_session(session_id="23424")  # nonexistent


async def test_bad_database_filepath(jp_runtime_dir):
    kernel_manager = MockMKM()

    # Try to write to a path that's a directory, not a file.
    path_id_directory = str(jp_runtime_dir)
    # Should raise an error because the path is a directory.
    with pytest.raises(TraitError) as err:
        SessionManager(
            kernel_manager=kernel_manager,
            contents_manager=ContentsManager(),
            database_filepath=str(path_id_directory),
        )

    # Try writing to file that's not a valid SQLite 3 database file.
    non_db_file = jp_runtime_dir.joinpath("non_db_file.db")
    non_db_file.write_bytes(b"this is a bad file")

    # Should raise an error because the file doesn't
    # start with an SQLite database file header.
    with pytest.raises(TraitError) as err:
        SessionManager(
            kernel_manager=kernel_manager,
            contents_manager=ContentsManager(),
            database_filepath=str(non_db_file),
        )


async def test_good_database_filepath(jp_runtime_dir):
    kernel_manager = MockMKM()

    # Try writing to an empty file.
    empty_file = jp_runtime_dir.joinpath("empty.db")
    empty_file.write_bytes(b"")

    session_manager = SessionManager(
        kernel_manager=kernel_manager,
        contents_manager=ContentsManager(),
        database_filepath=str(empty_file),
    )

    await session_manager.create_session(
        path="/path/to/test.ipynb", kernel_name="python", type="notebook"
    )
    # Assert that the database file exists
    assert empty_file.exists()

    # Close the current session manager
    del session_manager

    # Try writing to a file that already exists.
    session_manager = SessionManager(
        kernel_manager=kernel_manager,
        contents_manager=ContentsManager(),
        database_filepath=str(empty_file),
    )

    assert session_manager.database_filepath == str(empty_file)


async def test_session_persistence(jp_runtime_dir):
    session_db_path = jp_runtime_dir.joinpath("test-session.db")
    # Kernel manager needs to persist.
    kernel_manager = MockMKM()

    # Initialize a session and start a connection.
    # This should create the session database the first time.
    session_manager = SessionManager(
        kernel_manager=kernel_manager,
        contents_manager=ContentsManager(),
        database_filepath=str(session_db_path),
    )

    session = await session_manager.create_session(
        path="/path/to/test.ipynb", kernel_name="python", type="notebook"
    )

    # Assert that the database file exists
    assert session_db_path.exists()

    with open(session_db_path, "rb") as f:
        header = f.read(100)

    assert header.startswith(b"SQLite format 3")

    # Close the current session manager
    del session_manager

    # Get a new session_manager
    session_manager = SessionManager(
        kernel_manager=kernel_manager,
        contents_manager=ContentsManager(),
        database_filepath=str(session_db_path),
    )

    # Assert that the session database persists.
    session = await session_manager.get_session(session_id=session["id"])


async def test_pending_kernel():
    session_manager = SessionManager(
        kernel_manager=SlowStartingKernelsMKM(), contents_manager=ContentsManager()
    )
    # Create a session with a slow starting kernel
    fut = session_manager.create_session(
        path="/path/to/test.ipynb", kernel_name="python", type="notebook"
    )
    task = asyncio.create_task(fut)
    await asyncio.sleep(0.1)
    assert len(session_manager._pending_sessions) == 1
    # Get a handle on the record
    record = session_manager._pending_sessions._records[0]
    session = await task
    # Check that record is cleared after the task has completed.
    assert record not in session_manager._pending_sessions

    # Check pending kernel list when sessions are
    fut = session_manager.delete_session(session_id=session["id"])
    task = asyncio.create_task(fut)
    await asyncio.sleep(0.1)
    assert len(session_manager._pending_sessions) == 1
    # Get a handle on the record
    record = session_manager._pending_sessions._records[0]
    session = await task
    # Check that record is cleared after the task has completed.
    assert record not in session_manager._pending_sessions

    # Test multiple, parallel pending kernels
    fut1 = session_manager.create_session(
        path="/path/to/test.ipynb", kernel_name="python", type="notebook"
    )
    fut2 = session_manager.create_session(
        path="/path/to/test.ipynb", kernel_name="python", type="notebook"
    )
    task1 = asyncio.create_task(fut1)
    await asyncio.sleep(0.1)
    task2 = asyncio.create_task(fut2)
    await asyncio.sleep(0.1)
    assert len(session_manager._pending_sessions) == 2

    await task1
    await task2
    session1, session2 = await asyncio.gather(task1, task2)
    assert len(session_manager._pending_sessions) == 0
