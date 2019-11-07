import os, jinja2
from jupyter_server.extension.application import ExtensionApp
from .handlers import (DefaultHandler, RedirectHandler, 
  ParameterHandler, TemplateHandler, TypescriptHandler, ErrorHandler)

DEFAULT_STATIC_FILES_PATH = os.path.join(os.path.dirname(__file__), "static")
DEFAULT_TEMPLATE_FILES_PATH = os.path.join(os.path.dirname(__file__), "templates")

class SimpleApp1(ExtensionApp):
    
    # The name of the extension.
    extension_name = "simple_ext1"

    # Te url that your extension will serve its homepage.
    default_url = '/simple_ext1/default'

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
            (r'/{}/default'.format(self.extension_name), DefaultHandler),
            (r'/{}/params/(.+)$'.format(self.extension_name), ParameterHandler),
            (r'/{}/template1/(.*)$'.format(self.extension_name), TemplateHandler),
            (r'/{}/redirect'.format(self.extension_name), RedirectHandler),
            (r'/{}/typescript/?'.format(self.extension_name), TypescriptHandler),
            (r'/{}/(.*)', ErrorHandler)
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

    def get_conf(self, key):
        return self.settings.get('config').get('SimpleApp1').get(key, None)

    def initialize_settings(self):
        self.settings.get('config').get('SimpleApp1').update({'app': 'OK'})
        self.log.info('SimpleApp1.app {}'.format(self.get_conf('app')))
        self.log.info('SimpleApp1.file {}'.format(self.get_conf('file')))
        self.log.info('SimpleApp1.cli {}'.format(self.get_conf('cli')))
        self.log.info('Complete Settings {}'.format(self.settings))
        # TODO Check this setting/config handling... Updating does not look to be fine here...
        self.settings["{}_config".format(self.extension_name)].update(**self.settings.get('config').get('SimpleApp1'))

#-----------------------------------------------------------------------------
# Main entry point
#-----------------------------------------------------------------------------

main = launch_new_instance = SimpleApp1.launch_instance
