from jupyter_server.extension.handler import ExtensionHandler

class ServerSimpleTemplateHandler(ExtensionHandler):
    
    def get_template(self, name):
        """Return the jinja template object for a given name"""
        return self.settings['server_simple_jinja2_env'].get_template(name)

    def get(self):
#        print(self.get_template('server_simple.html'))
        self.write(self.render_template('server_simple.html'))
