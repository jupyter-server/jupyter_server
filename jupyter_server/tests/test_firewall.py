import logging

import pytest
from tornado.httputil import HTTPServerRequest, HTTPHeaders
from tornado.log import access_log
from jupyter_server.firewall import FireWall

access_log.setLevel(logging.DEBUG)

spec1 = {
    "openapi": "3.0.1",
    "info": {"title": "Test specs", "version": "0.0.1"},
    "paths": {
        "/pet": {
            "put": {
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/Pet"}
                        },
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

spec2 = {
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


def format_id(val):
    if isinstance(val, HTTPServerRequest):
        return f"{val.method}-{val.uri}-{val.body.decode('utf-8') or None}"


@pytest.mark.parametrize(
    "base_url, server_request, expected",
    (
        (
            "/",
            HTTPServerRequest(
                "put",
                "/pet",
                body=b'{"name":"puppy"}',
                headers=HTTPHeaders({"Content-Type": "application/json"}),
                host="localhost:8888",
            ),
            True,
        ),
        (
            "/dummy/base_url/",
            HTTPServerRequest(
                "put",
                "/dummy/base_url/pet",
                body=b'{"name":"puppy"}',
                headers=HTTPHeaders({"Content-Type": "application/json"}),
                host="localhost:8888",
            ),
            True,
        ),
        # No body
        (
            "/",
            HTTPServerRequest(
                "put",
                "/pet",
                body=b"",
                headers=HTTPHeaders({"Content-Type": "application/json"}),
                host="localhost:8888",
            ),
            False,
        ),
        # Wrong body
        (
            "/",
            HTTPServerRequest(
                "put",
                "/pet",
                body=b'{"id":"puppy"}',
                headers=HTTPHeaders({"Content-Type": "application/json"}),
                host="localhost:8888",
            ),
            False,
        ),
        # Method not allowed
        (
            "/",
            HTTPServerRequest(
                "get",
                "/pet",
                body=b'{"name":"puppy"}',
                headers=HTTPHeaders({"Content-Type": "application/json"}),
                host="localhost:8888",
            ),
            False,
        ),
        (
            "/",
            HTTPServerRequest(
                "get",
                "/pet/22",
                host="localhost:8888",
            ),
            True,
        ),
        # Wrong path parameter
        (
            "/",
            HTTPServerRequest(
                "get",
                "/pet/hello",
                host="localhost:8888",
            ),
            False,
        ),
        (
            "/",
            HTTPServerRequest(
                "get",
                "/pet/findByTags?tags=cat",
                host="localhost:8888",
            ),
            True,
        ),
        # Missing query parameter
        (
            "/",
            HTTPServerRequest(
                "get",
                "/pet/findByTags",
                host="localhost:8888",
            ),
            False,
        ),
    ),
    ids=format_id,
)
def test_Firewall_allowed_spec(base_url, server_request, expected):
    firewall = FireWall(base_url, spec1, None)

    assert firewall.validate(server_request) == expected


@pytest.mark.parametrize(
    "base_url, server_request, expected",
    (
        (
            "/",
            HTTPServerRequest(
                "put",
                "/pet",
                body=b'{"name":"puppy"}',
                headers=HTTPHeaders({"Content-Type": "application/json"}),
                host="localhost:8888",
            ),
            False,
        ),
        (
            "/dummy/base_url/",
            HTTPServerRequest(
                "put",
                "/dummy/base_url/pet",
                body=b'{"name":"puppy"}',
                headers=HTTPHeaders({"Content-Type": "application/json"}),
                host="localhost:8888",
            ),
            False,
        ),
        # No body
        (
            "/",
            HTTPServerRequest(
                "put",
                "/pet",
                body=b"",
                headers=HTTPHeaders({"Content-Type": "application/json"}),
                host="localhost:8888",
            ),
            False,
        ),
        (
            "/",
            HTTPServerRequest(
                "put",
                "/pet?tags=22",
                host="localhost:8888",
            ),
            False,
        ),
        # Other method
        (
            "/",
            HTTPServerRequest(
                "get",
                "/pet",
                body=b'{"name":"puppy"}',
                headers=HTTPHeaders({"Content-Type": "application/json"}),
                host="localhost:8888",
            ),
            True,
        ),
        (
            "/",
            HTTPServerRequest(
                "put",
                "/pet/22",
                host="localhost:8888",
            ),
            True,
        ),
        (
            "/",
            HTTPServerRequest(
                "get",
                "/user?id=42",
                host="localhost:8888",
            ),
            True,
        ),
        (
            "/",
            HTTPServerRequest(
                "get",
                "/user/john/smith",
                host="localhost:8888",
            ),
            False,
        ),
        (
            "/",
            HTTPServerRequest(
                "get",
                "/user/william?page=42",
                host="localhost:8888",
            ),
            False,
        ),
    ),
    ids=format_id,
)
def test_Firewall_blocked_spec(base_url, server_request, expected):
    firewall = FireWall(base_url, None, spec2)

    assert firewall.validate(server_request) == expected


def test_Firewall_allowed_and_blocked_spec():
    pass
