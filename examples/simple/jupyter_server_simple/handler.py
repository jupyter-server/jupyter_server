from jupyter_server.extension.handler import ExtensionHandler

class ServerSimpleHandler(ExtensionHandler):
    
    def get(self, matched_part=None, *args, **kwargs):
        var1 = self.get_argument('var1', default=None)
        components = [x for x in self.request.path.split("/") if x]
        self.write('<h1>Hello Server Simple from Handler.</h1>')
        self.write('<p>matched_part: {}</p>'.format(matched_part))
        self.write('<p>var1: {}</p>'.format(var1))
        self.write('<p>components: {}</p>'.format(components))
