Authoring a configurable, server extension application
======================================================

Jupyter Server offers a base class, ``ExtensionApp``, for authoring configurable Jupyter Server extensions. This class handles most of the boilerplate code for setting up config, CLI, and registration with Jupyter Server.

Writing an extension application
--------------------------------

Jupyter Server provides two key classes for writing a server extension: i) ``ExtensionApp`` and ii) ``ExtensionHandlerMixin``

The ExtensionApp:

    - can have traits.
    - is configurable (from file or CLI)
    - creates a namespace for a extension's static files under ``/static/<extension_name>/``.
    - loads itself as a server extension beside other Jupyter frontends and extensions.
    - provides a command-line interface to launch the frontend extension directly (starting a server along the way).

To create a new Jupyter extension application, subclass the ``ExtensionApp`` like the example below:

.. code-block:: python

    from jupyter_server.extension.application import ExtensionApp


    class MyFrontend(ExtensionApp):

        # -------------- Required traits --------------
        name = 'myfrontend'
        default_url = 'myfrontend'
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
            self.settings.update({'myfrontend_jinja2_env': ...})

The ``ExtensionApp`` uses the following methods and properties to connect your extension to the Jupyter server. Overwrite these pieces to add your custom settings, handlers and templates:

Methods

* ``initialize_setting()``: adds custom settings to the Tornado Web Application.
* ``initialize_handlers()``: appends handlers to the Tornado Web Application.
* ``initialize_templates()``: initialize the templating engine (e.g. jinja2) for your frontend.

Properties

* ``name``: the name of the extension
* ``default_url``: the url that your extension will serve its homepage.
* ``load_other_extensions``: should your extension expose other server extensions when launched directly?


Writing handlers for an extension
---------------------------------

To write handlers for an ``ExtensionApp``, use the ``ExtensionHandlerMixin`` and ``JupyterHandler`` classes. The former class routes Tornado's ``static_url`` attribute to the ``/static/<extension_name>/`` namespace where your extension's static files will be served. The latter class provides Jupyter Server's auth methods and other handler settings.

.. code-block:: python

    from jupyter_server.extension.handler import ExtensionHandlerMixin

    class MyFrontendHandler(ExtensionHandlerMixin, JupyterHandler):

        urls = ['/myfrontend/hello']

        def get(self):
            ...

        def post(self):
            ...

ExtensionHandlerMixin comes with the following properties:

* ``config``: the ExtensionApp's config object.
* ``server_config``: the ServerApp's config object.
* ``extension_name``: the name of the extension to which this handler is linked.
* ``static_url()``: a method for getting the url to static files (prefixed with ``/static/<extension_name>``).

Launching the application
-------------------------

To launch the application, simply call the ``ExtensionApp``'s ``launch_instance`` method.

.. code-block:: python

    main = MyFrontend.launch_instance
    main()


To make your frontend executable from anywhere on your system, added this method as an entry-point in your application's ``setup.py``:

.. code-block:: python

    from setuptools import setup


    setup(
        name='myfrontend',
        ...
        entry_points={
            'console_scripts': [
                'jupyter-myfrontend = myfrontend.app:main'
            ]
        }
    )

Examples
--------

You can check some simple example on the `GitHub jupyter_server repository
<https://github.com/jupyter/jupyter_server/tree/master/examples/simple>`_.

Extension Repositories
----------------------

We invite developers to tag the extension repositories with ``jupyter-server-extension``.
