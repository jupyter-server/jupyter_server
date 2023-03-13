"""Kernelspecs API Handlers."""
from jupyter_core.utils import ensure_async
from tornado import web

from jupyter_server.auth import authorized

from ..base.handlers import JupyterHandler
from ..services.kernelspecs.handlers import kernel_name_regex

AUTH_RESOURCE = "kernelspecs"


class KernelSpecResourceHandler(web.StaticFileHandler, JupyterHandler):
    """A Kernelspec resource handler."""

    SUPPORTED_METHODS = ("GET", "HEAD")  # type:ignore[assignment]
    auth_resource = AUTH_RESOURCE

    def initialize(self):
        """Initialize a kernelspec resource handler."""
        web.StaticFileHandler.initialize(self, path="")

    @web.authenticated
    @authorized
    async def get(self, kernel_name, path, include_body=True):
        """Get a kernelspec resource."""
        ksm = self.kernel_spec_manager
        if path.lower().endswith(".png"):
            self.set_header("Cache-Control", f"max-age={60*60*24*30}")
        try:
            kspec = await ensure_async(ksm.get_kernel_spec(kernel_name))
            self.root = kspec.resource_dir
        except KeyError as e:
            raise web.HTTPError(404, "Kernel spec %s not found" % kernel_name) from e
        self.log.debug("Serving kernel resource from: %s", self.root)
        return await web.StaticFileHandler.get(self, path, include_body=include_body)

    @web.authenticated
    @authorized
    async def head(self, kernel_name, path):
        """Get the head infor for a kernel resource."""
        return await ensure_async(self.get(kernel_name, path, include_body=False))


default_handlers = [
    (r"/kernelspecs/%s/(?P<path>.*)" % kernel_name_regex, KernelSpecResourceHandler),
]
