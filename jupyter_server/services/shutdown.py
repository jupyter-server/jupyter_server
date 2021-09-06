"""HTTP handler to shut down the Jupyter server.
"""
from tornado import ioloop
from tornado import web

from jupyter_server.base.handlers import JupyterHandler


class ShutdownHandler(JupyterHandler):
    @web.authenticated
    async def post(self):
        self.log.info("Shutting down on /api/shutdown request.")

        await self.terminal_manager.terminate_all()
        await self.kernel_manager.shutdown_all()

        ioloop.IOLoop.current().stop()


default_handlers = [
    (r"/api/shutdown", ShutdownHandler),
]
