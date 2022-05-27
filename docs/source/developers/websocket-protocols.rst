.. _websocket_protocols:

WebSocket kernel wire protocols
===============================

The Jupyter Server needs to pass messages between kernels and the Jupyter web application. Kernels use ZeroMQ sockets, and the web application uses a WebSocket.

ZeroMQ wire protocol
--------------------

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
------------------------------

When opening a WebSocket, the Jupyter web application can optionally provide a list of subprotocols it supports (see e.g. the `MDN documentation <https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_servers#subprotocols>`_). If nothing is provided (empty list), then the Jupyter Server assumes the default protocol will be used. Otherwise, the Jupyter Server must select one of the provided subprotocols, or none of them. If none of them is selected, the Jupyter Server must reply with an empty string, which means that the default protocol will be used.

Default WebSocket protocol
--------------------------

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
--------------------------------------------

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
