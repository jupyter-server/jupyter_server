.. _migrate_from_notebook:

Migrate from Notebook
=====================

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
