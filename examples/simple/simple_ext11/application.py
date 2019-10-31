import os
from simple_ext1.application import SimpleApp1
from jupyter_server.serverapp import aliases, flags

DEFAULT_STATIC_FILES_PATH = os.path.join(os.path.dirname(__file__), "./../simple_ext1/static")
DEFAULT_TEMPLATE_FILES_PATH = os.path.join(os.path.dirname(__file__), "./../simple_ext1/templates")

class SimpleApp11(SimpleApp1):
    flags['hello']=(
        {'SimpleApp11' : {'hello' : True}},
        "Say hello on startup."
    )
    aliases.update({
        'notebook-dir': 'ServerApp.notebook_dir',
    })
    
    # The name of the extension.
    extension_name = "simple_ext11"

    # Local path to static files directory.
    static_paths = [
        DEFAULT_STATIC_FILES_PATH
    ]

    # Local path to templates directory.
    template_paths = [
        DEFAULT_TEMPLATE_FILES_PATH
    ]

    def get_conf(self, key):
        simple_app_11 = self.settings.get('config').get('SimpleApp11')
        if simple_app_11:
            return simple_app_11.get(key, None)
        return None

    def initialize_settings(self):
        if self.get_conf('hello') == True:
            self.log.info('Hello Simple11 - You have provided the --hello flag or defined a c.SimpleApp1.hello == True')
        super().initialize_settings()

#-----------------------------------------------------------------------------
# Main entry point
#-----------------------------------------------------------------------------

main = launch_new_instance = SimpleApp11.launch_instance
