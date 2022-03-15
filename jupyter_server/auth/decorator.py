"""Decorator for layering authorization into JupyterHandlers.
"""
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
import warnings
from functools import wraps
from typing import Callable
from typing import Optional
from typing import Union

from tornado.log import app_log
from tornado.web import HTTPError

from .utils import HTTP_METHOD_TO_AUTH_ACTION


def authorized(
    action: Optional[Union[str, Callable]] = None,
    resource: Optional[str] = None,
    message: Optional[str] = None,
) -> Callable:
    """A decorator for tornado.web.RequestHandler methods
    that verifies whether the current user is authorized
    to make the following request.

    Helpful for adding an 'authorization' layer to
    a REST API.

    .. versionadded:: 2.0

    Parameters
    ----------
    action : str
        the type of permission or action to check.

    resource: str or None
        the name of the resource the action is being authorized
        to access.

    message : str or none
        a message for the unauthorized action.
    """

    def wrapper(method):
        @wraps(method)
        def inner(self, *args, **kwargs):
            # default values for action, resource
            nonlocal action
            nonlocal resource
            nonlocal message
            if action is None:
                http_method = self.request.method.upper()
                action = HTTP_METHOD_TO_AUTH_ACTION[http_method]
            if resource is None:
                resource = self.auth_resource
            if message is None:
                message = f"User is not authorized to {action} on resource: {resource}."

            user = self.current_user
            if not user:
                app_log.warning("Attempting to authorize request without authentication!")
                raise HTTPError(status_code=403, log_message=message)

            # Handle the case where an authorizer wasn't attached to the handler.
            if not self.authorizer:
                warnings.warn(
                    "The Tornado web application does not have an 'authorizer' defined "
                    "in its settings. In future releases of jupyter_server, this will "
                    "be a required key for all subclasses of `JupyterHandler`. For an "
                    "example, see the jupyter_server source code for how to "
                    "add an authorizer to the tornado settings: "
                    "https://github.com/jupyter-server/jupyter_server/blob/"
                    "653740cbad7ce0c8a8752ce83e4d3c2c754b13cb/jupyter_server/serverapp.py"
                    "#L234-L256",
                    FutureWarning,
                )
                return method(self, *args, **kwargs)

            # Only return the method if the action is authorized.
            if self.authorizer.is_authorized(self, user, action, resource):
                return method(self, *args, **kwargs)

            # Raise an exception if the method wasn't returned (i.e. not authorized)
            raise HTTPError(status_code=403, log_message=message)

        return inner

    if callable(action):
        method = action
        action = None
        # no-arguments `@authorized` decorator called
        return wrapper(method)

    return wrapper
