"""HTTP handler to shut down the Jupyter server.
"""
from tornado import ioloop
from tornado import web

from jupyter_server.base.handlers import JupyterHandler


class ShutdownHandler(JupyterHandler):
    @web.authenticated
    async def post(self):
        self.log.info("Shutting down on /api/shutdown request.")

        await self.serverapp._cleanup()

        ioloop.IOLoop.current().stop()


default_handlers = [
    (r"/api/shutdown", ShutdownHandler),
]
