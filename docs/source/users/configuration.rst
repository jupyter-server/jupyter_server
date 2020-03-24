Configuring a Jupyter Server
============================

By default, Jupyter Server looks for server-specific configuration in a ``jupyter_server_config.py|json`` file located on a Jupyter path. To list the possible paths, run:

.. code-block:: console

    > jupyter --paths

    config:
        /Users/username/.jupyter
        /usr/local/etc/jupyter
        /etc/jupyter
    data:
        /Users/username/Library/Jupyter
        /usr/local/share/jupyter
        /usr/share/jupyter
    runtime:
        /Users/username/Library/Jupyter/runtime


The paths under ``config`` are listed in order of precedence. If the same trait is listed in multiple places, it will be set to the value from the file will highest precendence.

Jupyter Server uses IPython's traitlets system for configuration. Traits can be listed in a Python or JSON config file. In Python files, these traits will have the prefix ``ServerApp``. For example, your configuration file could look like:

.. code-block:: python

    # inside a jupyter_server_config.py file.
    c.ServerApp.port = 9999


