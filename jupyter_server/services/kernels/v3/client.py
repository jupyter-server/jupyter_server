import asyncio
import time
import typing as t
from datetime import datetime, timezone

from jupyter_client.asynchronous.client import AsyncKernelClient
from jupyter_client.channels import AsyncZMQSocketChannel
from jupyter_client.channelsabc import ChannelABC
from traitlets import HasTraits, Type

from .message_utils import encode_channel_in_message_dict, parse_msg_id
from .states import ExecutionStates


class NamedAsyncZMQSocketChannel(AsyncZMQSocketChannel):
    """Prepends the channel name to all message IDs to this socket."""

    channel_name = "unknown"

    def send(self, msg):
        """Send a message with automatic channel encoding."""
        msg = encode_channel_in_message_dict(msg, self.channel_name)
        return super().send(msg)


class ShellChannel(NamedAsyncZMQSocketChannel):
    """Shell channel that automatically encodes 'shell' in outgoing msg_ids."""

    channel_name = "shell"


class ControlChannel(NamedAsyncZMQSocketChannel):
    """Control channel that automatically encodes 'control' in outgoing msg_ids."""

    channel_name = "control"


class StdinChannel(NamedAsyncZMQSocketChannel):
    """Stdin channel that automatically encodes 'stdin' in outgoing msg_ids."""

    channel_name = "stdin"


class JupyterServerKernelClientMixin(HasTraits):
    """Mixin that enhances AsyncKernelClient with listener API, message queuing, and channel encoding.

    Key Features:

    1. **Listener API**: Register multiple listeners to receive kernel messages without blocking.
       - `add_listener()`: Add a callback function to receive messages from the kernel
       - `remove_listener()`: Remove a registered listener
       - Supports message filtering by type and channel
       - Multiple listeners can be registered (e.g., multiple WebSocket connections)

    2. **Message Queuing**: Queue messages that arrive before the kernel client is ready.
       - Messages from WebSockets are queued during kernel startup
       - Queued messages are processed once the kernel connection is established
       - Prevents message loss during the connection handshake
       - Configurable queue size to prevent memory issues

    3. **Channel Encoding**: Automatically encode channel names in all outgoing message IDs.
       - All messages sent through shell, control, or stdin channels get the channel name prepended
       - Format: `{channel}:{base_msg_id}` (e.g., "shell:abc123_456_0")
       - Makes it easy to identify which channel status messages came from
       - Enables proper execution state tracking (shell vs control channel responses)
       - Uses custom channel classes (ShellChannel, ControlChannel, StdinChannel)

    This mixin is designed to work with Jupyter Server's multi-websocket architecture where
    a single kernel client is shared across multiple WebSocket connections.
    """

    # Track kernel execution state (simplified - just a string)
    execution_state: str = ExecutionStates.UNKNOWN.value

    # Track kernel activity
    last_activity: datetime = None

    # Track last status message time per channel (shell and control)
    last_shell_status_time: datetime = None
    last_control_status_time: datetime = None

    # Connection test configuration
    connection_test_timeout: float = 120.0  # Total timeout for connection test in seconds
    connection_test_check_interval: float = 0.1  # How often to check for messages in seconds
    connection_test_retry_interval: float = (
        10.0  # How often to retry kernel_info requests in seconds
    )

    # Override channel classes to use our custom ones with automatic encoding
    shell_channel_class = Type(ShellChannel)
    control_channel_class = Type(ControlChannel)
    stdin_channel_class = Type(StdinChannel)

    # Set of listener functions - don't use Traitlets Set, just plain Python set
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._listeners = {}  # Maps callback -> filter config
        self._listening = False

        # Connection state tracking
        self._connecting = False
        self._connection_ready = False
        self._connection_ready_event = asyncio.Event()

        # Message queue for messages received before connection is ready
        self._queued_messages = []
        self._max_queue_size = 1000  # Prevent memory issues

        # Note: The session is already EncodedMsgIdSession, created by the KernelManager
        # No need to replace it here

    def add_listener(
        self,
        callback: t.Callable[[str, list[bytes]], None],
        msg_types: t.Optional[list[tuple[str, str]]] = None,
        exclude_msg_types: t.Optional[list[tuple[str, str]]] = None,
    ):
        """Add a listener to be called when messages are received.

        Args:
            callback: Function that takes (channel_name, msg_bytes) as arguments
            msg_types: Optional list of (msg_type, channel) tuples to include.
                      If provided, only messages matching these filters will be sent to the listener.
                      Example: [("status", "iopub"), ("execute_reply", "shell")]
            exclude_msg_types: Optional list of (msg_type, channel) tuples to exclude.
                              If provided, messages matching these filters will NOT be sent to the listener.
                              Example: [("status", "iopub")]

        Note:
            - If both msg_types and exclude_msg_types are provided, msg_types takes precedence
            - If neither is provided, all messages are sent (default behavior)
        """
        if msg_types is not None and exclude_msg_types is not None:
            raise ValueError("Cannot specify both msg_types and exclude_msg_types")

        # Store the listener with its filter configuration
        self._listeners[callback] = {
            "msg_types": set(msg_types) if msg_types else None,
            "exclude_msg_types": set(exclude_msg_types) if exclude_msg_types else None,
        }

    def remove_listener(self, callback: t.Callable[[str, list[bytes]], None]):
        """Remove a listener."""
        self._listeners.pop(callback, None)

    def mark_connection_ready(self):
        """Mark the connection as ready and process queued messages."""
        if not self._connection_ready:
            self._connecting = False
            self._connection_ready = True
            self._connection_ready_event.set()

            # Process queued messages
            asyncio.create_task(self._process_queued_messages())

    async def wait_for_connection_ready(self, timeout: float = 30.0) -> bool:
        """Wait for the connection to be ready."""
        try:
            await asyncio.wait_for(self._connection_ready_event.wait(), timeout=timeout)
            return True
        except asyncio.TimeoutError:
            return False

    async def _process_queued_messages(self):
        """Process all messages that were queued during startup."""
        self.log.info(f"Processing {len(self._queued_messages)} queued messages")

        queued_messages = self._queued_messages.copy()
        self._queued_messages.clear()

        for channel_name, msg in queued_messages:
            try:
                # Send queued messages to the kernel (these are incoming from websockets)
                self._send_message(channel_name, msg)
            except Exception as e:
                self.log.error(f"Error processing queued message: {e}")

    def _queue_message_if_not_ready(self, channel_name: str, msg: list[bytes]) -> bool:
        """Queue a message if connection is not ready. Returns True if queued."""
        if not self._connection_ready:
            if len(self._queued_messages) < self._max_queue_size:
                self._queued_messages.append((channel_name, msg))
                return True
            else:
                # Queue is full, drop oldest message
                self._queued_messages.pop(0)
                self._queued_messages.append((channel_name, msg))
                self.log.warning("Message queue full, dropping oldest message")
                return True
        return False

    def _send_message(self, channel_name: str, msg: list[bytes]):
        # Route message to the appropriate kernel channel
        try:
            channel = getattr(self, f"{channel_name}_channel", None)
            channel.session.send_raw(channel.socket, msg)

        except Exception:
            self.log.warn("Error handling incoming message.")

    def handle_incoming_message(self, channel_name: str, msg: list[bytes]):
        """Handle incoming kernel messages and encode channel in msg_id.

        This method processes incoming kernel messages from WebSocket clients.
        It prepends the channel name to the msg_id for internal routing.

        Args:
            channel_name: The channel the message came from ('shell', 'iopub', etc.)
            msg: The raw message bytes (already deserialized from websocket format)
        """
        # Validate message has content
        if not msg or len(msg) == 0:
            return

        # Prepend channel to msg_id for internal routing
        try:
            header = self.session.unpack(msg[0])
            msg_id = header["msg_id"]

            # Check if msg_id already has channel encoded
            if not msg_id.startswith(f"{channel_name}:"):
                # Prepend channel
                header["msg_id"] = f"{channel_name}:{msg_id}"
                msg[0] = self.session.pack(header)

        except Exception as e:
            self.log.debug(f"Error encoding channel in incoming message ID: {e}")

        # If connection is not ready, queue the message
        if self._queue_message_if_not_ready(channel_name, msg):
            return

        self._send_message(channel_name, msg)

    def handle_outgoing_message(self, channel_name: str, msg: list[bytes]):
        """Public API for manufacturing messages to send to kernel client listeners.

        This allows external code to simulate kernel messages and send them to all
        registered listeners, useful for testing and message injection.

        Args:
            channel_name: The channel the message came from ('shell', 'iopub', etc.)
            msg: The raw message bytes
        """
        # Same as handle_incoming_message - route to all listeners
        asyncio.create_task(self._route_to_listeners(channel_name, msg))

    async def _route_to_listeners(self, channel_name: str, msg: list[bytes]):
        """Route message to all registered listeners based on their filters."""
        if not self._listeners:
            return

        # Validate message format before routing
        if not msg or len(msg) < 4:
            self.log.warning(
                f"Cannot route malformed message on {channel_name}: {len(msg) if msg else 0} parts (expected at least 4)"
            )
            return

        # Extract message type for filtering
        msg_type = None
        try:
            header = self.session.unpack(msg[0]) if msg and len(msg) > 0 else {}
            msg_type = header.get("msg_type", "unknown")
        except Exception as e:
            self.log.debug(f"Error extracting message type: {e}")
            msg_type = "unknown"

        # Create tasks for listeners that match the filter
        tasks = []
        for listener, filter_config in self._listeners.items():
            if self._should_route_to_listener(msg_type, channel_name, filter_config):
                task = asyncio.create_task(self._call_listener(listener, channel_name, msg))
                tasks.append(task)

        # Wait for all listeners to complete
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    def _should_route_to_listener(
        self, msg_type: str, channel_name: str, filter_config: dict
    ) -> bool:
        """Determine if a message should be routed to a listener based on its filter configuration.

        Args:
            msg_type: The message type (e.g., "status", "execute_reply")
            channel_name: The channel name (e.g., "iopub", "shell")
            filter_config: Dictionary with 'msg_types' and 'exclude_msg_types' keys

        Returns:
            bool: True if the message should be routed to the listener, False otherwise
        """
        msg_types = filter_config.get("msg_types")
        exclude_msg_types = filter_config.get("exclude_msg_types")

        # If msg_types is specified (inclusion filter)
        if msg_types is not None:
            return (msg_type, channel_name) in msg_types

        # If exclude_msg_types is specified (exclusion filter)
        if exclude_msg_types is not None:
            return (msg_type, channel_name) not in exclude_msg_types

        # No filter specified - route all messages
        return True

    async def _call_listener(self, listener: t.Callable, channel_name: str, msg: list[bytes]):
        """Call a single listener, ensuring it's async and handling errors."""
        try:
            result = listener(channel_name, msg)
            if asyncio.iscoroutine(result):
                await result
        except Exception as e:
            self.log.error(f"Error in listener {listener}: {e}")

    def _update_execution_state_from_status(
        self,
        channel_name: str,
        msg_dict: dict,
        parent_msg_id: str = None,
        execution_state: str = None,
    ):
        """Update execution state from a status message if it originated from shell channel.

        This method checks if a status message on the iopub channel originated from a shell
        channel request before updating the execution state. This prevents control channel
        status messages from affecting execution state tracking.

        Additionally tracks the last time we received status messages from shell and control
        channels for connection monitoring purposes.

        Args:
            channel_name: The channel the message came from (should be 'iopub')
            msg_dict: The deserialized message dictionary
            parent_msg_id: Optional parent message ID (extracted if not provided)
            execution_state: Optional execution state (extracted if not provided)
        """
        if channel_name != "iopub" or msg_dict.get("msg_type") != "status":
            return

        try:
            # Extract parent_msg_id if not provided
            if parent_msg_id is None:
                parent_header = msg_dict.get("parent_header", {})
                if isinstance(parent_header, bytes):
                    parent_header = self.session.unpack(parent_header)
                parent_msg_id = parent_header.get("msg_id")

            # Parse parent_msg_id to extract channel
            if parent_msg_id:
                try:
                    parent_channel, _, _ = parse_msg_id(parent_msg_id)
                except Exception as e:
                    self.log.debug(f"Error parsing parent msg_id '{parent_msg_id}': {e}")
                    parent_channel = None

                # Track last status message time for both shell and control channels
                current_time = datetime.now(timezone.utc)
                if parent_channel == "shell":
                    self.last_shell_status_time = current_time
                    self.last_activity = current_time
                elif parent_channel == "control":
                    self.last_control_status_time = current_time

                # Only update execution state if message came from shell channel
                if parent_channel == "shell":
                    # Extract execution_state if not provided
                    if execution_state is None:
                        content = msg_dict.get("content", {})
                        if isinstance(content, bytes):
                            content = self.session.unpack(content)
                        execution_state = content.get("execution_state")

                    if execution_state:
                        old_state = self.execution_state
                        self.execution_state = execution_state
                        self.log.debug(f"Execution state: {old_state} -> {execution_state}")
                elif parent_channel is None:
                    # Log when we can't determine parent channel
                    if execution_state is None:
                        content = msg_dict.get("content", {})
                        if isinstance(content, bytes):
                            content = self.session.unpack(content)
                        execution_state = content.get("execution_state")
                    self.log.debug(
                        f"Ignoring status message - cannot parse parent channel (state would be: {execution_state})"
                    )
        except Exception as e:
            self.log.debug(f"Error updating execution state from status message: {e}")

    async def broadcast_state(self):
        """Broadcast current kernel execution state to all listeners.

        This method creates and sends a status message to all kernel listeners
        (typically WebSocket connections) to inform them of the current kernel
        execution state.

        The status message is manufactured using the session's message format
        and sent through the normal listener routing mechanism.

        Note: Only broadcasts if execution_state is a valid kernel protocol state.
        Skips broadcasting if state is "unknown" (not part of kernel protocol).
        """
        try:
            # Don't broadcast "unknown" state - it's not part of the kernel protocol
            # Valid states are: starting, idle, busy, restarting, dead
            if self.execution_state == ExecutionStates.UNKNOWN.value:
                self.log.debug("Skipping broadcast_state - execution state is unknown")
                return

            # Create status message
            msg_dict = self.session.msg("status", content={"execution_state": self.execution_state})

            # Serialize the message
            # session.serialize() returns:
            # [b'<IDS|MSG>', signature, header, parent_header, metadata, content, buffers...]
            serialized = self.session.serialize(msg_dict)

            # Skip delimiter (index 0) and signature (index 1) to get message parts
            # Result: [header, parent_header, metadata, content, buffers...]
            if len(serialized) < 6:  # Need delimiter + signature + 4 message parts minimum
                self.log.warning(
                    f"broadcast_state: serialized message too short: {len(serialized)} parts"
                )
                return

            msg_parts = serialized[2:]  # Skip delimiter and signature

            # Send to listeners
            self.handle_outgoing_message("iopub", msg_parts)

        except Exception as e:
            self.log.warning(f"Failed to broadcast state: {e}")

    async def start_listening(self):
        """Start listening for messages and monitoring channels."""
        # Start background tasks to monitor channels for messages
        self._monitoring_tasks = []
        self._listening = True

        # Monitor each channel for incoming messages
        for channel_name in ["iopub", "shell", "stdin", "control"]:
            channel = getattr(self, f"{channel_name}_channel", None)
            if channel and channel.is_alive():
                task = asyncio.create_task(self._monitor_channel_messages(channel_name, channel))
                self._monitoring_tasks.append(task)

        self.log.info(f"Started listening with {len(self._listeners)} listeners")

    async def stop_listening(self):
        """Stop listening for messages."""
        # Stop monitoring tasks
        if hasattr(self, "_monitoring_tasks"):
            for task in self._monitoring_tasks:
                task.cancel()
            self._monitoring_tasks = []

        self.log.info("Stopped listening")

    async def _monitor_channel_messages(self, channel_name: str, channel: ChannelABC):
        """Monitor a channel for incoming messages and route them to listeners."""
        try:
            while channel.is_alive():
                try:
                    # Check if there's a message ready (non-blocking)
                    has_message = await channel.msg_ready()
                    if has_message:
                        msg = await channel.socket.recv_multipart()

                        # For deserialization and state tracking, use feed_identities to strip routing frames
                        idents, msg_list = channel.session.feed_identities(msg)

                        # Deserialize WITHOUT content for performance (content=False)
                        msg_dict = channel.session.deserialize(msg_list, content=False)

                        # Update execution state from status messages
                        self._update_execution_state_from_status(channel_name, msg_dict)

                        # Route to listeners with msg_list
                        # After feed_identities, msg_list has format (delimiter already removed):
                        # [signature, header, parent_header, metadata, content, ...buffers]
                        # Skip signature (index 0) to get: [header, parent_header, metadata, content, ...buffers]
                        if msg_list and len(msg_list) >= 5:
                            await self._route_to_listeners(channel_name, msg_list[1:])
                        else:
                            self.log.warning(
                                f"Received malformed message on {channel_name}: {len(msg_list) if msg_list else 0} parts"
                            )

                except Exception as e:
                    # Log the error instead of silently ignoring it
                    self.log.debug(f"Error processing message in {channel_name}: {e}")
                    continue  # Continue with next message instead of breaking

                # Small sleep to avoid busy waiting
                await asyncio.sleep(0.01)

        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.log.error(f"Channel monitoring failed for {channel_name}: {e}")

    async def _test_kernel_communication(self, timeout: float = None) -> bool:
        """Test kernel communication by monitoring execution state and sending kernel_info requests.

        This method uses a robust heuristic to determine if the kernel is connected:
        1. Checks if execution state is 'idle' (indicates shell channel is responding)
        2. Sends kernel_info requests to both shell and control channels in parallel
        3. Monitors for status message responses from either channel
        4. Retries periodically if no response is received
        5. Considers kernel connected if we receive any status messages, even if state is 'busy'

        Args:
            timeout: Total timeout for connection test in seconds (uses connection_test_timeout if not provided)

        Returns:
            bool: True if communication test successful, False otherwise
        """
        if timeout is None:
            timeout = self.connection_test_timeout

        start_time = time.time()
        connection_attempt_time = datetime.now(timezone.utc)

        self.log.info("Starting kernel communication test")

        # Give the kernel a moment to be ready to receive messages
        # Heartbeat beating doesn't guarantee the kernel is ready for requests
        await asyncio.sleep(0.5)

        # Send initial kernel_info requests immediately
        try:
            await asyncio.gather(
                self._send_kernel_info_shell(),
                self._send_kernel_info_control(),
                return_exceptions=True,
            )
        except Exception as e:
            self.log.debug(f"Error sending initial kernel_info requests: {e}")

        last_kernel_info_time = time.time()

        while time.time() - start_time < timeout:
            elapsed = time.time() - start_time

            # Check if execution state is idle (shell channel responding and kernel ready)
            if self.execution_state == ExecutionStates.IDLE.value:
                self.log.info("Kernel communication test succeeded: execution state is idle")
                return True

            # Check if we've received any status messages since connection attempt
            # This indicates the kernel is connected, even if busy executing something
            if (
                self.last_shell_status_time
                and self.last_shell_status_time > connection_attempt_time
            ):
                self.log.info("Kernel communication test succeeded: received shell status message")
                return True

            if (
                self.last_control_status_time
                and self.last_control_status_time > connection_attempt_time
            ):
                self.log.info(
                    "Kernel communication test succeeded: received control status message"
                )
                return True

            # Send kernel_info requests at regular intervals
            time_since_last_request = time.time() - last_kernel_info_time
            if time_since_last_request >= self.connection_test_retry_interval:
                self.log.debug(
                    f"Sending kernel_info requests to shell and control channels (elapsed: {elapsed:.1f}s)"
                )

                try:
                    # Send kernel_info to both channels in parallel (no reply expected)
                    await asyncio.gather(
                        self._send_kernel_info_shell(),
                        self._send_kernel_info_control(),
                        return_exceptions=True,
                    )
                    last_kernel_info_time = time.time()
                except Exception as e:
                    self.log.debug(f"Error sending kernel_info requests: {e}")

            # Wait before next check
            await asyncio.sleep(self.connection_test_check_interval)

        self.log.error(f"Kernel communication test failed: no response after {timeout}s")
        return False

    async def _send_kernel_info_shell(self):
        """Send kernel_info request on shell channel (no reply expected)."""
        try:
            if hasattr(self, "kernel_info"):
                # Send without waiting for reply
                self.kernel_info()
        except Exception as e:
            self.log.debug(f"Error sending kernel_info on shell channel: {e}")

    async def _send_kernel_info_control(self):
        """Send kernel_info request on control channel (no reply expected)."""
        try:
            if hasattr(self.control_channel, "send"):
                msg = self.session.msg("kernel_info_request")
                # Channel wrapper will automatically encode channel in msg_id
                self.control_channel.send(msg)
        except Exception as e:
            self.log.debug(f"Error sending kernel_info on control channel: {e}")

    async def connect(self) -> bool:
        """Connect to the kernel and verify communication.

        This method:
        1. Starts all channels
        2. Begins listening for messages
        3. Waits for heartbeat to confirm connectivity
        4. Tests kernel communication with configurable retries
        5. Marks connection as ready

        Returns:
            bool: True if connection successful, False otherwise
        """
        if self._connecting:
            return await self.wait_for_connection_ready()

        if self._connection_ready:
            return True

        self._connecting = True

        try:
            self.execution_state = ExecutionStates.BUSY.value
            self.last_activity = datetime.now(timezone.utc)

            # Handle both sync and async versions of start_channels
            result = self.start_channels()
            if asyncio.iscoroutine(result):
                await result

            # Verify channels are running.
            assert self.channels_running

            # Start our listening
            await self.start_listening()

            # Unpause heartbeat channel if method exists
            if hasattr(self.hb_channel, "unpause"):
                self.hb_channel.unpause()

            # Wait for heartbeat
            attempt = 0
            max_attempts = 10
            while not self.hb_channel.is_beating():
                attempt += 1
                if attempt > max_attempts:
                    raise Exception("The kernel took too long to connect to the Kernel Sockets.")
                await asyncio.sleep(0.1)

            # Test kernel communication (handles retries internally)
            if not await self._test_kernel_communication():
                self.log.error(
                    f"Kernel communication test failed after {self.connection_test_timeout}s timeout"
                )
                return False

            # Mark connection as ready and process queued messages
            self.mark_connection_ready()

            # Update execution state to idle if it's not already set
            # (it might already be idle if we received a status message during connection test)
            if self.execution_state == ExecutionStates.BUSY.value:
                self.execution_state = ExecutionStates.IDLE.value
                self.last_activity = datetime.now(timezone.utc)

            self.log.info("Successfully connected to kernel")
            return True

        except Exception as e:
            self.log.error(f"Failed to connect to kernel: {e}")
            self._connecting = False
            return False

    async def disconnect(self):
        """Disconnect from the kernel and reset connection state.

        This method:
        1. Stops listening for messages
        2. Stops all channels
        3. Resets connection state flags
        4. Clears channel references

        Note: Does not remove listeners - they will be preserved for reconnection.
        """
        # Stop listening for messages
        await self.stop_listening()

        # Stop all channels
        self.stop_channels()

        # Reset connection state
        self._connecting = False
        self._connection_ready = False
        self._connection_ready_event.clear()

        # Clear channel references
        self._shell_channel = None
        self._iopub_channel = None
        self._stdin_channel = None
        self._control_channel = None
        self._hb_channel = None

        self.log.info("Disconnected from kernel")

    async def reconnect(self) -> bool:
        """Reconnect to the kernel.

        This is a convenience method that disconnects and then connects again.
        Useful for recovering from stale connections or network issues.

        Returns:
            bool: True if reconnection successful, False otherwise
        """
        self.log.info("Reconnecting to kernel...")
        await self.disconnect()
        return await self.connect()


class JupyterServerKernelClient(JupyterServerKernelClientMixin, AsyncKernelClient):
    """
    A kernel client with listener functionality and message queuing.
    """
