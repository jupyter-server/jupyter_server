import pathlib
import importlib

from jupyter_core.paths import jupyter_config_path
from traitlets import (
    HasTraits,
    Dict,
    Unicode,
    validate
)
from traitlets.config.loader import (
    JSONFileConfigLoader
)


def configd_path(
    config_dir=None,
    configd_prefix="jupyter_server",
):
    # Build directory name for `config.d` directory.
    configd = "_".join([configd_prefix, "config.d"])
    if not config_dir:
        config_dir = jupyter_config_path()
    # Leverage pathlib for path management.
    return [pathlib.Path(path).joinpath(configd) for path in config_dir]


def configd_files(
    config_dir=None,
    configd_prefix="jupyter_server",
):
    """Lists (only) JSON files found in a Jupyter config.d folder.
    """
    paths = configd_path(
        config_dir=config_dir,
        configd_prefix=configd_prefix
    )
    files = []
    for path in paths:
        json_files = path.glob("*.json")
        files.extend(json_files)
    return files


def enabled(name, server_config):
    """Given a server config object, return True if the extension
    is explicitly enabled in the config.
    """
    enabled = (
        server_config
        .get("ServerApp", {})
        .get("jpserver_extensions", {})
        .get(name, False)
    )
    return enabled


def find_extension_in_configd(
    name,
    config_dir=None,
    configd_prefix="jupyter_server",
):
    """Search through all config.d files and return the
    JSON Path for this named extension. If the extension
    is not found, return None
    """
    files = configd_files(
        config_dir=config_dir,
        configd_prefix=configd_prefix,
    )
    for f in files:
        if name == f.stem:
            return f


def configd_enabled(
    name,
    config_dir=None,
    configd_prefix="jupyter_server",
):
    """Check if the named extension is enabled somewhere in
    a config.d folder.
    """
    config_file = find_extension_in_configd(
        name,
        config_dir=config_dir,
        configd_prefix=configd_prefix,
    )
    if config_file:
        c = JSONFileConfigLoader(
            filename=str(config_file.name),
            path=str(config_file.parent)
        )
        config = c.load_config()
        return enabled(name, config)
    else:
        return False


def list_extensions_in_configd(
    configd_prefix="jupyter_server",
    config_paths=None
):
    """Get a dictionary of all jpserver_extensions found in the
    config directories list.

    Parameters
    ----------
    config_paths : list
        List of config directories to search for the
        `jupyter_server_config.d` directory.
    """

    # Build directory name for `config.d` directory.
    configd = "_".join([configd_prefix, "config.d"])

    if not config_paths:
        config_paths = jupyter_config_path()

    # Leverage pathlib for path management.
    config_paths = [pathlib.Path(p) for p in config_paths]

    extensions = []
    for path in config_paths:
        json_files = path.joinpath(configd).glob("*.json")
        for file in json_files:
            # The extension name is the file name (minus file suffix)
            extension_name = file.stem
            extensions.append(extension_name)

    return extensions


class ExtensionLoadingError(Exception):
    pass


def get_loader(obj):
    """Looks for _load_jupyter_server_extension as an attribute
    of the object or module.

    Adds backwards compatibility for old function name missing the
    underscore prefix.
    """
    try:
        func = getattr(obj, '_load_jupyter_server_extension')
    except AttributeError:
        func = getattr(obj, 'load_jupyter_server_extension')
    except Exception:
        raise ExtensionLoadingError("_load_jupyter_server_extension function was not found.")
    return func


class ExtensionMetadataError(Exception):
    pass


class ExtensionModuleNotFound(Exception):
    pass


class ExtensionPoint(HasTraits):
    """A simple API for connecting to a Jupyter Server extension
    point defined by metadata and importable from a Python package.

    Usage:

    metadata = {
        "module": "extension_module",
        "":
    }

    point = ExtensionPoint(metadata)
    """
    metadata = Dict()

    @validate('metadata')
    def _valid_metadata(self, metadata):
        # Verify that the metadata has a "name" key.
        try:
            self._module_name = metadata['module']
        except KeyError:
            raise ExtensionMetadataError(
                "There is no 'name' key in the extension's "
                "metadata packet."
            )

        try:
            self._module = importlib.import_module(self._module_name)
        except ModuleNotFoundError:
            raise ExtensionModuleNotFound(
                f"The module '{self._module_name}' could not be found. Are you "
                "sure the extension is installed?"
            )
        return metadata

    @property
    def app(self):
        """If the metadata includes an `app` field"""
        return self.metadata.get("app")

    @property
    def module_name(self):
        """Name of the Python package module where the extension's
        _load_jupyter_server_extension can be found.
        """
        return self._module_name

    @property
    def name(self):
        """Name of the extension.

        If it's not provided in the metadata, `name` is set
        to the extensions' module name.
        """
        return self.metadata.get("name", self.module_name)

    @property
    def module(self):
        """The imported module (using importlib.import_module)
        """
        return self._module

    def link(self, serverapp):
        """Link the extension to a Jupyter ServerApp object.

        This looks for a `_link_jupyter_server_extension` function
        in the extension's module or ExtensionApp class.
        """
        if self.app:
            linker = self.app._link_jupyter_server_extension
        else:
            linker = getattr(
                self.module,
                # Search for a _link_jupyter_extension
                '_link_jupyter_server_extension',
                # Otherwise return a dummy function.
                lambda serverapp: None
            )
        return linker(serverapp)

    def load(self, serverapp):
        """Load the extension in a Jupyter ServerApp object.

        This looks for a `_load_jupyter_server_extension` function
        in the extension's module or ExtensionApp class.
        """
        # Use the ExtensionApp object to find a loading function
        # if it exists. Otherwise, use the extension module given.
        loc = self.app
        if not loc:
            loc = self.module
        loader = get_loader(loc)
        return loader(serverapp)


def get_metadata(package_name):
    """Find the extension metadata from an extension package.

    If it doesn't exist, return a basic metadata packet given
    the module name.
    """
    module = importlib.import_module(package_name)
    try:
        return module._jupyter_server_extension_paths()
    except AttributeError:
        return [{
            "module": package_name,
            "name": package_name
        }]


class ExtensionPackage(HasTraits):
    """API for handling
    """
    name = Unicode(help="Name of the extension's Python package.")

    @validate("name")
    def _validate_name(self, name):
        try:
            self._metadata = get_metadata(name)
        except ModuleNotFoundError:
            raise ExtensionModuleNotFound(
                f"The module '{self._module_name}' could not be found. Are you "
                "sure the extension is installed?"
            )
        # Create extension point interfaces for each extension path.
        for m in self._metadata:
            point = ExtensionPoint(m)
            self._extension_points[point.name] = point
        return name

    @property
    def metadata(self):
        """Extension metadata loaded from the extension package."""
        return self._metadata

    @property
    def extension_points(self):
        """A dictionary of extension points."""
        return self._extension_points


class ExtensionManager:
    """High level interface for linking, loading, and managing
    Jupyter Server extensions.
    """
    jpserver_extensions = Dict()

    def __init__(self, jpserver_extensions):
        self.extensions = {}
        for package_name, enabled in jpserver_extensions.items():
            if enabled:
                self.extensions[package_name] = ExtensionPackage(package_name)

    @property
    def extension_points(self):
        _paths = {}
        for ext in self.extensions.values():
            _paths.update(ext.paths)
        return _paths


def validate_extension(name):
    """Raises an exception is the extension is missing a needed
    hook or metadata field.
    An extension is valid if:
    1) name is an importable Python package.
    1) the package has a _jupyter_server_extension_paths function
    2) each extension path has a _load_jupyter_server_extension function

    If this works, nothing should happen.
    """
    ExtensionPackage(name)