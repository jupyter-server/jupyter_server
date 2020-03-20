==============
Jupyter Server
==============

Jupyter Server is the backend to most Jupyter applications, providing the core services, APIs and `REST endpoints`_ for Jupyter applications. The Jupyter Server provides no frontend out-of-the-box; rather, it exposes `hooks <frontends.html>`_ to attach any number of Jupyter frontends.

*A bit of history...* before the Jupyter Server project, the `Jupyter Notebook`_ was the only first-class frontend to the Tornado Server. As a consequence, other Jupyter frontends had to include Jupyter Notebook (and all of its Javascript code) as a dependency. The Jupyter Server project views all frontends—including the `Jupyter Notebook`_—as equal and separate. Now, multiple frontends can plug into the Jupyter backend at the same time by using the Jupyter Server library.

.. _Tornado: https://www.tornadoweb.org/en/stable/
.. _Jupyter Notebook: https://github.com/jupyter/notebook
.. _REST endpoints: http://petstore.swagger.io/?url=https://raw.githubusercontent.com/jupyter/notebook/master/notebook/services/api/api.yaml

Documentation personas
----------------------

The Jupyter Server is a highly technical piece of the Jupyter Stack. Most users won't interact with this library directly, so the documentation will be different for different types of personas. To help you navigate the docs, we've separated the documentation for different personas:

1. Users: people using Jupyter applications
2. Operators: people deploying or serving Jupyter applications to others.
3. Extension authors: people writing Jupyter Server extensions
3. Contributors: people contributing directly to the Jupyter Server library.

For Users
~~~~~~~~~

For most Jupyter users, Jupyter Server will go unnoticed. The server automatically installs/runs when you install/run Jupyter Notebook, Jupyterlab, Voila, etc.

Sometimes you may need to configure the server, e.g. set the ``port`` number or some other property. We outline how to do that in the documentation below

.. contents::
   :depth: 2

   users/installation

- Configuring a Jupyter Server
- Launching a bare Jupyter Server
- Getting help

For Operators
~~~~~~~~~~~~~

- Serving a Jupyter Server with multiple frontends.
- Managing multiple extensions.
- Configuring multiple extensions.
- Changelog

For Extension Authors
~~~~~~~~~~~~~~~~~~~~~

- Depending on Jupyter Server
- Migrating a Notebook server extension to Jupyter Server
- Writing a basic server extension from scratch
- Writing a frontend server extension from scratch
- Changelog

For Contributors
~~~~~~~~~~~~~~~~

- Monthly Meetings and Roadmap
- Changelog
