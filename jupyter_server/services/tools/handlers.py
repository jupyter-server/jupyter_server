from tornado import web
from jupyter_server.base.handlers import APIHandler

class ListToolInfoHandler(APIHandler):
    @web.authenticated
    async def get(self):
        tools = self.serverapp.extension_manager.discover_tools()
        self.finish({"discovered_tools": tools}) 



default_handlers = [
        (r"/api/tools", ListToolInfoHandler),
]