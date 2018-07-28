"""HTTP handler to shut down the Jupyter server.
"""
from tornado import web, ioloop
from jupyter_server.base.handlers import JupyterHandler


class ShutdownHandler(JupyterHandler):
    @web.authenticated
    def post(self):
        self.log.info("Shutting down on /api/shutdown request.")
        ioloop.IOLoop.current().stop()


default_handlers = [
    (r"/api/shutdown", ShutdownHandler),
]
