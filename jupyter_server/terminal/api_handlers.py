import json
import os

from tornado import web

from ..base.handlers import APIHandler
from jupyter_server.auth import authorized


AUTH_RESOURCE = "terminals"


class TerminalAPIHandler(APIHandler):
    auth_resource = AUTH_RESOURCE


class TerminalRootHandler(TerminalAPIHandler):
    @web.authenticated
    @authorized
    def get(self):
        models = self.terminal_manager.list()
        self.finish(json.dumps(models))

    @web.authenticated
    @authorized
    def post(self):
        """POST /terminals creates a new terminal and redirects to it"""
        data = self.get_json_body() or {}

        # if cwd is a relative path, it should be relative to the root_dir,
        # but if we pass it as relative, it will we be considered as relative to
        # the path jupyter_server was started in
        if "cwd" in data.keys():
            if not os.path.isabs(data["cwd"]):
                cwd = data["cwd"]
                cwd = os.path.join(self.settings["server_root_dir"], cwd)
                data["cwd"] = cwd

        model = self.terminal_manager.create(**data)
        self.finish(json.dumps(model))


class TerminalHandler(TerminalAPIHandler):
    SUPPORTED_METHODS = ("GET", "DELETE")

    @web.authenticated
    @authorized
    def get(self, name):
        model = self.terminal_manager.get(name)
        self.finish(json.dumps(model))

    @web.authenticated
    @authorized
    async def delete(self, name):
        await self.terminal_manager.terminate(name, force=True)
        self.set_status(204)
        self.finish()
