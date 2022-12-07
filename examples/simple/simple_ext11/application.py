import os

from simple_ext1.application import SimpleApp1  # type:ignore
from traitlets import Bool, Unicode, observe

from jupyter_server.serverapp import aliases, flags

DEFAULT_STATIC_FILES_PATH = os.path.join(os.path.dirname(__file__), "./../simple_ext1/static")
DEFAULT_TEMPLATE_FILES_PATH = os.path.join(os.path.dirname(__file__), "./../simple_ext1/templates")


class SimpleApp11(SimpleApp1):
    flags["hello"] = ({"SimpleApp11": {"hello": True}}, "Say hello on startup.")
    aliases.update(
        {
            "simple11-dir": "SimpleApp11.simple11_dir",
        }
    )

    # The name of the extension.
    name = "simple_ext11"

    # Te url that your extension will serve its homepage.
    extension_url = "/simple_ext11/default"

    # Local path to static files directory.
    static_paths = [DEFAULT_STATIC_FILES_PATH]

    # Local path to templates directory.
    template_paths = [DEFAULT_TEMPLATE_FILES_PATH]

    simple11_dir = Unicode("", config=True, help="Simple directory")

    hello = Bool(
        False,
        config=True,
        help="Say hello",
    )

    ignore_js = Bool(
        False,
        config=True,
        help="Ignore Javascript",
    )

    @observe("ignore_js")
    def _update_ignore_js(self, change):
        """TODO Does the observe work?"""
        self.log.info(f"ignore_js has just changed: {change}")

    @property
    def simple11_dir_formatted(self):
        return "/" + self.simple11_dir

    def initialize_settings(self):
        self.log.info(f"hello: {self.hello}")
        if self.hello is True:
            self.log.info(
                "Hello Simple11: You have launched with --hello flag or defined 'c.SimpleApp1.hello == True' in your config file"
            )
        self.log.info(f"ignore_js: {self.ignore_js}")
        super().initialize_settings()

    def initialize_handlers(self):
        super().initialize_handlers()


# -----------------------------------------------------------------------------
# Main entry point
# -----------------------------------------------------------------------------

main = launch_new_instance = SimpleApp11.launch_instance
