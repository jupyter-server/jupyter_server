"""A simple Jupyter Server extension example."""
import os

from traitlets import Unicode

from jupyter_server.extension.application import ExtensionApp, ExtensionAppJinjaMixin

from .handlers import ErrorHandler, IndexHandler, ParameterHandler, TemplateHandler

DEFAULT_STATIC_FILES_PATH = os.path.join(os.path.dirname(__file__), "static")
DEFAULT_TEMPLATE_FILES_PATH = os.path.join(os.path.dirname(__file__), "templates")


class SimpleApp2(ExtensionAppJinjaMixin, ExtensionApp):
    """A simple application."""

    # The name of the extension.
    name = "simple_ext2"

    # The url that your extension will serve its homepage.
    extension_url = "/simple_ext2"

    # Should your extension expose other server extensions when launched directly?
    load_other_extensions = True

    # Local path to static files directory.
    static_paths = [DEFAULT_STATIC_FILES_PATH]  # type:ignore[assignment]

    # Local path to templates directory.
    template_paths = [DEFAULT_TEMPLATE_FILES_PATH]  # type:ignore[assignment]

    configD = Unicode("", config=True, help="Config D example.")  # noqa

    def initialize_handlers(self):
        """Initialize handlers."""
        self.handlers.extend(
            [
                (r"/simple_ext2/params/(.+)$", ParameterHandler),
                (r"/simple_ext2/template", TemplateHandler),
                (r"/simple_ext2/?", IndexHandler),
                (r"/simple_ext2/(.*)", ErrorHandler),
            ]
        )

    def initialize_settings(self):
        """Initialize settings."""
        self.log.info(f"Config {self.config}")


# -----------------------------------------------------------------------------
# Main entry point
# -----------------------------------------------------------------------------

main = launch_new_instance = SimpleApp2.launch_instance
