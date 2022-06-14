.. _websocket_protocols:


Kernel Messages
===============

When a kernel is created or connected to via the `REST API
<https://petstore.swagger.io/?url=https://raw.githubusercontent.com/jupyter/jupyter_server/master/jupyter_server/services/api/api.yaml>`__,
the Jupyter server sets up a websocket to ZeroMQ bridge for communicating
between the browser and the kernel. When the server connects to a kernel, the
server sends a ``request_kernel_info`` messages to retrieve the kernel message
spec version the kernel implements. The server automatically adapts messages
from the kernel spec version the kernel implements to the kernel spec
implemented by the current version of jupyter_client installed.

Restarting or shutting down a kernel should be done with a REST request to the
server, not through a kernel message, so that the kernel manager can do the
appropriate logic around kernel shutdown, like asking the kernel to shut down
first through a kernel message, then forcefully shutting down the kernel if
there is no response.

Kernel messages
---------------

A websocket client connecting to a kernel through the Jupyter server websocket
bridge will use messages according to the Jupyter kernel message spec, with the
modifications noted below.

Kernel Message Specification Changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Message Channels**

The notebook server multiplexes all kernel message channels into a single
websocket channel and encodes the channel name in the websocket message wire
format (see below).

**Kernel Status**

The Jupyter server sends several additional `kernel status <https://jupyter-client.readthedocs.io/en/stable/messaging.html#kernel-status>`__ messages in addition
to the kernel status messages that are sent by the kernel itself:

1. When a kernel is restarted, an ``execution_state: 'restarting'`` kernel status message is sent.
2. When a kernel dies, an ``execution_state: 'dead'`` kernel status message is sent.

These status messages will have a different message header ``session`` value
than the message header session values in messages from the kernel.

.. note::

    As an implementation detail, the message header session value of these
    messages matches the `session_id` in the kernel connection URL.

.. note::

    In the classic notebook and JupyterLab client code, the websocket connection
    is closed when explicitly requesting a restart or shutdown, so the
    restarting and dead messages aren't received if it was requested by the
    user. In those cases, receiving a ``restarting`` or ``dead`` message from
    the notebook server means that the kernel had something happen to it, and
    the user should be explicitly notified.

**IOpub Message Rate Limits**

The notebook server inspects the messages coming from the kernel to the client
to rate-limit iopub messages. These rate limits can be raised.


Buffering
~~~~~~~~~

If all websocket clients have disconnected from a kernel, the notebook server
will temporarily buffer messages from the kernel to be delivered to the first
websocket client that connects to the kernel.



.. note::

    In the classic notebook client and JupyterLab, requesting a kernel restart
    immediately closes all websocket connections to the kernel, so kernel
    buffering starts. When a new websocket connection is created connecting to
    the kernel, the notebook server transmits all of the messages buffered from
    the kernel. For the IPython kernel, this means the new websocket connection
    will start with receiving status busy, shutdown_reply, and status idle
    messages on the iopub channel from before the restart.

.. note::

    TODO
    
    Document the session URL parameter used in kernel connections. Is that
    created every time we request a kernel with a post request? Is it tied to
    just creating new sessions with the session rest api?


Wire protocol
-------------

Jupyter Server translates messages between the ZeroMQ channels connected to a
kernel and the websocket connection to the browser. The wire formats for these
messages is as follows.

ZeroMQ wire protocol
~~~~~~~~~~~~~~~~~~~~

The kernel wire protocol over ZeroMQ takes advantage of multipart messages,
allowing to decompose a message into parts and to send and receive them
unmerged. The following table shows the message format (the beginning has been
omitted for clarity):

.. list-table:: Format of a kernel message over ZeroMQ socket (indices refer to parts, not bytes)
   :header-rows: 1

   * - ...
     - 0
     - 1
     - 2
     - 3
     - 4
     - 5
     - ...
   * - ...
     - header
     - parent_header
     - metadata
     - content
     - buffer_0
     - buffer_1
     - ...

See also the `Jupyter Client documentation <https://jupyter-client.readthedocs.io/en/stable/messaging.html#the-wire-protocol>`_.

Note that a set of ZeroMQ sockets, one for each channel (shell, iopub, etc.), are multiplexed into one WebSocket. Thus, the channel name must be encoded in WebSocket messages.

WebSocket protocol negotiation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When opening a WebSocket, the Jupyter web application can optionally provide a list of subprotocols it supports (see e.g. the `MDN documentation <https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_servers#subprotocols>`_). If nothing is provided (empty list), then the Jupyter Server assumes the default protocol will be used. Otherwise, the Jupyter Server must select one of the provided subprotocols, or none of them. If none of them is selected, the Jupyter Server must reply with an empty string, which means that the default protocol will be used.

Default WebSocket protocol
~~~~~~~~~~~~~~~~~~~~~~~~~~

The Jupyter Server must support the default protocol, in which a kernel message is serialized over WebSocket as follows:

.. list-table:: Format of a kernel message over WebSocket (indices refer to bytes)
   :header-rows: 1

   * - 0
     - 4
     - 8
     - ...
     - offset_0
     - offset_1
     - offset_2
     - ...
   * - offset_0
     - offset_1
     - offset_2
     - ...
     - msg
     - buffer_0
     - buffer_1
     - ...

Where:

* ``offset_0`` is the position of the kernel message (``msg``) from the beginning of this message, in bytes.
* ``offset_1`` is the position of the first binary buffer (``buffer_0``) from the beginning of this message, in bytes (optional).
* ``offset_2`` is the position of the second binary buffer (``buffer_1``) from the beginning of this message, in bytes (optional).
* ``msg`` is the kernel message, excluding binary buffers and including the channel name, as a UTF8-encoded stringified JSON.
* ``buffer_0`` is the first binary buffer (optional).
* ``buffer_1`` is the second binary buffer (optional).

The message can be deserialized by parsing ``msg`` as a JSON object (after decoding it to a string):

.. code-block:: python

    msg = {
        'channel': channel,
        'header': header,
        'parent_header': parent_header,
        'metadata': metadata,
        'content': content
    }

Then retrieving the channel name, and updating with the buffers, if any:

.. code-block:: python

    buffers = {
        [
            buffer_0,
            buffer_1
            # ...
        ]
    }

``v1.kernel.websocket.jupyter.org`` protocol
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Jupyter Server can optionally support the ``v1.kernel.websocket.jupyter.org`` protocol, in which a kernel message is serialized over WebSocket as follows:

.. list-table:: Format of a kernel message over WebSocket (indices refer to bytes)
   :header-rows: 1

   * - 0
     - 8
     - 16
     - ...
     - 8*offset_number
     - offset_0
     - offset_1
     - offset_2
     - offset_3
     - offset_4
     - offset_5
     - offset_6
     - ...
   * - offset_number
     - offset_0
     - offset_1
     - ...
     - offset_n
     - channel
     - header
     - parent_header
     - metadata
     - content
     - buffer_0
     - buffer_1
     - ...

Where:

* ``offset_number`` is a 64-bit (little endian) unsigned integer.
* ``offset_0`` to ``offset_n`` are 64-bit (little endian) unsigned integers (with ``n=offset_number-1``).
* ``channel`` is a UTF-8 encoded string containing the channel for the message (shell, iopub, etc.).
* ``header``, ``parent_header``, ``metadata``, and ``content`` are UTF-8 encoded JSON text representing the given part of a message in the Jupyter message protocol.
* ``offset_n`` is the number of bytes in the message.
* The message can be deserialized from the ``bin_msg`` serialized message as follows (Python code):

.. code-block:: python

    import json
    channel = bin_msg[offset_0:offset_1].decode('utf-8')
    header = json.loads(bin_msg[offset_1:offset_2])
    parent_header = json.loads(bin_msg[offset_2:offset_3])
    metadata = json.loads(bin_msg[offset_3:offset_4])
    content = json.loads(bin_msg[offset_4:offset_5])
    buffer_0 = bin_msg[offset_5:offset_6]
    buffer_1 = bin_msg[offset_6:offset_7]
    # ...
    last_buffer = bin_msg[offset_n_minus_1:offset_n]
