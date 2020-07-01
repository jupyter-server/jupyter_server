import os

import terminado
from ..utils import check_version

if not check_version(terminado.__version__, '0.8.3'):
    raise ImportError("terminado >= 0.8.3 required, found %s" % terminado.__version__)

from ipython_genutils.py3compat import which
from terminado import NamedTermManager
from tornado.log import app_log
from jupyter_server.utils import url_path_join as ujoin
from . import api_handlers
from .handlers import TermSocket


def initialize(webapp, root_dir, connection_url, settings):
    if os.name == 'nt':
        default_shell = 'powershell.exe'
    else:
        default_shell = which('sh')
    shell = settings.get('shell_command',
        [os.environ.get('SHELL') or default_shell]
    )
    # Enable login mode - to automatically source the /etc/profile
    # script, but only for non-nested shells; for nested shells, it's
    # superfluous and may even be harmful (e.g. on macOS, where login
    # shells invoke /usr/libexec/path_helper to add entries from
    # /etc/paths{,.d} to the PATH, reordering it in the process and
    # potentially overriding virtualenvs and other PATH modifications)
    if os.name != 'nt' and int(os.environ.get("SHLVL", 0)) < 1:
        shell.append('-l')
    terminal_manager = webapp.settings['terminal_manager'] = NamedTermManager(
        shell_command=shell,
        extra_env={'JUPYTER_SERVER_ROOT': root_dir,
                   'JUPYTER_SERVER_URL': connection_url,
                   },
    )
    terminal_manager.log = app_log
    base_url = webapp.settings['base_url']
    handlers = [
        (ujoin(base_url, r"/terminals/websocket/(\w+)"), TermSocket,
             {'term_manager': terminal_manager}),
        (ujoin(base_url, r"/api/terminals"), api_handlers.TerminalRootHandler),
        (ujoin(base_url, r"/api/terminals/(\w+)"), api_handlers.TerminalHandler),
    ]
    webapp.add_handlers(".*$", handlers)
