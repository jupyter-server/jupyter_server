import pytest

from jupyter_server.auth import IdentityProvider, User
from jupyter_server.auth.identity import _backward_compat_user


class CustomUser:
    def __init__(self, name):
        self.name = name


@pytest.mark.parametrize(
    "old_user, expected",
    [
        (
            "str-name",
            {"username": "str-name", "name": "str-name", "display_name": "str-name"},
        ),
        (
            {"username": "user.username", "name": "user.name"},
            {
                "username": "user.username",
                "name": "user.name",
                "display_name": "user.name",
            },
        ),
        (
            {"username": "user.username", "display_name": "display"},
            {
                "username": "user.username",
                "name": "user.username",
                "display_name": "display",
            },
        ),
        ({"name": "user.name"}, {"username": "user.name", "name": "user.name"}),
        ({"unknown": "value"}, ValueError),
        (CustomUser("custom_name"), ValueError),
    ],
)
def test_identity_model(old_user, expected):
    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected):
            user = _backward_compat_user(old_user)
        return
    user = _backward_compat_user(old_user)
    idp = IdentityProvider()
    identity = idp.identity_model(user)
    print(identity)
    identity_subset = {key: identity[key] for key in expected}  # type:ignore[union-attr]
    print(type(identity), type(identity_subset), type(expected))
    assert identity_subset == expected


@pytest.mark.parametrize(
    "fields, expected",
    [
        ({"name": "user"}, TypeError),
        (
            {"username": "user.username"},
            {
                "username": "user.username",
                "name": "user.username",
                "initials": None,
                "avatar_url": None,
                "color": None,
            },
        ),
        (
            {"username": "user.username", "name": "user.name", "color": "#abcdef"},
            {
                "username": "user.username",
                "name": "user.name",
                "display_name": "user.name",
                "color": "#abcdef",
            },
        ),
        (
            {"username": "user.username", "display_name": "display"},
            {
                "username": "user.username",
                "name": "user.username",
                "display_name": "display",
            },
        ),
    ],
)
def test_user_defaults(fields, expected):
    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected):
            user = User(**fields)
        return
    user = User(**fields)

    # check expected fields
    for key in expected:  # type:ignore[union-attr]
        assert getattr(user, key) == expected[key]  # type:ignore[index]

    # check types
    for key in ("username", "name", "display_name"):
        value = getattr(user, key)
        assert isinstance(value, str)
        # don't allow empty strings
        assert value

    for key in ("initials", "avatar_url", "color"):
        value = getattr(user, key)
        assert value is None or isinstance(value, str)
