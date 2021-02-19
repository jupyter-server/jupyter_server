=================
Server Extensions
=================

A Jupyter Server extension is typically a module or package that extends to Server’s REST API/endpoints—i.e. adds extra request handlers to Server’s Tornado Web Application.

You can check some simple examples on the `examples folder
<https://github.com/jupyter/jupyter_server/tree/master/examples/simple>`_ in the GitHub jupyter_server repository.

Authoring a basic server extension
==================================

The simplest way to write a Jupyter Server extension is to write an extension module with a ``_load_jupyter_server_extension`` function. This function should take a single argument, an instance of the ``ServerApp``.


.. code-block:: python

    def _load_jupyter_server_extension(serverapp: jupyter_server.serverapp.ServerApp):
        """
        This function is called when the extension is loaded.
        """
        pass


Adding extension endpoints
--------------------------

The easiest way to add endpoints and handle incoming requests is to subclass the ``JupyterHandler`` (which itself is a subclass of Tornado's ``RequestHandler``).

.. code-block:: python

    from jupyter_server.base.handlers import JupyterHandler
    import tornado

    class MyExtensionHandler(JupyterHandler):

        @tornado.web.authenticated
        def get(self):
            ...

        @tornado.web.authenticated
        def post(self):
            ...

.. note::
   It is best practice to wrap each handler method with the ``authenticated`` decorator to ensure that each request is authenticated by the server.

Then add this handler to Jupyter Server's Web Application through the ``_load_jupyter_server_extension`` function.

.. code-block:: python

    def _load_jupyter_server_extension(serverapp: jupyter_server.serverapp.ServerApp):
        """
        This function is called when the extension is loaded.
        """
        handlers = [
            ('/myextension/hello', MyExtensionHandler)
        ]
        serverapp.web_app.add_handlers('.*$', handlers)


Making an extension discoverable
--------------------------------

To make this extension discoverable to Jupyter Server, first define a ``_jupyter_server_extension_points()`` function at the root of the module/package. This function returns metadata describing how to load the extension. Usually, this requires a ``module`` key with the import path to the extension's ``_load_jupyter_server_extension`` function.

.. code-block:: python

    def _jupyter_server_extension_points():
        """
        Returns a list of dictionaries with metadata describing
        where to find the `_load_jupyter_server_extension` function.
        """
        return [
            {
                "module": "my_extension"
            }
        ]

Second, add the extension to the ServerApp's ``jpserver_extensions`` trait. This can be manually added by users in their ``jupyter_server_config.py`` file,

.. code-block:: python

    c.ServerApp.jpserver_extensions = {
        "my_extension": True
    }

or loaded from a JSON file in the ``jupyter_server_config.d`` directory under one of `Jupyter's paths`_. (See the `Distributing a server extension`_ section for details on how to automatically enabled your extension when users install it.)

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
    - has a name (see the ``name`` trait).
    - has an entrypoint, ``jupyter <name>``.
    - can serve static content from the ``/static/<name>/`` endpoint.
    - can add new endpoints to the Jupyter Server.

The basic structure of an ExtensionApp is shown below:

.. code-block:: python

    from jupyter_server.extension.application import ExtensionApp


    class MyExtensionApp(ExtensionApp):

        # -------------- Required traits --------------
        name = "myextension"
        default_url = "/myextension"
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


The ``ExtensionApp`` uses the following methods and properties to connect your extension to the Jupyter server. You do not need to define a ``_load_jupyter_server_extension`` function for these apps. Instead, overwrite the pieces below to add your custom settings, handlers and templates:

Methods

* ``initialize_setting()``: adds custom settings to the Tornado Web Application.
* ``initialize_handlers()``: appends handlers to the Tornado Web Application.
* ``initialize_templates()``: initialize the templating engine (e.g. jinja2) for your frontend.

Properties

* ``name``: the name of the extension
* ``default_url``: the default url for this extension—i.e. the landing page for this extension when launched from the CLI.
* ``load_other_extensions``: a boolean enabling/disabling other extensions when launching this extension directly.

``ExtensionApp`` request handlers
---------------------------------

``ExtensionApp`` Request Handlers have a few extra properties.

* ``config``: the ExtensionApp's config object.
* ``server_config``: the ServerApp's config object.
* ``name``: the name of the extension to which this handler is linked.
* ``static_url()``: a method that returns the url to static files (prefixed with ``/static/<name>``).

Jupyter Server provides a convenient mixin class for adding these properties to any ``JupyterHandler``. For example, the basic server extension handler in the section above becomes:

.. code-block:: python

    from jupyter_server.base.handlers import JupyterHandler
    from jupyter_server.extension.handler import ExtensionHandlerMixin
    import tornado


    class MyExtensionHandler(ExtensionHandlerMixin, JupyterHandler):

        @tornado.web.authenticated
        def get(self):
            ...

        @tornado.web.authenticated
        def post(self):
            ...


Jinja templating from frontend extensions
-----------------------------------------

Many Jupyter frontend applications use Jinja for basic HTML templating. Since this is common enough, Jupyter Server provides some extra mixin that integrate Jinja with Jupyter server extensions.

Use ``ExtensionAppJinjaMixin`` to automatically add a Jinja templating environment to an ``ExtensionApp``. This adds a ``<name>_jinja2_env`` setting to Tornado Web Server's settings that will be used by request handlers.

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
    import tornado

    class MyExtensionHandler(
        ExtensionHandlerMixin,
        ExtensionHandlerJinjaMixin,
        JupyterHandler
    ):

        @tornado.web.authenticated
        def get(self):
            ...

        @tornado.web.authenticated
        def post(self):
            ...


.. note:: The mixin classes in this example must come before the base classes, ``ExtensionApp`` and ``ExtensionHandler``.


Making an ``ExtensionApp`` discoverable
---------------------------------------

To make an ``ExtensionApp`` discoverable by Jupyter Server, add the ``app`` key+value pair to the ``_jupyter_server_extension_points()`` function example above:

.. code-block:: python

    from myextension import MyExtensionApp


    def _jupyter_server_extension_points():
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

``ExtensionApp`` as a classic Notebook server extension
-------------------------------------------------------

An extension that extends ``ExtensionApp`` should still work with the old Tornado server from the classic Jupyter Notebook. The ``ExtensionApp`` class
provides a method, ``load_classic_server_extension``, that handles the extension initialization. Simply  define a ``load_jupyter_server_extension`` reference
pointing at the ``load_classic_server_extension`` method:

.. code-block:: python

    # This is typically defined in the root `__init__.py`
    # file of the extension package.
    load_jupyter_server_extension = MyExtensionApp.load_classic_server_extension


If the extension is enabled, the extension will be loaded when the server starts.


Distributing a server extension
===============================

Putting it all together, authors can distribute their extension following this steps:

1. Add a ``_jupyter_server_extension_points()`` function at the extension's root.
    This function should likely live in the ``__init__.py`` found at the root of the extension package. It will look something like this:

    .. code-block:: python

        # Found in the __init__.py of package

        def _jupyter_server_extension_points():
            return [
                {
                    "module": "myextension.app",
                    "app": MyExtensionApp
                }
            ]

2. Create an extension by writing a ``_load_jupyter_server_extension()`` function or subclassing ``ExtensionApp``.
    This is where the extension logic will live (i.e. custom extension handlers, config, etc). See the sections above for more information on how to create an extension.

3. Add the following JSON config file to the extension package.
    The file should be named after the extension (e.g. ``myextension.json``) and saved in a subdirectory of the package with the prefix: ``jupyter-config/jupyter_server_config.d/``. The extension package will have a similar structure to this example:

    .. code-block::

        myextension
        ├── myextension/
        │   ├── __init__.py
        │   └── app.py
        ├── jupyter-config/
        │   └── jupyter_server_config.d/
        │       └── myextension.json
        └── setup.py

    The contents of the JSON file will tell Jupyter Server to load the extension when a user installs the package:

    .. code-block:: json

        {
            "ServerApp": {
                "jpserver_extensions": {
                    "myextension": true
                }
            }
        }

    When the extension is installed, this JSON file will be copied to the ``jupyter_server_config.d`` directory found in one of `Jupyter's paths`_.

    Users can toggle the enabling/disableing of extension using the command:

    .. code-block:: console

        jupyter server disable myextension

    which will change the boolean value in the JSON file above.

4. Create a ``setup.py`` that automatically enables the extension.
    Add a few extra lines the extension package's ``setup`` function

    .. code-block:: python

        from setuptools import setup

        setup(
            name="myextension",
            ...
            include_package_data=True,
            data_files=[
                (
                    "etc/jupyter/jupyter_server_config.d",
                    ["jupyter-config/jupyter_server_config.d/myextension.json"]
                ),
            ]

        )




.. links

.. _`Jupyter's paths`: https://jupyter.readthedocs.io/en/latest/use/jupyter-directories.html


Migrating an extension to use Jupyter Server
============================================

If you're a developer of a `classic Notebook Server`_ extension, your extension should be able to work with *both* the classic notebook server and ``jupyter_server``.

There are a few key steps to make this happen:

1. Point Jupyter Server to the ``load_jupyter_server_extension`` function with a new reference name.
    The ``load_jupyter_server_extension`` function was the key to loading a server extension in the classic Notebook Server. Jupyter Server expects the name of this function to be prefixed with an underscore—i.e. ``_load_jupyter_server_extension``. You can easily achieve this by adding a reference to the old function name with the new name in the same module.

    .. code-block:: python

        def load_jupyter_server_extension(nb_server_app):
            ...

        # Reference the old function name with the new function name.

        _load_jupyter_server_extension = load_jupyter_server_extension

2. Add new data files to your extension package that enable it with Jupyter Server.
    This new file can go next to your classic notebook server data files. Create a new sub-directory, ``jupyter_server_config.d``, and add a new ``.json`` file there:

    .. raw:: html

        <pre>
        myextension
        ├── myextension/
        │   ├── __init__.py
        │   └── app.py
        ├── jupyter-config/
        │   └── jupyter_notebook_config.d/
        │       └── myextension.json
        │   <b>└── jupyter_server_config.d/</b>
        │       <b>└── myextension.json</b>
        └── setup.py
        </pre>

    The new ``.json`` file should look something like this (you'll notice the changes in the configured class and trait names):

    .. code-block:: json

        {
            "ServerApp": {
                "jpserver_extensions": {
                    "myextension": true
                }
            }
        }

    Update your extension package's ``setup.py`` so that the data-files are moved into the jupyter configuration directories when users download the package.

    .. code-block:: python

        from setuptools import setup

        setup(
            name="myextension",
            ...
            include_package_data=True,
            data_files=[
                (
                    "etc/jupyter/jupyter_server_config.d",
                    ["jupyter-config/jupyter_server_config.d/myextension.json"]
                ),
                (
                    "etc/jupyter/jupyter_notebook_config.d",
                    ["jupyter-config/jupyter_notebook_config.d/myextension.json"]
                ),
            ]

        )

3. (Optional) Point extension at the new favicon location.
    The favicons in the Jupyter Notebook have been moved to a new location in Jupyter Server. If your extension is using one of these icons, you'll want to add a set of redirect handlers this. (In ``ExtensionApp``, this is handled automatically).

    This usually means adding a chunk to your ``load_jupyter_server_extension`` function similar to this:

    .. code-block:: python

        def load_jupyter_server_extension(nb_server_app):

            web_app = nb_server_app.web_app
            host_pattern = '.*$'
            base_url = web_app.settings['base_url']

            # Add custom extensions handler.
            custom_handlers = [
                ...
            ]

            # Favicon redirects.
            favicon_redirects = [
                (
                    url_path_join(base_url, "/static/favicons/favicon.ico"),
                    RedirectHandler,
                    {"url": url_path_join(serverapp.base_url, "static/base/images/favicon.ico")
                ),
                (
                    url_path_join(base_url, "/static/favicons/favicon-busy-1.ico"),
                    RedirectHandler,
                    {"url": url_path_join(serverapp.base_url, "static/base/images/favicon-busy-1.ico")}
                ),
                (
                    url_path_join(base_url, "/static/favicons/favicon-busy-2.ico"),
                    RedirectHandler,
                    {"url": url_path_join(serverapp.base_url, "static/base/images/favicon-busy-2.ico")}
                ),
                (
                    url_path_join(base_url, "/static/favicons/favicon-busy-3.ico"),
                    RedirectHandler,
                    {"url": url_path_join(serverapp.base_url, "static/base/images/favicon-busy-3.ico")}
                ),
                (
                    url_path_join(base_url, "/static/favicons/favicon-file.ico"),
                    RedirectHandler,
                    {"url": url_path_join(serverapp.base_url, "static/base/images/favicon-file.ico")}
                ),
                (
                    url_path_join(base_url, "/static/favicons/favicon-notebook.ico"),
                    RedirectHandler,
                    {"url": url_path_join(serverapp.base_url, "static/base/images/favicon-notebook.ico")}
                ),
                (
                    url_path_join(base_url, "/static/favicons/favicon-terminal.ico"),
                    RedirectHandler,
                    {"url": url_path_join(serverapp.base_url, "static/base/images/favicon-terminal.ico")}
                ),
                (
                    url_path_join(base_url, "/static/logo/logo.png"),
                    RedirectHandler,
                    {"url": url_path_join(serverapp.base_url, "static/base/images/logo.png")}
                ),
            ]

            web_app.add_handlers(
                host_pattern,
                custom_handlers + favicon_redirects
            )


.. _`classic Notebook Server`: https://jupyter-notebook.readthedocs.io/en/stable/extending/handlers.html
