import os
import sys
import ctypes
import pytest

from traitlets.tests.utils import check_help_all_output
from jupyter_server.utils import url_escape, url_unescape, is_hidden, is_file_hidden, secure_write
from ipython_genutils.py3compat import cast_unicode
from ipython_genutils.tempdir import TemporaryDirectory
from ipython_genutils.testing.decorators import skip_if_not_win32, skip_win32


def test_help_output():
    check_help_all_output('jupyter_server')



@pytest.mark.parametrize(
    'unescaped,escaped',
    [
        (
            '/this is a test/for spaces/', 
            '/this%20is%20a%20test/for%20spaces/'
        ),
        (
            'notebook with space.ipynb',
            'notebook%20with%20space.ipynb'
        ),
        (
            '/path with a/notebook and space.ipynb',
            '/path%20with%20a/notebook%20and%20space.ipynb'
        ),
        (
            '/ !@$#%^&* / test %^ notebook @#$ name.ipynb',
            '/%20%21%40%24%23%25%5E%26%2A%20/%20test%20%25%5E%20notebook%20%40%23%24%20name.ipynb'
        )
    ]
)
def test_url_escaping(unescaped, escaped):
    # Test escaping.
    path = url_escape(unescaped)
    assert path == escaped
    # Test unescaping.
    path = url_unescape(escaped)
    assert path == unescaped


def test_is_hidden(tmp_path):
    root = str(tmp_path)
    subdir1_path = tmp_path / 'subdir'
    subdir1_path.mkdir()
    subdir1 = str(subdir1_path)
    assert not is_hidden(subdir1, root)
    assert not is_file_hidden(subdir1)

    subdir2_path = tmp_path / '.subdir2'
    subdir2_path.mkdir()
    subdir2 = str(subdir2_path)
    assert is_hidden(subdir2, root)
    assert is_file_hidden(subdir2)

    subdir34_path = tmp_path / 'subdir3' / '.subdir4'
    subdir34_path.mkdir(parents=True)
    subdir34 = str(subdir34_path)
    assert is_hidden(subdir34, root)
    assert is_hidden(subdir34)

    subdir56_path = tmp_path / '.subdir5' / 'subdir6'
    subdir56_path.mkdir(parents=True)
    subdir56 = str(subdir56_path)
    assert is_hidden(subdir56, root)
    assert is_hidden(subdir56)
    assert not is_file_hidden(subdir56)
    assert not is_file_hidden(subdir56, os.stat(subdir56))


@pytest.mark.skipif(sys.platform != "win32", reason="Test is not windows.")
def test_is_hidden_win32(tmp_path):
    root = str(tmp_path)
    root = cast_unicode(root)
    subdir1 = tmp_path / 'subdir'
    subdir1.mkdir()
    assert not is_hidden(str(subdir1), root)
    ctypes.windll.kernel32.SetFileAttributesW(str(subdir1), 0x02)
    assert is_hidden(str(subdir1), root)
    assert is_file_hidden(str(subdir1))
