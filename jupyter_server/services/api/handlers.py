"""Tornado handlers for api specifications."""

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

from tornado import web
from ...base.handlers import JupyterHandler
import os

class APISpecHandler(web.StaticFileHandler, JupyterHandler):

    def initialize(self):
        web.StaticFileHandler.initialize(self, path=os.path.dirname(__file__))

    @web.authenticated
    def get(self):
        self.log.warning("Serving api spec (experimental, incomplete)")
        self.set_header('Content-Type', 'text/x-yaml')
        return web.StaticFileHandler.get(self, 'api.yaml')

default_handlers = [
    (r"/api/spec.yaml", APISpecHandler)
]
