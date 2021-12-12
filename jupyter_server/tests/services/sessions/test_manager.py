import pytest
from tornado import web
from traitlets import TraitError

from jupyter_server._tz import isoformat
from jupyter_server._tz import utcnow
from jupyter_server.services.contents.manager import ContentsManager
from jupyter_server.services.kernels.kernelmanager import MappingKernelManager
from jupyter_server.services.sessions.sessionmanager import SessionManager


class DummyKernel(object):
    def __init__(self, kernel_name="python"):
        self.kernel_name = kernel_name


dummy_date = utcnow()
dummy_date_s = isoformat(dummy_date)


class DummyMKM(MappingKernelManager):
    """MappingKernelManager interface that doesn't start kernels, for testing"""

    def __init__(self, *args, **kwargs):
        super(DummyMKM, self).__init__(*args, **kwargs)
        self.id_letters = iter(u"ABCDEFGHIJK")

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


@pytest.fixture
def session_manager():
    return SessionManager(kernel_manager=DummyMKM(), contents_manager=ContentsManager())


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
        "path": u"/path/to/test.ipynb",
        "notebook": {"path": u"/path/to/test.ipynb", "name": None},
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
            "path": u"/path/to/1/test1.ipynb",
            "type": "notebook",
            "notebook": {"path": u"/path/to/1/test1.ipynb", "name": None},
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
            "path": u"/path/to/2/test2.py",
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
            "path": u"/path/to/3",
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
            "path": u"/path/to/2/test2.ipynb",
            "type": "notebook",
            "name": None,
            "notebook": {"path": u"/path/to/2/test2.ipynb", "name": None},
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
        "path": u"/path/to/new_name.ipynb",
        "type": "notebook",
        "name": None,
        "notebook": {"path": u"/path/to/new_name.ipynb", "name": None},
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
            "path": u"/path/to/1/test1.ipynb",
            "type": "notebook",
            "name": None,
            "notebook": {"path": u"/path/to/1/test1.ipynb", "name": None},
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
            "path": u"/path/to/3",
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
    kernel_manager = DummyMKM()

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
    kernel_manager = DummyMKM()

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
    kernel_manager = DummyMKM()

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
