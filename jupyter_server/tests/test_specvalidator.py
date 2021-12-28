import logging

import pytest
from tornado.httputil import HTTPHeaders
from tornado.httputil import HTTPServerRequest
from tornado.log import access_log

pytest.importorskip("tornado_openapi3")

from jupyter_server.specvalidator import SpecValidator, encode_slash


access_log.setLevel(logging.DEBUG)

allowed_spec = {
    "openapi": "3.0.1",
    "info": {"title": "Test specs", "version": "0.0.1"},
    "paths": {
        "/pet": {
            "put": {
                "requestBody": {
                    "content": {
                        "application/json": {"schema": {"$ref": "#/components/schemas/Pet"}},
                    },
                    "required": True,
                },
                "responses": {"400": {"description": ""}},
            }
        },
        "/pet/findByTags": {
            "get": {
                "parameters": [
                    {
                        "name": "tags",
                        "in": "query",
                        "description": "Tags to filter by",
                        "required": True,
                        "style": "form",
                        "schema": {"type": "array", "items": {"type": "string"}},
                    }
                ],
                "responses": {
                    "200": {
                        "description": "successful operation",
                    }
                },
            }
        },
        "/pet/{petId}": {
            "get": {
                "parameters": [
                    {
                        "name": "petId",
                        "in": "path",
                        "description": "ID of pet to return",
                        "required": True,
                        "schema": {"type": "integer", "format": "int64"},
                    }
                ],
                "responses": {"200": {"description": ""}},
            },
        },
    },
    "components": {
        "schemas": {
            "Pet": {
                "required": ["name"],
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "format": "int64"},
                    "name": {"type": "string", "example": "doggie"},
                },
            },
        }
    },
}

blocked_spec = {
    "openapi": "3.0.1",
    "info": {"title": "Test specs", "version": "0.0.1"},
    "paths": {
        "/pet": {
            "put": {
                "responses": {"400": {"description": ""}},
            }
        },
        "/user/{anyId}": {
            "get": {
                "parameters": [
                    {
                        "name": "anyId",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "responses": {"200": {"description": ""}},
            }
        },
    },
}


@pytest.mark.parametrize(
    "base_url, server_request, expected",
    (
        pytest.param(
            "/",
            dict(
                method="put",
                uri="/pet",
                body=b'{"name":"puppy"}',
                headers=dict({"Content-Type": "application/json"}),
                host="localhost:8888",
            ),
            True,
            id="Default case",
        ),
        pytest.param(
            "/dummy/base_url/",
            dict(
                method="put",
                uri="/dummy/base_url/pet",
                body=b'{"name":"puppy"}',
                headers=dict({"Content-Type": "application/json"}),
                host="localhost:8888",
            ),
            True,
            id="Non default base URL",
        ),
        pytest.param(
            "/",
            dict(
                method="put",
                uri="/pet",
                body=b"",
                headers=dict({"Content-Type": "application/json"}),
                host="localhost:8888",
            ),
            False,
            id="No body",
        ),
        pytest.param(
            "/",
            dict(
                method="put",
                uri="/pet",
                body=b'{"id":"puppy"}',
                headers=dict({"Content-Type": "application/json"}),
                host="localhost:8888",
            ),
            False,
            id="Wrong body",
        ),
        pytest.param(
            "/",
            dict(
                method="get",
                uri="/pet",
                body=b'{"name":"puppy"}',
                headers=dict({"Content-Type": "application/json"}),
                host="localhost:8888",
            ),
            False,
            id="Method not allowed",
        ),
        pytest.param(
            "/",
            dict(
                method="get",
                uri="/pet/22",
                host="localhost:8888",
            ),
            True,
            id="Path argument",
        ),
        pytest.param(
            "/",
            dict(
                method="get",
                uri="/pet/hello",
                host="localhost:8888",
            ),
            False,
            id="Wrong path parameter",
        ),
        pytest.param(
            "/",
            dict(
                method="get",
                uri="/pet/findByTags?tags=cat",
                host="localhost:8888",
            ),
            True,
            id="Query parameters",
        ),
        pytest.param(
            "/",
            dict(
                method="get",
                uri="/pet/findByTags",
                host="localhost:8888",
            ),
            False,
            id="Missing query parameter",
        ),
    ),
)
def test_SpecValidator_allowed_spec(base_url, server_request, expected):
    validator = SpecValidator(base_url, allowed_spec, None)

    headers = server_request.pop("headers") if "headers" in server_request else {}

    assert (
        validator.validate(HTTPServerRequest(**server_request, headers=HTTPHeaders(headers)))
        == expected
    )


@pytest.mark.parametrize(
    "base_url, server_request, expected",
    (
        pytest.param(
            "/",
            dict(
                method="put",
                uri="/pet",
                body=b'{"name":"puppy"}',
                headers=dict({"Content-Type": "application/json"}),
                host="localhost:8888",
            ),
            False,
            id="Default case",
        ),
        pytest.param(
            "/dummy/base_url/",
            dict(
                method="put",
                uri="/dummy/base_url/pet",
                body=b'{"name":"puppy"}',
                headers=dict({"Content-Type": "application/json"}),
                host="localhost:8888",
            ),
            False,
            id="Non default base URL",
        ),
        pytest.param(
            "/",
            dict(
                method="put",
                uri="/pet",
                body=b"",
                headers=dict({"Content-Type": "application/json"}),
                host="localhost:8888",
            ),
            False,
            id="Missing body",
        ),
        pytest.param(
            "/",
            dict(
                method="put",
                uri="/pet?tags=22",
                host="localhost:8888",
            ),
            False,
            id="Query argument",
        ),
        pytest.param(
            "/",
            dict(
                method="get",
                uri="/pet",
                body=b'{"name":"puppy"}',
                headers=dict({"Content-Type": "application/json"}),
                host="localhost:8888",
            ),
            True,
            id="Non-blocked method",
        ),
        pytest.param(
            "/",
            dict(
                method="put",
                uri="/pet/22",
                host="localhost:8888",
            ),
            True,
        ),
        pytest.param(
            "/",
            dict(
                method="get",
                uri="/user?id=42",
                host="localhost:8888",
            ),
            True,
        ),
        pytest.param(
            "/",
            dict(
                method="get",
                uri="/user/john/smith",
                host="localhost:8888",
            ),
            True,
            id="Sub path is allowed",
        ),
        pytest.param(
            "/",
            dict(
                method="get",
                uri="/user/william?page=42",
                host="localhost:8888",
            ),
            False,
            id="Blocked path with query argument",
        ),
    ),
)
def test_SpecValidator_blocked_spec(base_url, server_request, expected):
    validator = SpecValidator(base_url, None, blocked_spec)

    headers = server_request.pop("headers") if "headers" in server_request else {}

    assert (
        validator.validate(HTTPServerRequest(**server_request, headers=HTTPHeaders(headers)))
        == expected
    )


@pytest.mark.parametrize(
    "server_request, expected",
    (
        pytest.param(
            dict(
                method="put",
                uri="/pet",
                body=b'{"name":"puppy"}',
                headers=dict({"Content-Type": "application/json"}),
                host="localhost:8888",
            ),
            False,
            id="Blocked although allowed",
        ),
        pytest.param(
            dict(
                method="get",
                uri="/pet/22",
                host="localhost:8888",
            ),
            True,
            id="Allowed and not part of blocked",
        ),
    ),
)
def test_SpecValidator_allowed_and_blocked_spec(server_request, expected):
    validator = SpecValidator(allowed_spec=allowed_spec, blocked_spec=blocked_spec)

    headers = server_request.pop("headers") if "headers" in server_request else {}

    assert (
        validator.validate(HTTPServerRequest(**server_request, headers=HTTPHeaders(headers)))
        == expected
    )


@pytest.mark.parametrize(
    "server_request, expected",
    (
        pytest.param(
            dict(
                method="get",
                uri="/api/contents/path/to/file.txt/checkpoints/.ipynb_checkpoints/file.txt",
                host="localhost:8888",
            ),
            True,
            id="Checkpoint path",
        ),
        pytest.param(
            dict(
                method="get",
                uri="/api/contents/path/to/file.txt",
                host="localhost:8888",
            ),
            True,
            id="Content path",
        ),
        pytest.param(
            dict(
                method="get",
                uri="/api/contents/path/to/file.txt?tags=dummy",
                host="localhost:8888",
            ),
            True,
            id="Encode with query arguments",
        ),
        pytest.param(
            dict(
                method="get",
                uri="/api/sessions/path/to/file.txt",
                host="localhost:8888",
            ),
            False,
            id="Session Id does not support slashes",
        ),
    ),
)
def test_SpecValidator_encoded_slash(server_request, expected):
    validator = SpecValidator(
        allowed_spec={
            "openapi": "3.0.1",
            "info": {"title": "Test specs", "version": "0.0.1"},
            "paths": {
                "/api/contents/{path}": {
                    "get": {
                        "parameters": [
                            {
                                "name": "path",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string"},
                            }
                        ],
                        "responses": {"200": {"description": ""}},
                    },
                },
                "/api/contents/{path}/checkpoints/{checkpointId}": {
                    "get": {
                        "parameters": [
                            {
                                "name": "path",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string"},
                            },
                            {
                                "name": "checkpointId",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string"},
                            },
                        ],
                        "responses": {"200": {"description": ""}},
                    },
                },
                "/api/sessions/{sessionId}": {
                    "get": {
                        "parameters": [
                            {
                                "name": "sessionId",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string"},
                            }
                        ],
                        "responses": {"200": {"description": ""}},
                    },
                },
            },
        },
        encoded_slash_regex=(
            r"/api/contents/([^/?]+(?:(?:/[^/]+)*?))/checkpoints/([^/]+(?:(?:/[^/]+)*?))$",
            r"/api/contents/([^/?]+(?:(?:/[^/]+)*?))$",
            # Test regex without group match
            r"/api/sessions",
        ),
    )

    headers = server_request.pop("headers") if "headers" in server_request else {}

    assert (
        validator.validate(HTTPServerRequest(**server_request, headers=HTTPHeaders(headers)))
        == expected
    )


@pytest.mark.parametrize(
    "regex, test, expected",
    (
        pytest.param(
            (r"/api/contents/([^/]+(?:(?:/[^/]+)*?))$",),
            "/api/contents/path/to/file.txt",
            "/api/contents/path%2Fto%2Ffile.txt",
            id="Path to encode",
        ),
        pytest.param(
            (
                r"/api/contents/([^/]+(?:(?:/[^/]+)*))$",
                r"/api/contents/([^/]+(?:(?:/[^/]+)*?))/checkpoints/([^/]+(?:(?:/[^/]+)*?))$",
            ),
            "/api/contents/path/to/file.txt/checkpoints/.ipynb_checkpoints/file.txt",
            r"/api/contents/path%2Fto%2Ffile.txt%2Fcheckpoints%2F.ipynb_checkpoints%2Ffile.txt",
            id="Bad regex order",
        ),
        pytest.param(
            (
                r"/api/contents/([^/]+(?:(?:/[^/]+)*?))/checkpoints/([^/]+(?:(?:/[^/]+)*?))$",
                r"/api/contents/([^/]+(?:(?:/[^/]+)*))$",
            ),
            "/api/contents/path/to/file.txt/checkpoints/.ipynb_checkpoints/file.txt",
            r"/api/contents/path%2Fto%2Ffile.txt/checkpoints/.ipynb_checkpoints%2Ffile.txt",
            id="Multiple regex",
        ),
        pytest.param(
            (r"/api/contents/([^/]+(?:(?:/[^/]+)*?))$",),
            "/api/sessions/path/to/file.txt",
            "/api/sessions/path/to/file.txt",
            id="No match",
        ),
        pytest.param(
            (r"/api/sessions",),
            "/api/sessions/path/to/file.txt",
            "/api/sessions/path/to/file.txt",
            id="No group",
        ),
    ),
)
def test_encode_slash(regex, test, expected):
    assert encode_slash(regex, test) == expected
