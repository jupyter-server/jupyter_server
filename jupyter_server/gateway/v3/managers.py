"""Gateway kernel manager that integrates with our kernel monitoring system."""

import asyncio
from jupyter_server.gateway.managers import GatewayMappingKernelManager
from jupyter_server.gateway.managers import GatewayKernelManager as _GatewayKernelManager
from jupyter_server.gateway.managers import GatewayKernelClient as _GatewayKernelClient
from traitlets import default, Instance, Type

from jupyter_server.services.kernels.v3.client import JupyterServerKernelClientMixin


class GatewayKernelClient(JupyterServerKernelClientMixin, _GatewayKernelClient):
    """
    Gateway kernel client that combines our monitoring capabilities with gateway support.

    This client inherits from:
    - JupyterServerKernelClientMixin: Provides kernel monitoring capabilities, message caching,
      and execution state tracking that integrates with our kernel monitor system
    - GatewayKernelClient: Provides gateway communication capabilities for remote kernels

    The combination allows remote gateway kernels to be monitored with the same level of
    detail as local kernels, including heartbeat monitoring, execution state tracking,
    and kernel lifecycle management.
    """

    async def _test_kernel_communication(self, timeout: float = 10.0) -> bool:
        """Skip kernel_info test for gateway kernels.

        Gateway kernels handle communication differently and the kernel_info
        test can hang due to message routing differences.

        Returns:
            bool: Always returns True for gateway kernels
        """
        return True

    def _send_message(self, channel_name: str, msg: list[bytes]):
        # Send to gateway channel
        try:
            channel = getattr(self, f"{channel_name}_channel", None)
            if channel and hasattr(channel, 'send'):
                # Convert raw message to gateway format
                header = self.session.unpack(msg[0])
                parent_header = self.session.unpack(msg[1])
                metadata = self.session.unpack(msg[2])
                content = self.session.unpack(msg[3])

                full_msg = {
                    'header': header,
                    'parent_header': parent_header,
                    'metadata': metadata,
                    'content': content,
                    'buffers': msg[4:] if len(msg) > 4 else [],
                    'channel': channel_name,
                    'msg_id': header.get('msg_id'),
                    'msg_type': header.get('msg_type')
                }

                channel.send(full_msg)
        except Exception as e:
            self.log.warn(f"Error handling incoming message on gateway: {e}")

    async def _monitor_channel_messages(self, channel_name: str, channel):
        """Monitor a gateway channel for incoming messages."""
        try:
            while channel.is_alive():
                try:
                    # Get message from gateway channel queue
                    message = await channel.get_msg()

                    # Update execution state from status messages
                    # Gateway messages are already deserialized dicts
                    self._update_execution_state_from_status(
                        channel_name,
                        message,
                        parent_msg_id=message.get("parent_header", {}).get("msg_id"),
                        execution_state=message.get("content", {}).get("execution_state")
                    )

                    # Serialize message to standard format for listeners
                    # Gateway messages are dicts, convert to list[bytes] format
                    # session.serialize() returns: [b'<IDS|MSG>', signature, header, parent_header, metadata, content, buffers...]
                    serialized = self.session.serialize(message)

                    # Skip delimiter (index 0) and signature (index 1) to get [header, parent_header, metadata, content, ...]
                    if serialized and len(serialized) >= 6:  # Need delimiter + signature + 4 message parts
                        msg_list = serialized[2:]
                    else:
                        self.log.warning(f"Gateway message too short: {len(serialized) if serialized else 0} parts")
                        continue

                    # Route to listeners
                    await self._route_to_listeners(channel_name, msg_list)

                except asyncio.TimeoutError:
                    # No message available, continue loop
                    continue
                except Exception as e:
                    self.log.debug(f"Error processing gateway message in {channel_name}: {e}")
                    continue

                await asyncio.sleep(0.01)

        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.log.error(f"Gateway channel monitoring failed for {channel_name}: {e}")


class GatewayKernelManager(_GatewayKernelManager):
    """
    Gateway kernel manager that uses our enhanced gateway kernel client.

    This manager inherits from jupyter_server's GatewayKernelManager and configures it
    to use our GatewayKernelClient, which provides:

    - Gateway communication capabilities for remote kernels
    - Kernel monitoring integration (heartbeat, execution state tracking)
    - Message ID encoding with channel and src_id using simple string operations
    - Full compatibility with our kernel monitor extension
    - Pre-created kernel client instance stored as a property
    - Automatic client connection/disconnection on kernel start/shutdown

    When jupyter_server is configured to use a gateway, this manager ensures that
    remote kernels receive the same level of monitoring as local kernels.
    """
    # Configure the manager to use our enhanced gateway client
    client_class = GatewayKernelClient
    client_factory = GatewayKernelClient

    kernel_client = Instance(
        'jupyter_client.client.KernelClient',
        allow_none=True,
        help="""Pre-created kernel client instance. Created on initialization."""
    )

    def __init__(self, **kwargs):
        """Initialize the kernel manager and create a kernel client instance."""
        super().__init__(**kwargs)

        # Create a kernel client instance immediately
        self.kernel_client = self.client(session=self.session)

    async def post_start_kernel(self, **kwargs):
        """After kernel starts, connect the kernel client.

        This method is called after the kernel has been successfully started.
        It loads the latest connection info (with ports set by provisioner)
        and connects the kernel client to the kernel.

        Note: If you override this method, make sure to call super().post_start_kernel(**kwargs)
        to ensure the kernel client connects properly.
        """
        await super().post_start_kernel(**kwargs)

        try:
            # Load latest connection info from kernel manager
            # The provisioner has now set the real ports
            self.kernel_client.load_connection_info(self.get_connection_info(session=True))

            # Connect the kernel client
            success = await self.kernel_client.connect()

            if not success:
                raise RuntimeError(f"Failed to connect kernel client for kernel {self.kernel_id}")

            self.log.info(f"Successfully connected kernel client for kernel {self.kernel_id}")

        except Exception as e:
            self.log.error(f"Failed to connect kernel client: {e}")
            # Re-raise to fail the kernel start
            raise

    async def cleanup_resources(self, restart=False):
        """Cleanup resources, disconnecting the kernel client if not restarting.

        Parameters
        ----------
        restart : bool
            If True, the kernel is being restarted and we should keep the client
            connected but clear its state. If False, fully disconnect.
        """
        if self.kernel_client:
            if restart:
                # On restart, clear client state but keep connection
                # The connection will be refreshed in post_start_kernel after restart
                self.log.debug(f"Clearing kernel client state for restart of kernel {self.kernel_id}")
                self.kernel_client.last_shell_status_time = None
                self.kernel_client.last_control_status_time = None
                # Disconnect before restart - will reconnect after
                await self.kernel_client.stop_listening()
                self.kernel_client.stop_channels()
            else:
                # On shutdown, fully disconnect the client
                self.log.debug(f"Disconnecting kernel client for kernel {self.kernel_id}")
                await self.kernel_client.stop_listening()
                self.kernel_client.stop_channels()

        await super().cleanup_resources(restart=restart)


class GatewayMultiKernelManager(GatewayMappingKernelManager):
    """Custom kernel manager that uses enhanced monitoring kernel manager with v3 API."""

    @default("kernel_manager_class")
    def _default_kernel_manager_class(self):
        return "jupyter_server.gateway.v3.managers.GatewayKernelManager"

    def start_watching_activity(self, kernel_id):
        pass
    
    def stop_buffering(self, kernel_id):
        pass

