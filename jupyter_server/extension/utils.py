import importlib


class ExtensionLoadingError(Exception):
    pass


class ExtensionMetadataError(Exception):
    pass


class ExtensionModuleNotFound(Exception):
    pass


class NotAnExtensionApp(Exception):
    pass


def get_extension_app_pkg(app_cls):
    """Get the Python package name
    """
    if not isinstance(app_cls, "ExtensionApp"):
        raise NotAnExtensionApp("The ")


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


def validate_extension(name):
    """Raises an exception is the extension is missing a needed
    hook or metadata field.
    An extension is valid if:
    1) name is an importable Python package.
    1) the package has a _jupyter_server_extension_paths function
    2) each extension path has a _load_jupyter_server_extension function

    If this works, nothing should happen.
    """
    from .manager import ExtensionPackage
    return ExtensionPackage(name=name)