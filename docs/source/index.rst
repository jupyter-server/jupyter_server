Welcome!
========

You've landed on the documentation pages for the **Jupyter Server** Project. Some other pages you may have been looking for:

* `Jupyter Server Github Repo <https://github.com/jupyter/jupyter_server>`_
* `JupyterLab Github Repo <https://github.com/jupyterlab/jupyterlab>`_
* `Jupyter Notebook Github Repo <https://github.com/jupyter/notebook>`_


Introduction
------------

Jupyter Server is the backend—the core services, APIs, and `REST endpoints`_—to Jupyter web applications.

.. note::

   This project replaces the Tornado Web Server in the `Jupyter Notebook`_. Previously, Jupyter applications depended on Jupyter Notebook's server (and thus, got all of its Javascript code). Jupyter Server comes without a default frontend and views all frontends—including the `Jupyter Notebook`_—as equal and separate. For help on migrating from Notebook Server to Jupyter Server, see `this page <operators/migrate-from-nbserver>`_.

.. _Tornado: https://www.tornadoweb.org/en/stable/
.. _Jupyter Notebook: https://github.com/jupyter/notebook
.. _REST endpoints: http://petstore.swagger.io/?url=https://raw.githubusercontent.com/jupyter/notebook/master/notebook/services/api/api.yaml

Who's this for?
---------------

The Jupyter Server is a highly technical piece of the Jupyter Stack, so we've separated documentation to help specific personas:

1. :ref:`Users <users>`: people using Jupyter applications
2. :ref:`Operators <operators>`: people deploying or serving Jupyter applications to others.
3. :ref:`Developers <developers>`: people writing Jupyter Server extensions
4. :ref:`Contributors <contributors>`: people contributing directly to the Jupyter Server library.

If you finds gaps in our documentation, please open an issue (or better, a pull request) on the Jupyter Server `Github repo <https://github.com/jupyter/jupyter_server>`_.


Table of Contents
-----------------

.. toctree::
   :maxdepth: 2

   Users <users/index>
   Operators <operators/index>
   Developers <developers/index>
   Contributors <contributors/index>
   Other <other/index>