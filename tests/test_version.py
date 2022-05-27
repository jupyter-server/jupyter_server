import re

import pytest

from jupyter_server import __version__

pep440re = re.compile(r"^(\d+)\.(\d+)\.(\d+((a|b|rc)\d+)?)(\.post\d+)?(\.dev\d*)?$")


def raise_on_bad_version(version):
    if not pep440re.match(version):
        raise ValueError(
            "Versions String does apparently not match Pep 440 specification, "
            "which might lead to sdist and wheel being seen as 2 different release. "
            "E.g: do not use dots for beta/alpha/rc markers."
        )


# --------- Meta test to test the versioning tests -------------


@pytest.mark.parametrize(
    "version",
    [
        "4.1.0.b1",
        "4.1.b1",
        "4.2",
        "X.y.z",
        "1.2.3.dev1.post2",
    ],
)
def test_invalid_pep440_versions(version):
    with pytest.raises(ValueError):
        raise_on_bad_version(version)


@pytest.mark.parametrize(
    "version",
    [
        "4.1.1",
        "4.2.1b3",
    ],
)
def test_valid_pep440_versions(version):
    assert raise_on_bad_version(version) is None


# --------- Test current version --------------
def test_current_version():
    raise_on_bad_version(__version__)
