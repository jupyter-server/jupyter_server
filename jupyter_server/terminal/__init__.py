"""Terminals support."""
import warnings

# Shims
from jupyter_server_terminals import api_handlers, initialize  # noqa
from jupyter_server_terminals.handlers import TermSocket  # noqa
from jupyter_server_terminals.terminalmanager import TerminalManager  # noqa

warnings.warn(
    "Terminals support has moved to `jupyter_server_terminals`",
    DeprecationWarning,
    stacklevel=2,
)
