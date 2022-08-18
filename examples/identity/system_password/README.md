# Jupyter login with system password

This `jupyter_server_config.py` defines and enables a `SystemPasswordIdentityProvider`.
This IdentityProvider checks the entered password against your system password using PAM.
Only the current user's password (the user the server is running as) is accepted.

The result is a User whose name matches the system user, rather than a randomly generated one.
