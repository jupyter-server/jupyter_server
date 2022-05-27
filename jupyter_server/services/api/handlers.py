"""Tornado handlers for api specifications."""
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
import json
import os
from typing import Dict, List

from tornado import web

from jupyter_server._tz import isoformat, utcfromtimestamp
from jupyter_server.auth import authorized
from jupyter_server.utils import ensure_async

from ...base.handlers import APIHandler, JupyterHandler

AUTH_RESOURCE = "api"


class APISpecHandler(web.StaticFileHandler, JupyterHandler):
    auth_resource = AUTH_RESOURCE

    def initialize(self):
        web.StaticFileHandler.initialize(self, path=os.path.dirname(__file__))

    @web.authenticated
    @authorized
    def get(self):
        self.log.warning("Serving api spec (experimental, incomplete)")
        return web.StaticFileHandler.get(self, "api.yaml")

    def get_content_type(self):
        return "text/x-yaml"


class APIStatusHandler(APIHandler):

    auth_resource = AUTH_RESOURCE
    _track_activity = False

    @web.authenticated
    @authorized
    async def get(self):
        # if started was missing, use unix epoch
        started = self.settings.get("started", utcfromtimestamp(0))
        started = isoformat(started)

        kernels = await ensure_async(self.kernel_manager.list_kernels())
        total_connections = sum(k["connections"] for k in kernels)
        last_activity = isoformat(self.application.last_activity())
        model = {
            "started": started,
            "last_activity": last_activity,
            "kernels": len(kernels),
            "connections": total_connections,
        }
        self.finish(json.dumps(model, sort_keys=True))


class IdentityHandler(APIHandler):
    """Get the current user's identity model"""

    @web.authenticated
    def get(self):
        permissions_json: str = self.get_argument("permissions", "")
        bad_permissions_msg = f'permissions should be a JSON dict of {{"resource": ["action",]}}, got {permissions_json!r}'
        if permissions_json:
            try:
                permissions_to_check = json.loads(permissions_json)
            except ValueError:
                raise web.HTTPError(400, bad_permissions_msg)
            if not isinstance(permissions_to_check, dict):
                raise web.HTTPError(400, bad_permissions_msg)
        else:
            permissions_to_check = {}

        permissions: Dict[str, List[str]] = {}
        user = self.current_user

        for resource, actions in permissions_to_check.items():
            if (
                not isinstance(resource, str)
                or not isinstance(actions, list)
                or not all(isinstance(action, str) for action in actions)
            ):
                raise web.HTTPError(400, bad_permissions_msg)

            allowed = permissions[resource] = []
            for action in actions:
                if self.authorizer.is_authorized(self, user=user, resource=resource, action=action):
                    allowed.append(action)

        identity: Dict = self.identity_provider.identity_model(user)
        model = {
            "identity": identity,
            "permissions": permissions,
        }
        self.write(json.dumps(model))


default_handlers = [
    (r"/api/spec.yaml", APISpecHandler),
    (r"/api/status", APIStatusHandler),
    (r"/api/me", IdentityHandler),
]
