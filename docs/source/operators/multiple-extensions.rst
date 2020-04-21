
.. _managing-multiple-extensions:

Managing multiple extensions
----------------------------

One of the major benefits of Jupyter Server is that you can run serve multiple Jupyter frontend applications above the same Tornado web server. That's because every Jupyter frontend application is now a server extension. When you run a Jupyter Server will multiple extensions enabled, each extension appends its own set of handlers and static assets to the server.

Listing extensions
~~~~~~~~~~~~~~~~~~

When you install a Jupyter Server extension, it *should* automatically add itself to your list of enabled extensions. You can see a list of installed extensions by calling:

.. code-block:: console

    > jupyter server extension list

    config dir: /Users/username/etc/jupyter
        myextension enabled
        - Validating myextension...
          myextension  OK

Enabling/disabling extensions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You enable/disable an extension using the following commands:

.. code-block:: console

    > jupyter server extension enable myextension

    Enabling: myextension
        - Validating myextension...
          myextension  OK
        - Extension successfully enabled.


    > jupyter server extension disable myextension

    Disabling: jupyter_home
        - Validating jupyter_home...
          jupyter_home  OK
        - Extension successfully disabled.


Running an extensions from its entrypoint
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Extensions that are also Jupyter applications (i.e. Notebook, JupyterLab, Voila, etc.) can be launched
from a CLI entrypoint. For example, launch Jupyter Notebook using:

.. code-block:: console

    > jupyter notebook


Jupyter Server will automatically start a server and the browser will be routed to Jupyter Notebook's default URL (typically, ``/tree``).

Other enabled extension will still be available to the user. The entrypoint simply offers a more direct (backwards compatible) launching mechanism.

Launching a server with multiple extensions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If multiple extensions are enabled, a Jupyter Server can be launched directly:

.. code-block:: console

    > jupyter server

    [I 2020-03-23 15:44:53.290 ServerApp] Serving notebooks from local directory: /Users/username/path
    [I 2020-03-23 15:44:53.290 ServerApp] Jupyter Server 0.3.0.dev is running at:
    [I 2020-03-23 15:44:53.290 ServerApp] http://localhost:8888/?token=<...>
    [I 2020-03-23 15:44:53.290 ServerApp]  or http://127.0.0.1:8888/?token=<...>
    [I 2020-03-23 15:44:53.290 ServerApp] Use Control-C to stop this server and shut down all kernels (twice to skip confirmation).
    [I 2020-03-23 15:44:53.290 ServerApp] Welcome to Project Jupyter! Explore the various tools available and their corresponding documentation. If you are interested in contributing to the platform, please visit the communityresources section at https://jupyter.org/community.html.
    [C 2020-03-23 15:44:53.296 ServerApp]

        To access the server, open this file in a browser:
            file:///Users/username/pathjpserver-####-open.html
        Or copy and paste one of these URLs:
            http://localhost:8888/?token=<...>
        or http://127.0.0.1:8888/?token=<...>


Extensions can also be enabled manually from the Jupyter Server entrypoint using the ``jpserver_extensions`` trait:

.. code-block:: console

    > jupyter server --ServerApp.jpserver_extensions='{"myextension":{"enabled": True}}'
