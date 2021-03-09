import importlib

from traitlets.config import LoggingConfigurable, Config

from traitlets import (
    HasTraits,
    Dict,
    Unicode,
    Bool,
    Any,
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
    """
    _linked = Bool(False)
    _app = Any(None, allow_none=True)

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
        except ImportError:
            raise ExtensionModuleNotFound(
                "The submodule '{}' could not be found. Are you "
                "sure the extension is installed?".format(self._module_name)
            )
        # If the metadata includes an ExtensionApp, create an instance.
        if 'app' in metadata:
            self._app = metadata["app"]()
        return metadata

    @property
    def linked(self):
        """Has this extension point been linked to the server.

        Will pull from ExtensionApp's trait, if this point
        is an instance of ExtensionApp.
        """
        if self.app:
            return self.app._linked
        return self._linked

    @property
    def app(self):
        """If the metadata includes an `app` field"""
        return self._app

    @property
    def config(self):
        """Return any configuration provided by this extension point."""
        if self.app:
            return self.app._jupyter_server_config()
        # At some point, we might want to add logic to load config from
        # disk when extensions don't use ExtensionApp.
        else:
            return {}

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

    def _get_linker(self):
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
        return linker

    def _get_loader(self):
        loc = self.app
        if not loc:
            loc = self.module
        loader = get_loader(loc)
        return loader

    def validate(self):
        """Check that both a linker and loader exists."""
        try:
            self._get_linker()
            self._get_loader()
        except Exception:
            return False

    def link(self, serverapp):
        """Link the extension to a Jupyter ServerApp object.

        This looks for a `_link_jupyter_server_extension` function
        in the extension's module or ExtensionApp class.
        """
        if not self.linked:
            linker = self._get_linker()
            linker(serverapp)
            # Store this extension as already linked.
            self._linked = True

    def load(self, serverapp):
        """Load the extension in a Jupyter ServerApp object.

        This looks for a `_load_jupyter_server_extension` function
        in the extension's module or ExtensionApp class.
        """
        loader = self._get_loader()
        return loader(serverapp)


class ExtensionPackage(HasTraits):
    """An API for interfacing with a Jupyter Server extension package.

    Usage:

    ext_name = "my_extensions"
    extpkg = ExtensionPackage(name=ext_name)
    """
    name = Unicode(help="Name of the an importable Python package.")
    enabled = Bool(False).tag(config=True)

    def __init__(self, *args, **kwargs):
        # Store extension points that have been linked.
        self._linked_points = {}
        super().__init__(*args, **kwargs)

    _linked_points = {}

    @validate("name")
    def _validate_name(self, proposed):
        name = proposed['value']
        self._extension_points = {}
        try:
            self._module, self._metadata = get_metadata(name)
        except ImportError:
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
    def module(self):
        """Extension metadata loaded from the extension package."""
        return self._module

    @property
    def version(self):
        """Get the version of this package, if it's given. Otherwise, return an empty string"""
        return getattr(self._module, "__version__", "")

    @property
    def metadata(self):
        """Extension metadata loaded from the extension package."""
        return self._metadata

    @property
    def extension_points(self):
        """A dictionary of extension points."""
        return self._extension_points

    def validate(self):
        """Validate all extension points in this package."""
        for extension in self.extension_points.values():
            if not extension.validate():
                return False
        return True

    def link_point(self, point_name, serverapp):
        linked = self._linked_points.get(point_name, False)
        if not linked:
            point = self.extension_points[point_name]
            point.link(serverapp)

    def load_point(self, point_name, serverapp):
        point = self.extension_points[point_name]
        point.load(serverapp)

    def link_all_points(self, serverapp):
        for point_name in self.extension_points:
            self.link_point(point_name, serverapp)

    def load_all_points(self, serverapp):
        for point_name in self.extension_points:
            self.load_point(point_name, serverapp)


class ExtensionManager(LoggingConfigurable):
    """High level interface for findind, validating,
    linking, loading, and managing Jupyter Server extensions.

    Usage:
    m = ExtensionManager(jpserver_extensions=extensions)
    """
    def __init__(self, config_manager=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # The `enabled_extensions` attribute provides a dictionary
        # with extension (package) names mapped to their ExtensionPackage interface
        # (see above). This manager simplifies the interaction between the
        # ServerApp and the extensions being appended.
        self._extensions = {}
        # The `_linked_extensions` attribute tracks when each extension
        # has been successfully linked to a ServerApp. This helps prevent
        # extensions from being re-linked recursively unintentionally if another
        # extension attempts to link extensions again.
        self._linked_extensions = {}
        self._config_manager = config_manager
        if self._config_manager:
            self.from_config_manager(self._config_manager)

    @property
    def config_manager(self):
        return self._config_manager

    @property
    def extensions(self):
        """Dictionary with extension package names as keys
        and an ExtensionPackage objects as values.
        """
        # Sort enabled extensions before
        return self._extensions

    @property
    def extension_points(self):
        extensions = self.extensions
        return {
            name: point
            for value in extensions.values()
            for name, point in value.extension_points.items()
        }

    @property
    def linked_extensions(self):
        """Dictionary with extension names as keys; values are
        True if the extension is linked, False if not."""
        return self._linked_extensions

    def from_config_manager(self, config_manager):
        """Add extensions found by an ExtensionConfigManager"""
        self._config_manager = config_manager
        jpserver_extensions = self._config_manager.get_jpserver_extensions()
        self.from_jpserver_extensions(jpserver_extensions)

    def from_jpserver_extensions(self, jpserver_extensions):
        """Add extensions from 'jpserver_extensions'-like dictionary."""
        for name, enabled in jpserver_extensions.items():
            self.add_extension(name, enabled=enabled)

    def add_extension(self, extension_name, enabled=False):
        """Try to add extension to manager, return True if successful.
        Otherwise, return False.
        """
        try:
            extpkg = ExtensionPackage(name=extension_name, enabled=enabled)
            self._extensions[extension_name] = extpkg
            return True
        # Raise a warning if the extension cannot be loaded.
        except Exception as e:
            self.log.warning(e)
        return False

    def link_extension(self, name, serverapp):
        linked = self._linked_extensions.get(name, False)
        extension = self.extensions[name]
        if not linked and extension.enabled:
            try:
                # Link extension and store links
                extension.link_all_points(serverapp)
                self._linked_extensions[name] = True
                self.log.info("{name} | extension was successfully linked.".format(name=name))
            except Exception as e:
                self.log.warning(e)

    def load_extension(self, name, serverapp):
        extension = self.extensions.get(name)
        if extension.enabled:
            try:
                extension.load_all_points(serverapp)
                self.log.info("{name} | extension was successfully loaded.".format(name=name))
            except Exception as e:
                self.log.warning("{name} | extension failed loading with message: {error}".format(name=name,error=str(e)))

    def link_all_extensions(self, serverapp):
        """Link all enabled extensions
        to an instance of ServerApp
        """
        # Sort the extension names to enforce deterministic linking
        # order.
        for name in sorted(self.extensions.keys()):
            self.link_extension(name, serverapp)

    def load_all_extensions(self, serverapp):
        """Load all enabled extensions and append them to
        the parent ServerApp.
        """
        # Sort the extension names to enforce deterministic loading
        # order.
        for name in sorted(self.extensions.keys()):
            self.load_extension(name, serverapp)
