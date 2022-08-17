import os
import shutil
from pathlib import Path

import pytest
from traitlets import TraitError

from jupyter_server.services.contents.fileidmanager import FileIdManager


@pytest.fixture
def test_path(jp_root_dir):
    path = os.path.join(jp_root_dir, "test_path")
    os.mkdir(path)
    return path


@pytest.fixture
def test_path_child(test_path):
    path = os.path.join(test_path, "child")
    Path(path).touch()
    return path


@pytest.fixture
def old_path(jp_root_dir):
    """Fixture for source path to be moved/copied via FID manager"""
    path = os.path.join(jp_root_dir, "old_path")
    os.mkdir(path)
    return path


@pytest.fixture
def old_path_child(old_path):
    path = os.path.join(old_path, "child")
    os.mkdir(path)
    return path


@pytest.fixture
def old_path_grandchild(old_path_child):
    path = os.path.join(old_path_child, "grandchild")
    os.mkdir(path)
    return path


@pytest.fixture
def new_path(jp_root_dir):
    """Fixture for destination path for a FID manager move/copy operation"""
    return os.path.join(jp_root_dir, "new_path")


@pytest.fixture
def new_path_child(new_path):
    return os.path.join(new_path, "child")


@pytest.fixture
def new_path_grandchild(new_path_child):
    return os.path.join(new_path_child, "grandchild")


def get_id_nosync(fid_manager, path):
    row = fid_manager.con.execute("SELECT id FROM Files WHERE path = ?", (path,)).fetchone()
    return row and row[0]


def get_path_nosync(fid_manager, id):
    row = fid_manager.con.execute("SELECT path FROM Files WHERE id = ?", (id,)).fetchone()
    return row and row[0]


def test_validates_root_dir(fid_db_path):
    with pytest.raises(TraitError, match="must be an absolute path"):
        FileIdManager(root_dir=os.path.join("some", "rel", "path"), db_path=fid_db_path)


def test_validates_db_path(jp_root_dir):
    with pytest.raises(TraitError, match="must be an absolute path"):
        FileIdManager(root_dir=str(jp_root_dir), db_path=os.path.join("some", "rel", "path"))


def test_index(fid_manager, test_path):
    id = fid_manager.index(test_path)
    assert id is not None


def test_index_already_indexed(fid_manager, test_path):
    id = fid_manager.index(test_path)
    assert id == fid_manager.index(test_path)


def test_index_symlink(fid_manager, test_path, jp_root_dir):
    link_path = os.path.join(jp_root_dir, "link_path")
    os.symlink(test_path, link_path)
    id = fid_manager.index(link_path)

    # we want to assert that the "real path" is the only path associated with an
    # ID. get_path() *sometimes* returns the real path if _sync_file() happens
    # to be called on the real path after the symlink path when _sync_all() is
    # run, causing this test to flakily pass when it shouldn't.
    assert get_path_nosync(fid_manager, id) == test_path


# test out-of-band move detection for FIM.index()
def test_index_oob_move(fid_manager, old_path, new_path):
    id = fid_manager.index(old_path)
    os.rename(old_path, new_path)
    assert fid_manager.index(new_path) == id


@pytest.fixture
def stub_stat_crtime(fid_manager, request):
    """Fixture that stubs the _stat() method on fid_manager to always return a
    StatStruct with a fixed crtime."""
    if hasattr(request, "param") and not request.param:
        return False

    stat_real = fid_manager._stat

    def stat_stub(path):
        stat = stat_real(path)
        if stat:
            stat.crtime = 123456789
        return stat

    fid_manager._stat = stat_stub
    return True


# sync file should work even after directory mtime changes when children are
# added/removed/renamed on platforms supporting crtime
def test_index_crtime(fid_manager, test_path, stub_stat_crtime):
    stat = os.stat(test_path)
    id = fid_manager.index(test_path)
    os.utime(test_path, ns=(stat.st_atime_ns, stat.st_mtime_ns + 1000))

    assert fid_manager.index(test_path) == id


def test_getters_indexed(fid_manager, test_path):
    id = fid_manager.index(test_path)

    assert fid_manager.get_id(test_path) == id
    assert fid_manager.get_path(id) == test_path


def test_getters_nonnormalized(fid_manager, test_path):
    path1 = os.path.join(test_path, "file")
    path2 = os.path.join(test_path, "some_dir", "..", "file")
    path3 = os.path.join(test_path, ".", ".", ".", "file")
    Path(path1).touch()

    id = fid_manager.index(path1)

    assert fid_manager.get_id(path1) == id
    assert fid_manager.get_id(path2) == id
    assert fid_manager.get_id(path3) == id


def test_getters_oob_delete(fid_manager, test_path):
    id = fid_manager.index(test_path)
    os.rmdir(test_path)
    assert id is not None
    assert fid_manager.get_id(test_path) == None
    assert fid_manager.get_path(id) == None


def test_get_id_unindexed(fid_manager, test_path_child):
    assert fid_manager.get_id(test_path_child) == None


# test out-of-band move detection for FIM.get_id()
def test_get_id_oob_move(fid_manager, old_path, new_path):
    id = fid_manager.index(old_path)
    os.rename(old_path, new_path)
    assert fid_manager.get_id(new_path) == id


def test_get_id_oob_move_recursive(fid_manager, old_path, old_path_child, new_path, new_path_child):
    parent_id = fid_manager.index(old_path)
    child_id = fid_manager.index(old_path_child)

    os.rename(old_path, new_path)

    assert fid_manager.get_id(new_path) == parent_id
    assert fid_manager.get_id(new_path_child) == child_id


# make sure that out-of-band moves are detected even when a new file is created
# at the old path.  this is what forces relaxation of the UNIQUE constraint on
# path column, since we need to keep records of deleted files that used to
# occupy a path, which is possibly occupied by a new file.
def test_get_id_oob_move_new_file_at_old_path(fid_manager, old_path, new_path, jp_root_dir):
    old_id = fid_manager.index(old_path)
    other_path = os.path.join(jp_root_dir, "other_path")

    os.rename(old_path, new_path)
    Path(old_path).touch()
    other_id = fid_manager.index(old_path)
    os.rename(old_path, other_path)

    assert other_id != old_id
    assert fid_manager.get_id(new_path) == old_id
    assert fid_manager.get_path(old_id) == new_path
    assert fid_manager.get_id(other_path) == other_id


def test_get_path_oob_move(fid_manager, old_path, new_path):
    id = fid_manager.index(old_path)
    os.rename(old_path, new_path)
    assert fid_manager.get_path(id) == new_path


def test_get_path_oob_move_recursive(
    fid_manager, old_path, old_path_child, new_path, new_path_child
):
    id = fid_manager.index(old_path)
    child_id = fid_manager.index(old_path_child)

    os.rename(old_path, new_path)

    assert fid_manager.get_path(id) == new_path
    assert fid_manager.get_path(child_id) == new_path_child


def test_get_path_oob_move_into_unindexed(
    fid_manager, old_path, old_path_child, new_path, new_path_child
):
    fid_manager.index(old_path)
    id = fid_manager.index(old_path_child)

    os.mkdir(new_path)
    os.rename(old_path_child, new_path_child)

    assert fid_manager.get_path(id) == new_path_child


# move file into an indexed-but-moved directory
# this test should work regardless of whether crtime is supported on platform
@pytest.mark.parametrize("stub_stat_crtime", [True, False], indirect=["stub_stat_crtime"])
def test_get_path_oob_move_nested(fid_manager, old_path, new_path, jp_root_dir, stub_stat_crtime):
    old_test_path = os.path.join(jp_root_dir, "test_path")
    new_test_path = os.path.join(new_path, "test_path")
    Path(old_test_path).touch()
    stat = os.stat(old_test_path)
    fid_manager.index(old_path)
    id = fid_manager.index(old_test_path)

    os.rename(old_path, new_path)
    os.rename(old_test_path, new_test_path)
    # ensure new_path has different mtime after moving test_path. moving a file
    # into an indexed-but-moved dir has a chance of not changing the dir's
    # mtime. since we fallback to mtime, this makes the dir look unindexed and
    # causes this test to flakily pass when it should not.
    os.utime(new_path, ns=(stat.st_atime_ns, stat.st_mtime_ns + 1000))

    assert fid_manager.get_path(id) == new_test_path


# move file into directory within an indexed-but-moved directory
# this test should work regardless of whether crtime is supported on platform
@pytest.mark.parametrize("stub_stat_crtime", [True, False], indirect=["stub_stat_crtime"])
def test_get_path_oob_move_deeply_nested(
    fid_manager, old_path, new_path, old_path_child, new_path_child, jp_root_dir, stub_stat_crtime
):
    old_test_path = os.path.join(jp_root_dir, "test_path")
    new_test_path = os.path.join(new_path_child, "test_path")
    Path(old_test_path).touch()
    stat = os.stat(old_test_path)
    fid_manager.index(old_path)
    fid_manager.index(old_path_child)
    id = fid_manager.index(old_test_path)

    os.rename(old_path, new_path)
    os.rename(old_test_path, new_test_path)
    os.utime(new_path_child, ns=(stat.st_atime_ns, stat.st_mtime_ns + 1000))

    assert fid_manager.get_path(id) == new_test_path


def test_move_unindexed(fid_manager, old_path, new_path):
    os.rename(old_path, new_path)
    id = fid_manager.move(old_path, new_path)

    assert id is not None
    assert fid_manager.get_id(old_path) is None
    assert fid_manager.get_id(new_path) is id
    assert fid_manager.get_path(id) == new_path


def test_move_indexed(fid_manager, old_path, new_path):
    old_id = fid_manager.index(old_path)

    os.rename(old_path, new_path)
    new_id = fid_manager.move(old_path, new_path)

    assert old_id == new_id
    assert fid_manager.get_id(old_path) == None
    assert fid_manager.get_id(new_path) == new_id
    assert fid_manager.get_path(old_id) == new_path


# test for disjoint move handling
# disjoint move: any out-of-band move that does not preserve stat info
def test_disjoint_move_indexed(fid_manager, old_path, new_path):
    old_id = fid_manager.index(old_path)

    os.rmdir(old_path)
    os.mkdir(new_path)
    new_id = fid_manager.move(old_path, new_path)

    assert old_id == new_id


def test_move_recursive(
    fid_manager,
    old_path,
    old_path_child,
    old_path_grandchild,
    new_path,
    new_path_child,
    new_path_grandchild,
):
    parent_id = fid_manager.index(old_path)
    child_id = fid_manager.index(old_path_child)
    grandchild_id = fid_manager.index(old_path_grandchild)

    os.rename(old_path, new_path)
    fid_manager.move(old_path, new_path, recursive=True)

    # we avoid using get_id() here as it auto-corrects wrong path updates via
    # its out-of-band move detection logic. too smart for its own good!
    assert get_id_nosync(fid_manager, new_path) == parent_id
    assert get_id_nosync(fid_manager, new_path_child) == child_id
    assert get_id_nosync(fid_manager, new_path_grandchild) == grandchild_id


def test_copy(fid_manager, old_path, new_path):
    shutil.copytree(old_path, new_path)
    new_id = fid_manager.copy(old_path, new_path)
    old_id = fid_manager.get_id(old_path)

    assert old_id is not None
    assert new_id is not None
    assert old_id != new_id


def test_copy_recursive(fid_manager, old_path, old_path_child, new_path, new_path_child):
    fid_manager.index(old_path)
    fid_manager.index(old_path_child)

    shutil.copytree(old_path, new_path)
    fid_manager.copy(old_path, new_path, recursive=True)

    assert fid_manager.get_id(new_path_child) is not None


def test_delete(fid_manager, test_path):
    id = fid_manager.index(test_path)

    shutil.rmtree(test_path)
    fid_manager.delete(test_path)

    assert fid_manager.get_id(test_path) is None
    assert fid_manager.get_path(id) is None


def test_delete_recursive(fid_manager, test_path, test_path_child):
    fid_manager.index(test_path)
    fid_manager.index(test_path_child)

    shutil.rmtree(test_path)
    fid_manager.delete(test_path, recursive=True)

    assert fid_manager.get_id(test_path_child) is None
