import os
import sys
import time
import pytest
import functools
from traitlets import TraitError
from tornado.web import HTTPError
from itertools import combinations


from nbformat import v4 as nbformat

from jupyter_server.services.contents.filemanager import FileContentsManager
from ...utils import expected_http_error

# -------------- Functions ----------------------------

def _make_dir(contents_manager, api_path):
    """
    Make a directory.
    """
    os_path = contents_manager._get_os_path(api_path)
    try:
        os.makedirs(os_path)
    except OSError:
        print("Directory already exists: %r" % os_path)


def symlink(contents_manager, src, dst):
    """Make a symlink to src from dst

    src and dst are api_paths
    """
    src_os_path = contents_manager._get_os_path(src)
    dst_os_path = contents_manager._get_os_path(dst)
    print(src_os_path, dst_os_path, os.path.isfile(src_os_path))
    os.symlink(src_os_path, dst_os_path)


def add_code_cell(notebook):
    output = nbformat.new_output("display_data", {'application/javascript': "alert('hi');"})
    cell = nbformat.new_code_cell("print('hi')", outputs=[output])
    notebook.cells.append(cell)


def new_notebook(contents_manager):
    cm = contents_manager
    model = cm.new_untitled(type='notebook')
    name = model['name']
    path = model['path']

    full_model = cm.get(path)
    nb = full_model['content']
    nb['metadata']['counter'] = int(1e6 * time.time())
    add_code_cell(nb)

    cm.save(full_model, path)
    return nb, name, path


def make_populated_dir(contents_manager, api_path):
    cm = contents_manager
    _make_dir(cm, api_path)
    cm.new(path="/".join([api_path, "nb.ipynb"]))
    cm.new(path="/".join([api_path, "file.txt"]))


def check_populated_dir_files(contents_manager, api_path):
    dir_model = contents_manager.get(api_path)

    assert dir_model['path'] == api_path
    assert dir_model['type'] == "directory"

    for entry in dir_model['content']:
        if entry['type'] == "directory":
            continue
        elif entry['type'] == "file":
            assert entry['name'] == "file.txt"
            complete_path = "/".join([api_path, "file.txt"])
            assert entry["path"] == complete_path
        elif entry['type'] == "notebook":
            assert entry['name'] == "nb.ipynb"
            complete_path = "/".join([api_path, "nb.ipynb"])
            assert entry["path"] == complete_path

# ----------------- Tests ----------------------------------

def test_root_dir(tmp_path):
    fm = FileContentsManager(root_dir=str(tmp_path))
    assert fm.root_dir == str(tmp_path)


def test_missing_root_dir(tmp_path):
    root = tmp_path / 'notebook' / 'dir' / 'is' / 'missing'
    with pytest.raises(TraitError):
        FileContentsManager(root_dir=str(root))


def test_invalid_root_dir(tmp_path):
    temp_file = tmp_path / 'file.txt'
    temp_file.write_text('')
    with pytest.raises(TraitError):
        FileContentsManager(root_dir=str(temp_file))

def test_get_os_path(tmp_path):
    fm = FileContentsManager(root_dir=str(tmp_path))
    path = fm._get_os_path('/path/to/notebook/test.ipynb')
    rel_path_list =  '/path/to/notebook/test.ipynb'.split('/')
    fs_path = os.path.join(fm.root_dir, *rel_path_list)
    assert path == fs_path

    fm = FileContentsManager(root_dir=str(tmp_path))
    path = fm._get_os_path('test.ipynb')
    fs_path = os.path.join(fm.root_dir, 'test.ipynb')
    assert path == fs_path

    fm = FileContentsManager(root_dir=str(tmp_path))
    path = fm._get_os_path('////test.ipynb')
    fs_path = os.path.join(fm.root_dir, 'test.ipynb')
    assert path == fs_path


def test_checkpoint_subdir(tmp_path):
    subd = 'sub ∂ir'
    cp_name = 'test-cp.ipynb'
    fm = FileContentsManager(root_dir=str(tmp_path))
    tmp_path.joinpath(subd).mkdir()
    cpm = fm.checkpoints
    cp_dir = cpm.checkpoint_path('cp', 'test.ipynb')
    cp_subdir = cpm.checkpoint_path('cp', '/%s/test.ipynb' % subd)
    assert cp_dir != cp_subdir
    assert cp_dir == os.path.join(str(tmp_path), cpm.checkpoint_dir, cp_name)


@pytest.mark.skipif(
    sys.platform == 'win32' and sys.version_info[0] < 3,
    reason="System platform is Windows, version < 3"
)
def test_bad_symlink(tmp_path):
    td = str(tmp_path)

    cm = FileContentsManager(root_dir=td)
    path = 'test bad symlink'
    _make_dir(cm, path)

    file_model = cm.new_untitled(path=path, ext='.txt')

    # create a broken symlink
    symlink(cm, "target", '%s/%s' % (path, 'bad symlink'))
    model = cm.get(path)

    contents = {
        content['name']: content for content in model['content']
    }
    assert 'untitled.txt' in contents
    assert contents['untitled.txt'] == file_model
    assert 'bad symlink' in contents


@pytest.mark.skipif(
    sys.platform == 'win32' and sys.version_info[0] < 3,
    reason="System platform is Windows, version < 3"
)
def test_good_symlink(tmp_path):
    td = str(tmp_path)
    cm = FileContentsManager(root_dir=td)
    parent = 'test good symlink'
    name = 'good symlink'
    path = '{0}/{1}'.format(parent, name)
    _make_dir(cm, parent)

    file_model = cm.new(path=parent + '/zfoo.txt')

    # create a good symlink
    symlink(cm, file_model['path'], path)
    symlink_model = cm.get(path, content=False)
    dir_model = cm.get(parent)
    assert sorted(dir_model['content'], key=lambda x: x['name']) == [symlink_model, file_model]


def test_403(tmp_path):
    if hasattr(os, 'getuid'):
        if os.getuid() == 0:
            raise pytest.skip("Can't test permissions as root")
    if sys.platform.startswith('win'):
        raise pytest.skip("Can't test permissions on Windows")

    td = str(tmp_path)
    cm = FileContentsManager(root_dir=td)
    model = cm.new_untitled(type='file')
    os_path = cm._get_os_path(model['path'])

    os.chmod(os_path, 0o400)
    try:
        with cm.open(os_path, 'w') as f:
            f.write(u"don't care")
    except HTTPError as e:
        assert e.status_code == 403

def test_escape_root(tmp_path):
    td = str(tmp_path)
    cm = FileContentsManager(root_dir=td)
    # make foo, bar next to root
    with open(os.path.join(cm.root_dir, '..', 'foo'), 'w') as f:
        f.write('foo')
    with open(os.path.join(cm.root_dir, '..', 'bar'), 'w') as f:
        f.write('bar')

    with pytest.raises(HTTPError) as e:
        cm.get('..')
    expected_http_error(e, 404)

    with pytest.raises(HTTPError) as e:
        cm.get('foo/../../../bar')
    expected_http_error(e, 404)

    with pytest.raises(HTTPError) as e:
        cm.delete('../foo')
    expected_http_error(e, 404)

    with pytest.raises(HTTPError) as e:
        cm.rename('../foo', '../bar')
    expected_http_error(e, 404)

    with pytest.raises(HTTPError) as e:
        cm.save(model={
            'type': 'file',
            'content': u'',
            'format': 'text',
        }, path='../foo')
    expected_http_error(e, 404)


def test_new_untitled(contents_manager):
    cm = contents_manager
    # Test in root directory
    model = cm.new_untitled(type='notebook')
    assert isinstance(model, dict)
    assert 'name' in model
    assert 'path' in model
    assert 'type' in model
    assert model['type'] == 'notebook'
    assert model['name'] == 'Untitled.ipynb'
    assert model['path'] == 'Untitled.ipynb'

    # Test in sub-directory
    model = cm.new_untitled(type='directory')
    assert isinstance(model, dict)
    assert 'name' in model
    assert 'path' in model
    assert 'type' in model
    assert model['type'] == 'directory'
    assert model['name'] == 'Untitled Folder'
    assert model['path'] == 'Untitled Folder'
    sub_dir = model['path']

    model = cm.new_untitled(path=sub_dir)
    assert isinstance(model, dict)
    assert 'name' in model
    assert 'path' in model
    assert 'type' in model
    assert model['type'] == 'file'
    assert model['name'] == 'untitled'
    assert model['path'] == '%s/untitled' % sub_dir

    # Test with a compound extension
    model = cm.new_untitled(path=sub_dir, ext='.foo.bar')
    assert model['name'] == 'untitled.foo.bar'
    model = cm.new_untitled(path=sub_dir, ext='.foo.bar')
    assert model['name'] == 'untitled1.foo.bar'


def test_modified_date(contents_manager):
    cm = contents_manager
    # Create a new notebook.
    nb, name, path = new_notebook(cm)
    model = cm.get(path)

    # Add a cell and save.
    add_code_cell(model['content'])
    cm.save(model, path)

    # Reload notebook and verify that last_modified incremented.
    saved = cm.get(path)
    assert saved['last_modified'] >= model['last_modified']

    # Move the notebook and verify that last_modified stayed the same.
    # (The frontend fires a warning if last_modified increases on the
    # renamed file.)
    new_path = 'renamed.ipynb'
    cm.rename(path, new_path)
    renamed = cm.get(new_path)
    assert renamed['last_modified'] >= saved['last_modified']


def test_get(contents_manager):
    cm = contents_manager
    # Create a notebook
    model = cm.new_untitled(type='notebook')
    name = model['name']
    path = model['path']

    # Check that we 'get' on the notebook we just created
    model2 = cm.get(path)
    assert isinstance(model2, dict)
    assert 'name' in model2
    assert 'path' in model2
    assert model['name'] == name
    assert model['path'] == path

    nb_as_file = cm.get(path, content=True, type='file')
    assert nb_as_file['path'] == path
    assert nb_as_file['type'] == 'file'
    assert nb_as_file['format'] == 'text'
    assert not isinstance(nb_as_file['content'], dict)

    nb_as_bin_file = cm.get(path, content=True, type='file', format='base64')
    assert nb_as_bin_file['format'] == 'base64'

    # Test in sub-directory
    sub_dir = '/foo/'
    _make_dir(cm, 'foo')
    model = cm.new_untitled(path=sub_dir, ext='.ipynb')
    model2 = cm.get(sub_dir + name)
    assert isinstance(model2, dict)
    assert 'name' in model2
    assert 'path' in model2
    assert 'content' in model2
    assert model2['name'] == 'Untitled.ipynb'
    assert model2['path'] == '{0}/{1}'.format(sub_dir.strip('/'), name)


    # Test with a regular file.
    file_model_path = cm.new_untitled(path=sub_dir, ext='.txt')['path']
    file_model = cm.get(file_model_path)
    expected_model = {
        'content': u'',
        'format': u'text',
        'mimetype': u'text/plain',
        'name': u'untitled.txt',
        'path': u'foo/untitled.txt',
        'type': u'file',
        'writable': True,
    }
    # Assert expected model is in file_model
    for key, value in expected_model.items():
        assert file_model[key] == value
    assert 'created' in file_model
    assert 'last_modified' in file_model

    # Create a sub-sub directory to test getting directory contents with a
    # subdir.
    _make_dir(cm, 'foo/bar')
    dirmodel = cm.get('foo')
    assert dirmodel['type'] == 'directory'
    assert isinstance(dirmodel['content'], list)
    assert len(dirmodel['content']) == 3
    assert dirmodel['path'] == 'foo'
    assert dirmodel['name'] == 'foo'

    # Directory contents should match the contents of each individual entry
    # when requested with content=False.
    model2_no_content = cm.get(sub_dir + name, content=False)
    file_model_no_content = cm.get(u'foo/untitled.txt', content=False)
    sub_sub_dir_no_content = cm.get('foo/bar', content=False)
    assert sub_sub_dir_no_content['path'] == 'foo/bar'
    assert sub_sub_dir_no_content['name'] == 'bar'

    for entry in dirmodel['content']:
        # Order isn't guaranteed by the spec, so this is a hacky way of
        # verifying that all entries are matched.
        if entry['path'] == sub_sub_dir_no_content['path']:
            assert entry == sub_sub_dir_no_content
        elif entry['path'] == model2_no_content['path']:
            assert entry == model2_no_content
        elif entry['path'] == file_model_no_content['path']:
            assert entry == file_model_no_content
        else:
            assert False, "Unexpected directory entry: %s" % entry()

    with pytest.raises(HTTPError):
        cm.get('foo', type='file')


def test_update(contents_manager):
    cm = contents_manager
    # Create a notebook.
    model = cm.new_untitled(type='notebook')
    name = model['name']
    path = model['path']

    # Change the name in the model for rename
    model['path'] = 'test.ipynb'
    model = cm.update(model, path)
    assert isinstance(model, dict)
    assert 'name' in model
    assert 'path' in model
    assert model['name'] == 'test.ipynb'

    # Make sure the old name is gone
    with pytest.raises(HTTPError):
        cm.get(path)

    # Test in sub-directory
    # Create a directory and notebook in that directory
    sub_dir = '/foo/'
    _make_dir(cm, 'foo')
    model = cm.new_untitled(path=sub_dir, type='notebook')
    path = model['path']

    # Change the name in the model for rename
    d = path.rsplit('/', 1)[0]
    new_path = model['path'] = d + '/test_in_sub.ipynb'
    model = cm.update(model, path)
    assert isinstance(model, dict)
    assert 'name' in model
    assert 'path' in model
    assert model['name'] == 'test_in_sub.ipynb'
    assert model['path'] == new_path

    # Make sure the old name is gone
    with pytest.raises(HTTPError):
        cm.get(path)


def test_save(contents_manager):
    cm = contents_manager
    # Create a notebook
    model = cm.new_untitled(type='notebook')
    name = model['name']
    path = model['path']

    # Get the model with 'content'
    full_model = cm.get(path)

    # Save the notebook
    model = cm.save(full_model, path)
    assert isinstance(model, dict)
    assert 'name' in model
    assert 'path' in model
    assert model['name'] == name
    assert model['path'] == path

    # Test in sub-directory
    # Create a directory and notebook in that directory
    sub_dir = '/foo/'
    _make_dir(cm, 'foo')
    model = cm.new_untitled(path=sub_dir, type='notebook')
    name = model['name']
    path = model['path']
    model = cm.get(path)

    # Change the name in the model for rename
    model = cm.save(model, path)
    assert isinstance(model, dict)
    assert 'name' in model
    assert 'path' in model
    assert model['name'] == 'Untitled.ipynb'
    assert model['path'] == 'foo/Untitled.ipynb'


def test_delete(contents_manager):
    cm = contents_manager
    # Create a notebook
    nb, name, path = new_notebook(cm)

    # Delete the notebook
    cm.delete(path)

    # Check that deleting a non-existent path raises an error.
    with pytest.raises(HTTPError):
        cm.delete(path)

    # Check that a 'get' on the deleted notebook raises and error
    with pytest.raises(HTTPError):
        cm.get(path)


def test_rename(contents_manager):
    cm = contents_manager
    # Create a new notebook
    nb, name, path = new_notebook(cm)

    # Rename the notebook
    cm.rename(path, "changed_path")

    # Attempting to get the notebook under the old name raises an error
    with pytest.raises(HTTPError):
        cm.get(path)
    # Fetching the notebook under the new name is successful
    assert isinstance(cm.get("changed_path"), dict)

    # Ported tests on nested directory renaming from pgcontents
    all_dirs = ['foo', 'bar', 'foo/bar', 'foo/bar/foo', 'foo/bar/foo/bar']
    unchanged_dirs = all_dirs[:2]
    changed_dirs = all_dirs[2:]

    for _dir in all_dirs:
        make_populated_dir(cm, _dir)
        check_populated_dir_files(cm, _dir)

    # Renaming to an existing directory should fail
    for src, dest in combinations(all_dirs, 2):
        with pytest.raises(HTTPError) as e:
            cm.rename(src, dest)
        assert expected_http_error(e, 409)

    # Creating a notebook in a non_existant directory should fail
    with pytest.raises(HTTPError) as e:
        cm.new_untitled("foo/bar_diff", ext=".ipynb")
    assert expected_http_error(e, 404)

    cm.rename("foo/bar", "foo/bar_diff")

    # Assert that unchanged directories remain so
    for unchanged in unchanged_dirs:
        check_populated_dir_files(cm, unchanged)

    # Assert changed directories can no longer be accessed under old names
    for changed_dirname in changed_dirs:
        with pytest.raises(HTTPError) as e:
            cm.get(changed_dirname)
        assert expected_http_error(e, 404)
        new_dirname = changed_dirname.replace("foo/bar", "foo/bar_diff", 1)
        check_populated_dir_files(cm, new_dirname)

    # Created a notebook in the renamed directory should work
    cm.new_untitled("foo/bar_diff", ext=".ipynb")


def test_delete_root(contents_manager):
    cm = contents_manager
    with pytest.raises(HTTPError) as e:
        cm.delete('')
    assert expected_http_error(e, 400)


def test_copy(contents_manager):
    cm = contents_manager
    parent = u'å b'
    name = u'nb √.ipynb'
    path = u'{0}/{1}'.format(parent, name)
    _make_dir(cm, parent)

    orig = cm.new(path=path)
    # copy with unspecified name
    copy = cm.copy(path)
    assert copy['name'] == orig['name'].replace('.ipynb', '-Copy1.ipynb')

    # copy with specified name
    copy2 = cm.copy(path, u'å b/copy 2.ipynb')
    assert copy2['name'] == u'copy 2.ipynb'
    assert copy2['path'] == u'å b/copy 2.ipynb'
    # copy with specified path
    copy2 = cm.copy(path, u'/')
    assert copy2['name'] == name
    assert copy2['path'] == name


def test_mark_trusted_cells(contents_manager):
    cm = contents_manager
    nb, name, path = new_notebook(cm)

    cm.mark_trusted_cells(nb, path)
    for cell in nb.cells:
        if cell.cell_type == 'code':
            assert not cell.metadata.trusted

    cm.trust_notebook(path)
    nb = cm.get(path)['content']
    for cell in nb.cells:
        if cell.cell_type == 'code':
            assert cell.metadata.trusted


def test_check_and_sign(contents_manager):
    cm = contents_manager
    nb, name, path = new_notebook(cm)

    cm.mark_trusted_cells(nb, path)
    cm.check_and_sign(nb, path)
    assert not cm.notary.check_signature(nb)

    cm.trust_notebook(path)
    nb = cm.get(path)['content']
    cm.mark_trusted_cells(nb, path)
    cm.check_and_sign(nb, path)
    assert cm.notary.check_signature(nb)
