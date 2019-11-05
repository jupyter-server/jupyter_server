import os
from simple_ext1.application import SimpleApp1
from jupyter_server.serverapp import aliases, flags
from traitlets import Bool, Unicode, observe

DEFAULT_STATIC_FILES_PATH = os.path.join(os.path.dirname(__file__), "./../simple_ext1/static")
DEFAULT_TEMPLATE_FILES_PATH = os.path.join(os.path.dirname(__file__), "./../simple_ext1/templates")

class SimpleApp11(SimpleApp1):
    flags['hello']=(
        { 'SimpleApp11' : {'hello' : False} }, "Say hello on startup."
    )
    aliases.update({
        'simple11-dir': 'SimpleApp11.simple11_dir',
    })
    
    # The name of the extension.
    extension_name = "simple_ext11"

    # Te url that your extension will serve its homepage.
    default_url = '/simple_ext11/default'

    # Local path to static files directory.
    static_paths = [
        DEFAULT_STATIC_FILES_PATH
    ]

    # Local path to templates directory.
    template_paths = [
        DEFAULT_TEMPLATE_FILES_PATH
    ]

    simple11_dir = Unicode('',
        config=True,
        help='Simple directory'
    )

    hello = Bool(False,
        config=True,
        help='Say hello', 
    )

    ignore_js = Bool(False,
        config=True,
        help='Ignore Javascript', 
    )

    @observe('ignore_js')
    def _update_ignore_js(self, change):
        """TODO The observe does not work"""
        self.log.info('ignore_js has just changed: {}'.format(change))

    @property
    def simple11_dir_formatted(self):
        return "/" + self.simple11_dir

    def get_conf(self, key):
        return self.settings.get('config').get('SimpleApp11').get(key, None)

    def initialize_settings(self):
        self.log.info('SimpleApp11.hello: {}'.format(self.get_conf('hello')))
        self.log.info('hello: {}'.format(self.hello))
        if self.get_conf('hello') == True:
            self.log.info("Hello Simple11 - You have provided the --hello flag or defined 'c.SimpleApp1.hello == True' in jupyter_server_config.py")
        self.log.info('SimpleApp11.simple11_dir: {}'.format(self.get_conf('simple11_dir')))
        self.log.info('SimpleApp11.ignore_js: {}'.format(self.get_conf('ignore_js')))
        self.log.info('ignore_js: {}'.format(self.ignore_js))
        # TODO Check this setting/config handling... Updating does not look to be fine here...
        self.settings["{}_config".format(self.extension_name)].update(**self.settings.get('config').get('SimpleApp11'))
        super().initialize_settings()

#-----------------------------------------------------------------------------
# Main entry point
#-----------------------------------------------------------------------------

main = launch_new_instance = SimpleApp11.launch_instance
