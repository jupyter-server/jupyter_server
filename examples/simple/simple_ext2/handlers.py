"""API handlers for the Jupyter Server example."""
from jupyter_server.base.handlers import JupyterHandler
from jupyter_server.extension.handler import ExtensionHandlerJinjaMixin, ExtensionHandlerMixin
from jupyter_server.utils import url_escape


class ParameterHandler(ExtensionHandlerMixin, JupyterHandler):
    """A parameterized handler."""

    def get(self, matched_part=None, *args, **kwargs):
        """Get a parameterized response."""
        var1 = self.get_argument("var1", default=None)
        components = [x for x in self.request.path.split("/") if x]
        self.write("<h1>Hello Simple App 2 from Handler.</h1>")
        self.write(f"<p>matched_part: {url_escape(matched_part)}</p>")
        self.write(f"<p>var1: {url_escape(var1)}</p>")
        self.write(f"<p>components: {components}</p>")


class BaseTemplateHandler(ExtensionHandlerJinjaMixin, ExtensionHandlerMixin, JupyterHandler):
    """A base template handler."""

    pass


class IndexHandler(BaseTemplateHandler):
    """The root API handler."""

    def get(self):
        """Get the root response."""
        self.write(self.render_template("index.html"))


class TemplateHandler(BaseTemplateHandler):
    """A template handler."""

    def get(self, path):
        """Get the template for the path."""
        self.write(self.render_template("simple_ext2.html", path=path))


class ErrorHandler(BaseTemplateHandler):
    """An error handler."""

    def get(self, path):
        """Handle the error."""
        self.write_error(400)
