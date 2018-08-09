import json
from tornado import web
from ..base.handlers import APIHandler


class TerminalRootHandler(APIHandler):

    @web.authenticated
    def get(self):
        tm = self.terminal_manager
        terms = [{'name': name} for name in tm.terminals]
        self.finish(json.dumps(terms))

    @web.authenticated
    def post(self):
        """POST /terminals creates a new terminal and redirects to it"""
        name, _ = self.terminal_manager.new_named_terminal()
        self.finish(json.dumps({'name': name}))


class TerminalHandler(APIHandler):
    SUPPORTED_METHODS = ('GET', 'DELETE')

    @web.authenticated
    def get(self, name):
        tm = self.terminal_manager
        if name in tm.terminals:
            self.finish(json.dumps({'name': name}))
        else:
            raise web.HTTPError(404, "Terminal not found: %r" % name)

    @web.authenticated
    async def delete(self, name):
        tm = self.terminal_manager
        if name in tm.terminals:
            await tm.terminate(name, force=True)
            self.set_status(204)
            self.finish()
        else:
            raise web.HTTPError(404, "Terminal not found: %r" % name)
