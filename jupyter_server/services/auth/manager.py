"""An AuthorizationManager for use in the Jupyter server.

The default manager is a No-op manager, NOPAuthorizationManager
"""
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
from traitlets.config import LoggingConfigurable


class AuthorizationManager(LoggingConfigurable):
    """Base class for managing authorization to resources
    in the Jupyter Server.

    All authorization managers used in Jupyter Server
    should inherit from this base class and, at the very minimum,
    override and implement an `is_authorized` method with the
    same signature as in this base class.

    The `is_authorized` method is called by the `@authorized` decorator
    in JupyterHandler. If it returns True, the incoming request
    to the server is accepted; if it returns False, the server
    returns a 401 (Not Authorized) error code.
    """

    def is_authorized(self, handler, subject, action, resource):
        """A method to determine if `subject` is authorized to perform `action`
        (read, write, or execute) on the `resource` type.

        Parameters
        ------------
        subject : usually a dict
            a subject model with group, role, or permissions information.

        action : str
            the category of action for the current request: read, write, or execute.

        resource : str
            the type of resource (i.e. contents, kernels, files, etc.) the subject is requesting.

        Returns True if subject authorized to make request; otherwise, returns False.
        """
        raise NotImplementedError


class NOPAuthorizationManager(AuthorizationManager):
    """A no-op implementation of the Authorization Manager."""

    def is_authorized(self, handler, subject, action, resource):
        """This method always returns True. Subject is allowed to
        to do anything in the Jupyter Server.
        """
        return True
