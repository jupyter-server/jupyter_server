# coding: utf-8
"""Utilities for installing extensions"""
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
import os
import sys

from jupyter_core.application import JupyterApp
from jupyter_core.paths import ENV_CONFIG_PATH
from jupyter_core.paths import jupyter_config_dir
from jupyter_core.paths import SYSTEM_CONFIG_PATH
from tornado.log import LogFormatter
from traitlets import Bool

from jupyter_server._version import __version__
from jupyter_server.extension.config import ExtensionConfigManager
from jupyter_server.extension.manager import ExtensionManager
from jupyter_server.extension.manager import ExtensionPackage


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
    if user and sys_prefix:
        sys_prefix = False
    if user:
        extdir = jupyter_config_dir()
    elif sys_prefix:
        extdir = ENV_CONFIG_PATH[0]
    else:
        extdir = SYSTEM_CONFIG_PATH[0]
    return extdir


def _get_extmanager_for_context(write_dir="jupyter_server_config.d", user=False, sys_prefix=False):
    """Get an extension manager pointing at the current context

    Returns the path to the current context and an ExtensionManager object.

    Parameters
    ----------
    write_dir : str [default: 'jupyter_server_config.d']
        Name of config directory to write extension config.
    user : bool [default: False]
        Get the user's .jupyter config directory
    sys_prefix : bool [default: False]
        Get sys.prefix, i.e. ~/.envs/my-env/etc/jupyter
    """
    config_dir = _get_config_dir(user=user, sys_prefix=sys_prefix)
    config_manager = ExtensionConfigManager(
        read_config_path=[config_dir],
        write_config_dir=os.path.join(config_dir, write_dir),
    )
    extension_manager = ExtensionManager(
        config_manager=config_manager,
    )
    return config_dir, extension_manager


class ArgumentConflict(ValueError):
    pass


_base_flags = {}
_base_flags.update(JupyterApp.flags)
_base_flags.pop("y", None)
_base_flags.pop("generate-config", None)
_base_flags.update(
    {
        "user": (
            {
                "BaseExtensionApp": {
                    "user": True,
                }
            },
            "Apply the operation only for the given user",
        ),
        "system": (
            {
                "BaseExtensionApp": {
                    "user": False,
                    "sys_prefix": False,
                }
            },
            "Apply the operation system-wide",
        ),
        "sys-prefix": (
            {
                "BaseExtensionApp": {
                    "sys_prefix": True,
                }
            },
            "Use sys.prefix as the prefix for installing extensions (for environments, packaging)",
        ),
        "py": (
            {
                "BaseExtensionApp": {
                    "python": True,
                }
            },
            "Install from a Python package",
        ),
    }
)
_base_flags["python"] = _base_flags["py"]

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

    @property
    def config_dir(self):
        return _get_config_dir(user=self.user, sys_prefix=self.sys_prefix)


# Constants for pretty print extension listing function.
# Window doesn't support coloring in the commandline
GREEN_ENABLED = "\033[32menabled\033[0m" if os.name != "nt" else "enabled"
RED_DISABLED = "\033[31mdisabled\033[0m" if os.name != "nt" else "disabled"
GREEN_OK = "\033[32mOK\033[0m" if os.name != "nt" else "ok"
RED_X = "\033[31m X\033[0m" if os.name != "nt" else " X"

# ------------------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------------------


def toggle_server_extension_python(
    import_name, enabled=None, parent=None, user=False, sys_prefix=True
):
    """Toggle the boolean setting for a given server extension
    in a Jupyter config file.
    """
    sys_prefix = False if user else sys_prefix
    config_dir = _get_config_dir(user=user, sys_prefix=sys_prefix)
    manager = ExtensionConfigManager(
        read_config_path=[config_dir],
        write_config_dir=os.path.join(config_dir, "jupyter_server_config.d"),
    )
    if enabled:
        manager.enable(import_name)
    else:
        manager.disable(import_name)


# ----------------------------------------------------------------------
# Applications
# ----------------------------------------------------------------------

flags = {}
flags.update(BaseExtensionApp.flags)
flags.pop("y", None)
flags.pop("generate-config", None)
flags.update(
    {
        "user": (
            {
                "ToggleServerExtensionApp": {
                    "user": True,
                }
            },
            "Perform the operation for the current user",
        ),
        "system": (
            {
                "ToggleServerExtensionApp": {
                    "user": False,
                    "sys_prefix": False,
                }
            },
            "Perform the operation system-wide",
        ),
        "sys-prefix": (
            {
                "ToggleServerExtensionApp": {
                    "sys_prefix": True,
                }
            },
            "Use sys.prefix as the prefix for installing server extensions",
        ),
        "py": (
            {
                "ToggleServerExtensionApp": {
                    "python": True,
                }
            },
            "Install from a Python package",
        ),
    }
)
flags["python"] = flags["py"]


class ToggleServerExtensionApp(BaseExtensionApp):
    """A base class for enabling/disabling extensions"""

    name = "jupyter server extension enable/disable"
    description = "Enable/disable a server extension using frontend configuration files."

    flags = flags

    _toggle_value = Bool()
    _toggle_pre_message = ""
    _toggle_post_message = ""

    def toggle_server_extension(self, import_name):
        """Change the status of a named server extension.

        Uses the value of `self._toggle_value`.

        Parameters
        ---------

        import_name : str
            Importable Python module (dotted-notation) exposing the magic-named
            `load_jupyter_server_extension` function
        """
        # Create an extension manager for this instance.
        config_dir, extension_manager = _get_extmanager_for_context(
            user=self.user, sys_prefix=self.sys_prefix
        )
        try:
            self.log.info("{}: {}".format(self._toggle_pre_message.capitalize(), import_name))
            self.log.info("- Writing config: {}".format(config_dir))
            # Validate the server extension.
            self.log.info("    - Validating {}...".format(import_name))
            # Interface with the Extension Package and validate.
            extpkg = ExtensionPackage(name=import_name)
            extpkg.validate()
            version = extpkg.version
            self.log.info("      {} {} {}".format(import_name, version, GREEN_OK))

            # Toggle extension config.
            config = extension_manager.config_manager
            if self._toggle_value is True:
                config.enable(import_name)
            else:
                config.disable(import_name)

            # If successful, let's log.
            self.log.info("    - Extension successfully {}.".format(self._toggle_post_message))
        except Exception as err:
            self.log.info("     {} Validation failed: {}".format(RED_X, err))

    def start(self):
        """Perform the App's actions as configured"""
        if not self.extra_args:
            sys.exit("Please specify a server extension/package to enable or disable")
        for arg in self.extra_args:
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
        configurations = (
            {"user": True, "sys_prefix": False},
            {"user": False, "sys_prefix": True},
            {"user": False, "sys_prefix": False},
        )

        for option in configurations:
            config_dir, ext_manager = _get_extmanager_for_context(**option)
            self.log.info("Config dir: {}".format(config_dir))
            for name, extension in ext_manager.extensions.items():
                enabled = extension.enabled
                # Attempt to get extension metadata
                self.log.info(u"    {} {}".format(name, GREEN_ENABLED if enabled else RED_DISABLED))
                try:
                    self.log.info("    - Validating {}...".format(name))
                    if not extension.validate():
                        raise ValueError("validation failed")
                    version = extension.version
                    self.log.info("      {} {} {}".format(name, version, GREEN_OK))
                except Exception as err:
                    self.log.warn("      {} {}".format(RED_X, err))
            # Add a blank line between paths.
            self.log.info("")

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
        list=(ListServerExtensionsApp, "List server extensions"),
    )

    def start(self):
        """Perform the App's actions as configured"""
        super(ServerExtensionApp, self).start()

        # The above should have called a subcommand and raised NoStart; if we
        # get here, it didn't, so we should self.log.info a message.
        subcmds = ", ".join(sorted(self.subcommands))
        sys.exit("Please supply at least one subcommand: %s" % subcmds)


main = ServerExtensionApp.launch_instance


if __name__ == "__main__":
    main()
