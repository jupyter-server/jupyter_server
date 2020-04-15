=========================
Jupyter Server Extensions
=========================

A Jupyter Server extension is typically a module or package that extends to Server’s REST API/endpoints—i.e. adds extra request handlers to Server’s Tornado Web Application.

Authoring a basic server extension
==================================

The simplest way to write a Jupyter Server extension is to write an extension module with a ``_load_jupyter_server_extension`` function. This function should take a single argument, an instance of the ``ServerApp``.


.. code-block:: python

    def _load_jupyter_server_extension(serverapp):
        """
        This function is called when the extension is loaded.
        """
        pass


Adding extension endpoints
--------------------------

The easiest way to add endpoints and handle incoming requests is to subclass the ``JupyterHandler`` (which itself is a subclass of Tornado's ``RequestHandler``).

.. code-block:: python

    from jupyter_server.base.handlers import JupyterHandler

    class MyExtensionHandler(JupyterHandler):

        def get(self):
            ...

        def post(self):
            ...


Then add this handler to Jupyter Server's Web Application through the ``_load_jupyter_server_extension`` function.

.. code-block:: python

    def _load_jupyter_server_extension(serverapp):
        """
        This function is called when the extension is loaded.
        """
        handlers = [
            ('/myextension/hello', MyExtensionHandler)
        ]
        serverapp.web_app.add_handlers('.*$', handlers)



Making an extension discoverable
--------------------------------

To make this extension discoverable to Jupyter Server, there are two steps. First, the extension module must define a ``_jupyter_server_extension_paths()`` function that returns some metadata about the extension entry-points in the module. This informs Jupyter Server what type of extension is being loaded and where to find the ``_load_jupyter_server_extension``.

.. code-block:: python

    def _jupyter_server_extension_paths():
        """
        Returns a list of dictionaries with metadata describing
        where to find the `_load_jupyter_server_extension` function.
        """
        return [
            {
                "module": "my_extension"
            }
        ]

Second, the extension must be listed in the user’s ``jpserver_extensions`` config trait. This can be manually added by users in their ``jupyter_server_config.py`` file:

.. code-block:: python

    c.ServerApp.jpserver_extensions = {
        "my_extension": True
    }

Alternatively, an extension can automatically enable itself by creating the following JSON in the jupyter_server_config.d directory on installation. See XX for more details.

.. code-block:: python

    {
        "ServerApp": {
            "jpserver_extensions": {
                "my_extension": true
            }
        }
    }


Authoring a configurable extension application
==============================================

Some extensions are full-fledged client applications that sit on top of the Jupyter Server. For example, `JupyterLab <https://jupyterlab.readthedocs.io/en/stable/>`_ is a server extension. It can be launched from the command line, configured by CLI or config files, and serves+loads static assets behind the server (i.e. html templates, Javascript, etc.)

Jupyter Server offers a convenient base class, ``ExtensionsApp``, that handles most of the boilerplate code for building such extensions.

Anatomy of an ``ExtensionApp``
------------------------------

An ExtensionApp:

    - has traits.
    - is configurable (from file or CLI)
    - has a name (see the ``extension_name`` trait).
    - has an entrypoint, ``jupyter <extension_name>``.
    - can server static content from the ``/static/<extension_name>/`` endpoint.
    - can add new endpoints to the Jupyter Server.

The basic structure of an ExtensionApp is shown below:

.. code-block:: python

    from jupyter_server.extension.application import ExtensionApp


    class MyExtensionApp(ExtensionApp):

        # -------------- Required traits --------------
        extension_name = "myextension"
        extension_url = "/myextension"
        load_other_extensions = True

        # --- ExtensionApp traits you can configure ---
        static_paths = [...]
        template_paths = [...]
        settings = {...}
        handlers = [...]

        # ----------- add custom traits below ---------
        ...

        def initialize_settings(self):
            ...
            # Update the self.settings trait to pass extra
            # settings to the underlying Tornado Web Application.
            self.settings.update({'<trait>':...})

        def initialize_handlers(self):
            ...
            # Extend the self.handlers trait
            self.handlers.extend(...)

        def initialize_templates(self):
            ...
            # Change the jinja templating environment


The ``ExtensionApp`` uses the following methods and properties to connect your extension to the Jupyter server. You do no need to define a ``_load_jupyter_server_extension`` function for these apps. Instead, overwrite the pieces below to add your custom settings, handlers and templates:

Methods

* ``initialize_setting()``: adds custom settings to the Tornado Web Application.
* ``initialize_handlers()``: appends handlers to the Tornado Web Application.
* ``initialize_templates()``: initialize the templating engine (e.g. jinja2) for your frontend.

Properties

* ``extension_name``: the name of the extension
* ``extension_url``: the default url for this extension—i.e. the landing page for this extension when launched from the CLI.
* ``load_other_extensions``: a boolean enabling/disabling other extensions when launching this extension directly.

``ExtensionApp`` request handlers
---------------------------------

``ExtensionApp`` Request Handlers have a few extra properties.

* ``config``: the ExtensionApp's config object.
* ``server_config``: the ServerApp's config object.
* ``extension_name``: the name of the extension to which this handler is linked.
* ``static_url()``: a method that returns the url to static files (prefixed with ``/static/<extension_name>``).

Jupyter Server provides a convenient mixin class for adding these properties to any ``JupyterHandler``. For example, the basic server extension handler in the section above becomes:

.. code-block:: python

    from jupyter_server.base.handlers import JupyterHandler
    from jupyter_server.extension.handler import ExtensionHandlerMixin


    class MyExtensionHandler(ExtensionHandlerMixin, JupyterHandler):

        def get(self):
            ...

        def post(self):
            ...


Jinja templating from frontend extensions
-----------------------------------------

Many Jupyter frontend applications use Jinja for basic HTML templating. Since this is common enough, Jupyter Server provides some extra mixin that integrate Jinja with Jupyter server extensions.

Use ``ExtensionAppJinjaMixin`` to automatically add a Jinja templating environment to an ``ExtensionApp``. This adds a ``<extension_name>_jinja2_env`` setting to Tornado Web Server's settings that be be used by request handlers.

.. code-block:: python


    from jupyter_server.extension.application import ExtensionApp, ExtensionAppJinjaMixin


    class MyExtensionApp(ExtensionAppJinjaMixin, ExtensionApp):
        ...


Pair the example above with ``ExtensionHandlers`` that also inherit the ``ExtensionHandlerJinjaMixin`` mixin. This will automatically load HTML templates from the Jinja templating environment created by the ``ExtensionApp``.


.. code-block:: python


    from jupyter_server.base.handlers import JupyterHandler
    from jupyter_server.extension.handler import (
        ExtensionHandlerMixin,
        ExtensionHandlerJinjaMixin
    )

    class MyExtensionHandler(
        ExtensionHandlerMixin,
        ExtensionHandlerJinjaMixin,
        JupyterHandler
    ):

        def get(self):
            ...

        def post(self):
            ...


.. note:: The mixin classes in this example must come before the base classes, ``ExtensionApp`` and ``ExtensionHandler``.


Making an ``ExtensionApp`` discoverable
---------------------------------------

To make an ``ExtensionApp`` discoverable by Jupyter Server, add the ``app`` key+value pair to the ``_jupyter_server_extension_paths()`` function example above:

.. code-block:: python

    from myextension import MyExtensionApp


    def _jupyter_server_extension_paths():
        """
        Returns a list of dictionaries with metadata describing
        where to find the `_load_jupyter_server_extension` function.
        """
        return [
            {
                "module": "myextension",
                "app": MyExtensionApp
            }
        ]


Launching an ``ExtensionApp``
-----------------------------

To launch the application, simply call the ``ExtensionApp``'s ``launch_instance`` method.

.. code-block:: python

    launch_instance = MyFrontend.launch_instance
    launch_instance()


To make your extension executable from anywhere on your system, point an entry-point at the ``launch_instance`` method in the extension's ``setup.py``:

.. code-block:: python

    from setuptools import setup


    setup(
        name='myfrontend',
        ...
        entry_points={
            'console_scripts': [
                'jupyter-myextension = myextension:launch_instance'
            ]
        }
    )

Distributing a server extension
===============================



Example Server Extension
========================

You can check some simple example on the `GitHub jupyter_server repository
<https://github.com/jupyter/jupyter_server/tree/master/examples/simple>`_.
