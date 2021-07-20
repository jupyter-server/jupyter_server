"""Tornado handlers for frontend config storage."""
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
import json

from tornado import web

from ...base.handlers import APIHandler
from jupyter_server.services.auth.decorator import authorized


RESOURCE_NAME = "config"


class ConfigHandler(APIHandler):
    @web.authenticated
    @authorized("read", resource=RESOURCE_NAME)
    def get(self, section_name):
        self.set_header("Content-Type", "application/json")
        self.finish(json.dumps(self.config_manager.get(section_name)))

    @web.authenticated
    @authorized("write", resource=RESOURCE_NAME)
    def put(self, section_name):
        data = self.get_json_body()  # Will raise 400 if content is not valid JSON
        self.config_manager.set(section_name, data)
        self.set_status(204)

    @web.authenticated
    @authorized("write", resource=RESOURCE_NAME)
    def patch(self, section_name):
        new_data = self.get_json_body()
        section = self.config_manager.update(section_name, new_data)
        self.finish(json.dumps(section))


# URL to handler mappings

section_name_regex = r"(?P<section_name>\w+)"

default_handlers = [
    (r"/api/config/%s" % section_name_regex, ConfigHandler),
]
