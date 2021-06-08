.. _roles:

Roles
=====

Jupyter Server provides three roles that are available by default:

- ``user`` role provides a default user scope ``self`` that grants access to the user's own
  resources.
- ``admin`` role contains all available scopes and grants full rights to all actions. This role
  cannot be edited.
- ``token`` role provides a default token scope ``all`` that resolves to the same permissions as
  the token's owner has.

**These roles cannot be deleted.**

Additional custom roles can also be defined. Roles can be assigned to the following entities:

- Users
- Groups
- Tokens

An entity can have zero, one, or multiple roles, and there are no restrictions on which roles can be
assigned to which entity. Roles can be added to or removed from entities at any time.

Users
-----

When a new user gets created, they are assigned their default role (``user`` or ``admin``) if no
custom role is requested, currently based on their admin status.

Groups
------

A group does not require any role, and has no roles by default. If a user is a member of a group,
they automatically inherit any of the group's permissions. This is useful for assigning a set of
common permissions to several users.

Tokens
------

A token's permissions are evaluated based on their owning entity. Since a token is always issued for
a user, it can never have more permissions than its owner. If no specific role is requested for a
new token, the token is assigned the token role.

Defining roles
==============

