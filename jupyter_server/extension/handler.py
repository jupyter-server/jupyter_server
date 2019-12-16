from jupyter_server.base.handlers import JupyterHandler, FileFindHandler
from traitlets import Unicode, default


class ExtensionHandlerJinjaMixin:
    """Mixin class for ExtensionApp handlers that use jinja templating for 
    template rendering.
    """
    def get_template(self, name):
        """Return the jinja template object for a given name"""
        env = '{}_jinja2_env'.format(self.extension_name)
        return self.settings[env].get_template(name)


class ExtensionHandler(JupyterHandler):
    """Base class for Jupyter server extension handlers. 

    Subclasses can serve static files behind a namespaced 
    endpoint: "/static/<extension_name>/" 

    This allows multiple extensions to serve static files under
    their own namespace and avoid intercepting requests for 
    other extensions. 
    """
    def initialize(self, extension_name):
        self.extension_name = extension_name

    @property
    def config(self):
        return self.settings["{}_config".format(self.extension_name)]

    @property
    def server_config(self):
        return self.settings["config"]

    @property
    def static_url_prefix(self):
        return "/static/{extension_name}/".format(
            extension_name=self.extension_name)

    @property
    def static_path(self):
        return self.settings['{}_static_paths'.format(self.extension_name)]

    def static_url(self, path, include_host=None, **kwargs):
        """Returns a static URL for the given relative static file path.
        This method requires you set the ``{extension_name}_static_path`` 
        setting in your extension (which specifies the root directory 
        of your static files).
        This method returns a versioned url (by default appending
        ``?v=<signature>``), which allows the static files to be
        cached indefinitely.  This can be disabled by passing
        ``include_version=False`` (in the default implementation;
        other static file implementations are not required to support
        this, but they may support other options).
        By default this method returns URLs relative to the current
        host, but if ``include_host`` is true the URL returned will be
        absolute.  If this handler has an ``include_host`` attribute,
        that value will be used as the default for all `static_url`
        calls that do not pass ``include_host`` as a keyword argument.
        """
        key = "{}_static_paths".format(self.extension_name)
        try:
            self.require_setting(key, "static_url")
        except Exception as e:
            if key in self.settings:
                raise Exception(
                    "This extension doesn't have any static paths listed. Check that the "
                    "extension's `static_paths` trait is set."
                )
            else:
                raise e

        get_url = self.settings.get(
            "static_handler_class", FileFindHandler
        ).make_static_url

        if include_host is None:
            include_host = getattr(self, "include_host", False)

        if include_host:
            base = self.request.protocol + "://" + self.request.host
        else:
            base = ""

        # Hijack settings dict to send extension templates to extension
        # static directory.
        settings = {
            "static_path": self.static_path,
            "static_url_prefix": self.static_url_prefix
        }

        return base + get_url(settings, path, **kwargs)
