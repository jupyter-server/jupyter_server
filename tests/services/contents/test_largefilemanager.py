import pytest
import tornado

from jupyter_server.services.contents.largefilemanager import LargeFileManager
from ...utils import expected_http_error

contents_manager = pytest.fixture(lambda tmp_path: LargeFileManager(root_dir=str(tmp_path)))


def test_save(contents_manager):
    cm = contents_manager
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


@pytest.mark.parametrize(
    'model,err_message',
    [
        (
            {'name': 'test', 'path': 'test', 'chunk': 1},
            'HTTP 400: Bad Request (No file type provided)'
        ),
        (
            {'name': 'test', 'path': 'test', 'chunk': 1, 'type': 'notebook'},
            'HTTP 400: Bad Request (File type "notebook" is not supported for large file transfer)'
        ),
        (
            {'name': 'test', 'path': 'test', 'chunk': 1, 'type': 'file'},
            'HTTP 400: Bad Request (No file content provided)',
        ),
        (
            {'name': 'test', 'path': 'test', 'chunk': 2, 'type': 'file',
                'content': u'test', 'format': 'json'},
            "HTTP 400: Bad Request (Must specify format of file contents as 'text' or 'base64')"
        )
    ]
)
def test_bad_save(contents_manager, model, err_message):
    with pytest.raises(tornado.web.HTTPError) as e:
        contents_manager.save(model, model['path'])
    assert expected_http_error(e, 400, expected_message=err_message)


def test_saving_different_chunks(contents_manager):
    cm = contents_manager
    model = {'name': 'test', 'path': 'test', 'type': 'file',
                'content': u'test==', 'format': 'text'}
    name = model['name']
    path = model['path']
    cm.save(model, path)

    for chunk in (1, 2, -1):
        for fm in ('text', 'base64'):
            full_model = cm.get(path)
            full_model['chunk'] = chunk
            full_model['format'] = fm
            model_res = cm.save(full_model, path)
            assert isinstance(model_res, dict)
            assert 'name' in model_res
            assert 'path' in model_res
            assert 'chunk' not in model_res
            assert model_res['name'] == name
            assert model_res['path'] == path


def test_save_in_subdirectory(contents_manager, tmp_path):
    cm = contents_manager
    sub_dir = tmp_path / 'foo'
    sub_dir.mkdir()
    model = cm.new_untitled(path='/foo/', type='notebook')
    path = model['path']
    model = cm.get(path)

    # Change the name in the model for rename
    model = cm.save(model, path)
    assert isinstance(model, dict)
    assert 'name' in model
    assert 'path' in model
    assert model['name'] == 'Untitled.ipynb'
    assert model['path'] == 'foo/Untitled.ipynb'