"""Tornado handlers for logging into the Jupyter Server."""

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

try:
    from urllib.parse import urlparse # Py 3
except ImportError:
    from urlparse import urlparse # Py 2
import uuid

from tornado.escape import url_escape

from ..auth.security import passwd_check

from ..base.handlers import JupyterHandler


class LoginHandler(JupyterHandler):
    """The basic tornado login handler

    authenticates with a hashed password from the configuration.
    """
    def _render(self, message=None):
        self.write(self.render_template('login.html',
                next=url_escape(self.get_argument('next', default=self.base_url)),
                message=message,
        ))

    def _redirect_safe(self, url, default=None):
        """Redirect if url is on our PATH

        Full-domain redirects are allowed if they pass our CORS origin checks.

        Otherwise use default (self.base_url if unspecified).
        """
        if default is None:
            default = self.base_url
        if not url.startswith(self.base_url):
            # require that next_url be absolute path within our path
            allow = False
            # OR pass our cross-origin check
            if '://' in url:
                # if full URL, run our cross-origin check:
                parsed = urlparse(url.lower())
                origin = '%s://%s' % (parsed.scheme, parsed.netloc)
                if self.allow_origin:
                    allow = self.allow_origin == origin
                elif self.allow_origin_pat:
                    allow = bool(self.allow_origin_pat.match(origin))
            if not allow:
                # not allowed, use default
                self.log.warn("Not allowing login redirect to %r" % url)
                url = default
        self.redirect(url)

    def get(self):
        if self.current_user:
            next_url = self.get_argument('next', default=self.base_url)
            self._redirect_safe(next_url)
        else:
            self._render()

    @property
    def hashed_password(self):
        return self.password_from_settings(self.settings)

    def post(self):
        typed_password = self.get_argument('password', default=u'')
        cookie_options = self.settings.get('cookie_options', {})
        cookie_options.setdefault('httponly', True)
        if self.login_available(self.settings):
            if passwd_check(self.hashed_password, typed_password):
                # tornado <4.2 has a bug that considers secure==True as soon as
                # 'secure' kwarg is passed to set_secure_cookie
                if self.settings.get('secure_cookie', self.request.protocol == 'https'):
                    cookie_options.setdefault('secure', True)
                self.set_secure_cookie(self.cookie_name, str(uuid.uuid4()), **cookie_options)
            else:
                self.set_status(401)
                self._render(message={'error': 'Invalid password'})
                return

        next_url = self.get_argument('next', default=self.base_url)
        self._redirect_safe(next_url)

    @classmethod
    def get_user(cls, handler):
        """Called by handlers.get_current_user for identifying the current user.

        See tornado.web.RequestHandler.get_current_user for details.
        """
        # Can't call this get_current_user because it will collide when
        # called on LoginHandler itself.

        user_id = handler.get_secure_cookie(handler.cookie_name)
        # For now the user_id should not return empty, but it could, eventually.
        if user_id == '':
            user_id = 'anonymous'
        if user_id is None:
            # prevent extra Invalid cookie sig warnings:
            handler.clear_login_cookie()
            if not handler.login_available:
                user_id = 'anonymous'
        return user_id


    @classmethod
    def validate_security(cls, app, ssl_options=None):
        """Check the application's security.

        Show messages, or abort if necessary, based on the security configuration.
        """
        if not app.ip:
            warning = "WARNING: The Jupyter Server is listening on all IP addresses"
            if ssl_options is None:
                app.log.warning(warning + " and not using encryption. This "
                    "is not recommended.")
            if not app.password:
                app.log.warning(warning + " and not using authentication. "
                    "This is highly insecure and not recommended.")

    @classmethod
    def password_from_settings(cls, settings):
        """Return the hashed password from the tornado settings.

        If there is no configured password, an empty string will be returned.
        """
        return settings.get('password', u'')

    @classmethod
    def login_available(cls, settings):
        """Whether this LoginHandler is needed - and therefore whether the login page should be displayed."""
        return bool(cls.password_from_settings(settings))
