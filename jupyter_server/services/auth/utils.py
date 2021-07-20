"""A module with various utility methods for authorization in Jupyter Server.
"""
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
import importlib
import re

from jupyter_server.serverapp import JUPYTER_SERVICE_HANDLERS


HTTP_METHOD_TO_AUTH_ACTION = {
    "GET": "read",
    "HEAD": "read",
    "POST": "write",
    "PUT": "write",
    "PATCH": "write",
    "DELETE": "write",
    "WEBSOCKET": "execute",
}


def get_regex_to_resource_map():
    """Returns a dictionary with all of Jupyter Server's
    request handler URL regex patterns mapped to
    their resource name.

    e.g.
    { "/api/contents/<regex_pattern>": "contents", ...}
    """
    modules = []
    for mod in JUPYTER_SERVICE_HANDLERS.values():
        if mod:
            modules.extend(mod)
    resource_map = {}
    for handler_module in modules:
        mod = importlib.import_module(handler_module)
        name = mod.RESOURCE_NAME
        for handler in mod.default_handlers:
            url_regex = handler[0]
            resource_map[url_regex] = name
    return resource_map


def match_url_to_resource(url, regex_mapping=None):
    """Finds the JupyterHandler regex pattern that would
    match the given URL and returns the resource name (str)
    of that handler.

    e.g.
    /api/contents/... returns "contents"
    """
    if not regex_mapping:
        regex_mapping = get_regex_to_resource_map()
    for regex, resource_name in regex_mapping.items():
        pattern = re.compile(regex)
        if pattern.fullmatch(url):
            return resource_name
