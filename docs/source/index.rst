Welcome!
========

You've landed on the documentation pages for the **Jupyter Server** Project. Some other pages you may have been looking for:

* `Jupyter Server Github Repo <https://github.com/jupyter/jupyter_server>`_, the source code we describe in this code.
* `Jupyter Notebook Github Repo <https://github.com/jupyter/notebook>`_ , the source code for the classic Notebook.
* `JupyterLab Github Repo <https://github.com/jupyterlab/jupyterlab>`_, the JupyterLab server wich runs on the Jupyter Server.


Introduction
------------

Jupyter Server is the backend—the core services, APIs, and `REST endpoints`_—to Jupyter web applications.

.. note::

   Jupyter Server is a replacement for the Tornado Web Server in `Jupyter Notebook`_. Jupyter web applications should move to using Jupyter Server. For help, see the :ref:`migrate_from_notebook` page.

.. _Tornado: https://www.tornadoweb.org/en/stable/
.. _Jupyter Notebook: https://github.com/jupyter/notebook
.. _REST endpoints: https://petstore.swagger.io/?url=https://raw.githubusercontent.com/jupyter/jupyter_server/1.x/jupyter_server/services/api/api.yaml

Who's this for?
---------------

The Jupyter Server is a highly technical piece of the Jupyter Stack, so we've separated documentation to help specific personas:

1. :ref:`Users <users>`: people using Jupyter web applications.
2. :ref:`Operators <operators>`: people deploying or serving Jupyter web applications to others.
3. :ref:`Developers <developers>`: people writing Jupyter Server extensions and web applications.
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
