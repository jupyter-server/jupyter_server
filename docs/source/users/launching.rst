.. _user-launching-a-bare-jupyter-server:

Launching a bare Jupyter Server
===============================

Most of the time, you won't need to start the Jupyter Server directly. Jupyter Web Applications (like Jupyter Notebook, Jupyterlab, Voila, etc.) come with their own entry points that start a server automatically.

Sometimes, though, it can be useful to start Jupyter Server directly when you want to run multiple Jupyter Web applications at the same time. For more details, see the  :ref:`Managing multiple extensions <managing-multiple-extensions>` page. If these extensions are enabled, you can simple run the following:

.. code-block:: bash

    > jupyter server

    [I 2020-03-20 15:48:20.903 ServerApp] Serving notebooks from local directory: /Users/username/home
    [I 2020-03-20 15:48:20.903 ServerApp] Jupyter Server 1.0.0 is running at:
    [I 2020-03-20 15:48:20.903 ServerApp] http://localhost:8888/?token=<...>
    [I 2020-03-20 15:48:20.903 ServerApp]  or http://127.0.0.1:8888/?token=<...>
    [I 2020-03-20 15:48:20.903 ServerApp] Use Control-C to stop this server and shut down all kernels (twice to skip confirmation).
    [I 2020-03-20 15:48:20.903 ServerApp] Welcome to Project Jupyter! Explore the various tools available and their corresponding documentation. If you are interested in contributing to the platform, please visit the communityresources section at https://jupyter.org/community.html.
    [C 2020-03-20 15:48:20.907 ServerApp]

        To access the server, open this file in a browser:
            file:///Users/username/jpserver-###-open.html
        Or copy and paste one of these URLs:
            http://localhost:8888/?token=<...>
        or http://127.0.0.1:8888/?token=<...>