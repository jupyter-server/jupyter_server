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
    Path(path).touch()
    return path


@pytest.fixture
def new_path(jp_root_dir):
    """Fixture for destination path for a FID manager move/copy operation"""
    return os.path.join(jp_root_dir, "new_path")


@pytest.fixture
def new_path_child(new_path):
    return os.path.join(new_path, "child")


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


def test_getters_indexed(fid_manager, test_path):
    id = fid_manager.index(test_path)

    assert fid_manager.get_id(test_path) == id
    assert fid_manager.get_path(id) == test_path


def test_get_id_unindexed(fid_manager, test_path_child):
    assert fid_manager.get_id(test_path_child) == None


def test_getters_nonnormalized(fid_manager, test_path):
    path1 = os.path.join(test_path, "file")
    path2 = os.path.join(test_path, "some_dir", "..", "file")
    path3 = os.path.join(test_path, ".", ".", ".", "file")
    Path(path1).touch()

    id = fid_manager.index(path1)

    assert fid_manager.get_id(path1) == id
    assert fid_manager.get_id(path2) == id
    assert fid_manager.get_id(path3) == id


# test out-of-band move detection for FIM.index()
def test_index_oob_move(fid_manager, old_path, new_path):
    id = fid_manager.index(old_path)
    os.rename(old_path, new_path)
    assert fid_manager.index(new_path) == id


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


def test_get_path_oob_move(fid_manager, old_path, new_path):
    id = fid_manager.index(old_path)
    os.rename(old_path, new_path)
    assert fid_manager.get_path(id) == new_path


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


def test_move_recursive(fid_manager, old_path, old_path_child, new_path, new_path_child):
    parent_id = fid_manager.index(old_path)
    child_id = fid_manager.index(old_path_child)

    os.rename(old_path, new_path)
    fid_manager.move(old_path, new_path, recursive=True)

    assert fid_manager.get_id(new_path) == parent_id
    assert fid_manager.get_id(new_path_child) == child_id


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
