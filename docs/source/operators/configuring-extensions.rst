.. _configure-multiple-extensions:

Configuring Extensions
======================

Some Jupyter Server extensions are also configurable applications. There are
two ways to configure such extensions: i) pass arguments to the extension's
entry point or ii) list configurable options in a Jupyter config file.

Jupyter Server looks for an extension's config file in a set of specific paths. Use the ``jupyter`` entry point to list these paths:

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


Extension config from file
--------------------------

Jupyter Server expects the file to be named after the extension's name like so: ``jupyter_{name}_config``. For example, the Jupyter Notebook's config file is ``jupyter_notebook_config``.

Configuration files can be Python or JSON files.

In Python config files, each trait will be prefixed with ``c.`` that links the trait to the config loader. For example, Jupyter Notebook config might look like:

.. code-block:: python

    # jupyter_notebook_config.py

    c.NotebookApp.mathjax_enabled = False


A Jupyter Server will automatically load config for each enabled extension. You can configure each extension by creating their corresponding Jupyter config file.


Extension config on the command line
------------------------------------

Server extension applications can also be configured from the command line, and
multiple extension can be configured at the same time. Simply pass the traits
(with their appropriate prefix) to the ``jupyter server`` entrypoint, e.g.:

.. code-block:: console

    > jupyter server --ServerApp.port=9999 --MyExtension1.trait=False --MyExtension2.trait=True


This will also work with any extension entrypoints that allow other extensions to run side-by-side, e.g.:

.. code-block:: console

    > jupyter myextension --ServerApp.port=9999 --MyExtension1.trait=False --MyExtension2.trait=True
