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

Authorization
-------------

.. versionadded:: 2.0

Authorization in Jupyter Server serves to provide finer grained control of access to its
API resources. With authentication, requests are accepted if the current user is known by
the server. Thus it can restrain access to specific users, but there is no way to give allowed
users more or less permissions. Jupyter Server provides a thin and extensible authorization layer
which checks if the current user is authorized to make a specific request.

This is done by calling a ``is_authorized(handler, user, action, resource)`` method before each
request handler. Each request is labeled as either a "read", "write", or "execute" ``action``:

- "read" wraps all ``GET`` and ``HEAD`` requests.
- "write" wraps all ``POST``, ``PUT``, ``PATCH``, and ``DELETE`` requests.
- "execute" wraps all requests to ZMQ/Websocket channels (terminals and kernels).

The ``resource`` being accessed refers to the resource name in the Jupyter Server's API endpoints in
most cases.
For instance, values for ``resource`` in the endpoints provided by the base jupyter server package:

- "kernelspecs" corresponds to endpoints beginning with ``/kernelspecs`` and ``/api/kernelspecs``.
- "nbconvert" corresponds to endpoints beginning with ``/nbconvert`` and ``/api/nbconvert``.
- "config" corresponds to endpoints beginning with ``/api/config``.
- "contents" corresponds to endpoints beginning with ``/api/contents`` and ``/view``.
- "kernels" corresponds to endpoints beginning with ``/api/kernels``.
- "sessions" corresponds to endpoints beginning with ``/api/sessions``.
- "terminals" corresponds to endpoints beginning with ``/api/terminals``.
- "server" applies to the endpoint ``/api/shutdown``.
- "api" corresponds to endpoints ``/api/status`` and ``/api/spec.yaml``.
- "csp" corresponds to the endpoint ``/api/security/csp-report``

Extensions may define their own resource.
Extension resources should start with `extension_name:`.

If ``is_authorized(...)`` returns ``True``, the request is made; otherwise, a
``HTTPError(403)`` (403 means "Forbidden") error is raised, and the request is blocked.

By default, authorization is turned off—i.e. ``is_authorized()`` always returns ``True`` and
all authenticated users are allowed to make all types of requests. To turn-on authorization, pass
a class that inherits from ``Authorizer`` to the ``ServerApp.authorizer_class``
parameter, implementing a ``is_authorized()`` method with your desired authorization logic, as
follows:

.. sourcecode:: python

    from jupyter_server.services.auth.authorizer import Authorizer

    class MyAuthorizationManager(Authorizer):
        """Class for authorizing access to resources in the Jupyter Server.

        All authorizers used in Jupyter Server should inherit from
        AuthorizationManager and, at the very minimum, override and implement
        an `is_authorized` method with the following signature.

        The `is_authorized` method is called by the `@authorized` decorator in
        JupyterHandler. If it returns True, the incoming request to the server
        is accepted; if it returns False, the server returns a 403 (Forbidden) error code.
        """

        def is_authorized(self, handler: JupyterHandler, user: Any, action: str, resource: str) -> bool:
            """A method to determine if `user` is authorized to perform `action`
            (read, write, or execute) on the `resource` type.

            Parameters
            ------------
            user : usually a dict or string
                A truthy model representing the authenticated user.
                A username string by default,
                but usually a dict when integrating with an auth provider.

            action : str
                the category of action for the current request: read, write, or execute.

            resource : str
                the type of resource (i.e. contents, kernels, files, etc.) the user is requesting.

            Returns True if user authorized to make request; otherwise, returns False.
            """
            return True  # implement your authorization logic here

The ``is_authorized()`` method will automatically be called whenever a handler is decorated with
``@authorized`` (from ``jupyter_server.services.auth``), similarly to the
``@authenticated`` decorator for authorization (from ``tornado.web``).

Security in notebook documents
==============================

As Jupyter Server become more popular for sharing and collaboration,
the potential for malicious people to attempt to exploit the notebook
for their nefarious purposes increases. IPython 2.0 introduced a
security model to prevent execution of untrusted code without explicit
user input.

The problem
-----------

The whole point of Jupyter is arbitrary code execution. We have no
desire to limit what can be done with a notebook, which would negatively
impact its utility.

Unlike other programs, a Jupyter notebook document includes output.
Unlike other documents, that output exists in a context that can execute
code (via Javascript).

The security problem we need to solve is that no code should execute
just because a user has **opened** a notebook that **they did not
write**. Like any other program, once a user decides to execute code in
a notebook, it is considered trusted, and should be allowed to do
anything.

Our security model
------------------

-  Untrusted HTML is always sanitized
-  Untrusted Javascript is never executed
-  HTML and Javascript in Markdown cells are never trusted
-  **Outputs** generated by the user are trusted
-  Any other HTML or Javascript (in Markdown cells, output generated by
   others) is never trusted
-  The central question of trust is "Did the current user do this?"

The details of trust
--------------------

When a notebook is executed and saved, a signature is computed from a
digest of the notebook's contents plus a secret key. This is stored in a
database, writable only by the current user. By default, this is located at::

    ~/.local/share/jupyter/nbsignatures.db  # Linux
    ~/Library/Jupyter/nbsignatures.db       # OS X
    %APPDATA%/jupyter/nbsignatures.db       # Windows

Each signature represents a series of outputs which were produced by code the
current user executed, and are therefore trusted.

When you open a notebook, the server computes its signature, and checks if it's
in the database. If a match is found, HTML and Javascript
output in the notebook will be trusted at load, otherwise it will be
untrusted.

Any output generated during an interactive session is trusted.

Updating trust
**************

A notebook's trust is updated when the notebook is saved. If there are
any untrusted outputs still in the notebook, the notebook will not be
trusted, and no signature will be stored. If all untrusted outputs have
been removed (either via ``Clear Output`` or re-execution), then the
notebook will become trusted.

While trust is updated per output, this is only for the duration of a
single session. A newly loaded notebook file is either trusted or not in its
entirety.

Explicit trust
**************

Sometimes re-executing a notebook to generate trusted output is not an
option, either because dependencies are unavailable, or it would take a
long time. Users can explicitly trust a notebook in two ways:

-  At the command-line, with::

    jupyter trust /path/to/notebook.ipynb

-  After loading the untrusted notebook, with ``File / Trust Notebook``

These two methods simply load the notebook, compute a new signature, and add
that signature to the user's database.

Reporting security issues
-------------------------

If you find a security vulnerability in Jupyter, either a failure of the
code to properly implement the model described here, or a failure of the
model itself, please report it to security@ipython.org.

If you prefer to encrypt your security reports,
you can use :download:`this PGP public key <ipython_security.asc>`.

Affected use cases
------------------

Some use cases that work in Jupyter 1.0 became less convenient in
2.0 as a result of the security changes. We do our best to minimize
these annoyances, but security is always at odds with convenience.

Javascript and CSS in Markdown cells
************************************

While never officially supported, it had become common practice to put
hidden Javascript or CSS styling in Markdown cells, so that they would
not be visible on the page. Since Markdown cells are now sanitized (by
`Google Caja <https://developers.google.com/caja>`__), all Javascript
(including click event handlers, etc.) and CSS will be stripped.

We plan to provide a mechanism for notebook themes, but in the meantime
styling the notebook can only be done via either ``custom.css`` or CSS
in HTML output. The latter only have an effect if the notebook is
trusted, because otherwise the output will be sanitized just like
Markdown.

Collaboration
*************

When collaborating on a notebook, people probably want to see the
outputs produced by their colleagues' most recent executions. Since each
collaborator's key will differ, this will result in each share starting
in an untrusted state. There are three basic approaches to this:

-  re-run notebooks when you get them (not always viable)
-  explicitly trust notebooks via ``jupyter trust`` or the notebook menu
   (annoying, but easy)
-  share a notebook signatures database, and use configuration dedicated to the
   collaboration while working on the project.

To share a signatures database among users, you can configure:

.. code-block:: python

    c.NotebookNotary.data_dir = "/path/to/signature_dir"

to specify a non-default path to the SQLite database (of notebook hashes,
essentially).
