import json
from typing import Awaitable, Dict, List
from unittest import mock

import pytest
from tornado.httpclient import HTTPError

from jupyter_server.auth import Authorizer, IdentityProvider, User


async def test_get_spec(jp_fetch):
    response = await jp_fetch("api", "spec.yaml", method="GET")
    assert response.code == 200


async def test_get_status(jp_fetch):
    response = await jp_fetch("api", "status", method="GET")
    assert response.code == 200
    assert response.headers.get("Content-Type") == "application/json"
    status = json.loads(response.body.decode("utf8"))
    assert sorted(status.keys()) == [
        "connections",
        "kernels",
        "last_activity",
        "started",
    ]
    assert status["connections"] == 0
    assert status["kernels"] == 0
    assert status["last_activity"].endswith("Z")
    assert status["started"].endswith("Z")


class MockUser(User):
    permissions: Dict[str, List[str]]


class MockIdentityProvider(IdentityProvider):
    mock_user: MockUser

    async def get_user(self, handler):
        # super returns a UUID
        # return our mock user instead, as long as the request is authorized
        _authenticated = super().get_user(handler)
        if isinstance(_authenticated, Awaitable):
            _authenticated = await _authenticated
        authenticated = _authenticated
        if isinstance(self.mock_user, dict):
            self.mock_user = MockUser(**self.mock_user)
        if authenticated:
            return self.mock_user


class MockAuthorizer(Authorizer):
    def is_authorized(self, handler, user, action, resource):
        permissions = user.permissions
        if permissions == "*":
            return True
        actions = permissions.get(resource, [])
        return action in actions


@pytest.fixture
def identity_provider(jp_serverapp):
    idp = MockIdentityProvider(parent=jp_serverapp)
    authorizer = MockAuthorizer(parent=jp_serverapp)
    with mock.patch.dict(
        jp_serverapp.web_app.settings,
        {"identity_provider": idp, "authorizer": authorizer},
    ):
        yield idp


@pytest.mark.parametrize(
    "identity, expected",
    [
        (
            {"username": "user.username"},
            {
                "username": "user.username",
                "name": "user.username",
                "display_name": "user.username",
            },
        ),
        (
            {"username": "user", "name": "name", "display_name": "display"},
            {"username": "user", "name": "name", "display_name": "display"},
        ),
        (
            None,
            403,
        ),
    ],
)
async def test_identity(jp_fetch, identity, expected, identity_provider):
    if identity:
        identity_provider.mock_user = MockUser(**identity)
    else:
        identity_provider.mock_user = None

    if isinstance(expected, int):
        with pytest.raises(HTTPError) as exc:
            await jp_fetch("api/me")
        print(exc)
        assert exc.value.code == expected
        return

    r = await jp_fetch("api/me")

    assert r.code == 200
    response = json.loads(r.body.decode())
    assert set(response.keys()) == {"identity", "permissions"}
    identity_model = response["identity"]
    print(identity_model)
    for key, value in expected.items():
        assert identity_model[key] == value

    assert set(identity_model.keys()) == set(User.__dataclass_fields__)


@pytest.mark.parametrize(
    "have_permissions, check_permissions, expected",
    [
        ("*", None, {}),
        (
            {
                "contents": ["read"],
                "kernels": ["read", "write"],
                "sessions": ["write"],
            },
            {
                "contents": ["read", "write"],
                "kernels": ["read", "write", "execute"],
                "terminals": ["execute"],
            },
            {
                "contents": ["read"],
                "kernels": ["read", "write"],
                "terminals": [],
            },
        ),
        ("*", {"contents": ["write"]}, {"contents": ["write"]}),
    ],
)
async def test_identity_permissions(
    jp_fetch, have_permissions, check_permissions, expected, identity_provider
):
    user = MockUser("username")
    user.permissions = have_permissions
    identity_provider.mock_user = user

    if check_permissions is not None:
        params = {"permissions": json.dumps(check_permissions)}
    else:
        params = None

    r = await jp_fetch("api/me", params=params)
    assert r is not None
    assert r.code == 200
    response = json.loads(r.body.decode())
    assert set(response.keys()) == {"identity", "permissions"}
    assert response["permissions"] == expected


@pytest.mark.parametrize(
    "permissions",
    [
        "",
        "[]",
        '"abc"',
        json.dumps({"resource": "action"}),
        json.dumps({"resource": [5]}),
        json.dumps({"resource": {}}),
    ],
)
async def test_identity_bad_permissions(jp_fetch, permissions):
    with pytest.raises(HTTPError) as exc:
        await jp_fetch("api/me", params={"permissions": json.dumps(permissions)})

    r = exc.value.response
    assert r is not None
    assert r.code == 400
    reply = json.loads(r.body.decode())
    assert "permissions should be a JSON dict" in reply["message"]
