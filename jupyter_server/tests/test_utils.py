from pathlib import Path
from unittest.mock import patch

import pytest

from traitlets.tests.utils import check_help_all_output
from jupyter_server.utils import (
    url_escape,
    url_unescape,
    is_namespace_package
)


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


@pytest.mark.parametrize(
    'name, expected',
    [
        # returns True if it is a namespace package
        ('test_namespace', True),
        # returns False if it isn't a namespace package
        ('sys', False),
        ('jupyter_server', False),
        # returns None if it isn't importable
        ('not_a_python_namespace', None)
    ]
)
def test_is_namespace_package(monkeypatch, name, expected):
    monkeypatch.syspath_prepend(Path(__file__).parent / 'namespace-package-test')
    
    assert is_namespace_package(name) is expected
    

def test_is_namespace_package_no_spec():
    with patch("importlib.util.find_spec") as mocked_spec:
        mocked_spec.side_effect = ValueError()

        assert is_namespace_package('dummy') is None
        mocked_spec.assert_called_once_with('dummy')
