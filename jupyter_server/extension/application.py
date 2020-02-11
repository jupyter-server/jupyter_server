import sys
import re

from jinja2 import Environment, FileSystemLoader

from traitlets import (
    Unicode, 
    List, 
    Dict,
    Bool,
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

#-----------------------------------------------------------------------------
# Util functions and classes.
#-----------------------------------------------------------------------------

def _preparse_for_subcommand(Application, argv):
    """Preparse command line to look for subcommands.
    """
    # Read in arguments from command line.
    if len(argv) == 0:
        return

    # Find any subcommands.
    if Application.subcommands and len(argv) > 0:
        # we have subcommands, and one may have been specified
        subc, subargv = argv[0], argv[1:]
        if re.match(r'^\w(\-?\w)*$', subc) and subc in Application.subcommands:
            # it's a subcommand, and *not* a flag or class parameter
            app = Application()
            app.initialize_subcommand(subc, subargv)
            return app.subapp


def _preparse_for_stopping_flags(Application, argv):
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
        interpreted_argv = argv[:argv.index('--')]
    except ValueError:
        interpreted_argv = argv

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


class ExtensionAppJinjaMixin:
    """Use Jinja templates for HTML templates on top of an ExtensionApp."""
    
    jinja2_options = Dict(
        help=_("""Options to pass to the jinja2 environment for this
        extension.
        """)
    ).tag(config=True)

    def _prepare_templates(self):
        # Add templates to web app settings if extension has templates.
        if len(self.template_paths) > 0:
            self.settings.update({
                "{}_template_paths".format(self.extension_name): self.template_paths
            })

        # Create a jinja environment for logging html templates.
        self.jinja2_env = Environment(
            loader=FileSystemLoader(self.template_paths), 
            extensions=['jinja2.ext.i18n'],
            autoescape=True,
            **self.jinja2_options
        )

        # Get templates defined in a subclass.
        self.initialize_templates()

        # Add the jinja2 environment for this extension to the tornado settings.
        self.settings.update(
            {
                "{}_jinja2_env".format(self.extension_name): self.jinja2_env 
            }
        )

#-----------------------------------------------------------------------------
# Aliases and Flags
#-----------------------------------------------------------------------------

flags['no-browser']=(
    {'ExtensionApp' : {'open_browser' : True}},
    _("Prevent the opening of the default url in the browser.")
)

#-----------------------------------------------------------------------------
# ExtensionApp
#-----------------------------------------------------------------------------

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
    # Subclasses should override this trait. Tells the server if
    # this extension allows other other extensions to be loaded
    # side-by-side when launched directly.
    load_other_extensions = True

    # Name of the extension
    extension_name = Unicode(
        help="Name of extension."
    )

    @default('extension_name')
    def _extension_name_default(self):
        try:
            return self.name
        except AttributeError:
            raise ValueError("The extension must be given a `name`.")

    INVALID_EXTENSION_NAME_CHARS = [' ', '.', '+', '/']

    @validate('extension_name')
    def _validate_extension_name(self, proposal):
        value = proposal['value']
        if isinstance(value, str):
            # Validate that extension_name doesn't contain any invalid characters.
            for c in ExtensionApp.INVALID_EXTENSION_NAME_CHARS:
                if c in value:
                    raise ValueError("Extension name '{name}' cannot contain any of the following characters: "
                                     "{invalid_chars}.".
                                     format(name=value, invalid_chars=ExtensionApp.INVALID_EXTENSION_NAME_CHARS))
            return value
        raise ValueError("Extension name must be a string, found {type}.".format(type=type(value)))

    # Extension can configure the ServerApp from the command-line
    classes = [
        ServerApp,
    ]

    aliases = aliases
    flags = flags

    subcommands = {}

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

    def _config_dir_default(self):
        """Point the config directory at the server's config_dir by default."""
        try:
            return self.serverapp.config_dir
        except AttributeError:
            raise AttributeError(
                "The ExtensionApp has not ServerApp "
                "initialized. Try `.initialize_server()`."
            )

    def _config_file_name_default(self):
        """The default config file name."""
        if not self.extension_name:
            return ''
        return 'jupyter_{}_config'.format(self.extension_name.replace('-','_'))

    default_url = Unicode('/', config=True,
        help=_("The default URL to redirect to from `/`")
    )

    open_browser = Bool(
        True,
        help=_("Should the extension open a browser window?")
    )

    custom_display_url = Unicode(u'', config=True,
        help=_("""Override URL shown to users.

        Replace actual URL, including protocol, address, port and base URL,
        with the given value when displaying URL to the users. Do not change
        the actual connection URL. If authentication token is enabled, the
        token is added to the custom URL automatically.

        This option is intended to be used when the URL to display to the user
        cannot be determined reliably by the Jupyter server (proxified
        or containerized setups for example).""")
    )

    @default('custom_display_url') 
    def _default_custom_display_url(self):
        """URL to display to the user."""
        # Get url from server.
        url = url_path_join(self.serverapp.base_url, self.default_url)
        return self.serverapp.get_url(self.serverapp.ip, url)

    def _write_browser_open_file(self, url, fh):
        """Use to hijacks the server's browser-open file and open at 
        the extension's homepage.
        """
        # Ignore server's url
        del url
        path = url_path_join(self.serverapp.base_url, self.default_url)
        url = self.serverapp.get_url(path=path, token=self.serverapp.token)
        jinja2_env = self.serverapp.web_app.settings['jinja2_env']
        template = jinja2_env.get_template('browser-open.html')
        fh.write(template.render(open_url=url))

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

    @staticmethod
    def initialize_server(argv=[], load_other_extensions=True, **kwargs):
        """Get an instance of the Jupyter Server."""
        # Get a jupyter server instance
        serverapp = ServerApp.instance(**kwargs)
        # Initialize ServerApp config.
        # Parses the command line looking for 
        # ServerApp configuration.
        serverapp.initialize(argv=argv, load_extensions=load_other_extensions)
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
        # Initialize ServerApp.
        self.serverapp = serverapp
        
        # Initialize the extension application
        super(ExtensionApp, self).initialize(argv=argv)

        # Initialize config, settings, templates, and handlers.
        self._prepare_config()
        self._prepare_templates()
        self._prepare_settings()
        self._prepare_handlers()

    def start(self):
        """Start the underlying Jupyter server.
        
        Server should be started after extension is initialized.
        """
        super(ExtensionApp, self).start()
        # Override the browser open file to 
        # Override the server's display url to show extension's display URL.
        self.serverapp.custom_display_url = self.custom_display_url
        # Override the server's default option and open a broswer window.
        self.serverapp.open_browser = self.open_browser
        # Hijack the server's browser-open file to land on
        # the extensions home page.
        self.serverapp._write_browser_open_file = self._write_browser_open_file
        # Start the server.
        self.serverapp.start()

    def stop(self):
        """Stop the underlying Jupyter server.
        """
        self.serverapp.stop()
        self.serverapp.clear_instance()

    @classmethod
    def load_jupyter_server_extension(cls, serverapp, argv=[], **kwargs):
        """Initialize and configure this extension, then add the extension's
        settings and handlers to the server's web application.
        """
        # Configure and initialize extension.
        extension = cls()
        extension.initialize(serverapp, argv=argv)
        return extension

    @classmethod
    def launch_instance(cls, argv=None, **kwargs):
        """Launch the extension like an application. Initializes+configs a stock server 
        and appends the extension to the server. Then starts the server and routes to
        extension's landing page.
        """
        # Handle arguments.
        if argv is None:
            args = sys.argv[1:]  # slice out extension config.
        else:
            args = []
        # Check for subcommands
        subapp = _preparse_for_subcommand(cls, args)
        if subapp:
            subapp.start()
        else:
            # Check for help, version, and generate-config arguments
            # before initializing server to make sure these
            # arguments trigger actions from the extension not the server.
            _preparse_for_stopping_flags(cls, args) 
            # Get a jupyter server instance.
            serverapp = cls.initialize_server(
                argv=args, 
                load_other_extensions=cls.load_other_extensions
            )
            # Log if extension is blocking other extensions from loading.
            if not cls.load_other_extensions:
                serverapp.log.info(
                    "{ext_name} is running without loading "
                    "other extensions.".format(ext_name=cls.extension_name)
                )

            extension = cls.load_jupyter_server_extension(serverapp, argv=args, **kwargs)
            # Start the ioloop.
            extension.start()