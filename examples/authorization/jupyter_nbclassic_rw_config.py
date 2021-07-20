from jupyter_server.services.auth.manager import AuthorizationManager


class ReadWriteOnly(AuthorizationManager):
    """Manager class that makes Jupyter Server a read-only server."""

    def is_authorized(self, handler, subject, action, resource):
        """Only allows `read` operations."""
        if action == "execute":
            return False
        return True


c.ServerApp.authorization_manager_class = ReadWriteOnly
