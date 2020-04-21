.. _user-configuring-a-jupyter-server:

Configuring a Jupyter Server
============================

Using a Jupyter config file
---------------------------

By default, Jupyter Server looks for server-specific configuration in a ``jupyter_server_config`` file located on a Jupyter path. To list the paths where Jupyter Server will look, run:

.. code-block:: console

    $ jupyter --paths

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


Jupyter Server uses IPython's traitlets system for configuration. Traits can be listed in a Python or JSON config file. You can quickly create a ``jupyter_server_config.py`` file in the ``.jupyter`` directory, with all the defaults commented out, use the following command:

.. code-block:: console

    $ jupyter server --generate-config

In Python files, these traits will have the prefix ``c.ServerApp``. For example, your configuration file could look like:

.. code-block:: python

    # inside a jupyter_server_config.py file.

    c.ServerApp.port = 9999

The same configuration in JSON, looks like:

.. code-block:: json

    {
        "ServerApp": {
            "port": 9999
        }
    }


Using the CLI
-------------

Alternatively, you can configure Jupyter Server when launching from the command line using CLI args. Prefix each argument with ``--ServerApp`` like so:

.. code-block:: console

    $ jupyter server --ServerApp.port=9999


Full configuration list
-----------------------

See the full list of configuration options for the server :ref:`here <other-full-config>`.