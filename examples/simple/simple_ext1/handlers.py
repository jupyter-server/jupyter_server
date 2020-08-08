from jupyter_server.base.handlers import JupyterHandler
from jupyter_server.extension.handler import ExtensionHandlerMixin, ExtensionHandlerJinjaMixin

class DefaultHandler(ExtensionHandlerMixin, JupyterHandler):
    def get(self):
        # The name of the extension to which this handler is linked.
        self.log.info("Extension Name in {} Default Handler: {}".format(self.name, self.name))
        # A method for getting the url to static files (prefixed with /static/<name>).
        self.log.info("Static URL for / in simple_ext1 Default Handler:".format(self.static_url(path='/')))
        self.write('<h1>Hello Simple 1 - I am the default...</h1>')
        self.write('Config in {} Default Handler: {}'.format(self.name, self.config))

class RedirectHandler(ExtensionHandlerMixin, JupyterHandler):
    def get(self):
        self.redirect("/static/{}/favicon.ico".format(self.name))

class ParameterHandler(ExtensionHandlerMixin, JupyterHandler):
    def get(self, matched_part=None, *args, **kwargs):
        var1 = self.get_argument('var1', default=None)
        components = [x for x in self.request.path.split("/") if x]
        self.write('<h1>Hello Simple App 1 from Handler.</h1>')
        self.write('<p>matched_part: {}</p>'.format(matched_part))
        self.write('<p>var1: {}</p>'.format(var1))
        self.write('<p>components: {}</p>'.format(components))

class BaseTemplateHandler(ExtensionHandlerJinjaMixin, ExtensionHandlerMixin, JupyterHandler): pass

class TypescriptHandler(BaseTemplateHandler):
    def get(self):
        self.write(self.render_template("typescript.html"))

class TemplateHandler(BaseTemplateHandler):
    def get(self, path):
        """ Optionaly, you can print(self.get_template('simple1.html'))"""
        self.write(self.render_template('simple1.html', path=path))

class ErrorHandler(BaseTemplateHandler):
    def get(self, path):
        self.write(self.render_template('error.html', path=path))
