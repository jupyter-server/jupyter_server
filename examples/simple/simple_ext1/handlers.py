from jupyter_server.auth import authorized
from jupyter_server.base.handlers import JupyterHandler
from jupyter_server.extension.handler import ExtensionHandlerJinjaMixin, ExtensionHandlerMixin
from jupyter_server.utils import url_escape


class DefaultHandler(ExtensionHandlerMixin, JupyterHandler):
    auth_resource = "simple_ext1:default"

    @authorized
    def get(self):
        # The name of the extension to which this handler is linked.
        self.log.info(f"Extension Name in {self.name} Default Handler: {self.name}")
        # A method for getting the url to static files (prefixed with /static/<name>).
        self.log.info(
            "Static URL for / in simple_ext1 Default Handler: {}".format(self.static_url(path="/"))
        )
        self.write("<h1>Hello Simple 1 - I am the default...</h1>")
        self.write(f"Config in {self.name} Default Handler: {self.config}")


class RedirectHandler(ExtensionHandlerMixin, JupyterHandler):
    def get(self):
        self.redirect(f"/static/{self.name}/favicon.ico")


class ParameterHandler(ExtensionHandlerMixin, JupyterHandler):
    def get(self, matched_part=None, *args, **kwargs):
        var1 = self.get_argument("var1", default=None)
        components = [x for x in self.request.path.split("/") if x]
        self.write("<h1>Hello Simple App 1 from Handler.</h1>")
        self.write(f"<p>matched_part: {url_escape(matched_part)}</p>")
        self.write(f"<p>var1: {url_escape(var1)}</p>")
        self.write(f"<p>components: {components}</p>")


class BaseTemplateHandler(ExtensionHandlerJinjaMixin, ExtensionHandlerMixin, JupyterHandler):
    pass


class TypescriptHandler(BaseTemplateHandler):
    def get(self):
        self.write(self.render_template("typescript.html"))


class TemplateHandler(BaseTemplateHandler):
    def get(self, path):
        """Optionally, you can print(self.get_template('simple1.html'))"""
        self.write(self.render_template("simple1.html", path=path))


class ErrorHandler(BaseTemplateHandler):
    def get(self, path):
        # write_error renders template from error.html file.
        self.write_error(400)
