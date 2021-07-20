"""Decorator for layering authorization into JupyterHandlers.
"""
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
from tornado.web import HTTPError


def authorized(action, resource=None, message=None):
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
        "User is not authorized to make this request."

    error = HTTPError(status_code=401, log_message=message)

    def wrapper(method):
        def inner(self, *args, **kwargs):
            subject = self.current_user
            # If the user is allowed to do this action,
            # call the method.
            handler = self
            if self.authorization_manager.is_authorized(handler, subject, action, resource):
                return method(self, *args, **kwargs)
            # else raise an exception.
            else:
                raise error

        return inner

    return wrapper
