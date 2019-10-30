import os
from simple_ext1.application import SimpleApp1

DEFAULT_STATIC_FILES_PATH = os.path.join(os.path.dirname(__file__), "./../simple_ext1/static")
DEFAULT_TEMPLATE_FILES_PATH = os.path.join(os.path.dirname(__file__), "./../simple_ext1/templates")

class SimpleApp11(SimpleApp1):
    
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

    def initialize_handlers(self):
        super().initialize_handlers()

    def initialize_templates(self):
        super().initialize_templates()

    def initialize_settings(self):
        super().initialize_templates()

#-----------------------------------------------------------------------------
# Main entry point
#-----------------------------------------------------------------------------

main = launch_new_instance = SimpleApp11.launch_instance
