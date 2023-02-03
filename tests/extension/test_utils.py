import pytest

from jupyter_server.extension.utils import (
    ExtensionLoadingError,
    get_loader,
    validate_extension,
)
from tests.extension.mockextensions import mockext_deprecated, mockext_sys

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


def test_get_loader():
    assert get_loader(mockext_sys) == mockext_sys._load_jupyter_server_extension
    with pytest.deprecated_call():
        assert get_loader(mockext_deprecated) == mockext_deprecated.load_jupyter_server_extension
    with pytest.raises(ExtensionLoadingError):
        get_loader(object())
