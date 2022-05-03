"""Identity Provider interface

This defines the _authentication_ layer of Jupyter Server,
to be used in combination with Authorizer for _authorization_.

.. versionadded:: 2.0
"""
from dataclasses import asdict, dataclass
from typing import Any, Optional

from tornado.web import RequestHandler
from traitlets.config import LoggingConfigurable

# from dataclasses import field


@dataclass
class User:
    """Object representing a User

    This or a subclass should be returned from IdentityProvider.get_user
    """

    username: str  # the only truly required field

    # these fields are filled from username if not specified
    # name is the 'real' name of the user
    name: str = ""
    # display_name is a shorter name for us in UI,
    # if different from name. e.g. a nickname
    display_name: str = ""

    # these fields are left as None if undefined
    initials: Optional[str] = None
    avatar_url: Optional[str] = None
    color: Optional[str] = None

    # TODO: extension fields?
    # ext: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def __post_init__(self):
        self.fill_defaults()

    def fill_defaults(self):
        """Fill out default fields in the identity model

        - Ensures all values are defined
        - Fills out derivative values for name fields fields
        - Fills out null values for optional fields
        """

        # username is the only truly required field
        if not self.username:
            raise ValueError(f"user.username must not be empty: {self}")

        # derive name fields from username -> name -> display name
        if not self.name:
            self.name = self.username
        if not self.display_name:
            self.display_name = self.name

    def to_dict(self):
        pass


def _backward_compat_user(got_user: Any) -> User:
    """Backward-compatibility for LoginHandler.get_user

    Prior to 2.0, LoginHandler.get_user could return anything truthy.

    Typically, this was either a simple string username,
    or a simple dict.

    Make some effort to allow common patterns to keep working.
    """
    if isinstance(got_user, str):
        return User(username=got_user)
    elif isinstance(got_user, dict):
        kwargs = {}
        if "username" not in got_user:
            if "name" in got_user:
                kwargs["username"] = got_user["name"]
        for field in User.__dataclass_fields__:
            if field in got_user:
                kwargs[field] = got_user[field]
        try:
            return User(**kwargs)
        except TypeError:
            raise ValueError(f"Unrecognized user: {got_user}")
    else:
        raise ValueError(f"Unrecognized user: {got_user}")


class IdentityProvider(LoggingConfigurable):
    """
    Interface for providing identity

    _may_ be a coroutine.

    Two principle methods:

    - :meth:`~.IdentityProvider.get_user` returns a :class:`~.User` object
      for successful authentication, or None for no-identity-found.
    - :meth:`~.IdentityProvider.identity_model` turns a :class:`~.User` into a JSONable dict.
      The default is to use :py:meth:`dataclasses.asdict`,
      and usually shouldn't need override.

    .. versionadded:: 2.0
    """

    def get_user(self, handler: RequestHandler) -> User:
        """Get the authenticated user for a request

        Must return a :class:`.jupyter_server.auth.User`,
        though it may be a subclass.

        Return None if the request is not authenticated.
        """

        if handler.login_handler is None:
            return User("anonymous")

        # The default: call LoginHandler.get_user for backward-compatibility
        # TODO: move default implementation to this class,
        # deprecate `LoginHandler.get_user`
        user = handler.login_handler.get_user(handler)
        if user and not isinstance(user, User):
            return _backward_compat_user(user)
        return user

    def identity_model(self, user: User) -> dict:
        """Return a User as an Identity model"""
        # TODO: validate?
        return asdict(user)

    def get_handlers(self) -> list:
        """Return list of additional handlers for this identity provider

        For example, an OAuth callback handler.
        """
        return []
