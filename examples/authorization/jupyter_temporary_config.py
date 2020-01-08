from jupyter_server.base.handlers import JupyterHandler

def user_is_authorized(self, user, action, resource=None):
    """Only allows `read` operations."""
    if action == 'write' and resource == 'contents':
        return False
    return True

JupyterHandler.user_is_authorized = user_is_authorized