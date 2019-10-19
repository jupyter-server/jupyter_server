import os, jinja2
from jupyter_server.extension.application import ExtensionApp
from .handlers import RedirectHandler, ParameterHandler, TemplateHandler, TypescriptHandler, ErrorHandler

DEFAULT_STATIC_FILES_PATH = os.path.join(os.path.dirname(__file__), "static")
DEFAULT_TEMPLATE_FILES_PATH = os.path.join(os.path.dirname(__file__), "templates")

class SimpleApp1(ExtensionApp):
    
    # The name of the extension
    extension_name = "simple_ext1"

    # Te url that your extension will serve its homepage.
    default_url = '/template/home'

    # Should your extension expose other server extensions when launched directly?
    load_other_extensions = True

    # Local path to static files directory.
    static_paths = [
        DEFAULT_STATIC_FILES_PATH
    ]

    # Local path to templates directory.
    template_paths = [
        DEFAULT_TEMPLATE_FILES_PATH
    ]

    def initialize_handlers(self):
        self.handlers.extend([
            (r'/simple_ext1/params/(.+)$', ParameterHandler),
            (r'/simple_ext1/template1/(.*)$', TemplateHandler),
            (r'/simple_ext1/redirect', RedirectHandler),
            (r'/simple_ext1/typescript/?', TypescriptHandler),
            (r'/simple_ext1/(.*)', ErrorHandler)
        ])

    def initialize_templates(self):
        jenv_opt = {"autoescape": True}
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.template_paths),
            extensions=["jinja2.ext.i18n"],
            **jenv_opt
        )
        template_settings = {"simple_ext1_jinja2_env": env}
        self.settings.update(**template_settings)

    def initialize_settings(self):
        pass

#-----------------------------------------------------------------------------
# Main entry point
#-----------------------------------------------------------------------------

main = launch_new_instance = SimpleApp1.launch_instance
