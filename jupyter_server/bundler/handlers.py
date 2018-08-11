"""Tornado handler for bundling content."""

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
from . import tools
from ..utils import force_async, import_item
from jupyter_server.utils import url2path
from jupyter_server.base.handlers import JupyterHandler
from jupyter_server.services.config import ConfigManager
from tornado import web


class BundlerHandler(JupyterHandler):

    def initialize(self):
        """Make tools module available on the handler instance for compatibility
        with existing bundler API and ease of reference."""
        self.tools = tools

    def get_bundler(self, bundler_id):
        """
        Get bundler metadata from config given a bundler ID.

        Parameters
        ----------
        bundler_id: str
            Unique bundler ID within the jupyter_server/bundlerextensions config section

        Returns
        -------
        dict
            Bundler metadata with label, group, and module_name attributes

        Raises
        ------
        KeyError
            If the bundler ID is unknown
        """
        cm = ConfigManager()
        return cm.get('jupyter_server').get('bundlerextensions', {})[bundler_id]

    @web.authenticated
    async def get(self, path):
        """Bundle the given notebook.

        Parameters
        ----------
        path: str
            Path to the notebook (path parameter)
        bundler: str
            Bundler ID to use (query parameter)
        """
        bundler_id = self.get_query_argument('bundler')
        model = self.contents_manager.get(path=url2path(path))

        try:
            bundler = self.get_bundler(bundler_id)
        except KeyError:
            raise web.HTTPError(400, 'Bundler %s not enabled' % bundler_id)

        module_name = bundler['module_name']
        try:
            # no-op in python3, decode error in python2
            module_name = str(module_name)
        except UnicodeEncodeError:
            # Encode unicode as utf-8 in python2 else import_item fails
            module_name = module_name.encode('utf-8')

        try:
            bundler_mod = import_item(module_name)
        except ImportError:
            raise web.HTTPError(500, 'Could not import bundler %s ' % bundler_id)

        # Let the bundler respond in any way it sees fit and assume it will
        # finish the request
        await force_async(bundler_mod.bundle(self, model))


_bundler_id_regex = r'(?P<bundler_id>[A-Za-z0-9_]+)'

default_handlers = [
    (r"/bundle/(.*)", BundlerHandler)
]
