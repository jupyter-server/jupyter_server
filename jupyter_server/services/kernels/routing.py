import copy
import typing as t

from jupyter_client.kernelspec import KernelSpecManager
from jupyter_client.manager import in_pending_state
from jupyter_client.managerabc import KernelManagerABC
from jupyter_core.utils import ensure_async, run_sync
from traitlets import (
    Dict,
    Instance,
    List,
    Type,
    Unicode,
    default,
    observe,
)
from traitlets.config import LoggingConfigurable

from jupyter_server.gateway.gateway_client import GatewayClient
from jupyter_server.gateway.managers import GatewayKernelSpecManager, GatewayMappingKernelManager
from jupyter_server.services.kernels.connection.base import BaseKernelWebsocketConnection
from jupyter_server.services.kernels.connection.channels import ZMQChannelsWebsocketConnection
from jupyter_server.services.kernels.kernelmanager import (
    AsyncMappingKernelManager,
    ServerKernelManager,
)
from jupyter_server.transutils import _i18n


class RoutingProvider(LoggingConfigurable):
    connection_dir = Unicode("")

    primary_manager = Instance(AsyncMappingKernelManager)

    additional_managers = List(trait=Instance(AsyncMappingKernelManager))

    @default("primary_manager")
    def _default_primary_manager(self):
        ksm = KernelSpecManager(parent=self.parent)
        return AsyncMappingKernelManager(
            parent=self.parent,
            log=self.log,
            connection_dir=self.connection_dir,
            kernel_spec_manager=ksm,
        )

    info = Unicode("")


class RemoteOnlyRoutingProvider(RoutingProvider):
    @default("primary_manager")
    def _default_primary_manager(self):
        ksm = GatewayKernelSpecManager(parent=self.parent)
        return GatewayMappingKernelManager(
            parent=self.parent,
            log=self.log,
            connection_dir=self.connection_dir,
            kernel_spec_manager=ksm,
        )

    @default("info")
    def _default_info(self):
        return (
            _i18n("\nKernels will be managed by the Gateway server running at:\n%s")
            % self.gateway_config.url
        )


class SideBySideRoutingProvider(RoutingProvider):
    @default("additional_managers")
    def _default_additional_managers(self):
        ksm = GatewayKernelSpecManager(parent=self.parent)
        return [
            GatewayMappingKernelManager(
                parent=self.parent,
                log=self.log,
                connection_dir=self.connection_dir,
                kernel_spec_manager=ksm,
            )
        ]


class AsyncRoutingKernelSpecManager(KernelSpecManager):
    """KernelSpecManager that routes to multiple nested kernel spec managers.

    This async version of the wrapper exists because the base KernelSpecManager
    class only has synchronous methods, but some child classes (in particular,
    GatewayKernelManager) change those methods to be async.

    In order to support both versions, we first implement the routing in this async
    class, but then make it synchronous in the child, RoutingKernelSpecManager class.
    """

    @property
    def primary_manager(self):
        if hasattr(self.parent.kernel_manager, "routing_provider"):
            return self.parent.kernel_manager.routing_provider.primary_manager

        # This happens if the server administrator configured just the kernel_manager_class
        # while leaving the kernel_spec_manager_class as the default.
        # In that case we want this class to just pass through to the kernel manager's
        # nested kernelspec manager.
        km = self.parent.kernel_manager

        # On the odd chance that an administrator explicitly configured a non
        # RoutingKernelManager with an instance of AsyncRoutingKernelSpecManager as
        # its nested `kernel_spec_manager`, all attempts to list or get kernelspecs
        # will result in an infinite loop.
        #
        # Accordingly, we use an assert to catch this early.
        assert not isinstance(km, AsyncRoutingKernelSpecManager)

        return km

    @property
    def additional_managers(self):
        if hasattr(self.parent.kernel_manager, "routing_provider"):
            return self.parent.kernel_manager.routing_provider.additional_managers
        return []

    spec_to_manager_map = Dict(key_trait=Unicode(), value_trait=Instance(AsyncMappingKernelManager))

    async def get_all_specs(self):
        ks = await ensure_async(self.primary_manager.kernel_spec_manager.get_all_specs())
        for spec_name, _spec in ks.items():
            self.spec_to_manager_map[spec_name] = self.primary_manager
        for additional_manager in self.additional_managers:
            additional_ks = await ensure_async(
                additional_manager.kernel_spec_manager.get_all_specs()
            )
            for spec_name, spec in additional_ks.items():
                if spec_name not in ks:
                    ks[spec_name] = spec
                    self.spec_to_manager_map[spec_name] = additional_manager
        return ks

    def get_mapping_kernel_manager(self, kernel_name: str) -> AsyncMappingKernelManager:
        km = self.spec_to_manager_map.get(kernel_name, None)
        if km is None:
            return self.primary_manager
        return km

    async def get_kernel_spec(self, kernel_name, **kwargs):
        wrapped_manager = self.get_mapping_kernel_manager(kernel_name).kernel_spec_manager
        return ensure_async(wrapped_manager.get_kernel_spec(kernel_name, **kwargs))

    async def get_kernel_spec_resource(self, kernel_name, path):
        wrapped_manager = self.get_mapping_kernel_manager(kernel_name).kernel_spec_manager
        if hasattr(wrapped_manager, "get_kernel_spec_resource"):
            return await ensure_async(wrapped_manager.get_kernel_spec_resource(kernel_name, path))
        return None

    def is_remote(self, kernel_name):
        wrapped_manager = self.get_mapping_kernel_manager(kernel_name).kernel_spec_manager
        return isinstance(wrapped_manager, GatewayKernelSpecManager)


class RoutingKernelSpecManager(AsyncRoutingKernelSpecManager):
    """KernelSpecManager that routes to multiple nested kernel spec managers."""

    def get_all_specs(self):
        return run_sync(super().get_all_specs)()

    def get_kernel_spec(self, kernel_name, *args, **kwargs):
        return run_sync(super().get_kernel_spec)(kernel_name, *args, **kwargs)


class RoutingKernelManagerWebsocketConnection(BaseKernelWebsocketConnection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        km = self.kernel_manager.wrapped_kernel_manager
        wrapped_class = ZMQChannelsWebsocketConnection
        if hasattr(km, "websocket_connection_class"):
            wrapped_class = km.websocket_connection_class
        self.wrapped = wrapped_class(
            parent=km, websocket_handler=self.websocket_handler, config=self.config
        )

    async def connect(self):
        """Connect the kernel websocket to the kernel ZMQ connections"""
        return await self.wrapped.connect()

    # N.B. The disconnect method in the BaseKernelWebsocketConnection is defined
    # to be async, but in all of the implementing subclasses it is sync, and
    # the Jupyter server does not await the value returned from this method.
    def disconnect(self):
        """Disconnect the kernel websocket from the kernel ZMQ connections"""
        return self.wrapped.disconnect()

    def handle_incoming_message(self, incoming_msg: str) -> None:
        """Broker the incoming websocket message to the appropriate ZMQ channel."""
        self.wrapped.handle_incoming_message(incoming_msg)

    def handle_outgoing_message(self, stream: str, outgoing_msg: list) -> None:
        """Broker outgoing ZMQ messages to the kernel websocket."""
        self.wrapped.handle_outgoing_message(stream, outgoing_msg)

    async def prepare(self):
        if hasattr(self.wrapped, "prepare"):
            return await self.wrapped.prepare()


class RoutingKernelManager(ServerKernelManager):
    kernel_id_map: dict[str, str] = {}

    @property
    def is_remote(self):
        if not self.kernel_name or not self.kernel_id:
            return False
        return self.parent.kernel_spec_manager.is_remote(self.kernel_name)

    @property
    def wrapped_multi_kernel_manager(self):
        return self.parent.kernel_spec_manager.get_mapping_kernel_manager(self.kernel_name)

    @property
    def wrapped_kernel_manager(self):
        if not self.kernel_id:
            return None
        wrapped_kernel_id = RoutingKernelManager.kernel_id_map.get(self.kernel_id, self.kernel_id)
        return self.wrapped_multi_kernel_manager.get_kernel(wrapped_kernel_id)

    @property
    def websocket_connection_class(self):
        return RoutingKernelManagerWebsocketConnection

    @property
    def has_kernel(self):
        if not self.kernel_id:
            return False
        return self.wrapped_kernel_manager.has_kernel

    def client(self, *args, **kwargs):
        if not self.kernel_id:
            return None
        return self.wrapped_kernel_manager.client(*args, **kwargs)

    @in_pending_state
    async def start_kernel(self, *args, **kwargs):
        kernel_id: t.Optional[str] = kwargs.pop("kernel_id", self.kernel_id)
        if kernel_id:
            self.kernel_id = kernel_id

        km = self.wrapped_multi_kernel_manager
        wrapped_kernel_id: str = await ensure_async(
            km.start_kernel(kernel_name=self.kernel_name, **kwargs)
        )
        self.kernel_id = self.kernel_id or wrapped_kernel_id
        RoutingKernelManager.kernel_id_map[self.kernel_id] = wrapped_kernel_id
        self.log.debug(
            f"Created kernel {self.kernel_id} corresponding to {wrapped_kernel_id} in {km}"
        )
        self.log.debug(RoutingKernelManager.kernel_id_map)

    async def shutdown_kernel(self, now=False, restart=False):
        wrapped_kernel_id = RoutingKernelManager.kernel_id_map.get(self.kernel_id, self.kernel_id)
        km = self.wrapped_multi_kernel_manager
        await ensure_async(km.shutdown_kernel(wrapped_kernel_id, now=now, restart=restart))
        RoutingKernelManager.kernel_id_map.pop(self.kernel_id, None)

    async def restart_kernel(self, now=False):
        wrapped_kernel_id = RoutingKernelManager.kernel_id_map.get(self.kernel_id, self.kernel_id)
        km = self.wrapped_multi_kernel_manager
        return await ensure_async(km.restart_kernel(wrapped_kernel_id, now=now))

    async def interrupt_kernel(self):
        km = self.wrapped_kernel_manager
        return await ensure_async(km.interrupt_kernel())

    async def model(self):
        wrapped_kernel_id = RoutingKernelManager.kernel_id_map.get(self.kernel_id, self.kernel_id)
        wrapped_model = await ensure_async(
            self.wrapped_multi_kernel_manager.kernel_model(wrapped_kernel_id)
        )
        model = copy.deepcopy(wrapped_model)
        model["id"] = self.kernel_id
        return model


class RoutingMappingKernelManager(AsyncMappingKernelManager):
    @default("kernel_manager_class")
    def _default_kernel_manager_class(self):
        return "jupyter_server.services.kernels.routing.RoutingKernelManager"

    kernel_spec_manager = Instance(
        "jupyter_server.services.kernels.routing.RoutingKernelSpecManager"
    )

    _routing_provider = None
    routing_provider_class = Type(
        klass=RoutingProvider,
        config=True,
        help=_i18n(
            "The class defining how kernelspec and kernel requests are routed "
            + "to the various supported managers."
        ),
    )

    @default("routing_provider_class")
    def _default_routing_provider_class(self):
        gateway_config = GatewayClient.instance(parent=self.parent)
        if gateway_config.gateway_enabled:
            return RemoteOnlyRoutingProvider
        return RoutingProvider

    @property
    def routing_provider(self):
        if not self._routing_provider:
            self._routing_provider = self.routing_provider_class(
                parent=self.parent, log=self.log, connection_dir=self.connection_dir
            )
        return self._routing_provider

    def has_remote_kernels(self):
        for kid in self._kernels:
            if self._kernels[kid].is_remote:
                return True
        return False

    async def list_kernels(self):
        if self.has_remote_kernels():
            # We have remote kernels, so we must call `list_kernels` on the
            # wrapped Gateway kernel managers to update our kernel models.
            try:
                await ensure_async(self.routing_provider.primary_manager.list_kernels())
                for wrapped in self.routing_provider.additional_managers:
                    await ensure_async(wrapped.list_kernels())
            except Exception as ex:
                self.log.exception("Failure listing kernels: %s", ex)
                # Ignore the exception listing remote kernels, so that local kernels are still usable.
        return super().list_kernels()

    def kernel_model(self, kernel_id):
        self._check_kernel_id(kernel_id)
        kernel = self._kernels[kernel_id]
        # Normally, calls to `run_sync` pose a danger of locking up Tornado's
        # single-threaded event loop.
        #
        # However, the call below should be fine because it cannot block for an
        # arbitrary amount of time.
        #
        # This call blocks on the `model` method defined below, which in turn
        # blocks on the `GatewayMappingKernelManager`'s `kernel_model` method
        # (https://github.com/jupyter-server/jupyter_server/blob/547f7a244d89f79dd09fa7d382322d1c40890a3f/jupyter_server/gateway/managers.py#L94).
        #
        # That will only take a small, deterministic amount of time to complete
        # because that `kernel_model` only operates on existing, in-memory data
        # and does not block on any outgoing network requests.
        return run_sync(kernel.model)()

    @property
    def info(self):
        return self.routing_provider.info


KernelManagerABC.register(RoutingKernelManager)
