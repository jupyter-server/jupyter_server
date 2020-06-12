import pathlib
import importlib

from jupyter_core.paths import jupyter_config_path
from traitlets.config.loader import (
    JSONFileConfigLoader,
    PyFileConfigLoader,
    Config
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


class ExtensionPath:

    def __init__(self, metadata):
        self.module_name = metadata.get("module")
        self.module = importlib.import_module(self.module_name)
        self.app = metadata.get("app", None)
        if self.app:
            self.app = self.app()
            self.name = self.app.name
            self.link = self.app._link_jupyter_server_extension
            self.loader = get_loader(self.app)
        else:
            self.name = metadata.get("name", self.module_name)
            self.link = getattr(
                self.module,
                '_link_jupyter_server_extension',
                lambda serverapp: None
            )
            self.loader = get_loader(self.module)

    def load(self, serverapp):
        return self.loader(serverapp)


def get_metadata(package_name):
    """Find the extension metadata from an extension package.

    If it doesn't exist, return a basic metadata package given
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


class Extension:

    def __init__(self, package_name):
        self.package_name = package_name
        self.metadata = get_metadata(self.package_name)
        self.paths = {}
        for path_metadata in self.metadata:
            path = ExtensionPath(path_metadata)
            self.paths[path.name] = path


class ExtensionManager:
    """
    """
    def __init__(self, jpserver_extensions):
        self.extensions = {}
        for package_name, enabled in jpserver_extensions.items():
            if enabled:
                self.extensions[package_name] = Extension(package_name)

    @property
    def paths(self):
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
    # 1) Try importing
    mod = importlib.import_module(name)
    # 2) Try calling extension paths function.
    paths = mod._jupyter_server_extension_paths()
    for path in paths:
        submod_path = path.get("module")
        submod = importlib.import_module(submod_path)
        # Check that extension has loading function.
        get_loader(submod)