.. _server_rbac:

Jupyter Server RBAC
===================

Role Based Access Control (RBAC) in Jupyter Server serves to provide fine grained control of access
to Jupyter Server's API resources.

Motivation
----------

By default, the Jupyter Server API requires authentication to access its endpoints. This ensures
that an unauthenticated user is not allowed to perform such actions. While it already proves to be
very useful, this system lacks flexibility. For instance, it you want another user to access a
notebook, you can only send them the access token that they will insert in the URL, or set up a
password and share it with them. In both cases, the server cannot know two different users are
accessing a notebook.

That being said, the default authentication layer in Jupyter Server can easily be patched and
replaced with any other authentication system, such as OAuth2, which allows for providing a "real"
user identity. This information could then be used to enable new features.

Real Time Collaboration (RTC) support in JupyterLab can make great use of this kind of information.
When several people work on the same notebook, they can see the other users typing live into cells,
with their name poping up when the mouse pointer hovers over their cursor. This is only possible if
the server knows who is connected.

This kind of scenarios has some overlap with JupyterHub, although it doesn't operate quite at the
same level. In particular, JupyterHub has a "single-user notebook servers" mode that checks whether
incoming requests come from users known by its authenticator. JupyterHub is also transitioning to an
RBAC system.

Jupyter Server needs RBAC for the same reasons JupyterHub does, but without depending on it. It
should be possible to serve a notebook without deploying a Hub. Also, the resources being accessed
are actually orthogonal: while JupyterHub manages servers, Jupyter Server manages sub-server
resources such as kernels, sessions, files, terminals...

Definitions
-----------

**Scopes** are specific permissions used to evaluate API requests. For example: the API endpoint
``api/kernels``, which enables listing or starting kernels, is guarded by the scope
``users:kernels``.

Scopes are not directly assigned to requesters. Rather, when a client performs an API call, their
access will be evaluated based on their assigned roles.

**Roles** are collections of scopes that specify the level of what a client is allowed to do. For
example, a group administrator may be granted permission to control the kernels of group members,
but not to create, modify or delete group members themselves. Within the RBAC framework, this is
achieved by assigning a role to the administrator that covers exactly those privileges.

Technical overview
------------------

.. toctree::
   :maxdepth: 1
   :name: rbac

   roles
   scopes
