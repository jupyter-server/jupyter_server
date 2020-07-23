import pytest
from jupyter_server.extension.utils import validate_extension


def test_validate_extension():
    # enabled at sys level
    assert validate_extension('tests.extension.mockextensions.mockext_sys')
    # enabled at sys, disabled at user
    assert validate_extension('tests.extension.mockextensions.mockext_both')
    # enabled at user
    assert validate_extension('tests.extension.mockextensions.mockext_user')
    # enabled at Python
    assert validate_extension('tests.extension.mockextensions.mockext_py')