import os


def test_index(fid_manager):
    path = os.path.join("path", "to", "file")
    id = fid_manager.index(path)
    assert id is not None


def test_index_already_indexed(fid_manager):
    path = os.path.join("path", "to", "file")
    id = fid_manager.index(path)
    assert id == fid_manager.index(path)


def test_getters_indexed(fid_manager):
    path = os.path.join("path", "to", "file")

    id = fid_manager.index(path)
    id = fid_manager.index(path)

    assert fid_manager.get_id(path) == id
    assert fid_manager.get_path(id) == path


def test_getters_unindexed(fid_manager):
    path = os.path.join("path", "to", "file")
    id = 1

    assert fid_manager.get_id(path) == None
    assert fid_manager.get_path(id) == None


def test_getters_nonnormalized(fid_manager):
    path1 = os.path.join("dir", "something", "..", "file")
    path2 = os.path.join("dir", "file")
    path3 = os.path.join("dir", ".", ".", ".", "file")

    id = fid_manager.index(path1)

    assert fid_manager.get_id(path2) == id
    assert fid_manager.get_id(path3) == id


def test_move_unindexed(fid_manager):
    old_path = os.path.join("old", "path")
    new_path = os.path.join("new", "path")

    id = fid_manager.move(old_path, new_path)

    assert fid_manager.get_id(old_path) is None
    assert fid_manager.get_id(new_path) is id
    assert fid_manager.get_path(id) == new_path


def test_move_indexed(fid_manager):
    old_path = os.path.join("old", "path")
    new_path = os.path.join("new", "path")

    old_id = fid_manager.index(old_path)
    new_id = fid_manager.move(old_path, new_path)

    assert old_id == new_id
    assert fid_manager.get_id(old_path) is None
    assert fid_manager.get_id(new_path) is new_id
    assert fid_manager.get_path(old_id) == new_path


def test_move_recursive(fid_manager):
    old_path = os.path.join("old", "path")
    old_path_child = os.path.join(old_path, "child")
    new_path = os.path.join("new", "path")
    expected_new_path_child = os.path.join(new_path, "child")

    fid_manager.index(old_path)
    child_id = fid_manager.index(old_path_child)
    fid_manager.move(old_path, new_path, recursive=True)

    assert fid_manager.get_id(expected_new_path_child) == child_id


def test_copy(fid_manager):
    old_path = os.path.join("old", "path")
    new_path = os.path.join("new", "path")

    new_id = fid_manager.copy(old_path, new_path)
    old_id = fid_manager.get_id(old_path)

    assert old_id is not None
    assert new_id is not None
    assert old_id != new_id


def test_copy_recursive(fid_manager):
    from_path = os.path.join("from", "path")
    from_path_child = os.path.join(from_path, "child")
    to_path = os.path.join("to", "path")
    expected_to_path_child = os.path.join(to_path, "child")

    fid_manager.index(from_path)
    fid_manager.index(from_path_child)
    fid_manager.copy(from_path, to_path, recursive=True)

    assert fid_manager.get_id(expected_to_path_child) is not None


def test_delete(fid_manager):
    path = os.path.join("path", "to", "file")

    id = fid_manager.index(path)
    fid_manager.delete(path)

    assert fid_manager.get_id(path) is None
    assert fid_manager.get_path(id) is None


def test_delete_recursive(fid_manager):
    path = "path"
    path_child = os.path.join(path, "child")

    fid_manager.index(path)
    fid_manager.index(path_child)
    fid_manager.delete(path, recursive=True)

    assert fid_manager.get_id(path_child) is None
