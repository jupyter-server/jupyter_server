.. _configuration-overview:

Configuration Overview
======================

Beyond the default configuration settings, you can configure a rich array of
options to suit your workflow. Here are areas that are commonly configured
when using Jupyter Server:

    - :ref:`Jupyter's common configuration system <configure_common>`
    - :ref:`Jupyter server <configure_server>`
    - :ref:`Server extensions <configure_extensions>`

Let's look at highlights of each area.

.. _configure_common:

Jupyter's Common Configuration system
-------------------------------------

Jupyter applications, from the Notebook to JupyterHub to nbgrader, share a
common configuration system. The process for creating a configuration file
and editing settings is similar for all the Jupyter applications.

    - `Jupyter’s Common Configuration Approach <https://jupyter.readthedocs.io/en/latest/projects/config.html>`_
    - `Common Directories and File Locations <https://jupyter.readthedocs.io/en/latest/projects/jupyter-directories.html>`_
    - `Language kernels <https://jupyter.readthedocs.io/en/latest/projects/kernels.html>`_
    - `traitlets <https://traitlets.readthedocs.io/en/latest/config.html#module-traitlets.config>`_
      provide a low-level architecture for configuration.

.. _configure_server:

Server-specific configuration
-----------------------------

The  Jupyter server runs the language kernel and communicates with Jupyter Server frontends.

  - Configuring the Jupyter server

      To create a ``jupyter_server_config.py`` file in the ``.jupyter``
      directory, with all the defaults commented out, use the following
      command::

            $ jupyter server --generate-config

        :ref:`Command line arguments for configuration <config>` settings are
        documented in the configuration file and the user documentation.

  - :ref:`Running a Jupyter server <working_remotely>`
  - Related: `Configuring a language kernel <https://jupyter.readthedocs.io/en/latest/install-kernel.html>`_
    to run in the Jupyter server enables your server to run other languages, like R or Julia.

.. _configure_extensions:

Server extensions
-----------------

- `Distributing Jupyter Extensions as Python Packages <https://jupyter-server.readthedocs.io/en/latest/examples/Server/Distributing%20Jupyter%20Extensions%20as%20Python%20Packages.html#Distributing-Jupyter-Extensions-as-Python-Packages>`_
- `Extending the Server <https://jupyter-server.readthedocs.io/en/latest/extending/index.html>`_

Since security
policies vary from organization to organization, we encourage you to
consult with your security team on settings that would be best for your use
cases. Our documentation offers some responsible security practices, and we
recommend becoming familiar with the practices.
