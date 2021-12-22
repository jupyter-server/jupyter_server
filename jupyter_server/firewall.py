from typing import Optional, Union

from openapi_core import create_spec
from tornado import httpclient, httputil
from tornado.log import access_log
from tornado_openapi3 import RequestValidator


class FireWall:
    """Validate server request against a list of allowed and blocked OpenAPI v3 specifications.
    
    If allowed and blocked specifications are defined, the request must be allowed and not blocked;
    i.e. blocked specification takes precedence.

    Args:
        allowed_spec: [optional] Allowed endpoints
        blocked_spec: [optional] Blocked endpoints
    """

    def __init__(self, base_url: str, allowed_spec: Optional[dict], blocked_spec: Optional[dict]):
        self.__allowed_validator: Optional[RequestValidator] = None
        self.__blocked_validator: Optional[RequestValidator] = None

        def add_base_url_server(spec: dict):
            servers = spec.get("servers", [])
            if not any(map(lambda s: s.get("url") == base_url, servers)):
                servers.append({
                    "url": base_url
                })
            spec["servers"] = servers

        if allowed_spec is not None:
            add_base_url_server(allowed_spec)
            self.__allowed_validator = RequestValidator(create_spec(allowed_spec))
        if blocked_spec is not None:
            add_base_url_server(blocked_spec)
            self.__blocked_validator = RequestValidator(create_spec(blocked_spec))

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

        allowed = (allowed_result is None or len(allowed_result.errors) == 0)
        not_blocked = (
            blocked_result is None or len(blocked_result.errors) > 0
        )

        # The error raised if this is not valid will be logged
        # So we only give the reason in debug level
        if (not (allowed and not_blocked)):
            if(not allowed):
                # Provides only the first error
                access_log.debug(f"Request not allowed: {allowed_result.errors[0]!s}")
            elif (not not_blocked):
                access_log.debug(f"Request blocked.")

        return allowed and not_blocked
