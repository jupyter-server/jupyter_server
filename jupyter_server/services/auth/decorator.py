"""Decorator for layering authorization into JupyterHandlers.
"""
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
from typing import Callable
from typing import Optional

from tornado.log import app_log
from tornado.web import HTTPError


def authorized(
    action: str, resource: Optional[str] = None, message: Optional[str] = None
) -> Callable:
    """A decorator for tornado.web.RequestHandler methods
    that verifies whether the current user is authorized
    to make the following request.

    Helpful for adding an 'authorization' layer to
    a REST API.

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
    # Get message
    if message is None:
        message = f"User is not authorized to {action} on {resource}."

    def wrapper(method):
        def inner(self, *args, **kwargs):
            user = self.current_user
            if not user:
                app_log.warning("Attempting to authorize request without authentication!")
                return False
            # If the user is allowed to do this action,
            # call the method.
            if self.authorizer.is_authorized(self, user, action, resource):
                return method(self, *args, **kwargs)
            # else raise an exception.
            else:
                raise HTTPError(status_code=403, log_message=message)

        return inner

    return wrapper
