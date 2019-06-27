import sys

from traitlets import (
    Unicode, 
    List, 
    Dict, 
    default, 
    validate
)
from traitlets.config import Config

from jupyter_core.application import JupyterApp

from jupyter_server.serverapp import ServerApp, aliases, flags
from jupyter_server.transutils import _
from jupyter_server.utils import url_path_join


# Remove alias for nested classes in ServerApp.
# Nested classes are not allowed in ExtensionApp.
try:
    aliases.pop('transport')
except KeyError:
    pass


def _preparse_command_line(Application):
    """Looks for 'help', 'version', and 'generate-config; commands 
    in command line. If found, raises the help and version of 
    current Application.

    This is useful for traitlets applications that have to parse
    the command line multiple times, but want to control when
    when 'help' and 'version' is raised.
    """
    # Arguments after a '--' argument are for the script IPython may be
    # about to run, not IPython iteslf. For arguments parsed here (help and
    # version), we want to only search the arguments up to the first
    # occurrence of '--', which we're calling interpreted_argv.
    try:
        interpreted_argv = sys.argv[:sys.argv.index('--')]
    except ValueError:
        interpreted_argv = sys.argv

    # Catch any help calls.
    if any(x in interpreted_argv for x in ('-h', '--help-all', '--help')):
        app = Application()
        app.print_help('--help-all' in interpreted_argv)
        app.exit(0)

    # Catch version commands
    if '--version' in interpreted_argv or '-V' in interpreted_argv:
        app = Application()
        app.print_version()
        app.exit(0)

    # Catch generate-config commands.
    if '--generate-config' in interpreted_argv:
        app = Application()
        app.write_default_config()
        app.exit(0)


class ExtensionApp(JupyterApp):
    """Base class for configurable Jupyter Server Extension Applications.

    ExtensionApp subclasses can be initialized two ways:
    1. Extension is listed as a jpserver_extension, and ServerApp calls 
        its load_jupyter_server_extension classmethod. This is the 
        classic way of loading a server extension.
    2. Extension is launched directly by calling its `launch_instance`
        class method. This method can be set as a entry_point in 
        the extensions setup.py
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
        ServerApp,
    ]

    aliases = aliases
    flags = flags

    @property
    def static_url_prefix(self):
        return "/static/{extension_name}/".format(
            extension_name=self.extension_name)

    static_paths = List(Unicode(),
        help="""paths to search for serving static files.
        
        This allows adding javascript/css to be available from the notebook server machine,
        or overriding individual files in the IPython
        """
    ).tag(config=True)

    template_paths = List(Unicode(), 
        help=_("""Paths to search for serving jinja templates.

        Can be used to override templates from notebook.templates.""")
    ).tag(config=True)

    settings = Dict(
        help=_("""Settings that will passed to the server.""")
    ).tag(config=True)

    handlers = List(
        help=_("""Handlers appended to the server.""")
    ).tag(config=True)

    default_url = Unicode('/', config=True,
        help=_("The default URL to redirect to from `/`")
    )

    def initialize_settings(self):
        """Override this method to add handling of settings."""
        pass

    def initialize_handlers(self):
        """Override this method to append handlers to a Jupyter Server."""
        pass

    def initialize_templates(self):
        """Override this method to add handling of template files."""
        pass

    def _prepare_config(self):
        """Builds a Config object from the extension's traits and passes
        the object to the webapp's settings as `<extension_name>_config`.  
        """
        traits = self.class_own_traits().keys()
        self.config = Config({t: getattr(self, t) for t in traits})
        self.settings['{}_config'.format(self.extension_name)] = self.config

    def _prepare_settings(self):
        # Make webapp settings accessible to initialize_settings method
        webapp = self.serverapp.web_app
        self.settings.update(**webapp.settings)

        # Add static and template paths to settings.
        self.settings.update({
            "{}_static_paths".format(self.extension_name): self.static_paths,
        })

        # Get setting defined by subclass using initialize_settings method.
        self.initialize_settings()

        # Update server settings with extension settings.
        webapp.settings.update(**self.settings)

    def _prepare_handlers(self):
        webapp = self.serverapp.web_app

        # Get handlers defined by extension subclass.
        self.initialize_handlers()

        # prepend base_url onto the patterns that we match
        new_handlers = []
        for handler_items in self.handlers:
            # Build url pattern including base_url
            pattern = url_path_join(webapp.settings['base_url'], handler_items[0])
            handler = handler_items[1]
            
            # Get handler kwargs, if given
            kwargs = {}
            try: 
                kwargs.update(handler_items[2])
            except IndexError:
                pass
            kwargs['extension_name'] = self.extension_name

            new_handler = (pattern, handler, kwargs)
            new_handlers.append(new_handler)

        # Add static endpoint for this extension, if static paths are given.
        if len(self.static_paths) > 0:
            # Append the extension's static directory to server handlers.
            static_url = url_path_join("/static", self.extension_name, "(.*)")
            
            # Construct handler.
            handler = (
                static_url, 
                webapp.settings['static_handler_class'], 
                {'path': self.static_paths}
            )
            new_handlers.append(handler)

        webapp.add_handlers('.*$', new_handlers)

    def _prepare_templates(self):
        # Add templates to web app settings if extension has templates.
        if len(self.template_paths) > 0:
            self.settings.update({
                "{}_template_paths".format(self.extension_name): self.template_paths
            })
        self.initialize_templates()

    @staticmethod
    def initialize_server():
        """Get an instance of the Jupyter Server."""
        # Get a jupyter server instance
        serverapp = ServerApp()
        # Initialize ServerApp config.
        # Parses the command line looking for 
        # ServerApp configuration.
        serverapp.initialize()
        return serverapp

    def initialize(self, serverapp, argv=None):
        """Initialize the extension app."""
        super(ExtensionApp, self).initialize(argv=argv)
        self.serverapp = serverapp

    def start(self, **kwargs):
        """Start the extension app.
        
        Also starts the server. This allows extensions to add settings to the 
        server before it starts.
        """
        # Start the server.
        self.serverapp.start()

    @classmethod
    def launch_instance(cls, argv=None, **kwargs):
        """Launch the ServerApp and Server Extension Application. 
        
        Properly orders the steps to initialize and start the server and extension.
        """
        # Check for help, version, and generate-config arguments
        # before initializing server to make sure these
        # arguments trigger actions from the extension not the server.
        _preparse_command_line(cls)

        # Initialize the server
        serverapp = cls.initialize_server()

        # Load the extension
        args = sys.argv[1:]  # slice out extension config.
        extension = cls.load_jupyter_server_extension(serverapp, argv=args, **kwargs)
        
        # Start the browser at this extensions default_url, unless user
        # configures ServerApp.default_url on command line.
        try:
            server_config = extension.config['ServerApp']
            if 'default_url' not in server_config:
                serverapp.default_url = extension.default_url
        except KeyError: 
            pass

        # Start the application.
        extension.start()

    @classmethod
    def load_jupyter_server_extension(cls, serverapp, argv=None, **kwargs):
        """Enables loading this extension application via the documented
        `load_jupyter_server_extension` mechanism.

        This method:
        - Initializes the ExtensionApp 
        - Loads the extension's config from file
        - Loads the extension's config from argv
        - Initializes templates environment
        - Passes settings to webapp
        - Appends handlers to webapp.
        """
        # Get webapp from the server.
        webapp = serverapp.web_app
        
        # Create an instance and initialize extension.
        extension = cls()
        extension.initialize(serverapp, argv=argv)

        # Initialize extension template, settings, and handlers.
        extension._prepare_config()
        extension._prepare_templates()
        extension._prepare_settings()
        extension._prepare_handlers()
        return extension