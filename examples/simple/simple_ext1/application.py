import os, jinja2
from traitlets import Unicode
from jupyter_server.extension.application import ExtensionApp, ExtensionAppJinjaMixin
from .handlers import (DefaultHandler, RedirectHandler,
  ParameterHandler, TemplateHandler, TypescriptHandler, ErrorHandler)

DEFAULT_STATIC_FILES_PATH = os.path.join(os.path.dirname(__file__), "static")
DEFAULT_TEMPLATE_FILES_PATH = os.path.join(os.path.dirname(__file__), "templates")

class SimpleApp1(ExtensionAppJinjaMixin, ExtensionApp):

    # The name of the extension.
    name = "simple_ext1"

    # The url that your extension will serve its homepage.
    extension_url = '/simple_ext1/default'

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

    configA = Unicode('',
        config=True,
        help='Config A example.'
    )

    configB = Unicode('',
        config=True,
        help='Config B example.'
    )

    configC = Unicode('',
        config=True,
        help='Config C example.'
    )

    def initialize_handlers(self):
        self.handlers.extend([
            (r'/{}/default'.format(self.name), DefaultHandler),
            (r'/{}/params/(.+)$'.format(self.name), ParameterHandler),
            (r'/{}/template1/(.*)$'.format(self.name), TemplateHandler),
            (r'/{}/redirect'.format(self.name), RedirectHandler),
            (r'/{}/typescript/?'.format(self.name), TypescriptHandler),
            (r'/{}/(.*)', ErrorHandler)
        ])

    def initialize_settings(self):
        self.log.info('Config {}'.format(self.config))

#-----------------------------------------------------------------------------
# Main entry point
#-----------------------------------------------------------------------------

main = launch_new_instance = SimpleApp1.launch_instance
