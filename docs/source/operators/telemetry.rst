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

.. note::
    This has not yet been implemented.

.. _below:
