import json

from tornado import web

from ..base.handlers import APIHandler
from jupyter_server.services.auth.decorator import authorized


RESOURCE_NAME = "terminal"


class TerminalRootHandler(APIHandler):
    @web.authenticated
    @authorized("read", resource=RESOURCE_NAME)
    def get(self):
        models = self.terminal_manager.list()
        self.finish(json.dumps(models))

    @web.authenticated
    @authorized("write", resource=RESOURCE_NAME)
    def post(self):
        """POST /terminals creates a new terminal and redirects to it"""
        data = self.get_json_body() or {}

        model = self.terminal_manager.create(**data)
        self.finish(json.dumps(model))


class TerminalHandler(APIHandler):
    SUPPORTED_METHODS = ("GET", "DELETE")

    @web.authenticated
    @authorized("read", resource=RESOURCE_NAME)
    def get(self, name):
        model = self.terminal_manager.get(name)
        self.finish(json.dumps(model))

    @web.authenticated
    @authorized("write", resource=RESOURCE_NAME)
    async def delete(self, name):
        await self.terminal_manager.terminate(name, force=True)
        self.set_status(204)
        self.finish()
