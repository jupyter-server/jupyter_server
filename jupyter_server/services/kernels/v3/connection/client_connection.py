from tornado.websocket import WebSocketClosedError
from traitlets import List as TraitletsList, Tuple as TraitletsTuple
from jupyter_server.services.kernels.connection.base import (
    BaseKernelWebsocketConnection,
)
from jupyter_server.services.kernels.connection.base import deserialize_msg_from_ws_v1, serialize_msg_to_ws_v1
from jupyter_client.session import Session
from ..message_utils import encode_cell_id_in_message, strip_encoding_from_message


class KernelClientWebsocketConnection(BaseKernelWebsocketConnection):
    """WebSocket connection that bridges frontend clients to the shared kernel client.

    This class implements the WebSocket side of the shared kernel client architecture.
    Instead of creating its own ZMQ connections to the kernel, it registers as a listener
    on the kernel manager's shared kernel client and routes messages bidirectionally.

    Key Responsibilities:

    1. **Listener Registration**:
       - Registers itself as a message listener on the shared kernel client
       - Receives all kernel messages through the listener callback
       - Automatically removed when the WebSocket disconnects

    2. **Cell ID Encoding** (Outgoing to Kernel):
       - Extracts `cellId` from message metadata
       - Appends cell ID to message ID: `msg_id#{cell_id}`
       - Enables routing responses back to the originating cell
       - Works in conjunction with kernel client's channel encoding

    3. **Message ID Decoding** (Incoming from Kernel):
       - Strips both channel and cell ID encoding from message IDs
       - Returns messages to frontend with original msg_ids
       - Frontend receives messages in the format it expects

    4. **Message Filtering** (Configurable):
       - Supports filtering messages by type and channel
       - Can include specific message types (`msg_types` trait)
       - Can exclude specific message types (`exclude_msg_types` trait)
       - Reduces bandwidth for specialized clients
    """

    kernel_ws_protocol = "v1.kernel.websocket.jupyter.org"

    # Configurable message filtering traits
    msg_types = TraitletsList(
        trait=TraitletsTuple(),
        default_value=None,
        allow_none=True,
        config=True,
        help="""
        List of (msg_type, channel) tuples to include for this websocket connection.
        If None (default), all messages are sent. If specified, only messages matching
        these (msg_type, channel) pairs will be sent to the websocket.

        Example: [("status", "iopub"), ("execute_reply", "shell")]
        """
    )

    exclude_msg_types = TraitletsList(
        trait=TraitletsTuple(),
        default_value=None,
        allow_none=True,
        config=True,
        help="""
        List of (msg_type, channel) tuples to exclude for this websocket connection.
        If None (default), no messages are excluded. If specified, messages matching
        these (msg_type, channel) pairs will NOT be sent to the websocket.

        Example: [("status", "iopub")]

        Note: Cannot be used together with msg_types. If both are specified,
        msg_types takes precedence.
        """
    )

    def _get_kernel_client(self):
        """Get the kernel client directly from the kernel manager.

        The kernel client is now a property on the kernel manager itself,
        created immediately when the kernel manager is instantiated.

        Note: self.kernel_manager is actually the parent, which is the specific
        KernelManager instance for this kernel (not the MultiKernelManager).
        """
        try:
            # self.kernel_manager is the specific KernelManager for this kernel
            km = self.kernel_manager
            if not km:
                raise RuntimeError(f"No kernel manager found for kernel {self.kernel_id}")

            # Get the pre-created kernel client from the kernel manager
            if not hasattr(km, 'kernel_client') or km.kernel_client is None:
                raise RuntimeError(f"Kernel manager for {self.kernel_id} has no kernel_client")

            return km.kernel_client

        except Exception as e:
            raise RuntimeError(f"Failed to get kernel client for kernel {self.kernel_id}: {e}")

    async def connect(self):
        """Connect to the kernel via a kernel session with deferred channel connection.

        The client connection is now handled by the kernel manager in post_start_kernel().
        The websocket just needs to add itself as a listener to receive messages.
        """
        # Get the client from the kernel manager
        client = self._get_kernel_client()

        # Add websocket listener immediately (messages will be queued if not ready)
        # Use configured message filtering if specified
        if self.msg_types is not None:
            # Convert list of tuples to list for the API
            msg_types_list = [tuple(item) for item in self.msg_types] if self.msg_types else None
            client.add_listener(self.handle_outgoing_message, msg_types=msg_types_list)
        elif self.exclude_msg_types is not None:
            # Convert list of tuples to list for the API
            exclude_msg_types_list = [tuple(item) for item in self.exclude_msg_types] if self.exclude_msg_types else None
            client.add_listener(self.handle_outgoing_message, exclude_msg_types=exclude_msg_types_list)
        else:
            # No filtering - listen to all messages (default)
            client.add_listener(self.handle_outgoing_message)

        # Broadcast current kernel state to this websocket immediately
        # This ensures websockets that connect during/after restart get the current state
        await client.broadcast_state()

        self.log.info(f"Kernel websocket connected and listening for kernel {self.kernel_id}")

    def disconnect(self):
        """Disconnect the websocket from the kernel client."""
        try:
            # Get the kernel client from the kernel manager
            client = self._get_kernel_client()
            if client:
                # Remove this websocket's listener from the client
                client.remove_listener(self.handle_outgoing_message)
        except Exception as e:
            self.log.warning(f"Failed to disconnect websocket for kernel {self.kernel_id}: {e}")

    def handle_incoming_message(self, incoming_msg):
        """Handle incoming messages from WebSocket, encoding cellId into msg_id."""
        channel_name, msg_list = deserialize_msg_from_ws_v1(incoming_msg)

        try:
            # Get the kernel client from the kernel manager
            client = self._get_kernel_client()
            if not client:
                return

            # Extract cellId from metadata and encode into msg_id
            try:
                if len(msg_list) >= 3:  # Need header, parent_header, metadata
                    session = Session()
                    metadata = session.unpack(msg_list[2])
                    cell_id = metadata.get("cellId")

                    if cell_id:
                        msg_list = encode_cell_id_in_message(msg_list, cell_id)
            except Exception as e:
                self.log.debug(f"Error encoding cellId in msg_id: {e}")

            # Send to kernel client (which will prepend channel)
            client.handle_incoming_message(channel_name, msg_list)
        except Exception as e:
            self.log.error(f"Failed to handle incoming message for kernel {self.kernel_id}: {e}")

    def handle_outgoing_message(self, channel_name, msg):
        """Handle outgoing messages to WebSocket, stripping channel and cellId from msg_id."""
        try:
            # Validate message has minimum required parts
            if not msg or len(msg) < 4:
                self.log.warning(f"Message on {channel_name} has insufficient parts: {len(msg) if msg else 0}")
                return

            # Validate parts are bytes
            for i, part in enumerate(msg[:4]):
                if not isinstance(part, bytes):
                    self.log.error(f"Message part {i} on {channel_name} is not bytes: {type(part)}")
                    return

            # Strip channel and cellId from msg_ids before sending to frontend
            try:
                msg = strip_encoding_from_message(msg)
            except Exception as e:
                self.log.debug(f"Error stripping encoding from msg_ids: {e}")
                # Continue with original message if stripping fails

            # Serialize to websocket format and send
            bin_msg = serialize_msg_to_ws_v1(msg, channel_name)
            self.websocket_handler.write_message(bin_msg, binary=True)
        except WebSocketClosedError:
            self.log.warning("A Kernel Socket message arrived on a closed websocket channel.")
        except Exception as err:
            self.log.error(f"Error handling outgoing message on {channel_name}: {err}", exc_info=True)