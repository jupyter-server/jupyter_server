import pytest

from jupyter_server.extension.utils import validate_extension

# Use ServerApps environment because it monkeypatches
# jupyter_core.paths and provides a config directory
# that's not cross contaminating the user config directory.
pytestmark = pytest.mark.usefixtures("jp_environ")


def test_validate_extension():
    # enabled at sys level
    assert validate_extension("tests.extension.mockextensions.mockext_sys")
    # enabled at sys, disabled at user
    assert validate_extension("tests.extension.mockextensions.mockext_both")
    # enabled at user
    assert validate_extension("tests.extension.mockextensions.mockext_user")
    # enabled at Python
    assert validate_extension("tests.extension.mockextensions.mockext_py")
