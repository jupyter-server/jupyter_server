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
from .handler import ExtensionHandler

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



class StandaloneApp(JupyterApp):
    """Base class for configurable Jupyter Server Extension Applications.

    StandaloneApp subclasses are launched directly by calling its
    `launch_instance` class method. This method can be set as an
    entry_point in the extensions setup.py
    """

    standalone = True

    # Name of the extension
    extension_name = Unicode(
        "",
        help="Name of extension."
    )

    @default("extension_name")
    def _default_extension_name(self):
        raise ValueError("The extension must be given a `name`.")

    INVALID_EXTENSION_NAME_CHARS = [' ', '.', '+', '/']

    def _validate_extension_name(self):
        value = self.extension_name
        if isinstance(value, str):
            # Validate that extension_name doesn't contain any invalid characters.
            for c in StandaloneApp.INVALID_EXTENSION_NAME_CHARS:
                if c in value:
                    raise ValueError("Extension name '{name}' cannot contain any of the following characters: "
                                     "{invalid_chars}.".
                                     format(name=value, invalid_chars=StandaloneApp.INVALID_EXTENSION_NAME_CHARS))
            return value
        raise ValueError("Extension name must be a string, found {type}.".format(type=type(value)))

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
        self.extension_config = Config({t: getattr(self, t) for t in traits})
        self.settings['{}_config'.format(self.extension_name)] = self.extension_config

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
            if issubclass(handler, ExtensionHandler):
                kwargs['extension_name'] = self.extension_name
            try: 
                kwargs.update(handler_items[2])
            except IndexError:
                pass

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

    @classmethod
    def initialize_server(cls, argv=[], **kwargs):
        """Get an instance of the Jupyter Server."""
        # Get a jupyter server instance
        serverapp = ServerApp(**kwargs)
        # Initialize ServerApp config.
        # Parses the command line looking for 
        # ServerApp configuration.
        serverapp.initialize(argv=argv, load_extensions=cls.standalone is False)
        return serverapp

    def initialize(self, serverapp, argv=[]):
        """Initialize the extension app.
        
        This method:
        - Loads the extension's config from file
        - Updates the extension's config from argv
        - Initializes templates environment
        - Passes settings to webapp
        - Appends handlers to webapp.
        """
        self._validate_extension_name()
        # Initialize the extension application
        super(StandaloneApp, self).initialize(argv=argv)
        self.serverapp = serverapp

        # Initialize config, settings, templates, and handlers.
        self._prepare_config()
        self._prepare_templates()
        self._prepare_settings()
        self._prepare_handlers()

    def listen(self):
        """Extension doesn't listen for anything. IOLoop lives
        in the attached server.
        """
        pass

    def start(self):
        """Extension has nothing to `start`. See `start_server`
        for starting the jupyter server application.
        """
        pass

    def start_server(self, **kwargs):
        """Start the Jupyter server.
        
        Server should be started after extension is initialized.
        """
        # Start the server.
        self.serverapp.start(**kwargs)

    @classmethod
    def _load_app(cls, serverapp, argv=[], **kwargs):
        """Initialize and configure this app, then add the apps's
        settings and handlers to the server's web application.
        """
        # Configure and initialize extension.
        extension = cls()
        extension.initialize(serverapp, argv=argv)
        return extension

    @classmethod
    def _prepare_launch(cls, serverapp, argv=[], **kwargs):
        """Prepare the extension application for launch by 
        configuring the server and the extension from argv.
        Does not start the ioloop.
        """
        # Load the extension
        extension = cls.load_jupyter_server_extension(serverapp, argv=argv, **kwargs)
        # Start the browser at this extensions default_url, unless user
        # configures ServerApp.default_url on command line.
        try:
            server_config = extension.config['ServerApp']
            if 'default_url' not in server_config:
                serverapp.default_url = extension.default_url
        except KeyError: 
            pass

        return extension

    @classmethod
    def launch_instance(cls, argv=None, **kwargs):
        """Launch the extension like an application. Initializes+configs a stock server 
        and appends the extension to the server. Then starts the server and routes to
        extension's landing page.
        """
        # Check for help, version, and generate-config arguments
        # before initializing server to make sure these
        # arguments trigger actions from the extension not the server.
        _preparse_command_line(cls)
        # Handle arguments.
        if argv is None:
            args = sys.argv[1:]  # slice out extension config.
        else:
            args = []
        # Get a jupyter server instance.
        serverapp = cls.initialize_server(argv=args)
        extension = cls._prepare_launch(serverapp, argv=args, **kwargs)
        # Start the ioloop.
        extension.start_server()


class ExtensionApp(StandaloneApp):
    """Base class for configurable Jupyter Server Extension Applications.

    ExtensionApp subclasses can be initialized two ways:
    1. Extension is listed as a jpserver_extension, and ServerApp calls
        its load_jupyter_server_extension classmethod. This is the
        classic way of loading a server extension.
    2. Extension is launched directly by calling its `launch_instance`
        class method. This method can be set as a entry_point in
        the extensions setup.py
    """

    standalone = False

    @classmethod
    def load_jupyter_server_extension(cls, serverapp, argv=[], **kwargs):
        """Initialize and configure this extension, then add the extension's
        settings and handlers to the server's web application.
        """
        # Configure and initialize extension.
        return cls._load_app(serverapp, argv=argv, **kwargs)
