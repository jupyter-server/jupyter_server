Welcome!
========

You've landed on the documentation pages for the **Jupyter Server** Project. Some other pages you may have been looking for:

* `Jupyter Server Github Repo <https://github.com/jupyter-server/jupyter_server>`_, the source code we describe in this code.
* `Jupyter Notebook Github Repo <https://github.com/jupyter/notebook>`_ , the source code for the classic Notebook.
* `JupyterLab Github Repo <https://github.com/jupyterlab/jupyterlab>`_, the JupyterLab server which runs on the Jupyter Server.


Introduction
------------

Jupyter Server is the backend that provides the core services, APIs, and
`REST endpoints`_ for Jupyter web applications.

.. note::

   Jupyter Server is a replacement for the Tornado Web Server in `Jupyter Notebook`_. Jupyter web applications should move to using Jupyter Server. For help, see the :ref:`migrate_from_notebook` page.

.. _Tornado: https://www.tornadoweb.org/en/stable/
.. _Jupyter Notebook: https://github.com/jupyter/notebook
.. _REST endpoints: https://petstore.swagger.io/?url=https://raw.githubusercontent.com/jupyter/jupyter_server/main/jupyter_server/services/api/api.yaml


Applications
------------

Jupyter Server extensions can use the framework and services provided by
Jupyter Server to create applications and services.

Examples of Jupyter Server extensions include:

.. _examples of jupyter server extensions:

`Jupyter Lab <https://jupyterlab.readthedocs.io>`_
   JupyterLab computational environment.
`Jupyter Resource Usage <https://github.com/jupyter-server/jupyter-resource-usage>`_
   Jupyter Notebook Extension for monitoring your own resource usage.
`Jupyter Scheduler <https://jupyter-scheduler.readthedocs.io>`_
   Run Jupyter notebooks as jobs.
`jupyter-collaboration <https://jupyterlab-realtime-collaboration.readthedocs.io>`_
   A Jupyter Server Extension Providing Support for Y Documents.
`NbClassic <https://jupyterlab.readthedocs.io>`_
   Jupyter notebook as a Jupyter Server extension.
`Cylc UI Server <https://cylc.org>`_
   A Jupyter Server extension that serves the cylc-ui web application for
   monitoring and controlling Cylc workflows.

For more information on extensions, see :ref:`extensions`.


Who's this for?
---------------

The Jupyter Server is a highly technical piece of the Jupyter Stack, so we've separated documentation to help specific personas:

1. :ref:`Users <users>`: people using Jupyter web applications.
2. :ref:`Operators <operators>`: people deploying or serving Jupyter web applications to others.
3. :ref:`Developers <developers>`: people writing Jupyter Server extensions and web applications.
4. :ref:`Contributors <contributors>`: people contributing directly to the Jupyter Server library.

If you finds gaps in our documentation, please open an issue (or better, a pull request) on the Jupyter Server `Github repo <https://github.com/jupyter-server/jupyter_server>`_.


Table of Contents
-----------------

.. toctree::
   :maxdepth: 2

   Users <users/index>
   Operators <operators/index>
   Developers <developers/index>
   Contributors <contributors/index>
   Other <other/index>
