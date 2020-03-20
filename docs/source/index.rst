==============
Jupyter Server
==============

Jupyter Server is the backend—the core services, APIs, and `REST endpoints`_—to most Jupyter applications.

.. note::

   This project replaces the Tornado Server in previous versions of the `Jupyter Notebook`_ project. Before the Jupyter Server project, the `Jupyter Notebook`_ came with it's own Tornado Web Server. As a consequence, other Jupyter frontends had to depend on Jupyter Notebook (and all of its Javascript code) to get a working Jupyter Server. This project provides Jupyter Server without a default frontend and views all frontends—including the `Jupyter Notebook`_—as equal and separate.

.. _Tornado: https://www.tornadoweb.org/en/stable/
.. _Jupyter Notebook: https://github.com/jupyter/notebook
.. _REST endpoints: http://petstore.swagger.io/?url=https://raw.githubusercontent.com/jupyter/notebook/master/notebook/services/api/api.yaml


The Jupyter Server is a highly technical piece of the Jupyter Stack. Most users won't touch this library directly, so the documentation will be different for different types of personas. To help you navigate the docs, we've separated the documentation for different personas:

1. :ref:`Users <users>`: people using Jupyter applications
2. Operators: people deploying or serving Jupyter applications to others.
3. Extension authors: people writing Jupyter Server extensions
4. Contributors: people contributing directly to the Jupyter Server library.

.. toctree::
   :caption: Users
   :maxdepth: 2
   :name: users
   :titlesonly:

   users/installation
   users/configuration
   users/launching
   users/help

Operators
~~~~~~~~~

- Serving a Jupyter Server with multiple frontends.
- Managing multiple extensions.
- Configuring multiple extensions.
- Changelog

Extension Authors
~~~~~~~~~~~~~~~~~

- Depending on Jupyter Server
- Migrating a Notebook server extension to Jupyter Server
- Writing a basic server extension from scratch
- Writing a frontend server extension from scratch
- Changelog

Contributors
~~~~~~~~~~~~

- Monthly Meetings and Roadmap
- Changelog
