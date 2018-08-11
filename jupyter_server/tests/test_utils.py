"""Test HTML utils"""

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

import ctypes
import os

from traitlets.tests.utils import check_help_all_output
from jupyter_server.utils import url_escape, url_unescape, is_hidden, is_file_hidden
import pytest

from ..utils import cast_unicode
from tempfile import TemporaryDirectory


def test_help_output():
    """jupyter server --help-all works"""
    check_help_all_output('jupyter_server')


def test_url_escape():

    # changes path or notebook name with special characters to url encoding
    # these tests specifically encode paths with spaces
    path = url_escape('/this is a test/for spaces/')
    assert path == '/this%20is%20a%20test/for%20spaces/'

    path = url_escape('notebook with space.ipynb')
    assert path == 'notebook%20with%20space.ipynb'

    path = url_escape('/path with a/notebook and space.ipynb')
    assert path == '/path%20with%20a/notebook%20and%20space.ipynb'

    path = url_escape('/ !@$#%^&* / test %^ notebook @#$ name.ipynb')
    assert (path ==
        '/%20%21%40%24%23%25%5E%26%2A%20/%20test%20%25%5E%20notebook%20%40%23%24%20name.ipynb')


def test_url_unescape():

    # decodes a url string to a plain string
    # these tests decode paths with spaces
    path = url_unescape('/this%20is%20a%20test/for%20spaces/')
    assert path == '/this is a test/for spaces/'

    path = url_unescape('notebook%20with%20space.ipynb')
    assert path == 'notebook with space.ipynb'

    path = url_unescape('/path%20with%20a/notebook%20and%20space.ipynb')
    assert path == '/path with a/notebook and space.ipynb'

    path = url_unescape(
        '/%20%21%40%24%23%25%5E%26%2A%20/%20test%20%25%5E%20notebook%20%40%23%24%20name.ipynb')
    assert path == '/ !@$#%^&* / test %^ notebook @#$ name.ipynb'


def test_is_hidden():
    with TemporaryDirectory() as root:
        subdir1 = os.path.join(root, 'subdir')
        os.makedirs(subdir1)
        assert not is_hidden(subdir1, root)
        assert not is_file_hidden(subdir1)

        subdir2 = os.path.join(root, '.subdir2')
        os.makedirs(subdir2)
        assert is_hidden(subdir2, root)
        assert is_file_hidden(subdir2)   #
        # root dir is always visible
        assert not is_hidden(subdir2, subdir2)

        subdir34 = os.path.join(root, 'subdir3', '.subdir4')
        os.makedirs(subdir34)
        assert is_hidden(subdir34, root)
        assert is_hidden(subdir34)

        subdir56 = os.path.join(root, '.subdir5', 'subdir6')
        os.makedirs(subdir56)
        assert is_hidden(subdir56, root)
        assert is_hidden(subdir56)
        assert not is_file_hidden(subdir56)
        assert not is_file_hidden(subdir56, os.stat(subdir56))


@pytest.mark.skipif(os.name != 'nt', reason='Only on windows')
def test_is_hidden_win32():
    with TemporaryDirectory() as root:
        root = cast_unicode(root)
        subdir1 = os.path.join(root, u'subdir')
        os.makedirs(subdir1)
        assert not is_hidden(subdir1, root)
        r = ctypes.windll.kernel32.SetFileAttributesW(subdir1, 0x02)
        print(r)
        assert is_hidden(subdir1, root)
        assert is_file_hidden(subdir1)
