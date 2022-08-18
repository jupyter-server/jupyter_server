import pwd
from getpass import getuser

from pamela import PAMError, authenticate

from jupyter_server.auth.identity import IdentityProvider, User


class SystemPasswordIdentityProvider(IdentityProvider):
    # no need to generate a default token (token can still be used, but it's opt-in)
    need_token = False

    def process_login_form(self, handler):
        username = getuser()
        password = handler.get_argument("password", "")
        try:
            authenticate(username, password)
        except PAMError as e:
            self.log.error(f"Failed login for {username}: {e}")
            return None

        user_info = pwd.getpwnam(username)
        # get human name from pwd, if not empty
        return User(username=username, name=user_info.pw_gecos or username)


c = get_config()  # type: ignore # noqa

c.ServerApp.identity_provider_class = SystemPasswordIdentityProvider
