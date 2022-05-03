from jupyter_server.auth import Authorizer


class TemporaryServerPersonality(Authorizer):
    """Authorizer that prevents modifying files via the contents service"""

    def is_authorized(self, handler, user, action, resource):
        """Allow everything but write on contents"""
        if action == "write" and resource == "contents":
            return False
        return True


c.ServerApp.authorizer_class = TemporaryServerPersonality  # type:ignore[name-defined]
