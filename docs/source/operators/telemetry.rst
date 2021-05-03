Eventlogging and Telemetry
==========================

Jupyter Server can be configured to record structured events from a running server using Jupyter's `Telemetry System`_. The types of events that Jupyter Server emits are defined by `JSON schemas`_ listed below_ emitted as JSON data, defined and validated by the JSON schemas listed below.


.. _logging: https://docs.python.org/3/library/logging.html
.. _`Telemetry System`: https://github.com/jupyter/telemetry
.. _`JSON schemas`: https://json-schema.org/

.. warning::
    Do NOT rely on this feature for security or auditing purposes. Neither `server <#emitting-server-events>`_ nor `client <#the-eventlog-endpoint>`_ events are protected against meddling. For server events, those who have access to the environment can change the server code to emit whatever they want. The same goes for client events where nothing prevents users from sending spurious data to the `eventlog` endpoint.

Emitting server events
----------------------

Event logging is handled by its ``Eventlog`` object. This leverages Python's standing logging_ library to emit, filter, and collect event data.

To begin recording events, you'll need to set two configurations:

    1. ``handlers``: tells the EventLog *where* to route your events. This trait is a list of Python logging handlers that route events to
    2. ``allows_schemas``: tells the EventLog *which* events should be recorded. No events are emitted by default; all recorded events must be listed here.

Here's a basic example for emitting events from the `contents` service:

.. code-block::

    import logging

    c.EventLog.handlers = [
        logging.FileHandler('event.log'),
    ]

    c.EventLog.allowed_schemas = [
        'hub.jupyter.org/server-action'
    ]

The output is a file, ``"event.log"``, with events recorded as JSON data.

Server event schemas
--------------------

.. toctree::
   :maxdepth: 2

   events/index

The ``eventlog`` endpoint
-------------------------

Jupyter Server provides a public REST endpoint for external applications to validate and log events
through the Server's Event Log.

To log events, send a `POST` request to the `/api/eventlog` endpoint. The body of the request should be a
JSON blog and is required to have the follow keys:

    1. `'schema'` : the event's schema ID.
    2. `'version'` : the version of the event's schema.
    3. `'event'` : the event data in JSON format.

Events that are validated by this endpoint must have their schema listed in the `allowed_schemas` trait listed above.

.. _below:

Register client event schemas
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``jupyter_server`` looks for locations of schema files provided by external packages by looking into the ``jupyter_telemetry`` entry point and then loads the files using the ``importlib.resources`` standard library.

For example, suppose there is a ``client_events`` package which wants to send events with schemas ``schema1.yaml``, ``schema2.yaml`` and ``extra_schema.yaml`` to the ``eventlog`` endpoint and has the following package structure:

.. code-block:: text

    client_events/
        __init__.py
        schemas/
            __init__.py
            schema1.yaml
            schema2.yaml
        extras/
            __init__.py
            extra_schema.yaml

``schema1.yaml`` and ``schema2.yaml`` are resources under ``client_events.schemas`` and ``extra_schema.yaml`` under ``client_events.extras``. To make these schemas discoverable by ``jupyter_server``, create an entry point under the ``jupyter_telemetry`` group which resolves to a list containing their locations, in this case ``['client_events.schemas', 'client_events.extras']``:

In :file:`setup.cfg`

.. code-block:: yaml

    [options.entry_points]
    jupyter_telemetry =
        my-event-entry-point = client_events:JUPYTER_TELEMETRY_SCHEMAS

In :file:`client_events/__init__.py`

.. code-block:: python

    JUPYTER_TELEMETRY_SCHEMAS = ['client_events.schemas', 'client_events.extras']
