import os, jinja2
from .handler import ServerSimpleHandler
from .handler_template import ServerSimpleTemplateHandler
from jupyter_server.extension.application import ExtensionApp

DEFAULT_STATIC_FILES_PATH = os.path.join(os.path.dirname(__file__), "static")
DEFAULT_TEMPLATE_FILES_PATH = os.path.join(os.path.dirname(__file__), "templates")

class ServerSimple(ExtensionApp):
    
    # Name of the extension
    extension_name = "server_simple"

    # Local path to static files directory.
    static_paths = [
        DEFAULT_STATIC_FILES_PATH
    ]

    # Local path to templates directory.
    template_paths = [
        DEFAULT_TEMPLATE_FILES_PATH
    ]

    def initialize_handlers(self):
        self.handlers.append(
            (r'/server_simple', ServerSimpleHandler, {})
        )
        self.handlers.append(
            (r'/server_simple/(.+)$', ServerSimpleHandler, {})
        )
        self.handlers.append(
            (r'/template', ServerSimpleTemplateHandler, {})
        )

    def initialize_templates(self):
        jenv_opt = {"autoescape": True}
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.template_paths),
            extensions=["jinja2.ext.i18n"],
            **jenv_opt
        )
        template_settings = {"server_simple_jinja2_env": env}
        self.settings.update(**template_settings)

    def initialize_settings(self):
        pass

#-----------------------------------------------------------------------------
# Main entry point
#-----------------------------------------------------------------------------

main = launch_new_instance = ServerSimple.launch_instance
