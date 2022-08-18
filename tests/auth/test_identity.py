import logging
from contextlib import nullcontext

import pytest

from jupyter_server.auth import IdentityProvider, User
from jupyter_server.auth.identity import PasswordIdentityProvider, _backward_compat_user
from jupyter_server.serverapp import ServerApp


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


@pytest.fixture
def identity_provider_class():
    """Allow override in other test modules"""
    return PasswordIdentityProvider


@pytest.mark.parametrize(
    "ip, token, ssl, warns",
    [
        ("", "", None, "highly insecure"),
        ("", "", {"key": "x"}, "all IP addresses"),
        ("", "secret", None, "and not using encryption"),
        ("", "secret", {"key": "x"}, False),
        ("127.0.0.1", "secret", None, False),
    ],
)
def test_validate_security(
    identity_provider_class,
    ip,
    token,
    ssl,
    warns,
    caplog,
):
    app = ServerApp(ip=ip, log=logging.getLogger())
    idp = identity_provider_class(parent=app, token=token)
    app.identity_provider = idp

    with caplog.at_level(logging.WARNING):
        idp.validate_security(app, ssl_options=ssl)
    for record in caplog.records:
        print(record)

    if warns:
        assert len(caplog.records) > 0
        if isinstance(warns, str):
            logged = "\n".join(record.msg for record in caplog.records)
            assert warns in logged
    else:
        assert len(caplog.records) == 0


@pytest.mark.parametrize(
    "password_set, password_required, ok",
    [
        (True, False, True),
        (True, True, True),
        (False, False, True),
        (False, True, False),
    ],
)
def test_password_required(identity_provider_class, password_set, password_required, ok):
    app = ServerApp()
    idp = identity_provider_class(
        parent=app,
        hashed_password="xxx" if password_set else "",
        password_required=password_required,
    )
    app.identity_provider = idp
    if ok:
        ctx = nullcontext()
    else:
        ctx = pytest.raises(SystemExit)

    with ctx:
        idp.validate_security(app, ssl_options=None)
