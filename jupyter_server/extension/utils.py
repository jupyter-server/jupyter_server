import pathlib
import pkgutil

from jupyter_core.paths import jupyter_config_path
from traitlets.utils.importstring import import_item
from traitlets.config.loader import (
    JSONFileConfigLoader,
    PyFileConfigLoader,
    Config
)


class JupyterServerExtensionPathsMissing(Exception):
    """"""


def list_extensions_from_configd(
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

    extensions = {}
    for path in config_paths:
        py_files = path.joinpath(configd).glob("*.py")
        json_files = path.joinpath(configd).glob("*.json")

        for f in py_files:
            pyc = PyFileConfigLoader(
                filename=str(f.name),
                path=str(f.parent)
            )
            c = pyc.load_config()
            items = c.get("ServerApp", {}).get("jpserver_extensions", {})
            extensions.update(items)

        for f in json_files:
            jsc = JSONFileConfigLoader(
                filename=str(f.name),
                path=str(f.parent)
            )
            c = jsc.load_config()
            items = c.get("ServerApp", {}).get("jpserver_extensions", {})
            extensions.update(items)

    return extensions


def _list_extensions_from_entrypoints():
    pass






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
        raise JupyterServerExtensionPathsMissing(
            'The Python module {} does not include '
            'any valid server extensions'.format(module)
        )
    return m, m._jupyter_server_extension_paths()



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