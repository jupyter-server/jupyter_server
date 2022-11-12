import logging
import warnings

import pytest

from jupyter_server.extension.utils import get_loader, get_metadata, validate_extension
from tests.extension.mockextensions import mockext_sys

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
    get_loader(mockext_sys)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        assert get_loader(object()) is None


def test_get_metadata():
    _, ext_points = get_metadata("tests.extension.mockextensions.mockext_sys")
    assert len(ext_points)
    _, ext_points = get_metadata("tests", logger=logging.getLogger())
    point = ext_points[0]
    assert point["module"] == "tests"
    assert point["name"] == "tests"
