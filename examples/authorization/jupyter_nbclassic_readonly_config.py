from jupyter_server.auth import Authorizer


class ReadOnly(Authorizer):
    """Authorizer that makes Jupyter Server a read-only server."""

    def is_authorized(self, handler, user, action, resource):
        """Only allows `read` operations."""
        if action != "read":
            return False
        return True


c.ServerApp.authorizer_class = ReadOnly  # type:ignore[name-defined]
