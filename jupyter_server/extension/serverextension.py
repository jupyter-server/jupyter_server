# coding: utf-8
"""Utilities for installing extensions"""

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

import os
import sys
import importlib
from tornado.log import LogFormatter
from traitlets import Bool, Any
from traitlets.utils.importstring import import_item

from jupyter_core.application import JupyterApp
from jupyter_core.paths import (
    jupyter_config_dir,
    jupyter_config_path,
    ENV_CONFIG_PATH,
    SYSTEM_CONFIG_PATH
)
from jupyter_server._version import __version__
from jupyter_server.config_manager import BaseJSONConfigManager


def _get_server_extension_metadata(module):
    """Load server extension metadata from a module.

    Returns a tuple of (
        the package as loaded
        a list of server extension specs: [
            {
                "module": "import.path.to.extension"
            }
        ]
    )

    Parameters
    ----------
    module : str
        Importable Python module exposing the
        magic-named `_jupyter_server_extension_paths` function
    """
    m = import_item(module)
    if not hasattr(m, '_jupyter_server_extension_paths'):
        raise KeyError(u'The Python module {} does not include any valid server extensions'.format(module))
    return m, m._jupyter_server_extension_paths()


class ArgumentConflict(ValueError):
    pass

_base_flags = {}
_base_flags.update(JupyterApp.flags)
_base_flags.pop("y", None)
_base_flags.pop("generate-config", None)
_base_flags.update({
    "user" : ({
        "BaseExtensionApp" : {
            "user" : True,
        }}, "Apply the operation only for the given user"
    ),
    "system" : ({
        "BaseExtensionApp" : {
            "user" : False,
            "sys_prefix": False,
        }}, "Apply the operation system-wide"
    ),
    "sys-prefix" : ({
        "BaseExtensionApp" : {
            "sys_prefix" : True,
        }}, "Use sys.prefix as the prefix for installing extensions (for environments, packaging)"
    ),
    "py" : ({
        "BaseExtensionApp" : {
            "python" : True,
        }}, "Install from a Python package"
    )
})
_base_flags['python'] = _base_flags['py']

_base_aliases = {}
_base_aliases.update(JupyterApp.aliases)


class BaseExtensionApp(JupyterApp):
    """Base extension installer app"""
    _log_formatter_cls = LogFormatter
    flags = _base_flags
    aliases = _base_aliases
    version = __version__

    user = Bool(False, config=True, help="Whether to do a user install")
    sys_prefix = Bool(True, config=True, help="Use the sys.prefix as the prefix")
    python = Bool(False, config=True, help="Install from a Python package")

    def _log_format_default(self):
        """A default format for messages"""
        return "%(message)s"


def _get_config_dir(user=False, sys_prefix=False):
    """Get the location of config files for the current context

    Returns the string to the environment

    Parameters
    ----------

    user : bool [default: False]
        Get the user's .jupyter config directory
    sys_prefix : bool [default: False]
        Get sys.prefix, i.e. ~/.envs/my-env/etc/jupyter
    """
    user = False if sys_prefix else user
    if user and sys_prefix:
        raise ArgumentConflict("Cannot specify more than one of user or sys_prefix")
    if user:
        extdir = jupyter_config_dir()
    elif sys_prefix:
        extdir = ENV_CONFIG_PATH[0]
    else:
        extdir = SYSTEM_CONFIG_PATH[0]
    return extdir


# Constants for pretty print extension listing function.
# Window doesn't support coloring in the commandline
GREEN_ENABLED = '\033[32menabled\033[0m' if os.name != 'nt' else 'enabled'
RED_DISABLED = '\033[31mdisabled\033[0m' if os.name != 'nt' else 'disabled'
GREEN_OK = '\033[32mOK\033[0m' if os.name != 'nt' else 'ok'
RED_X = '\033[31m X\033[0m' if os.name != 'nt' else ' X'

# ------------------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------------------

class ExtensionLoadingError(Exception): pass


class ExtensionValidationError(Exception): pass



def _get_load_jupyter_server_extension(obj):
    """Looks for load_jupyter_server_extension as an attribute
    of the object or module.
    """
    try:
        func = getattr(obj, '_load_jupyter_server_extension')
    except AttributeError:
        func = getattr(obj, 'load_jupyter_server_extension')
    except:
        raise ExtensionLoadingError("_load_jupyter_server_extension function was not found.")
    return func


def validate_server_extension(name):
    """Validates that you can import the extension module,
    gather all extension metadata, and find `load_jupyter_server_extension`
    functions for each extension.

    Raises a validation error if extensions cannot be found.

    Parameter
    ---------
    extension_module: module
        The extension module (first value) returned by _get_server_extension_metadata

    extension_metadata : list
        The list (second value) returned by _get_server_extension_metadata

    Returns
    -------
    version : str
        Extension version.
    """
    # If the extension does not exist, raise an exception
    try:
        mod, metadata = _get_server_extension_metadata(name)
        version = getattr(mod, '__version__', '')
    except ImportError:
        raise ExtensionValidationError('{} is not importable.'.format(name))

    try:
        for item in metadata:
            extapp = item.get('app', None)
            extloc = item.get('module', None)
            if extapp and extloc:
                func = _get_load_jupyter_server_extension(extapp)
            elif extloc:
                extmod = importlib.import_module(extloc)
                func = _get_load_jupyter_server_extension(extmod)
            else:
                raise AttributeError
    # If the extension does not have a `load_jupyter_server_extension` function, raise exception.
    except AttributeError:
        raise ExtensionValidationError('Found "{}" module but cannot load it.'.format(name))
    return version


def toggle_server_extension_python(import_name, enabled=None, parent=None, user=False, sys_prefix=True):
    """Toggle the boolean setting for a given server extension
    in a Jupyter config file.
    """
    sys_prefix = False if user else sys_prefix
    config_dir = _get_config_dir(user=user, sys_prefix=sys_prefix)
    cm = BaseJSONConfigManager(parent=parent, config_dir=config_dir)
    cfg = cm.get("jupyter_server_config")
    server_extensions = (
        cfg.setdefault("ServerApp", {})
        .setdefault("jpserver_extensions", {})
    )
    old_enabled = server_extensions.get(import_name, None)
    new_enabled = enabled if enabled is not None else not old_enabled
    server_extensions[import_name] = new_enabled
    cm.update("jupyter_server_config", cfg)

# ----------------------------------------------------------------------
# Applications
# ----------------------------------------------------------------------

flags = {}
flags.update(BaseExtensionApp.flags)
flags.pop("y", None)
flags.pop("generate-config", None)
flags.update({
    "user" : ({
        "ToggleServerExtensionApp" : {
            "user" : True,
        }}, "Perform the operation for the current user"
    ),
    "system" : ({
        "ToggleServerExtensionApp" : {
            "user" : False,
            "sys_prefix": False,
        }}, "Perform the operation system-wide"
    ),
    "sys-prefix" : ({
        "ToggleServerExtensionApp" : {
            "sys_prefix" : True,
        }}, "Use sys.prefix as the prefix for installing server extensions"
    ),
    "py" : ({
        "ToggleServerExtensionApp" : {
            "python" : True,
        }}, "Install from a Python package"
    ),
})
flags['python'] = flags['py']


class ToggleServerExtensionApp(BaseExtensionApp):
    """A base class for enabling/disabling extensions"""
    name = "jupyter server extension enable/disable"
    description = "Enable/disable a server extension using frontend configuration files."

    flags = flags

    user = Bool(False, config=True, help="Whether to do a user install")
    sys_prefix = Bool(True, config=True, help="Use the sys.prefix as the prefix")
    python = Bool(False, config=True, help="Install from a Python package")
    _toggle_value = Bool()
    _toggle_pre_message = ''
    _toggle_post_message = ''

    def toggle_server_extension(self, import_name):
        """Change the status of a named server extension.

        Uses the value of `self._toggle_value`.

        Parameters
        ---------

        import_name : str
            Importable Python module (dotted-notation) exposing the magic-named
            `load_jupyter_server_extension` function
        """
        try:
            self.log.info("{}: {}".format(self._toggle_pre_message.capitalize(), import_name))
            # Validate the server extension.
            self.log.info("    - Validating {}...".format(import_name))
            version = validate_server_extension(import_name)

            # Toggle the server extension to active.
            toggle_server_extension_python(
                import_name,
                self._toggle_value,
                parent=self,
                user=self.user,
                sys_prefix=self.sys_prefix
            )
            self.log.info("      {} {} {}".format(import_name, version, GREEN_OK))

            # If successful, let's log.
            self.log.info("    - Extension successfully {}.".format(self._toggle_post_message))
        except ExtensionValidationError as err:
            self.log.info("     {} Validation failed: {}".format(RED_X, err))

    def toggle_server_extension_python(self, package):
        """Change the status of some server extensions in a Python package.

        Uses the value of `self._toggle_value`.

        Parameters
        ---------

        package : str
            Importable Python module exposing the
            magic-named `_jupyter_server_extension_paths` function
        """
        _, server_exts = _get_server_extension_metadata(package)
        for server_ext in server_exts:
            module = server_ext['module']
            self.toggle_server_extension(module)

    def start(self):
        """Perform the App's actions as configured"""
        if not self.extra_args:
            sys.exit('Please specify a server extension/package to enable or disable')
        for arg in self.extra_args:
            if self.python:
                self.toggle_server_extension_python(arg)
            else:
                self.toggle_server_extension(arg)


class EnableServerExtensionApp(ToggleServerExtensionApp):
    """An App that enables (and validates) Server Extensions"""
    name = "jupyter server extension enable"
    description = """
    Enable a server extension in configuration.

    Usage
        jupyter server extension enable [--system|--sys-prefix]
    """
    _toggle_value = True
    _toggle_pre_message = "enabling"
    _toggle_post_message = "enabled"


class DisableServerExtensionApp(ToggleServerExtensionApp):
    """An App that disables Server Extensions"""
    name = "jupyter server extension disable"
    description = """
    Disable a server extension in configuration.

    Usage
        jupyter server extension disable [--system|--sys-prefix]
    """
    _toggle_value = False
    _toggle_pre_message = "disabling"
    _toggle_post_message = "disabled"


class ListServerExtensionsApp(BaseExtensionApp):
    """An App that lists (and validates) Server Extensions"""
    name = "jupyter server extension list"
    version = __version__
    description = "List all server extensions known by the configuration system"

    def list_server_extensions(self):
        """List all enabled and disabled server extensions, by config path

        Enabled extensions are validated, potentially generating warnings.
        """
        config_dirs = jupyter_config_path()

        # Iterate over all locations where extensions might be named.
        for config_dir in config_dirs:
            cm = BaseJSONConfigManager(parent=self, config_dir=config_dir)
            data = cm.get("jupyter_server_config")
            server_extensions = (
                data.setdefault("ServerApp", {})
                .setdefault("jpserver_extensions", {})
            )
            if server_extensions:
                self.log.info(u'config dir: {}'.format(config_dir))

            # Iterate over packages listed in jpserver_extensions.
            for pkg_name,  enabled in server_extensions.items():
                # Attempt to get extension metadata
                _, __ = _get_server_extension_metadata(pkg_name)
                self.log.info(u'    {} {}'.format(
                              pkg_name,
                              GREEN_ENABLED if enabled else RED_DISABLED))
                try:
                    self.log.info("    - Validating {}...".format(pkg_name))
                    version = validate_server_extension(pkg_name)
                    self.log.info("      {} {} {}".format(pkg_name, version, GREEN_OK))

                except ExtensionValidationError as err:
                    self.log.warn("      {} {}".format(RED_X, err))

    def start(self):
        """Perform the App's actions as configured"""
        self.list_server_extensions()


_examples = """
jupyter server extension list                        # list all configured server extensions
jupyter server extension enable --py <packagename>   # enable all server extensions in a Python package
jupyter server extension disable --py <packagename>  # disable all server extensions in a Python package
"""


class ServerExtensionApp(BaseExtensionApp):
    """Root level server extension app"""
    name = "jupyter server extension"
    version = __version__
    description = "Work with Jupyter server extensions"
    examples = _examples

    subcommands = dict(
        enable=(EnableServerExtensionApp, "Enable a server extension"),
        disable=(DisableServerExtensionApp, "Disable a server extension"),
        list=(ListServerExtensionsApp, "List server extensions")
    )

    def start(self):
        """Perform the App's actions as configured"""
        super(ServerExtensionApp, self).start()

        # The above should have called a subcommand and raised NoStart; if we
        # get here, it didn't, so we should self.log.info a message.
        subcmds = ", ".join(sorted(self.subcommands))
        sys.exit("Please supply at least one subcommand: %s" % subcmds)


main = ServerExtensionApp.launch_instance


if __name__ == '__main__':
    main()
