import json

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
