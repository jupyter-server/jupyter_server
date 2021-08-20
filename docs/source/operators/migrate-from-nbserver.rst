.. _migrate_from_notebook:

Migrating from Notebook Server
==============================

To migrate from notebook server to plain jupyter server, follow these steps:

- Rename your ``jupyter_notebook_config.py`` file to ``jupyter_server_config.py``.
- Rename all ``c.NotebookApp`` traits to ``c.ServerApp``.

For example if you have the following ``jupyter_notebook_config.py``.

.. code-block:: python

    c.NotebookApp.allow_credentials = False
    c.NotebookApp.port = 8889
    c.NotebookApp.password_required = True


You will have to create the following ``jupyter_server_config.py`` file.

.. code-block:: python

    c.ServerApp.allow_credentials = False
    c.ServerApp.port = 8889
    c.ServerApp.password_required = True


Running Jupyter Notebook on Jupyter Server
==========================================

If you want to switch to Jupyter Server, but you still want to serve `Jupyter Notebook <https://github.com/jupyter/notebook>`_ to users, you can try `NBClassic <https://github.com/jupyterlab/nbclassic>`_.

NBClassic is a Jupyter Server extension that serves the Notebook frontend (i.e. all static assets) on top of Jupyter Server. It even loads Jupyter Notebook's config files.

.. warning:: NBClassic will only work for a limited time. Jupyter Server is likely to evolve beyond a point where Jupyter Notebook frontend will no longer work with the underlying server. Consider switching to `JupyterLab <https://jupyterlab.readthedocs.io/en/stable/>`_ or `nteract <https://nteract.io/>`_ where there is active development happening.
