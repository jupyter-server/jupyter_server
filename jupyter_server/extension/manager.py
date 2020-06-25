import importlib

from traitlets.config import LoggingConfigurable
from traitlets import (
    HasTraits,
    Dict,
    Unicode,
    Instance,
    default,
    validate
)

from .utils import (
    ExtensionMetadataError,
    ExtensionModuleNotFound,
    get_loader,
    get_metadata,
)


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
    def _valid_metadata(self, proposed):
        metadata = proposed['value']
        # Verify that the metadata has a "name" key.
        try:
            self._module_name = metadata['module']
        except KeyError:
            raise ExtensionMetadataError(
                "There is no 'module' key in the extension's "
                "metadata packet."
            )

        try:
            self._module = importlib.import_module(self._module_name)
        except ModuleNotFoundError:
            raise ExtensionModuleNotFound(
                "The module '{}' could not be found. Are you "
                "sure the extension is installed?".format(self._module_name)
            )
        # Initialize the app object if it exists.
        app = self.metadata.get("app")
        if app:
            metadata["app"] = app()
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
        if self.app:
            return self.app.name
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


class ExtensionPackage(HasTraits):
    """An API for interfacing with a Jupyter Server extension package.

    Usage:

    ext_name = "my_extensions"
    extpkg = ExtensionPackage(name=ext_name)
    """
    name = Unicode(help="Name of the an importable Python package.")

    @validate("name")
    def _validate_name(self, proposed):
        name = proposed['value']
        self._extension_points = {}
        try:
            self._metadata = get_metadata(name)
        except ModuleNotFoundError:
            raise ExtensionModuleNotFound(
                "The module '{name}' could not be found. Are you "
                "sure the extension is installed?".format(name=name)
            )
        # Create extension point interfaces for each extension path.
        for m in self._metadata:
            point = ExtensionPoint(metadata=m)
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


class ExtensionManager(LoggingConfigurable):
    """High level interface for findind, validating,
    linking, loading, and managing Jupyter Server extensions.

    Usage:

    m = ExtensionManager(jpserver_extensions=extensions)
    """
    parent = Instance(
        klass="jupyter_server.serverapp.ServerApp",
        allow_none=True
    )

    jpserver_extensions = Dict(
        help=(
            "A dictionary with extension package names "
            "as keys and booleans to enable as values."
        )
    )

    @default('jpserver_extensions')
    def _default_jpserver_extensions(self):
        return self.parent.jpserver_extensions

    @validate('jpserver_extensions')
    def _validate_jpserver_extensions(self, proposed):
        jpserver_extensions = proposed['value']
        self._extensions = {}
        # Iterate over dictionary items and validate that
        # we can interface with each extension. If the extension
        # fails to interface, throw a warning through the logger
        # interface.
        for package_name, enabled in jpserver_extensions.items():
            if enabled:
                try:
                    self._extensions[package_name] = ExtensionPackage(
                        name=package_name
                    )
                # Raise a warning if the extension cannot be loaded.
                except Exception as e:
                    self.log.warning(e)
        return jpserver_extensions

    @property
    def extensions(self):
        """Dictionary with extension package names as keys
        and an ExtensionPackage objects as values.
        """
        return self._extensions

    @property
    def extension_points(self):
        points = {}
        for ext in self.extensions.values():
            points.update(ext.extension_points)
        return points

    def link_extensions(self):
        """Link all enabled extensions
         to an instance of ServerApp
        """
        # Sort the extension names to enforce deterministic linking
        # order.
        for name, ext in sorted(self.extension_points.items()):
            try:
                ext.link(self.parent)
            except Exception as e:
                self.log.warning(e)

    def load_extensions(self):
        """Load all enabled extensions and append them to
        the parent ServerApp.
        """
        # Sort the extension names to enforce deterministic loading
        # order.
        for name, ext in sorted(self.extension_points.items()):
            try:
                ext.load(self.parent)
            except Exception as e:
                self.log.warning(e)

