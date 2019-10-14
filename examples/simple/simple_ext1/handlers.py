from jupyter_server.extension.handler import ExtensionHandler

class TemplateHandler(ExtensionHandler):

    def get_template(self, name):
        """Return the jinja template object for a given name"""
        return self.settings['simple_ext1_jinja2_env'].get_template(name)

class RedirectHandler(ExtensionHandler):
    def get(self):
        self.redirect("/static/simple_ext1/favicon.ico")

class IndexHandler(TemplateHandler):
    
    def get(self):
        self.write(self.render_template("index.html"))

class ParameterHandler(ExtensionHandler):
    
    def get(self, matched_part=None, *args, **kwargs):
        var1 = self.get_argument('var1', default=None)
        components = [x for x in self.request.path.split("/") if x]
        self.write('<h1>Hello Simple App 1 from Handler.</h1>')
        self.write('<p>matched_part: {}</p>'.format(matched_part))
        self.write('<p>var1: {}</p>'.format(var1))
        self.write('<p>components: {}</p>'.format(components))

class TemplateHandler(TemplateHandler):
    
    def get(self):
        print(self.get_template('simple_ext1.html'))
        self.write(self.render_template('simple_ext1.html'))

class Page1Handler(TemplateHandler):
    
    def get(self, path):
        self.write(self.render_template('page1.html', text=path))

class ErrorHandler(TemplateHandler):
    
    def get(self, path):
        self.write(self.render_template('error.html'))
