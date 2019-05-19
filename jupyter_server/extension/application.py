import sys

from traitlets.config.application import catch_config_error
from traitlets.config.configurable import Configurable
from traitlets import (
    Unicode, 
    List, 
    Dict, 
    default, 
    validate
)

from jupyter_core.application import JupyterApp

from jupyter_server.serverapp import ServerApp
from jupyter_server.transutils import trans, _
from jupyter_server.utils import url_path_join
from jupyter_server.base.handlers import FileFindHandler


class ExtensionApp(JupyterApp):
    """A base class for writing configurable Jupyter Server extension applications.

    These applications can be loaded using jupyter_server's 
    extension load mechanism or launched using Jupyter's command line interface.
    """
    # Name of the extension
    extension_name = Unicode(
        "",
        help="Name of extension."
    )

    @default("extension_name")
    def _default_extension_name(self):
        raise Exception("The extension must be given a `name`.")

    @validate("extension_name")
    def _default_extension_name(self, obj, value):
        if isinstance(name, str):
            # Validate that extension_name doesn't contain any invalid characters.
            for char in [' ', '.', '+', '/']:
                self.error(obj, value)
            return value
        self.error(obj, value) 

    # Extension can configure the ServerApp from the command-line
    classes = [
        ServerApp
    ]

    static_file_path = List(Unicode(),
        help="""paths to search for serving static files for the extension."""
    ).tag(config=True)

    template_path = List(Unicode(), 
        help=_("""Paths to search for serving jinja templates for the extension.""")
    ).tag(config=True)

    settings = Dict(
        help=_("""Settings that will passed to the server.""")
    )

    handlers = List(
        help=_("""Handlers appended to the server.""")
    )

    default_url = Unicode('/', config=True,
        help=_("The default URL to redirect to from `/`")
    )

    def initialize_static_handler(self):
        # Check to see if 
        if len(self.static_file_path) > 0:
            # Append the extension's static directory to server handlers.
            static_url = url_path_join("/static", self.extension_name, "(.*)")

            # Construct handler.
            handler = (static_url, FileFindHandler, {'path': self.static_file_path})
            self.handlers.append(handler)

            # Add the file paths to webapp settings.
            self.settings.update({
                "{}_static_path".format(self.extension_name): self.static_file_path,
                "{}_template_path".format(self.extension_name): self.template_path
            })

    def initialize_handlers(self):
        """Override this method to append handlers to a Jupyter Server."""
        pass

    def initialize_templates(self):
        """Override this method to add handling of template files."""
        pass

    def initialize_settings(self):
        """Override this method to add handling of settings."""
        pass

    @staticmethod
    def initialize_server():
        """Add handlers to server."""
        serverapp = ServerApp()
        serverapp.initialize()
        return serverapp

    def initialize(self, serverapp, argv=None):
        """Initialize the extension app."""
        super(ExtensionApp, self).initialize(argv=argv)
        self.serverapp = serverapp

    def start(self, **kwargs):
        """Start the extension app."""
        # Start the server.
        self.serverapp.start()

    @classmethod
    def launch_instance(cls, argv=None, **kwargs):
        """Launch the ServerApp and Server Extension Application. 
        
        Properly orders the steps to initialize and start the server and extension.
        """
        # Initialize the server
        serverapp = cls.initialize_server()

        # Load the extension
        extension = cls.load_jupyter_server_extension(serverapp, argv=argv, **kwargs)
        
        # Start the browser at this extensions default_url.
        serverapp.default_url = extension.default_url

        # Start the application.
        extension.start()

    @classmethod
    def load_jupyter_server_extension(cls, serverapp, argv=None, **kwargs):
        """Load this extension following the server extension loading mechanism."""
        # Get webapp from the server.
        webapp = serverapp.web_app
        
        # Create an instance and initialize extension.
        extension = cls()
        extension.initialize(serverapp, argv=argv)
        extension.initialize_settings()
        extension.initialize_handlers()
        extension.initialize_static_handler()
        extension.initialize_templates()

        # Make extension settings accessible to handlers inside webapp settings.
        webapp.settings.update(**extension.settings)
        webapp.settings.update(**)

        # Add handlers to serverapp.
        webapp.add_handlers('.*$', extension.handlers)

        return extension