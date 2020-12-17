# coding: utf-8
"""A tornado based Jupyter server."""

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

from __future__ import absolute_import, print_function

import jupyter_server
import asyncio
import binascii
import datetime
import errno
import gettext
import hashlib
import hmac
import importlib
import io
import ipaddress
import json
import logging
import mimetypes
import os
import random
import re
import select
import signal
import socket
import sys
import tempfile
import threading
import time
import warnings
import webbrowser
import urllib
from ruamel.yaml import YAML
from glob import glob

from types import ModuleType
from base64 import encodebytes
from jinja2 import Environment, FileSystemLoader

from jupyter_server.transutils import trans, _
from jupyter_server.utils import secure_write, run_sync

# the minimum viable tornado version: needs to be kept in sync with setup.py
MIN_TORNADO = (6, 1, 0)

try:
    import tornado
    assert tornado.version_info >= MIN_TORNADO
except (ImportError, AttributeError, AssertionError) as e:  # pragma: no cover
    raise ImportError(
        _("The Jupyter Server requires tornado >=%s.%s.%s") % MIN_TORNADO
    ) from e

from tornado import httpserver
from tornado import ioloop
from tornado import web
from tornado.httputil import url_concat
from tornado.log import LogFormatter, app_log, access_log, gen_log

from jupyter_server import (
    DEFAULT_STATIC_FILES_PATH,
    DEFAULT_TEMPLATE_PATH_LIST,
    __version__,
)

from .base.handlers import MainHandler, RedirectWithParams, Template404
from .log import log_request
from .services.kernels.kernelmanager import MappingKernelManager, AsyncMappingKernelManager
from .services.config import ConfigManager
from .services.contents.manager import AsyncContentsManager, ContentsManager
from .services.contents.filemanager import AsyncFileContentsManager, FileContentsManager
from .services.contents.largefilemanager import LargeFileManager
from .services.sessions.sessionmanager import SessionManager
from .gateway.managers import GatewayKernelManager, GatewayKernelSpecManager, GatewaySessionManager, GatewayClient

from .auth.login import LoginHandler
from .auth.logout import LogoutHandler
from .base.handlers import FileFindHandler

from traitlets.config import Config
from traitlets.config.application import catch_config_error, boolean_flag
from jupyter_core.application import (
    JupyterApp, base_flags, base_aliases,
)
from jupyter_core.paths import jupyter_config_path
from jupyter_client import KernelManager
from jupyter_client.kernelspec import KernelSpecManager, NoSuchKernel, NATIVE_KERNEL_NAME
from jupyter_client.session import Session
from nbformat.sign import NotebookNotary
from traitlets import (
    Any, Dict, Unicode, Integer, List, Bool, Bytes, Instance,
    TraitError, Type, Float, observe, default, validate
)
from ipython_genutils import py3compat
from jupyter_core.paths import jupyter_runtime_dir, jupyter_path
from jupyter_telemetry.eventlog import EventLog

from jupyter_server._sysinfo import get_sys_info

from ._tz import utcnow, utcfromtimestamp
from .utils import (
    url_path_join,
    check_pid,
    url_escape,
    urljoin,
    pathname2url,
    get_schema_files
)

from jupyter_server.extension.serverextension import ServerExtensionApp
from jupyter_server.extension.manager import ExtensionManager
from jupyter_server.extension.config import ExtensionConfigManager

#-----------------------------------------------------------------------------
# Module globals
#-----------------------------------------------------------------------------

_examples = """
jupyter server                       # start the server
jupyter server  --certfile=mycert.pem # use SSL/TLS certificate
jupyter server password              # enter a password to protect the server
"""

JUPYTER_SERVICE_HANDLERS = dict(
    auth=None,
    api=['jupyter_server.services.api.handlers'],
    config=['jupyter_server.services.config.handlers'],
    contents=['jupyter_server.services.contents.handlers'],
    files=['jupyter_server.files.handlers'],
    kernels=['jupyter_server.services.kernels.handlers'],
    kernelspecs=[
        'jupyter_server.kernelspecs.handlers',
        'jupyter_server.services.kernelspecs.handlers'],
    nbconvert=[
        'jupyter_server.nbconvert.handlers',
        'jupyter_server.services.nbconvert.handlers'],
    security=['jupyter_server.services.security.handlers'],
    sessions=['jupyter_server.services.sessions.handlers'],
    shutdown=['jupyter_server.services.shutdown'],
    view=['jupyter_server.view.handlers']
)

#-----------------------------------------------------------------------------
# Helper functions
#-----------------------------------------------------------------------------

def random_ports(port, n):
    """Generate a list of n random ports near the given port.

    The first 5 ports will be sequential, and the remaining n-5 will be
    randomly selected in the range [port-2*n, port+2*n].
    """
    for i in range(min(5, n)):
        yield port + i
    for i in range(n-5):
        yield max(1, port + random.randint(-2*n, 2*n))

def load_handlers(name):
    """Load the (URL pattern, handler) tuples for each component."""
    mod = __import__(name, fromlist=['default_handlers'])
    return mod.default_handlers

#-----------------------------------------------------------------------------
# The Tornado web application
#-----------------------------------------------------------------------------

class ServerWebApplication(web.Application):

    def __init__(self, jupyter_app, default_services, kernel_manager, contents_manager,
                 session_manager, kernel_spec_manager,
                 config_manager, extra_services, log,
                 base_url, default_url, settings_overrides, jinja_env_options):

        settings = self.init_settings(
            jupyter_app, kernel_manager, contents_manager,
            session_manager, kernel_spec_manager, config_manager,
            extra_services, log, base_url,
            default_url, settings_overrides, jinja_env_options)
        handlers = self.init_handlers(default_services, settings)

        super(ServerWebApplication, self).__init__(handlers, **settings)

    def init_settings(self, jupyter_app, kernel_manager, contents_manager,
                      session_manager, kernel_spec_manager,
                      config_manager, extra_services,
                      log, base_url, default_url, settings_overrides,
                      jinja_env_options=None):

        _template_path = settings_overrides.get(
            "template_path",
            jupyter_app.template_file_path,
        )
        if isinstance(_template_path, py3compat.string_types):
            _template_path = (_template_path,)
        template_path = [os.path.expanduser(path) for path in _template_path]

        jenv_opt = {"autoescape": True}
        jenv_opt.update(jinja_env_options if jinja_env_options else {})

        env = Environment(loader=FileSystemLoader(template_path), extensions=['jinja2.ext.i18n'], **jenv_opt)
        sys_info = get_sys_info()

        # If the user is running the server in a git directory, make the assumption
        # that this is a dev install and suggest to the developer `npm run build:watch`.
        base_dir = os.path.realpath(os.path.join(__file__, '..', '..'))
        dev_mode = os.path.exists(os.path.join(base_dir, '.git'))

        nbui = gettext.translation('nbui', localedir=os.path.join(base_dir, 'jupyter_server/i18n'), fallback=True)
        env.install_gettext_translations(nbui, newstyle=False)

        if sys_info['commit_source'] == 'repository':
            # don't cache (rely on 304) when working from master
            version_hash = ''
        else:
            # reset the cache on server restart
            version_hash = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

        now = utcnow()

        root_dir = contents_manager.root_dir
        home = py3compat.str_to_unicode(os.path.expanduser('~'), encoding=sys.getfilesystemencoding())
        if root_dir.startswith(home + os.path.sep):
            # collapse $HOME to ~
            root_dir = '~' + root_dir[len(home):]

        settings = dict(
            # basics
            log_function=log_request,
            base_url=base_url,
            default_url=default_url,
            template_path=template_path,
            static_path=jupyter_app.static_file_path,
            static_custom_path=jupyter_app.static_custom_path,
            static_handler_class = FileFindHandler,
            static_url_prefix = url_path_join(base_url, '/static/'),
            static_handler_args = {
                # don't cache custom.js
                'no_cache_paths': [url_path_join(base_url, 'static', 'custom')],
            },
            version_hash=version_hash,

            # rate limits
            iopub_msg_rate_limit=jupyter_app.iopub_msg_rate_limit,
            iopub_data_rate_limit=jupyter_app.iopub_data_rate_limit,
            rate_limit_window=jupyter_app.rate_limit_window,

            # authentication
            cookie_secret=jupyter_app.cookie_secret,
            login_url=url_path_join(base_url, '/login'),
            login_handler_class=jupyter_app.login_handler_class,
            logout_handler_class=jupyter_app.logout_handler_class,
            password=jupyter_app.password,
            xsrf_cookies=True,
            disable_check_xsrf=jupyter_app.disable_check_xsrf,
            allow_remote_access=jupyter_app.allow_remote_access,
            local_hostnames=jupyter_app.local_hostnames,
            authenticate_prometheus=jupyter_app.authenticate_prometheus,

            # managers
            kernel_manager=kernel_manager,
            contents_manager=contents_manager,
            session_manager=session_manager,
            kernel_spec_manager=kernel_spec_manager,
            config_manager=config_manager,

            # handlers
            extra_services=extra_services,

            # Jupyter stuff
            started=now,
            # place for extensions to register activity
            # so that they can prevent idle-shutdown
            last_activity_times={},
            jinja_template_vars=jupyter_app.jinja_template_vars,
            websocket_url=jupyter_app.websocket_url,
            shutdown_button=jupyter_app.quit_button,
            config=jupyter_app.config,
            config_dir=jupyter_app.config_dir,
            allow_password_change=jupyter_app.allow_password_change,
            server_root_dir=root_dir,
            jinja2_env=env,
            terminals_available=False,  # Set later if terminals are available
            eventlog=jupyter_app.eventlog,
            serverapp=jupyter_app
        )

        # allow custom overrides for the tornado web app.
        settings.update(settings_overrides)
        return settings

    def init_handlers(self, default_services, settings):
        """Load the (URL pattern, handler) tuples for each component."""
        # Order matters. The first handler to match the URL will handle the request.
        handlers = []
        # load extra services specified by users before default handlers
        for service in settings['extra_services']:
            handlers.extend(load_handlers(service))

        # Add auth services.
        if 'auth' in default_services:
            handlers.extend([(r"/login", settings['login_handler_class'])])
            handlers.extend([(r"/logout", settings['logout_handler_class'])])

        # Load default services. Raise exception if service not
        # found in JUPYTER_SERVICE_HANLDERS.
        for service in default_services:
            if service in JUPYTER_SERVICE_HANDLERS:
                locations = JUPYTER_SERVICE_HANDLERS[service]
                if locations is not None:
                    for loc in locations:
                        handlers.extend(load_handlers(loc))
            else:
                raise Exception("{} is not recognized as a jupyter_server "
                                "service. If this is a custom service, "
                                "try adding it to the "
                                "`extra_services` list.".format(service))

        # Add extra handlers from contents manager.
        handlers.extend(settings['contents_manager'].get_extra_handlers())

        # If gateway mode is enabled, replace appropriate handlers to perform redirection
        if GatewayClient.instance().gateway_enabled:
            # for each handler required for gateway, locate its pattern
            # in the current list and replace that entry...
            gateway_handlers = load_handlers('jupyter_server.gateway.handlers')
            for i, gwh in enumerate(gateway_handlers):
                for j, h in enumerate(handlers):
                    if gwh[0] == h[0]:
                        handlers[j] = (gwh[0], gwh[1])
                        break

        # register base handlers last
        handlers.extend(load_handlers('jupyter_server.base.handlers'))

        if settings['default_url'] != settings['base_url']:
            # set the URL that will be redirected from `/`
            handlers.append(
                (r'/?', RedirectWithParams, {
                    'url' : settings['default_url'],
                    'permanent': False, # want 302, not 301
                })
            )
        else:
            handlers.append(
                (r"/", MainHandler))

        # prepend base_url onto the patterns that we match
        new_handlers = []
        for handler in handlers:
            pattern = url_path_join(settings['base_url'], handler[0])
            new_handler = tuple([pattern] + list(handler[1:]))
            new_handlers.append(new_handler)
        # add 404 on the end, which will catch everything that falls through
        new_handlers.append((r'(.*)', Template404))
        return new_handlers

    def last_activity(self):
        """Get a UTC timestamp for when the server last did something.

        Includes: API activity, kernel activity, kernel shutdown, and terminal
        activity.
        """
        sources = [
            self.settings['started'],
            self.settings['kernel_manager'].last_kernel_activity,
        ]
        try:
            sources.append(self.settings['api_last_activity'])
        except KeyError:
            pass
        try:
            sources.append(self.settings['terminal_last_activity'])
        except KeyError:
            pass
        sources.extend(self.settings['last_activity_times'].values())
        return max(sources)


class JupyterPasswordApp(JupyterApp):
    """Set a password for the Jupyter server.

    Setting a password secures the Jupyter server
    and removes the need for token-based authentication.
    """

    description = __doc__

    def _config_file_default(self):
        return os.path.join(self.config_dir, 'jupyter_server_config.json')

    def start(self):
        from .auth.security import set_password
        set_password(config_file=self.config_file)
        self.log.info("Wrote hashed password to %s" % self.config_file)


def shutdown_server(server_info, timeout=5, log=None):
    """Shutdown a notebook server in a separate process.

    *server_info* should be a dictionary as produced by list_running_servers().

    Will first try to request shutdown using /api/shutdown .
    On Unix, if the server is still running after *timeout* seconds, it will
    send SIGTERM. After another timeout, it escalates to SIGKILL.

    Returns True if the server was stopped by any means, False if stopping it
    failed (on Windows).
    """
    from tornado.httpclient import HTTPClient, HTTPRequest
    url = server_info['url']
    pid = server_info['pid']
    req = HTTPRequest(url + 'api/shutdown', method='POST', body=b'', headers={
        'Authorization': 'token ' + server_info['token']
    })
    if log: log.debug("POST request to %sapi/shutdown", url)
    HTTPClient().fetch(req)

    # Poll to see if it shut down.
    for _ in range(timeout*10):
        if not check_pid(pid):
            if log: log.debug("Server PID %s is gone", pid)
            return True
        time.sleep(0.1)

    if sys.platform.startswith('win'):
        return False

    if log: log.debug("SIGTERM to PID %s", pid)
    os.kill(pid, signal.SIGTERM)

    # Poll to see if it shut down.
    for _ in range(timeout * 10):
        if not check_pid(pid):
            if log: log.debug("Server PID %s is gone", pid)
            return True
        time.sleep(0.1)

    if log: log.debug("SIGKILL to PID %s", pid)
    os.kill(pid, signal.SIGKILL)
    return True  # SIGKILL cannot be caught


class JupyterServerStopApp(JupyterApp):

    version = __version__
    description = "Stop currently running Jupyter server for a given port"

    port = Integer(8888, config=True,
        help="Port of the server to be killed. Default 8888")

    def parse_command_line(self, argv=None):
        super(JupyterServerStopApp, self).parse_command_line(argv)
        if self.extra_args:
            self.port=int(self.extra_args[0])

    def shutdown_server(self, server):
        return shutdown_server(server, log=self.log)

    def start(self):
        servers = list(list_running_servers(self.runtime_dir))
        if not servers:
            self.exit("There are no running servers")
        for server in servers:
            if server['port'] == self.port:
                print("Shutting down server on port", self.port, "...")
                if not self.shutdown_server(server):
                    sys.exit("Could not stop server")
                return
        else:
            print("There is currently no server running on port {}".format(self.port), file=sys.stderr)
            print("Ports currently in use:", file=sys.stderr)
            for server in servers:
                print("  - {}".format(server['port']), file=sys.stderr)
            self.exit(1)


class JupyterServerListApp(JupyterApp):
    version = __version__
    description=_("List currently running notebook servers.")

    flags = dict(
        jsonlist=({'JupyterServerListApp': {'jsonlist': True}},
              _("Produce machine-readable JSON list output.")),
        json=({'JupyterServerListApp': {'json': True}},
              _("Produce machine-readable JSON object on each line of output.")),
    )

    jsonlist = Bool(False, config=True,
          help=_("If True, the output will be a JSON list of objects, one per "
                 "active notebook server, each with the details from the "
                 "relevant server info file."))
    json = Bool(False, config=True,
          help=_("If True, each line of output will be a JSON object with the "
                  "details from the server info file. For a JSON list output, "
                  "see the JupyterServerListApp.jsonlist configuration value"))

    def start(self):
        serverinfo_list = list(list_running_servers(self.runtime_dir))
        if self.jsonlist:
            print(json.dumps(serverinfo_list, indent=2))
        elif self.json:
            for serverinfo in serverinfo_list:
                print(json.dumps(serverinfo))
        else:
            print("Currently running servers:")
            for serverinfo in serverinfo_list:
                url = serverinfo['url']
                if serverinfo.get('token'):
                    url = url + '?token=%s' % serverinfo['token']
                print(url, "::", serverinfo['root_dir'])

#-----------------------------------------------------------------------------
# Aliases and Flags
#-----------------------------------------------------------------------------

flags = dict(base_flags)

flags['allow-root']=(
    {'ServerApp' : {'allow_root' : True}},
    _("Allow the server to be run from root user.")
)
flags["no-browser"] = (
    {"ServerApp": {"open_browser": False}},
    _("Prevent the opening of the default url in the browser."),
)

# Add notebook manager flags
flags.update(boolean_flag('script', 'FileContentsManager.save_script',
               'DEPRECATED, IGNORED',
               'DEPRECATED, IGNORED'))

aliases = dict(base_aliases)

aliases.update({
    'ip': 'ServerApp.ip',
    'port': 'ServerApp.port',
    'port-retries': 'ServerApp.port_retries',
    'transport': 'KernelManager.transport',
    'keyfile': 'ServerApp.keyfile',
    'certfile': 'ServerApp.certfile',
    'client-ca': 'ServerApp.client_ca',
    'notebook-dir': 'ServerApp.root_dir',
    'browser': 'ServerApp.browser',
    'pylab': 'ServerApp.pylab',
    'gateway-url': 'GatewayClient.url',
})

#-----------------------------------------------------------------------------
# ServerApp
#-----------------------------------------------------------------------------

class ServerApp(JupyterApp):

    name = 'jupyter-server'
    version = __version__
    description = _("""The Jupyter Server.

    This launches a Tornado-based Jupyter Server.""")
    examples = _examples

    flags = Dict(flags)
    aliases = Dict(aliases)

    classes = [
            KernelManager, Session, MappingKernelManager, KernelSpecManager, AsyncMappingKernelManager,
            ContentsManager, FileContentsManager, AsyncContentsManager, AsyncFileContentsManager, NotebookNotary,
            GatewayKernelManager, GatewayKernelSpecManager, GatewaySessionManager, GatewayClient
        ]

    subcommands = dict(
        list=(JupyterServerListApp, JupyterServerListApp.description.splitlines()[0]),
        stop=(JupyterServerStopApp, JupyterServerStopApp.description.splitlines()[0]),
        password=(JupyterPasswordApp, JupyterPasswordApp.description.splitlines()[0]),
        extension=(ServerExtensionApp, ServerExtensionApp.description.splitlines()[0]),
    )

    # A list of services whose handlers will be exposed.
    # Subclasses can override this list to
    # expose a subset of these handlers.
    default_services = (
        'api',
        'auth',
        'config',
        'contents',
        'files',
        'kernels',
        'kernelspecs',
        'nbconvert',
        'security',
        'sessions',
        'shutdown',
        'view'
    )

    _log_formatter_cls = LogFormatter

    @default('log_level')
    def _default_log_level(self):
        return logging.INFO

    @default('log_format')
    def _default_log_format(self):
        """override default log format to include date & time"""
        return u"%(color)s[%(levelname)1.1s %(asctime)s.%(msecs).03d %(name)s]%(end_color)s %(message)s"

    # file to be opened in the Jupyter server
    file_to_run = Unicode('', config=True)

    # Network related information

    allow_origin = Unicode('', config=True,
        help="""Set the Access-Control-Allow-Origin header

        Use '*' to allow any origin to access your server.

        Takes precedence over allow_origin_pat.
        """
    )

    allow_origin_pat = Unicode('', config=True,
        help="""Use a regular expression for the Access-Control-Allow-Origin header

        Requests from an origin matching the expression will get replies with:

            Access-Control-Allow-Origin: origin

        where `origin` is the origin of the request.

        Ignored if allow_origin is set.
        """
    )

    allow_credentials = Bool(False, config=True,
        help=_("Set the Access-Control-Allow-Credentials: true header")
    )

    allow_root = Bool(False, config=True,
        help=_("Whether to allow the user to run the server as root.")
    )

    default_url = Unicode('/', config=True,
        help=_("The default URL to redirect to from `/`")
    )

    ip = Unicode('localhost', config=True,
        help=_("The IP address the Jupyter server will listen on.")
    )

    @default('ip')
    def _default_ip(self):
        """Return localhost if available, 127.0.0.1 otherwise.

        On some (horribly broken) systems, localhost cannot be bound.
        """
        s = socket.socket()
        try:
            s.bind(('localhost', 0))
        except socket.error as e:
            self.log.warning(_("Cannot bind to localhost, using 127.0.0.1 as default ip\n%s"), e)
            return '127.0.0.1'
        else:
            s.close()
            return 'localhost'

    @validate('ip')
    def _valdate_ip(self, proposal):
        value = proposal['value']
        if value == u'*':
            value = u''
        return value

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

    port = Integer(8888, config=True,
        help=_("The port the Jupyter server will listen on.")
    )

    port_retries = Integer(50, config=True,
        help=_("The number of additional ports to try if the specified port is not available.")
    )

    certfile = Unicode(u'', config=True,
        help=_("""The full path to an SSL/TLS certificate file.""")
    )

    keyfile = Unicode(u'', config=True,
        help=_("""The full path to a private key file for usage with SSL/TLS.""")
    )

    client_ca = Unicode(u'', config=True,
        help=_("""The full path to a certificate authority certificate for SSL/TLS client authentication.""")
    )

    cookie_secret_file = Unicode(config=True,
        help=_("""The file where the cookie secret is stored.""")
    )

    @default('cookie_secret_file')
    def _default_cookie_secret_file(self):
        return os.path.join(self.runtime_dir, 'jupytr_cookie_secret')

    cookie_secret = Bytes(b'', config=True,
        help="""The random bytes used to secure cookies.
        By default this is a new random number every time you start the server.
        Set it to a value in a config file to enable logins to persist across server sessions.

        Note: Cookie secrets should be kept private, do not share config files with
        cookie_secret stored in plaintext (you can read the value from a file).
        """
    )

    @default('cookie_secret')
    def _default_cookie_secret(self):
        if os.path.exists(self.cookie_secret_file):
            with io.open(self.cookie_secret_file, 'rb') as f:
                key = f.read()
        else:
            key = encodebytes(os.urandom(32))
            self._write_cookie_secret_file(key)
        h = hmac.new(key, digestmod=hashlib.sha256)
        h.update(self.password.encode())
        return h.digest()

    def _write_cookie_secret_file(self, secret):
        """write my secret to my secret_file"""
        self.log.info(_("Writing notebook server cookie secret to %s"), self.cookie_secret_file)
        try:
            with secure_write(self.cookie_secret_file, True) as f:
                f.write(secret)
        except OSError as e:
            self.log.error(_("Failed to write cookie secret to %s: %s"),
                           self.cookie_secret_file, e)

    token = Unicode('<generated>',
        help=_("""Token used for authenticating first-time connections to the server.

        When no password is enabled,
        the default is to generate a new, random token.

        Setting to an empty string disables authentication altogether, which is NOT RECOMMENDED.
        """)
    ).tag(config=True)

    _token_generated = True

    @default('token')
    def _token_default(self):
        if os.getenv('JUPYTER_TOKEN'):
            self._token_generated = False
            return os.getenv('JUPYTER_TOKEN')
        if self.password:
            # no token if password is enabled
            self._token_generated = False
            return u''
        else:
            self._token_generated = True
            return binascii.hexlify(os.urandom(24)).decode('ascii')

    max_body_size = Integer(512 * 1024 * 1024, config=True,
        help="""
        Sets the maximum allowed size of the client request body, specified in
        the Content-Length request header field. If the size in a request
        exceeds the configured value, a malformed HTTP message is returned to
        the client.

        Note: max_body_size is applied even in streaming mode.
        """
    )

    max_buffer_size = Integer(512 * 1024 * 1024, config=True,
        help="""
        Gets or sets the maximum amount of memory, in bytes, that is allocated
        for use by the buffer manager.
        """
    )

    @observe('token')
    def _token_changed(self, change):
        self._token_generated = False

    password = Unicode(u'', config=True,
                      help="""Hashed password to use for web authentication.

                      To generate, type in a python/IPython shell:

                        from jupyter_server.auth import passwd; passwd()

                      The string should be of the form type:salt:hashed-password.
                      """
    )

    password_required = Bool(False, config=True,
                      help="""Forces users to use a password for the Jupyter server.
                      This is useful in a multi user environment, for instance when
                      everybody in the LAN can access each other's machine through ssh.

                      In such a case, serving on localhost is not secure since
                      any user can connect to the Jupyter server via ssh.

                      """
    )

    allow_password_change = Bool(True, config=True,
                    help="""Allow password to be changed at login for the Jupyter server.

                    While loggin in with a token, the Jupyter server UI will give the opportunity to
                    the user to enter a new password at the same time that will replace
                    the token login mechanism.

                    This can be set to false to prevent changing password from the UI/API.
                    """
    )


    disable_check_xsrf = Bool(False, config=True,
        help="""Disable cross-site-request-forgery protection

        Jupyter notebook 4.3.1 introduces protection from cross-site request forgeries,
        requiring API requests to either:

        - originate from pages served by this server (validated with XSRF cookie and token), or
        - authenticate with a token

        Some anonymous compute resources still desire the ability to run code,
        completely without authentication.
        These services can disable all authentication and security checks,
        with the full knowledge of what that implies.
        """
    )

    allow_remote_access = Bool(config=True,
       help="""Allow requests where the Host header doesn't point to a local server

       By default, requests get a 403 forbidden response if the 'Host' header
       shows that the browser thinks it's on a non-local domain.
       Setting this option to True disables this check.

       This protects against 'DNS rebinding' attacks, where a remote web server
       serves you a page and then changes its DNS to send later requests to a
       local IP, bypassing same-origin checks.

       Local IP addresses (such as 127.0.0.1 and ::1) are allowed as local,
       along with hostnames configured in local_hostnames.
       """)

    @default('allow_remote_access')
    def _default_allow_remote(self):
        """Disallow remote access if we're listening only on loopback addresses"""

        # if blank, self.ip was configured to "*" meaning bind to all interfaces,
        # see _valdate_ip
        if self.ip == "":
            return True

        try:
            addr = ipaddress.ip_address(self.ip)
        except ValueError:
            # Address is a hostname
            for info in socket.getaddrinfo(self.ip, self.port, 0, socket.SOCK_STREAM):
                addr = info[4][0]
                if not py3compat.PY3:
                    addr = addr.decode('ascii')

                try:
                    parsed = ipaddress.ip_address(addr.split('%')[0])
                except ValueError:
                    self.log.warning("Unrecognised IP address: %r", addr)
                    continue

                # Macs map localhost to 'fe80::1%lo0', a link local address
                # scoped to the loopback interface. For now, we'll assume that
                # any scoped link-local address is effectively local.
                if not (parsed.is_loopback
                        or (('%' in addr) and parsed.is_link_local)):
                    return True
            return False
        else:
            return not addr.is_loopback

    local_hostnames = List(Unicode(), ['localhost'], config=True,
       help="""Hostnames to allow as local when allow_remote_access is False.

       Local IP addresses (such as 127.0.0.1 and ::1) are automatically accepted
       as local as well.
       """
    )

    open_browser = Bool(False, config=True,
                        help="""Whether to open in a browser after starting.
                        The specific browser used is platform dependent and
                        determined by the python standard library `webbrowser`
                        module, unless it is overridden using the --browser
                        (ServerApp.browser) configuration option.
                        """)

    browser = Unicode(u'', config=True,
                      help="""Specify what command to use to invoke a web
                      browser when starting the server. If not specified, the
                      default browser will be determined by the `webbrowser`
                      standard library module, which allows setting of the
                      BROWSER environment variable to override it.
                      """)

    webbrowser_open_new = Integer(2, config=True,
        help=_("""Specify where to open the server on startup. This is the
        `new` argument passed to the standard library method `webbrowser.open`.
        The behaviour is not guaranteed, but depends on browser support. Valid
        values are:

         - 2 opens a new tab,
         - 1 opens a new window,
         - 0 opens in an existing window.

        See the `webbrowser.open` documentation for details.
        """))

    tornado_settings = Dict(config=True,
            help=_("Supply overrides for the tornado.web.Application that the "
                 "Jupyter server uses."))

    websocket_compression_options = Any(None, config=True,
        help=_("""
        Set the tornado compression options for websocket connections.

        This value will be returned from :meth:`WebSocketHandler.get_compression_options`.
        None (default) will disable compression.
        A dict (even an empty one) will enable compression.

        See the tornado docs for WebSocketHandler.get_compression_options for details.
        """)
    )
    terminado_settings = Dict(config=True,
            help=_('Supply overrides for terminado. Currently only supports "shell_command".'))

    cookie_options = Dict(config=True,
        help=_("Extra keyword arguments to pass to `set_secure_cookie`."
             " See tornado's set_secure_cookie docs for details.")
    )
    get_secure_cookie_kwargs = Dict(config=True,
        help=_("Extra keyword arguments to pass to `get_secure_cookie`."
             " See tornado's get_secure_cookie docs for details.")
    )
    ssl_options = Dict(
            allow_none=True,
            config=True,
            help=_("""Supply SSL options for the tornado HTTPServer.
            See the tornado docs for details."""))

    jinja_environment_options = Dict(config=True,
            help=_("Supply extra arguments that will be passed to Jinja environment."))

    jinja_template_vars = Dict(
        config=True,
        help=_("Extra variables to supply to jinja templates when rendering."),
    )

    base_url = Unicode('/', config=True,
                       help='''The base URL for the Jupyter server.

                       Leading and trailing slashes can be omitted,
                       and will automatically be added.
                       ''')

    @validate('base_url')
    def _update_base_url(self, proposal):
        value = proposal['value']
        if not value.startswith('/'):
            value = '/' + value
        if not value.endswith('/'):
            value = value + '/'
        return value

    extra_static_paths = List(Unicode(), config=True,
        help="""Extra paths to search for serving static files.

        This allows adding javascript/css to be available from the Jupyter server machine,
        or overriding individual files in the IPython"""
    )

    @property
    def static_file_path(self):
        """return extra paths + the default location"""
        return self.extra_static_paths + [DEFAULT_STATIC_FILES_PATH]

    static_custom_path = List(Unicode(),
        help=_("""Path to search for custom.js, css""")
    )

    @default('static_custom_path')
    def _default_static_custom_path(self):
        return [
            os.path.join(d, 'custom') for d in (
                self.config_dir,
                DEFAULT_STATIC_FILES_PATH)
        ]

    extra_template_paths = List(Unicode(), config=True,
        help=_("""Extra paths to search for serving jinja templates.

        Can be used to override templates from jupyter_server.templates.""")
    )

    @property
    def template_file_path(self):
        """return extra paths + the default locations"""
        return self.extra_template_paths + DEFAULT_TEMPLATE_PATH_LIST

    extra_services = List(Unicode(), config=True,
        help=_("""handlers that should be loaded at higher priority than the default services""")
    )

    websocket_url = Unicode("", config=True,
        help="""The base URL for websockets,
        if it differs from the HTTP server (hint: it almost certainly doesn't).

        Should be in the form of an HTTP origin: ws[s]://hostname[:port]
        """
    )

    quit_button = Bool(True, config=True,
        help="""If True, display controls to shut down the Jupyter server, such as menu items or buttons."""
    )

    contents_manager_class = Type(
        default_value=LargeFileManager,
        klass=ContentsManager,
        config=True,
        help=_('The content manager class to use.')
    )

    kernel_manager_class = Type(
        default_value=MappingKernelManager,
        config=True,
        help=_('The kernel manager class to use.')
    )

    session_manager_class = Type(
        default_value=SessionManager,
        config=True,
        help=_('The session manager class to use.')
    )

    config_manager_class = Type(
        default_value=ConfigManager,
        config = True,
        help=_('The config manager class to use')
    )

    kernel_spec_manager = Instance(KernelSpecManager, allow_none=True)

    kernel_spec_manager_class = Type(
        default_value=KernelSpecManager,
        config=True,
        help="""
        The kernel spec manager class to use. Should be a subclass
        of `jupyter_client.kernelspec.KernelSpecManager`.

        The Api of KernelSpecManager is provisional and might change
        without warning between this version of Jupyter and the next stable one.
        """
    )

    login_handler_class = Type(
        default_value=LoginHandler,
        klass=web.RequestHandler,
        config=True,
        help=_('The login handler class to use.'),
    )

    logout_handler_class = Type(
        default_value=LogoutHandler,
        klass=web.RequestHandler,
        config=True,
        help=_('The logout handler class to use.'),
    )

    trust_xheaders = Bool(False, config=True,
        help=(_("Whether to trust or not X-Scheme/X-Forwarded-Proto and X-Real-Ip/X-Forwarded-For headers"
              "sent by the upstream reverse proxy. Necessary if the proxy handles SSL"))
    )

    info_file = Unicode()

    @default('info_file')
    def _default_info_file(self):
        info_file = "jpserver-%s.json" % os.getpid()
        return os.path.join(self.runtime_dir, info_file)

    browser_open_file = Unicode()

    @default('browser_open_file')
    def _default_browser_open_file(self):
        basename = "jpserver-%s-open.html" % os.getpid()
        return os.path.join(self.runtime_dir, basename)

    pylab = Unicode('disabled', config=True,
        help=_("""
        DISABLED: use %pylab or %matplotlib in the notebook to enable matplotlib.
        """)
    )

    @observe('pylab')
    def _update_pylab(self, change):
        """when --pylab is specified, display a warning and exit"""
        if change['new'] != 'warn':
            backend = ' %s' % change['new']
        else:
            backend = ''
        self.log.error(_("Support for specifying --pylab on the command line has been removed."))
        self.log.error(
            _("Please use `%pylab{0}` or `%matplotlib{0}` in the notebook itself.").format(backend)
        )
        self.exit(1)

    notebook_dir = Unicode(
        config=True,
        help=_("DEPRECATED, use root_dir.")
    )

    @observe('notebook_dir')
    def _update_notebook_dir(self, change):
        self.log.warning(_("notebook_dir is deprecated, use root_dir"))
        self.root_dir = change['new']

    root_dir = Unicode(config=True,
        help=_("The directory to use for notebooks and kernels.")
    )

    @default('root_dir')
    def _default_root_dir(self):
        if self.file_to_run:
            return os.path.dirname(os.path.abspath(self.file_to_run))
        else:
            return py3compat.getcwd()

    @validate('root_dir')
    def _root_dir_validate(self, proposal):
        value = proposal['value']
        # Strip any trailing slashes
        # *except* if it's root
        _, path = os.path.splitdrive(value)
        if path == os.sep:
            return value
        value = value.rstrip(os.sep)
        if not os.path.isabs(value):
            # If we receive a non-absolute path, make it absolute.
            value = os.path.abspath(value)
        if not os.path.isdir(value):
            raise TraitError(trans.gettext("No such notebook dir: '%r'") % value)
        return value

    @observe('server_extensions')
    def _update_server_extensions(self, change):
        self.log.warning(_("server_extensions is deprecated, use jpserver_extensions"))
        self.server_extensions = change['new']

    jpserver_extensions = Dict({}, config=True,
        help=(_("Dict of Python modules to load as notebook server extensions."
              "Entry values can be used to enable and disable the loading of"
              "the extensions. The extensions will be loaded in alphabetical "
              "order."))
    )

    reraise_server_extension_failures = Bool(
        False,
        config=True,
        help=_("Reraise exceptions encountered loading server extensions?"),
    )

    iopub_msg_rate_limit = Float(1000, config=True, help=_("""(msgs/sec)
        Maximum rate at which messages can be sent on iopub before they are
        limited."""))

    iopub_data_rate_limit = Float(1000000, config=True, help=_("""(bytes/sec)
        Maximum rate at which stream output can be sent on iopub before they are
        limited."""))

    rate_limit_window = Float(3, config=True, help=_("""(sec) Time window used to
        check the message and data rate limits."""))

    shutdown_no_activity_timeout = Integer(0, config=True,
        help=("Shut down the server after N seconds with no kernels or "
              "terminals running and no activity. "
              "This can be used together with culling idle kernels "
              "(MappingKernelManager.cull_idle_timeout) to "
              "shutdown the Jupyter server when it's not in use. This is not "
              "precisely timed: it may shut down up to a minute later. "
              "0 (the default) disables this automatic shutdown.")
    )

    terminals_enabled = Bool(True, config=True,
         help=_("""Set to False to disable terminals.

         This does *not* make the server more secure by itself.
         Anything the user can in a terminal, they can also do in a notebook.

         Terminals may also be automatically disabled if the terminado package
         is not available.
         """))

    authenticate_prometheus = Bool(
        True,
        help=""""
        Require authentication to access prometheus metrics.
        """,
        config=True
    )

    def parse_command_line(self, argv=None):

        super(ServerApp, self).parse_command_line(argv)

        if self.extra_args:
            arg0 = self.extra_args[0]
            f = os.path.abspath(arg0)
            self.argv.remove(arg0)
            if not os.path.exists(f):
                self.log.critical(_("No such file or directory: %s"), f)
                self.exit(1)

            # Use config here, to ensure that it takes higher priority than
            # anything that comes from the config dirs.
            c = Config()
            if os.path.isdir(f):
                c.ServerApp.root_dir = f
            elif os.path.isfile(f):
                c.ServerApp.file_to_run = f
            self.update_config(c)

    def init_configurables(self):

        # If gateway server is configured, replace appropriate managers to perform redirection.  To make
        # this determination, instantiate the GatewayClient config singleton.
        self.gateway_config = GatewayClient.instance(parent=self)

        if self.gateway_config.gateway_enabled:
            self.kernel_manager_class = 'jupyter_server.gateway.managers.GatewayKernelManager'
            self.session_manager_class = 'jupyter_server.gateway.managers.GatewaySessionManager'
            self.kernel_spec_manager_class = 'jupyter_server.gateway.managers.GatewayKernelSpecManager'

        self.kernel_spec_manager = self.kernel_spec_manager_class(
            parent=self,
        )
        self.kernel_manager = self.kernel_manager_class(
            parent=self,
            log=self.log,
            connection_dir=self.runtime_dir,
            kernel_spec_manager=self.kernel_spec_manager,
        )
        self.contents_manager = self.contents_manager_class(
            parent=self,
            log=self.log,
        )
        self.session_manager = self.session_manager_class(
            parent=self,
            log=self.log,
            kernel_manager=self.kernel_manager,
            contents_manager=self.contents_manager,
        )
        self.config_manager = self.config_manager_class(
            parent=self,
            log=self.log,
        )

    def init_logging(self):
        # This prevents double log messages because tornado use a root logger that
        # self.log is a child of. The logging module dipatches log messages to a log
        # and all of its ancenstors until propagate is set to False.
        self.log.propagate = False

        for log in app_log, access_log, gen_log:
            # consistent log output name (ServerApp instead of tornado.access, etc.)
            log.name = self.log.name
        # hook up tornado 3's loggers to our app handlers
        logger = logging.getLogger('tornado')
        logger.propagate = True
        logger.parent = self.log
        logger.setLevel(self.log.level)

    def init_webapp(self):
        """initialize tornado webapp"""
        self.tornado_settings['allow_origin'] = self.allow_origin
        self.tornado_settings['websocket_compression_options'] = self.websocket_compression_options
        if self.allow_origin_pat:
            self.tornado_settings['allow_origin_pat'] = re.compile(self.allow_origin_pat)
        self.tornado_settings['allow_credentials'] = self.allow_credentials
        self.tornado_settings['cookie_options'] = self.cookie_options
        self.tornado_settings['get_secure_cookie_kwargs'] = self.get_secure_cookie_kwargs
        self.tornado_settings['token'] = self.token

        # ensure default_url starts with base_url
        if not self.default_url.startswith(self.base_url):
            self.default_url = url_path_join(self.base_url, self.default_url)

        if self.password_required and (not self.password):
            self.log.critical(_("Jupyter servers are configured to only be run with a password."))
            self.log.critical(_("Hint: run the following command to set a password"))
            self.log.critical(_("\t$ python -m jupyter_server.auth password"))
            sys.exit(1)

        self.web_app = ServerWebApplication(
            self, self.default_services, self.kernel_manager, self.contents_manager,
            self.session_manager, self.kernel_spec_manager,
            self.config_manager, self.extra_services,
            self.log, self.base_url, self.default_url, self.tornado_settings,
            self.jinja_environment_options,
        )
        if self.certfile:
            self.ssl_options['certfile'] = self.certfile
        if self.keyfile:
            self.ssl_options['keyfile'] = self.keyfile
        if self.client_ca:
            self.ssl_options['ca_certs'] = self.client_ca
        if not self.ssl_options:
            # could be an empty dict or None
            # None indicates no SSL config
            self.ssl_options = None
        else:
            # SSL may be missing, so only import it if it's to be used
            import ssl
            # PROTOCOL_TLS selects the highest ssl/tls protocol version that both the client and
            # server support. When PROTOCOL_TLS is not available use PROTOCOL_SSLv23.
            self.ssl_options.setdefault(
                'ssl_version',
                getattr(ssl, 'PROTOCOL_TLS', ssl.PROTOCOL_SSLv23)
            )
            if self.ssl_options.get('ca_certs', False):
                self.ssl_options.setdefault('cert_reqs', ssl.CERT_REQUIRED)
            ssl_options = self.ssl_options

        self.login_handler_class.validate_security(self, ssl_options=self.ssl_options)

    @property
    def display_url(self):
        if self.custom_display_url:
            parts = urllib.parse.urlparse(self.custom_display_url)
            path = parts.path
            ip = parts.hostname
        else:
            path = None
            if self.ip in ('', '0.0.0.0'):
                ip = "%s" % socket.gethostname()
            else:
                ip = self.ip

        token = None
        if self.token:
            # Don't log full token if it came from config
            token = self.token if self._token_generated else '...'

        url = (
            self.get_url(ip=ip, path=path, token=token)
            + '\n or '
            + self.get_url(ip='127.0.0.1', path=path, token=token)
        )
        return url

    @property
    def connection_url(self):
        ip = self.ip if self.ip else 'localhost'
        return self.get_url(ip=ip, path=self.base_url)

    def get_url(self, ip=None, path=None, token=None):
        """Build a url for the application with reasonable defaults."""
        if not ip:
            ip = self.ip if self.ip else 'localhost'
        if not path:
            path = self.default_url
        # Build query string.
        if token:
            token = urllib.parse.urlencode({'token': token})
        # Build the URL Parts to dump.
        urlparts = urllib.parse.ParseResult(
            scheme='https' if self.certfile else 'http',
            netloc="{ip}:{port}".format(ip=ip, port=self.port),
            path=path,
            params=None,
            query=token,
            fragment=None
        )
        return urlparts.geturl()

    def init_terminals(self):
        if not self.terminals_enabled:
            return

        try:
            from .terminal import initialize
            initialize(self.web_app, self.root_dir, self.connection_url, self.terminado_settings)
            self.web_app.settings['terminals_available'] = True
        except ImportError as e:
            self.log.warning(_("Terminals not available (error was %s)"), e)

    def init_signal(self):
        if not sys.platform.startswith('win') and sys.stdin and sys.stdin.isatty():
            signal.signal(signal.SIGINT, self._handle_sigint)
        signal.signal(signal.SIGTERM, self._signal_stop)
        if hasattr(signal, 'SIGUSR1'):
            # Windows doesn't support SIGUSR1
            signal.signal(signal.SIGUSR1, self._signal_info)
        if hasattr(signal, 'SIGINFO'):
            # only on BSD-based systems
            signal.signal(signal.SIGINFO, self._signal_info)

    def _handle_sigint(self, sig, frame):
        """SIGINT handler spawns confirmation dialog"""
        # register more forceful signal handler for ^C^C case
        signal.signal(signal.SIGINT, self._signal_stop)
        # request confirmation dialog in bg thread, to avoid
        # blocking the App
        thread = threading.Thread(target=self._confirm_exit)
        thread.daemon = True
        thread.start()

    def _restore_sigint_handler(self):
        """callback for restoring original SIGINT handler"""
        signal.signal(signal.SIGINT, self._handle_sigint)

    def _confirm_exit(self):
        """confirm shutdown on ^C

        A second ^C, or answering 'y' within 5s will cause shutdown,
        otherwise original SIGINT handler will be restored.

        This doesn't work on Windows.
        """
        info = self.log.info
        info(_('interrupted'))
        print(self.running_server_info())
        yes = _('y')
        no = _('n')
        sys.stdout.write(_("Shutdown this Jupyter server (%s/[%s])? ") % (yes, no))
        sys.stdout.flush()
        r,w,x = select.select([sys.stdin], [], [], 5)
        if r:
            line = sys.stdin.readline()
            if line.lower().startswith(yes) and no not in line.lower():
                self.log.critical(_("Shutdown confirmed"))
                # schedule stop on the main thread,
                # since this might be called from a signal handler
                self.io_loop.add_callback_from_signal(self.io_loop.stop)
                return
        else:
            print(_("No answer for 5s:"), end=' ')
        print(_("resuming operation..."))
        # no answer, or answer is no:
        # set it back to original SIGINT handler
        # use IOLoop.add_callback because signal.signal must be called
        # from main thread
        self.io_loop.add_callback_from_signal(self._restore_sigint_handler)

    def _signal_stop(self, sig, frame):
        self.log.critical(_("received signal %s, stopping"), sig)
        self.io_loop.add_callback_from_signal(self.io_loop.stop)

    def _signal_info(self, sig, frame):
        print(self.running_server_info())

    def init_components(self):
        """Check the components submodule, and warn if it's unclean"""
        # TODO: this should still check, but now we use bower, not git submodule
        pass

    def find_server_extensions(self):
        """
        Searches Jupyter paths for jpserver_extensions.
        """

        # Walk through all config files looking for jpserver_extensions.
        #
        # Each extension will likely have a JSON config file enabling itself in
        # the "jupyter_server_config.d" directory. Find each of these and
        # merge there results in order of precedence.
        #
        # Load server extensions with ConfigManager.
        # This enables merging on keys, which we want for extension enabling.
        # Regular config loading only merges at the class level,
        # so each level clobbers the previous.
        config_paths = jupyter_config_path()
        if self.config_dir not in config_paths:
            # add self.config_dir to the front, if set manually
            config_paths.insert(0, self.config_dir)
        manager = ExtensionConfigManager(read_config_path=config_paths)
        extensions = manager.get_jpserver_extensions()

        for modulename, enabled in sorted(extensions.items()):
            if modulename not in self.jpserver_extensions:
                self.config.ServerApp.jpserver_extensions.update({modulename: enabled})
                self.jpserver_extensions.update({modulename: enabled})

    def init_server_extensions(self):
        """
        If an extension's metadata includes an 'app' key,
        the value must be a subclass of ExtensionApp. An instance
        of the class will be created at this step. The config for
        this instance will inherit the ServerApp's config object
        and load its own config.
        """
        # Create an instance of the ExtensionManager.
        self.extension_manager = ExtensionManager(log=self.log)
        self.extension_manager.from_jpserver_extensions(self.jpserver_extensions)
        self.extension_manager.link_all_extensions(self)

    def load_server_extensions(self):
        """Load any extensions specified by config.

        Import the module, then call the load_jupyter_server_extension function,
        if one exists.

        The extension API is experimental, and may change in future releases.
        """
        self.extension_manager.load_all_extensions(self)

    def init_mime_overrides(self):
        # On some Windows machines, an application has registered incorrect
        # mimetypes in the registry.
        # Tornado uses this when serving .css and .js files, causing browsers to
        # reject these files. We know the mimetype always needs to be text/css for css
        # and application/javascript for JS, so we override it here
        # and explicitly tell the mimetypes to not trust the Windows registry
        if os.name == 'nt':
            # do not trust windows registry, which regularly has bad info
            mimetypes.init(files=[])
        # ensure css, js are correct, which are required for pages to function
        mimetypes.add_type('text/css', '.css')
        mimetypes.add_type('application/javascript', '.js')
        # for python <3.8
        mimetypes.add_type('application/wasm', '.wasm')

    def shutdown_no_activity(self):
        """Shutdown server on timeout when there are no kernels or terminals."""
        km = self.kernel_manager
        if len(km) != 0:
            return   # Kernels still running

        try:
            term_mgr = self.web_app.settings['terminal_manager']
        except KeyError:
            pass  # Terminals not enabled
        else:
            if term_mgr.terminals:
                return   # Terminals still running

        seconds_since_active = \
            (utcnow() - self.web_app.last_activity()).total_seconds()
        self.log.debug("No activity for %d seconds.",
                       seconds_since_active)
        if seconds_since_active > self.shutdown_no_activity_timeout:
            self.log.info("No kernels or terminals for %d seconds; shutting down.",
                          seconds_since_active)
            self.stop()

    def init_shutdown_no_activity(self):
        if self.shutdown_no_activity_timeout > 0:
            self.log.info("Will shut down after %d seconds with no kernels or terminals.",
                          self.shutdown_no_activity_timeout)
            pc = ioloop.PeriodicCallback(self.shutdown_no_activity, 60000)
            pc.start()

    @property
    def http_server(self):
        """An instance of Tornado's HTTPServer class for the Server Web Application."""
        try:
            return self._http_server
        except AttributeError as e:
            raise AttributeError(
                'An HTTPServer instance has not been created for the '
                'Server Web Application. To create an HTTPServer for this '
                'application, call `.init_httpserver()`.'
                ) from e

    def init_httpserver(self):
        """Creates an instance of a Tornado HTTPServer for the Server Web Application
        and sets the http_server attribute.
        """
        # Check that a web_app has been initialized before starting a server.
        if not hasattr(self, 'web_app'):
            raise AttributeError('A tornado web application has not be initialized. '
                                 'Try calling `.init_webapp()` first.')

        # Create an instance of the server.
        self._http_server = httpserver.HTTPServer(
            self.web_app,
            ssl_options=self.ssl_options,
            xheaders=self.trust_xheaders,
            max_body_size=self.max_body_size,
            max_buffer_size=self.max_buffer_size
        )
        success = None
        for port in random_ports(self.port, self.port_retries+1):
            try:
                self.http_server.listen(port, self.ip)
            except socket.error as e:
                if e.errno == errno.EADDRINUSE:
                    self.log.info(_('The port %i is already in use, trying another port.') % port)
                    continue
                elif e.errno in (errno.EACCES, getattr(errno, 'WSAEACCES', errno.EACCES)):
                    self.log.warning(_("Permission to listen on port %i denied") % port)
                    continue
                else:
                    raise
            else:
                self.port = port
                success = True
                break
        if not success:
            self.log.critical(_('ERROR: the Jupyter server could not be started because '
                              'no available port could be found.'))
            self.exit(1)

    @staticmethod
    def _init_asyncio_patch():
        """no longer needed with tornado 6.1"""
        warnings.warn(
            """ServerApp._init_asyncio_patch called, and is longer needed for """
            """tornado 6.1+, and will be removed in a future release.""",
            DeprecationWarning
        )

    def init_eventlog(self):
        self.eventlog = EventLog(parent=self)
        # Register schemas for notebook services.
        for file_path in get_schema_files():
            self.eventlog.register_schema_file(file_path)

    @catch_config_error
    def initialize(self, argv=None, find_extensions=True, new_httpserver=True):
        """Initialize the Server application class, configurables, web application, and http server.

        Parameters
        ----------
        argv: list or None
            CLI arguments to parse.

        find_extensions: bool
            If True, find and load extensions listed in Jupyter config paths. If False,
            only load extensions that are passed to ServerApp directy through
            the `argv`, `config`, or `jpserver_extensions` arguments.

        new_httpserver: bool
            If True, a tornado HTTPServer instance will be created and configured for the Server Web
            Application. This will set the http_server attribute of this class.
        """
        # Parse command line, load ServerApp config files,
        # and update ServerApp config.
        super(ServerApp, self).initialize(argv)
        # Initialize all components of the ServerApp.
        if self._dispatching:
            return
        # Then, use extensions' config loading mechanism to
        # update config. ServerApp config takes precedence.
        if find_extensions:
            self.find_server_extensions()
        self.init_logging()
        self.init_eventlog()
        self.init_server_extensions()
        self.init_configurables()
        self.init_components()
        self.init_eventlog()
        self.init_webapp()
        if new_httpserver:
            self.init_httpserver()
        self.init_terminals()
        self.init_signal()
        self.load_server_extensions()
        self.init_mime_overrides()
        self.init_shutdown_no_activity()

    def cleanup_kernels(self):
        """Shutdown all kernels.

        The kernels will shutdown themselves when this process no longer exists,
        but explicit shutdown allows the KernelManagers to cleanup the connection files.
        """
        n_kernels = len(self.kernel_manager.list_kernel_ids())
        kernel_msg = trans.ngettext('Shutting down %d kernel', 'Shutting down %d kernels', n_kernels)
        self.log.info(kernel_msg % n_kernels)
        run_sync(self.kernel_manager.shutdown_all())

    def running_server_info(self, kernel_count=True):
        "Return the current working directory and the server url information"
        info = self.contents_manager.info_string() + "\n"
        if kernel_count:
            n_kernels = len(self.kernel_manager.list_kernel_ids())
            kernel_msg = trans.ngettext("%d active kernel", "%d active kernels", n_kernels)
            info += kernel_msg % n_kernels
            info += "\n"
        # Format the info so that the URL fits on a single line in 80 char display
        info += _("Jupyter Server {version} is running at:\n{url}".
                  format(version=ServerApp.version, url=self.display_url))
        if self.gateway_config.gateway_enabled:
            info += _("\nKernels will be managed by the Gateway server running at:\n%s") % self.gateway_config.url
        return info

    def server_info(self):
        """Return a JSONable dict of information about this server."""
        return {'url': self.connection_url,
                'hostname': self.ip if self.ip else 'localhost',
                'port': self.port,
                'secure': bool(self.certfile),
                'base_url': self.base_url,
                'token': self.token,
                'root_dir': os.path.abspath(self.root_dir),
                'password': bool(self.password),
                'pid': os.getpid(),
                'version': ServerApp.version,
               }

    def write_server_info_file(self):
        """Write the result of server_info() to the JSON file info_file."""
        try:
            with secure_write(self.info_file) as f:
                json.dump(self.server_info(), f, indent=2, sort_keys=True)
        except OSError as e:
            self.log.error(_("Failed to write server-info to %s: %s"),
                           self.info_file, e)

    def remove_server_info_file(self):
        """Remove the jpserver-<pid>.json file created for this server.

        Ignores the error raised when the file has already been removed.
        """
        try:
            os.unlink(self.info_file)
        except OSError as e:
            if e.errno != errno.ENOENT:
                raise

    def write_browser_open_file(self):
        """Write an nbserver-<pid>-open.html file

        This can be used to open the notebook in a browser
        """
        # default_url contains base_url, but so does connection_url
        open_url = self.default_url[len(self.base_url):]

        with open(self.browser_open_file, 'w', encoding='utf-8') as f:
            self._write_browser_open_file(open_url, f)

    def _write_browser_open_file(self, url, fh):
        if self.token:
            url = url_concat(url, {'token': self.token})
        url = url_path_join(self.connection_url, url)

        jinja2_env = self.web_app.settings['jinja2_env']
        template = jinja2_env.get_template('browser-open.html')
        fh.write(template.render(open_url=url, base_url=self.base_url))

    def remove_browser_open_file(self):
        """Remove the nbserver-<pid>-open.html file created for this server.

        Ignores the error raised when the file has already been removed.
        """
        try:
            os.unlink(self.browser_open_file)
        except OSError as e:
            if e.errno != errno.ENOENT:
                raise

    def launch_browser(self):
        try:
            browser = webbrowser.get(self.browser or None)
        except webbrowser.Error as e:
            self.log.warning(_('No web browser found: %s.') % e)
            browser = None

        if not browser:
            return

        if self.file_to_run:
            if not os.path.exists(self.file_to_run):
                self.log.critical(_("%s does not exist") % self.file_to_run)
                self.exit(1)

            relpath = os.path.relpath(self.file_to_run, self.root_dir)
            uri = url_escape(url_path_join('notebooks', *relpath.split(os.sep)))

            # Write a temporary file to open in the browser
            fd, open_file = tempfile.mkstemp(suffix='.html')
            with open(fd, 'w', encoding='utf-8') as fh:
                self._write_browser_open_file(uri, fh)
        else:
            open_file = self.browser_open_file

        b = lambda: browser.open(
            urljoin('file:', pathname2url(open_file)),
            new=self.webbrowser_open_new)
        threading.Thread(target=b).start()

    def start_app(self):
        super(ServerApp, self).start()

        if not self.allow_root:
            # check if we are running as root, and abort if it's not allowed
            try:
                uid = os.geteuid()
            except AttributeError:
                uid = -1 # anything nonzero here, since we can't check UID assume non-root
            if uid == 0:
                self.log.critical(_("Running as root is not recommended. Use --allow-root to bypass."))
                self.exit(1)

        info = self.log.info
        for line in self.running_server_info(kernel_count=False).split("\n"):
            info(line)
        info(_("Use Control-C to stop this server and shut down all kernels (twice to skip confirmation)."))
        if 'dev' in jupyter_server.__version__:
            info(_("Welcome to Project Jupyter! Explore the various tools available"
                 " and their corresponding documentation. If you are interested"
                 " in contributing to the platform, please visit the community"
                 "resources section at https://jupyter.org/community.html."))

        self.write_server_info_file()
        self.write_browser_open_file()

        if self.open_browser:
            self.launch_browser()

        if self.token and self._token_generated:
            # log full URL with generated token, so there's a copy/pasteable link
            # with auth info.
            self.log.critical('\n'.join([
                '\n',
                'To access the server, open this file in a browser:',
                '    %s' % urljoin('file:', pathname2url(self.browser_open_file)),
                'Or copy and paste one of these URLs:',
                '    %s' % self.display_url,
            ]))

    def start_ioloop(self):
        """Start the IO Loop."""
        self.io_loop = ioloop.IOLoop.current()
        if sys.platform.startswith('win'):
            # add no-op to wake every 5s
            # to handle signals that may be ignored by the inner loop
            pc = ioloop.PeriodicCallback(lambda : None, 5000)
            pc.start()
        try:
            self.io_loop.start()
        except KeyboardInterrupt:
            self.log.info(_("Interrupted..."))
        finally:
            self.remove_server_info_file()
            self.remove_browser_open_file()
            self.cleanup_kernels()

    def start(self):
        """ Start the Jupyter server app, after initialization

        This method takes no arguments so all configuration and initialization
        must be done prior to calling this method."""
        self.start_app()
        self.start_ioloop()

    def stop(self):
        def _stop():
            # Stop a server if its set.
            if hasattr(self, '_http_server'):
                self.http_server.stop()
            self.io_loop.stop()
        self.io_loop.add_callback(_stop)


def list_running_servers(runtime_dir=None):
    """Iterate over the server info files of running notebook servers.

    Given a runtime directory, find jpserver-* files in the security directory,
    and yield dicts of their information, each one pertaining to
    a currently running notebook server instance.
    """
    if runtime_dir is None:
        runtime_dir = jupyter_runtime_dir()

    # The runtime dir might not exist
    if not os.path.isdir(runtime_dir):
        return

    for file_name in os.listdir(runtime_dir):
        if re.match('jpserver-(.+).json', file_name):
            with io.open(os.path.join(runtime_dir, file_name), encoding='utf-8') as f:
                info = json.load(f)

            # Simple check whether that process is really still running
            # Also remove leftover files from IPython 2.x without a pid field
            if ('pid' in info) and check_pid(info['pid']):
                yield info
            else:
                # If the process has died, try to delete its info file
                try:
                    os.unlink(os.path.join(runtime_dir, file_name))
                except OSError:
                    pass  # TODO: This should warn or log or something
#-----------------------------------------------------------------------------
# Main entry point
#-----------------------------------------------------------------------------

main = launch_new_instance = ServerApp.launch_instance
