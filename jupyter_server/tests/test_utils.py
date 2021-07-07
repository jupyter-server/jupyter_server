from pathlib import Path
import sys

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


@pytest.fixture
def namespace_package_test(monkeypatch):
    """Adds a blank namespace package into the PYTHONPATH for testing.

    Yields the name of the importable namespace.
    """
    monkeypatch.setattr(
        sys,
        'path',
        [
            str(Path(__file__).parent / 'namespace-package-test'),
            *sys.path
        ]
    )
    yield 'test_namespace'


def test_is_namespace_package(namespace_package_test):
    # returns True if it is a namespace package
    assert is_namespace_package(namespace_package_test)
    # returns False if it isn't a namespace package
    assert not is_namespace_package('sys')
    assert not is_namespace_package('jupyter_server')
    # returns None if it isn't importable
    assert is_namespace_package('not_a_python_namespace') is None
