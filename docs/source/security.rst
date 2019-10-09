.. _server_security:

Security in the Jupyter Server
==============================

Since access to the Jupyter Server means access to running arbitrary code,
it is important to restrict access to the server.
For this reason, Jupyter Server uses a token-based authentication that is **on by default**.

.. note::

    If you enable a password for your server,
    token authentication is not enabled by default.

When token authentication is enabled, the server uses a token to authenticate requests.
This token can be provided to login to the server in three ways:

- in the ``Authorization`` header, e.g.::

    Authorization: token abcdef...

- In a URL parameter, e.g.::

    https://my-server/tree/?token=abcdef...

- In the password field of the login form that will be shown to you if you are not logged in.

When you start a Jupyter server with token authentication enabled (default),
a token is generated to use for authentication.
This token is logged to the terminal, so that you can copy/paste the URL into your browser::

    [I 11:59:16.597 ServerApp] The Jupyter Server is running at:
    http://localhost:8888/?token=c8de56fa4deed24899803e93c227592aef6538f93025fe01


If the Jupyter server is going to open your browser automatically,
an *additional* token is generated for launching the browser.
This additional token can be used only once,
and is used to set a cookie for your browser once it connects.
After your browser has made its first request with this one-time-token,
the token is discarded and a cookie is set in your browser.

At any later time, you can see the tokens and URLs for all of your running servers with :command:`jupyter server list`::

    $ jupyter server list
    Currently running servers:
    http://localhost:8888/?token=abc... :: /home/you/notebooks
    https://0.0.0.0:9999/?token=123... :: /tmp/public
    http://localhost:8889/ :: /tmp/has-password

For servers with token-authentication enabled, the URL in the above listing will include the token,
so you can copy and paste that URL into your browser to login.
If a server has no token (e.g. it has a password or has authentication disabled),
the URL will not include the token argument.
Once you have visited this URL,
a cookie will be set in your browser and you won't need to use the token again,
unless you switch browsers, clear your cookies, or start a Jupyter server on a new port.

Alternatives to token authentication
------------------------------------

If a generated token doesn't work well for you,
you can set a password for your server.
:command:`jupyter server password` will prompt you for a password,
and store the hashed password in your :file:`jupyter_server_config.json`.

.. versionadded:: 5.0

    :command:`jupyter server password` command is added.


It is possible disable authentication altogether by setting the token and password to empty strings,
but this is **NOT RECOMMENDED**, unless authentication or access restrictions are handled at a different layer in your web application:

.. sourcecode:: python

    c.ServerApp.token = ''
    c.ServerApp.password = ''


.. _server_security:
