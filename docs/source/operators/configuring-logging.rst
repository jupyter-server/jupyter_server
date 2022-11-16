.. _configurable_logging:

Configuring Logging
===================

Jupyter Server (and Jupyter Server extension applications such as Jupyter Lab)
are Traitlets applications.

By default Traitlets applications log to stderr. You can configure them to log
to other locations e.g. log files.

Logging is configured via the ``logging_config`` "trait" which accepts a
:py:func:`logging.config.dictConfig` object. For more information look for
``Application.logging_config`` in :ref:`other-full-config`.


Examples
--------

.. _configurable_logging.jupyter_server:

Jupyter Server
^^^^^^^^^^^^^^

A minimal example which logs Jupyter Server output to a file:

.. code-block:: python

   c.ServerApp.logging_config = {
       'version': 1,
       'handlers': {
           'logfile': {
               'class': 'logging.FileHandler',
               'level': 'DEBUG',
               'filename': 'jupyter_server.log',
           },
       },
       'loggers': {
           'ServerApp': {
               'level': 'DEBUG',
               'handlers': ['console', 'logfile'],
           },
       },
   }

.. note::

   To keep the default behaviour of logging to stderr ensure the ``console``
   handler (provided by Traitlets) is included in the list of handlers.

.. warning::

   Be aware that the ``ServerApp`` log may contain security tokens. If
   redirecting to log files ensure they have appropriate permissions.


.. _configurable_logging.extension_applications:

Jupyter Server Extension Applications (e.g. Jupyter Lab)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

An example which logs both Jupyter Server and Jupyter Lab output to a file:

.. note::

   Because Jupyter Server and its extension applications are separate Traitlets
   applications their logging must be configured separately.

.. code-block:: python

   c.ServerApp.logging_config = {
       'version': 1,
       'handlers': {
           'logfile': {
               'class': 'logging.FileHandler',
               'level': 'DEBUG',
               'filename': 'jupyter_server.log',
               'formatter': 'my_format',
           },
       },
       'formatters': {
           'my_format': {
               'format': '%(asctime)s %(levelname)-8s %(name)-15s %(message)s',
               'datefmt': '%Y-%m-%d %H:%M:%S',
           },
       },
       'loggers': {
           'ServerApp': {
               'level': 'DEBUG',
               'handlers': ['console', 'logfile'],
           },
       },
   }

   c.LabApp.logging_config = {
       'version': 1,
       'handlers': {
           'logfile': {
               'class': 'logging.FileHandler',
               'level': 'DEBUG',
               'filename': 'jupyter_server.log',
               'formatter': 'my_format',
           },
       },
       'formatters': {
           'my_format': {
               'format': '%(asctime)s %(levelname)-8s %(name)-15s %(message)s',
               'datefmt': '%Y-%m-%d %H:%M:%S',
           },
       },
       'loggers': {
           'LabApp': {
               'level': 'DEBUG',
               'handlers': ['console', 'logfile'],
           },
       },
   }

.. note::

   The configured application name should match the logger name
   e.g. ``c.LabApp.logging_config`` defines a logger called ``LabApp``.

.. tip::

   This diff modifies the example to log Jupyter Server and Jupyter Lab output
   to different files:

   .. code-block:: diff

      --- before
      +++ after
       c.LabApp.logging_config = {
           'version': 1,
           'handlers': {
               'logfile': {
                   'class': 'logging.FileHandler',
                   'level': 'DEBUG',
      -            'filename': 'jupyter_server.log',
      +            'filename': 'jupyter_lab.log',
                   'formatter': 'my_format',
               },
           },
