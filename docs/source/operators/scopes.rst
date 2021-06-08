.. _scoles:

Scopes in Jupyter Server
========================

A scope has a syntax-based design that reveals which resources it provides access to. Resources are
objects with a type, associated data, relationships to other resources, and a set of methods that
operate on them.

``<resource>`` in the RBAC scope design refers to the resource name in the Jupyter Server's API
endpoints in most cases (maybe prefixed with ``/api/``). For instance, ``<resource>`` equal to
``users`` corresponds to Jupyter Server's API endpoints beginning with ``/api/users``.

Available scopes
----------------

The table below lists all available scopes.

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - Scope
     - Description
   * - ``self``
     - Metascope, grants access to user's own resources only.
   * - ``all``
     - Metascope, valid for tokens only. Grants access to everything that the token's owning entity can access.
   * - ``admin:users``
     - Grants read, write, create and delete access to users and their authentication state but not their tokens.
   * - ``admin:users:auth_state``
     - Grants access to users’ authentication state only.
   * - ``users``
     - Grants read and write permissions to users' models apart from tokens and authentication state.
   * - ``read:users``
     - Read-only access to users' models apart from tokens and authentication state.
   * - ``read:users:name``
     - Read-only access to users' names.
   * - ``read:users:groups``
     - Read-only access to users' group names.
   * - ``users:tokens``
     - Grants read, write, create and delete permissions to users' tokens.
   * - ``read:users:tokens``
     - Read-only access to users' tokens.
   * - ``admin:groups``
     - Grants read, write, create and delete access to groups.
   * - ``groups``
     - Grants read and write permissions to groups, including adding/removing users to/from groups.
   * - ``read:groups``
     - Read-only access to groups' models.

Scopes and APIs
---------------

.. list-table::
   :widths: 35 10 25 25
   :header-rows: 1

   * - Path
     - Operation
     - Description
     - Scopes
   * - ``/api/groups``
     - ``GET``
     - List groups
     - ``read:groups``
   * - ``/api/groups/{name}``
     - ``DELETE``
     - Delete a group
     - ``admin:groups``
   * -
     - ``GET``
     - Get a group by name
     - ``read:groups``
   * -
     - ``POST``
     - Create a group
     - ``admin:groups``
   * - ``/api/groups/{name}/users``
     - ``DELETE``
     - Remove users from a group
     - ``groups``
   * -
     - ``POST``
     - Add users to a group
     - ``groups``
   * - ``/api/user``
     - ``GET``
     - Return authenticated user's model
     - ``read:users``, ``read:users:name``, ``read:users:groups``, ``admin:users:auth_state``
   * - ``/api/users``
     - ``GET``
     - List users
     - ``read:users``, ``read:users:name``, ``read:users:groups``
   * -
     - ``POST``
     - Create multiple users
     - ``admin:users``
   * - ``/api/users/{name}``
     - ``DELETE``
     - Delete a user
     - ``admin:users``
   * -
     - ``GET``
     - Get a user by name
     - ``read:users``, ``read:users:name``, ``read:users:groups``, ``admin:users:auth_state``
   * -
     - ``PATCH``
     - Modify a user
     - ``admin:users``
   * -
     - ``POST``
     - Create a single user
     - ``admin:users``
   * - ``/api/users/{name}/tokens``
     - ``GET``
     - List tokens for the user
     - ``read:users:tokens``
   * -
     - ``POST``
     - Create a new token for the user
     - ``users:tokens``
   * - ``/api/users/{name}/tokens/{token_id}``
     - ``DELETE``
     - Delete (revoke) a token by id
     - ``users:tokens``
   * -
     - ``GET``
     - Get the model for a token by id
     - ``read:users:tokens``
   * - ``/api/contents/{path}``
     - ``GET``
     - Get contents of file or directory
     - ``read:contents``
   * -
     - ``POST``
     - Create a new file in the specified path
     - ``contents``
   * -
     - ``PATCH``
     - Rename a file or directory without re-uploading content
     - ``contents``
   * -
     - ``PUT``
     - Save or upload file
     - ``contents``
   * -
     - ``DELETE``
     - Delete a file in the given path
     - ``contents``
   * - ``/api/kernels``
     - ``GET``
     - List the JSON data for all kernels that are currently running
     - ``read:kernels``
   * - ``/api/kernels/{kernel_id}``
     - ``GET``
     - Get kernel information
     - ``read:kernels``
   * -
     - ``DELETE``
     - Kill a kernel and delete the kernel id
     - ``kernels``
   * - ``/api/kernels/{kernel_id}/interrupt``
     - ``POST``
     - Interrupt a kernel
     - ``kernels``
   * - ``/api/kernels/{kernel_id}/restart``
     - ``POST``
     - Restart a kernel
     - ``kernels``

Scopes and APIs
---------------

The scopes are also listed in the Jupyter Server REST API documentation. Each API endpoint has a
list of scopes which can be used to access the API; if no scopes are listed, the API is not
authenticated and can be accessed without any permissions (i.e., no scopes).

Listed scopes by each API endpoint reflect the "lowest" permissions required to gain any access to
the corresponding API. For example, posting user's activity (*POST /api/users/:name/tokens*) needs
``users:tokens`` scope. If scope ``users`` is passed during the request, the access will be granted
as the required scope is a subscope of the ``users`` scope. If, on the other hand,
``read:users:tokens`` scope is passed, the access will be denied.
