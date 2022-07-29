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


Authentication and Authorization
--------------------------------

.. versionadded:: 2.0

There are two steps to deciding whether to allow a given request to be happen.

The first step is "Authentication" (identifying who is making the request).
This is handled by the :class:`.IdentityProvider`.

Whether a given user is allowed to take a specific action is called "Authorization",
and is handled separately, by an :class:`.Authorizer`.

These two classes may work together,
as the information returned by the IdentityProvider is given to the Authorizer when it makes its decisions.

Authentication always takes precedence because if no user is authenticated,
no authorization checks need to be made,
as all requests requiring _authorization_ must first complete _authentication_.

Identity Providers
******************

The :class:`.IdentityProvider` class is responsible for the "authentication" step,
identifying the user making the request,
and constructing information about them.

It principally implements two methods.

.. autoclass:: jupyter_server.auth.IdentityProvider

  .. automethod:: get_user
  .. automethod:: identity_model

The first is :meth:`.IdentityProvider.get_user`.
This method is given a RequestHandler, and is responsible for deciding whether there is an authenticated user making the request.
If the request is authenticated, it should return a :class:`.jupyter_server.auth.User` object representing the authenticated user.
It should return None if the request is not authenticated.

The default implementation accepts token or password authentication.

This User object will be available as `self.current_user` in any request handler.
Request methods decorated with tornado's `@web.authenticated` decorator
will only be allowed if this method returns something.

The User object will be a Python :py:class:`dataclasses.dataclass`, `jupyter_server.auth.User`:

.. autoclass:: jupyter_server.auth.User

A custom IdentityProvider _may_ return a custom subclass.


The next method an identity provider has is :meth:`~.IdentityProvider.identity_model`.
`identity_model(user)` is responsible for transforming the user object returned from `.get_user()`
into a standard identity model dictionary,
for use in the `/api/me` endpoint.

If your user object is a simple username string or a dict with a `username` field,
you may not need to implement this method, as the default implementation will suffice.

Any required fields missing from the dict returned by this method will be filled-out with defaults.
Only `username` is strictly required, if that is all the information the identity provider has available.

Missing will be derived according to:

- if `name` is missing, use `username`
- if `display_name` is missing, use `name`

Other required fields will be filled with `None`.


Identity Model
^^^^^^^^^^^^^^

The identity model is the model accessed at `/api/me`,
and describes the currently authenticated user.

It has the following fields:

username
  (string)
  Unique string identifying the user.
  Must be non-empty.
name
  (string)
  For-humans name of the user.
  May be the same as `username` in systems where only usernames are available.
display_name
  (string)
  Alternate rendering of name for display, such as a nickname.
  Often the same as `name`.
initials
  (string or null)
  Short string of initials.
  Initials should not be derived automatically due to localization issues.
  May be `null` if unavailable.
avatar_url
  (string or null)
  URL of an avatar image to be used for the user.
  May be `null` if unavailable.
color
  (string or null)
  A CSS color string to use as a preferred color,
  such as for collaboration cursors.
  May be `null` if unavailable.

Authorization
*************

Authorization is the second step in allowing an action,
after a user has been _authenticated_ by the IdentityProvider.

Authorization in Jupyter Server serves to provide finer grained control of access to its
API resources. With authentication, requests are accepted if the current user is known by
the server. Thus it can restrain access to specific users, but there is no way to give allowed
users more or less permissions. Jupyter Server provides a thin and extensible authorization layer
which checks if the current user is authorized to make a specific request.

.. autoclass:: jupyter_server.auth.Authorizer

  .. automethod:: is_authorized

This is done by calling a ``is_authorized(handler, user, action, resource)`` method before each
request handler. Each request is labeled as either a "read", "write", or "execute" ``action``:

- "read" wraps all ``GET`` and ``HEAD`` requests.
  In general, read permissions grants access to read but not modify anything about the given resource.
- "write" wraps all ``POST``, ``PUT``, ``PATCH``, and ``DELETE`` requests.
  In general, write permissions grants access to modify the given resource.
- "execute" wraps all requests to ZMQ/Websocket channels (terminals and kernels).
  Execute is a special permission that usually corresponds to arbitrary execution,
  such as via a kernel or terminal.
  These permissions should generally be considered sufficient to perform actions equivalent
  to ~all other permissions via other means.

The ``resource`` being accessed refers to the resource name in the Jupyter Server's API endpoints.
In most cases, this is matches the field after `/api/`.
For instance, values for ``resource`` in the endpoints provided by the base jupyter server package,
and the corresponding permissions:

.. list-table::
   :header-rows: 1

   * - resource
     - read
     - write
     - execute
     - endpoints

   * - *resource name*
     - *what can you do with read permissions?*
     - *what can you do with write permissions?*
     - *what can you do with execute permissions, if anything?*
     - ``/api/...`` *what endpoints are governed by this resource?*

   * - api
     - read server status (last activity, number of kernels, etc.), OpenAPI specification
     -
     -
     - ``/api/status``, ``/api/spec.yaml``
   * - csp
     -
     - report content-security-policy violations
     -
     - ``/api/security/csp-report``
   * - config
     - read frontend configuration, such as for notebook extensions
     - modify frontend configuration
     -
     - ``/api/config``
   * - contents
     - read files
     - modify files (create, modify, delete)
     -
     - ``/api/contents``, ``/view``, ``/files``
   * - kernels
     - list kernels, get status of kernels
     - start, stop, and restart kernels
     - Connect to kernel websockets, send/recv kernel messages.
       **This generally means arbitrary code execution,
       and should usually be considered equivalent to having all other permissions.**
     - ``/api/kernels``
   * - kernelspecs
     - read, list information about available kernels
     -
     -
     - ``/api/kernelspecs``
   * - nbconvert
     - render notebooks to other formats via nbconvert.
       **Note: depending on server-side configuration,
       this *could* involve execution.**
     -
     -
     - ``/api/nbconvert``
   * - server
     -
     - Shutdown the server
     -
     - ``/api/shutdown``
   * - sessions
     - list current sessions (association of documents to kernels)
     - create, modify, and delete existing sessions,
       which includes starting, stopping, and deleting kernels.
     -
     - ``/api/sessions``
   * - terminals
     - list running terminals and their last activity
     - start new terminals, stop running terminals
     - Connect to terminal websockets, execute code in a shell.
       **This generally means arbitrary code execution,
       and should usually be considered equivalent to having all other permissions.**
     - ``/api/terminals``


Extensions may define their own resources.
Extension resources should start with ``extension_name:`` to avoid namespace conflicts.

If ``is_authorized(...)`` returns ``True``, the request is made; otherwise, a
``HTTPError(403)`` (403 means "Forbidden") error is raised, and the request is blocked.

By default, authorization is turned off—i.e. ``is_authorized()`` always returns ``True`` and
all authenticated users are allowed to make all types of requests. To turn-on authorization, pass
a class that inherits from ``Authorizer`` to the ``ServerApp.authorizer_class``
parameter, implementing a ``is_authorized()`` method with your desired authorization logic, as
follows:

.. sourcecode:: python

    from jupyter_server.auth import Authorizer

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
``@authorized`` (from ``jupyter_server.auth``), similarly to the
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
