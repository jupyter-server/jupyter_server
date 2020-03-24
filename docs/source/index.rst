==============
Jupyter Server
==============

Jupyter Server is the backend—the core services, APIs, and `REST endpoints`_—to Jupyter applications.

.. note::

   This project replaces the Tornado Web Server in the `Jupyter Notebook`_. Previously, Jupyter applications depended on Jupyter Notebook's server (and thus, got all of its Javascript code). Jupyter Server comes without a default frontend and views all frontends—including the `Jupyter Notebook`_—as equal and separate. For help on migrating from Notebook Server to Jupyter Server, see `this page <operators/migrate-from-nbserver>`_.

.. _Tornado: https://www.tornadoweb.org/en/stable/
.. _Jupyter Notebook: https://github.com/jupyter/notebook
.. _REST endpoints: http://petstore.swagger.io/?url=https://raw.githubusercontent.com/jupyter/notebook/master/notebook/services/api/api.yaml


The Jupyter Server is a highly technical piece of the Jupyter Stack. Since most users won't import this library directly, we broke the documentation into separate personas:

1. :ref:`Users <users>`: people using Jupyter applications
2. Operators: people deploying or serving Jupyter applications to others.
3. Extension authors: people writing Jupyter Server extensions
4. Contributors: people contributing directly to the Jupyter Server library.

.. toctree::
   :caption: Users
   :maxdepth: 1
   :name: users

   users/installation
   users/configuration
   users/launching
   users/help

.. toctree::
   :caption: Operators
   :maxdepth: 1
   :name: operators

   operators/multiple-frontends
   operators/configuring-extensions
   operators/migrate-from-nbserver
   operators/public-server
   operators/security

.. toctree::
   :caption: Developers
   :maxdepth: 1
   :name: developers

   developers/dependency
   developers/basic-extension
   developers/configurable-extension
   developers/rest-api
   changelog

.. toctree::
   :caption: Contributors
   :maxdepth: 1
   :name: contributors

   contributors/team-meetings
   contributors/contributing

.. - Depending on Jupyter Server
.. - Migrating a Notebook server extension to Jupyter Server
.. - Writing a basic server extension from scratch
.. - Writing a frontend server extension from scratch


.. Contributors
.. ~~~~~~~~~~~~

.. - Monthly Meetings and Roadmap
.. - Changelog
