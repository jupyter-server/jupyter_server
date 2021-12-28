import itertools
import re
from typing import Iterable, Optional, Union
from urllib.parse import parse_qsl

from openapi_core import create_spec
from openapi_core.validation.request import validators
from openapi_core.validation.request.datatypes import (
    OpenAPIRequest,
    RequestParameters,
    RequestValidationResult,
)
from openapi_spec_validator.handlers import base
from tornado import httpclient, httputil
from tornado.log import access_log
from tornado_openapi3.util import parse_mimetype
from werkzeug.datastructures import Headers, ImmutableMultiDict


def encode_slash(regex: Iterable[Union[str, re.Pattern]], path: str) -> str:
    """Encode slash (``%2F``) for regex groups found in URL path (it never contains the query arguments).

    Note:
        The regex order matters as only the first regex matching the path will be applied.

    Args:
        regex: List of regex to test the path against
        path: URL path to escape

    Returns:
        Escaped path
    """
    regex = [re.compile(r) if isinstance(r, str) else r for r in regex]
    for r in regex:
        m = re.search(r, path)
        if m is not None and m.lastindex is not None:
            # Start from latest group to the first one so that position is preserved
            #   Skip the first group as it matches the full path not only the group to be encoded
            for index in range(m.lastindex, 0, -1):
                path = (
                    path[: m.start(index)]
                    + path[m.start(index) : m.end(index)].replace("/", r"%2F")
                    + path[m.end(index) :]
                )
            # Break at first match
            break

    return path


# Ref: https://github.com/correl/tornado-openapi3/blob/master/tornado_openapi3/requests.py
class TornadoRequestFactory:
    """Factory for converting Tornado requests to OpenAPI request objects."""

    @classmethod
    def create(
        cls,
        request: Union[httpclient.HTTPRequest, httputil.HTTPServerRequest],
        encoded_slash_regex: Iterable[re.Pattern],
    ) -> OpenAPIRequest:
        """Creates an OpenAPI request from Tornado request objects.

        Supports both :class:`tornado.httpclient.HTTPRequest` and
        :class:`tornado.httputil.HTTPServerRequest` objects.
        """
        if isinstance(request, httpclient.HTTPRequest):
            if request.url:
                path, _, querystring = request.url.partition("?")
                query_arguments: ImmutableMultiDict[str, str] = ImmutableMultiDict(
                    parse_qsl(querystring)
                )
            else:
                path = ""
                query_arguments = ImmutableMultiDict()
        else:
            path, _, _ = request.full_url().partition("?")
            if path == "://":
                path = ""
            query_arguments = ImmutableMultiDict(
                itertools.chain(
                    *[
                        [(k, v.decode("utf-8")) for v in vs]
                        for k, vs in request.query_arguments.items()
                    ]
                )
            )

        # Encode slashes in path to be compliant with Open API specification
        # e.g. /api/contents/path/to/file.txt -> /api/contents/path%2Fto%2Ffile.txt
        path = encode_slash(encoded_slash_regex, path)

        return OpenAPIRequest(
            full_url_pattern=path,
            method=request.method.lower() if request.method else "get",
            parameters=RequestParameters(
                query=query_arguments,
                header=Headers(request.headers.get_all()),
                cookie=httputil.parse_cookie(request.headers.get("Cookie", "")),
            ),
            body=request.body if request.body else b"",
            mimetype=parse_mimetype(
                request.headers.get("Content-Type", "application/x-www-form-urlencoded")
            ),
        )


class RequestValidator(validators.RequestValidator):
    """Validator for Tornado HTTP Requests.

    Args:
        base_url: [optional] Server base URL
        custom_formatters: [optional]
        custom_media_type_deserializers: [optional]
        encoded_slash_regex: [optional] Regex expression to find part of URL path in which ``/`` must be escaped
    """

    def __init__(
        self,
        spec,
        base_url: Optional[str] = None,
        custom_formatters=None,
        custom_media_type_deserializers=None,
        encoded_slash_regex: Optional[Iterable[re.Pattern]] = None,
    ):
        super().__init__(
            spec,
            base_url=base_url,
            custom_formatters=custom_formatters,
            custom_media_type_deserializers=custom_media_type_deserializers,
        )
        self.__encoded_slash_regex = encoded_slash_regex

    def validate(
        self, request: Union[httpclient.HTTPRequest, httputil.HTTPServerRequest]
    ) -> RequestValidationResult:
        """Validate a Tornado HTTP request object."""
        return super().validate(
            TornadoRequestFactory.create(request, self.__encoded_slash_regex)
        )


class SpecValidator:
    """Validate server request against a list of allowed and blocked OpenAPI v3 specifications.

    If allowed and blocked specifications are defined, the request must be allowed and not blocked;
    i.e. blocked specification takes precedence.

    Note:
        OpenAPI does not accept path argument containing ``/``. Therefore you should provide regex to encode
        them; e.g. ``"/api/contents/([^/]+(?:/[^/]+)*?)$"`` to match ``/api/contents/{path}``. The order in
        which you provide the regex are important as only the first regex matching the path will be applied.
        You can test your expression using :ref:`jupyter_server.specvalidator.encode_slash`.

    Args:
        base_url: [optional] Server base URL
        allowed_spec: [optional] Allowed endpoints
        blocked_spec: [optional] Blocked endpoints
        encoded_slash_regex: [optional] Regex expression to find part of URL path in which ``/`` must be escaped
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        allowed_spec: Optional[dict] = None,
        blocked_spec: Optional[dict] = None,
        encoded_slash_regex: Optional[Iterable[str]] = None,
    ):
        self.__allowed_validator: Optional[RequestValidator] = None
        self.__blocked_validator: Optional[RequestValidator] = None
        slash_regex: Iterable[re.Pattern] = list(
            map(lambda s: re.compile(s), encoded_slash_regex or [])
        )

        def add_base_url_server(spec: dict):
            servers = spec.get("servers", [])
            if not any(map(lambda s: s.get("url") == base_url, servers)):
                servers.append({"url": base_url})
            spec["servers"] = servers

        if allowed_spec is not None:
            if base_url is not None:
                add_base_url_server(allowed_spec)
            self.__allowed_validator = RequestValidator(
                create_spec(allowed_spec),
                encoded_slash_regex=slash_regex,
            )
        if blocked_spec is not None:
            if base_url is not None:
                add_base_url_server(blocked_spec)
            self.__blocked_validator = RequestValidator(
                create_spec(blocked_spec),
                encoded_slash_regex=slash_regex,
            )

    def validate(
        self, request: Union[httpclient.HTTPRequest, httputil.HTTPServerRequest]
    ) -> bool:
        """Validate a request against allowed and blocked specifications.

        Args:
            request: Request to validate
        Returns:
            Whether the request is valid or not.
        """
        allowed_result = (
            None
            if self.__allowed_validator is None
            else self.__allowed_validator.validate(request)
        )

        blocked_result = (
            None
            if self.__blocked_validator is None
            else self.__blocked_validator.validate(request)
        )

        allowed = allowed_result is None or len(allowed_result.errors) == 0
        not_blocked = blocked_result is None or len(blocked_result.errors) > 0

        # The error raised if this is not valid will be logged
        # So we only give the reason in debug level
        if not (allowed and not_blocked):
            if not allowed:
                # Provides only the first error
                access_log.debug(f"Request not allowed: {allowed_result.errors[0]!s}")
            elif not not_blocked:
                access_log.debug(f"Request blocked.")

        return allowed and not_blocked
