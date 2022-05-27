from jupyter_server.auth import Authorizer


class ReadWriteOnly(Authorizer):
    """Authorizer class that makes Jupyter Server a read/write-only server."""

    def is_authorized(self, handler, user, action, resource):
        """Only allows `read` and `write` operations."""
        if action not in {"read", "write"}:
            return False
        return True


c.ServerApp.authorizer_class = ReadWriteOnly  # type:ignore[name-defined]
