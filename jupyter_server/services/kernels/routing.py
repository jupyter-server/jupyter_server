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

    @default("info")
    def _default_info(self):
        all_infos = []
        if hasattr(self.primary_manager, "info"):
            all_infos.append(self.primary_manager.info)
        for additional_manager in self.additional_managers:
            if hasattr(additional_manager, "info"):
                all_infos.append(additional_manager.info)
        return "\n".join(all_infos)


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
    def primary_manager(self) -> AsyncMappingKernelManager:
        # This kernelspec manager can only be used when the corresponding kernel
        # manager can tell us how to route requests to the nested managers.
        assert self.parent is not None
        assert hasattr(self.parent.kernel_manager, "routing_provider")
        assert isinstance(self.parent.kernel_manager.routing_provider, RoutingProvider)

        km = self.parent.kernel_manager.routing_provider.primary_manager

        # On the odd chance that an administrator explicitly configured a routing
        # provider with a nested routing kernelspec manager, all attempts to list
        # or get kernelspecs will result in an infinite loop.
        #
        # Accordingly, we use an assert to catch this early.
        assert not isinstance(km.kernel_spec_manager, AsyncRoutingKernelSpecManager)

        return km

    @property
    def additional_managers(self):
        # This kernelspec manager can only be used when the corresponding kernel
        # manager can tell us how to route requests to the nested managers.
        assert self.parent is not None
        assert hasattr(self.parent.kernel_manager, "routing_provider")

        kms = self.parent.kernel_manager.routing_provider.additional_managers

        # Similarly to the `primary_manager` property, we want to ensure that
        # none of the nested kernelspec managers are instances of this same class,
        # in order to prevent infinite loops and to catch the configuration
        # issues that could cause such loops early.
        for km in kms:
            assert not isinstance(km.kernel_spec_manager, AsyncRoutingKernelSpecManager)

        return kms

    spec_to_manager_map = Dict(key_trait=Unicode(), value_trait=Instance(AsyncMappingKernelManager))

    async def get_all_specs(self):
        ksm = self.primary_manager.kernel_spec_manager
        assert ksm is not None
        ks = await ensure_async(ksm.get_all_specs())
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
        assert wrapped_manager is not None

        return await ensure_async(wrapped_manager.get_kernel_spec(kernel_name, **kwargs))

    async def get_kernel_spec_resource(self, kernel_name, path):
        wrapped_manager = self.get_mapping_kernel_manager(kernel_name).kernel_spec_manager
        assert wrapped_manager is not None

        if hasattr(wrapped_manager, "get_kernel_spec_resource"):
            return await ensure_async(wrapped_manager.get_kernel_spec_resource(kernel_name, path))
        return None


class RoutingKernelSpecManager(AsyncRoutingKernelSpecManager):
    """KernelSpecManager that routes to multiple nested kernel spec managers."""

    def get_all_specs(self):
        return run_sync(super().get_all_specs)()

    def get_kernel_spec(self, kernel_name, *args, **kwargs):
        return run_sync(super().get_kernel_spec)(kernel_name, *args, **kwargs)


class RoutingKernelManager(ServerKernelManager):
    kernel_id: t.Optional[str] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Enforce that our kernel_id is only set in the `start_kernel` method.
        self.kernel_id = None

    @property
    def wrapped_multi_kernel_manager(self):
        assert self.parent is not None
        return self.parent.kernel_spec_manager.get_mapping_kernel_manager(self.kernel_name)

    @property
    def wrapped_kernel_manager(self):
        if not self.kernel_id:
            return None
        return self.wrapped_multi_kernel_manager.get_kernel(self.kernel_id)

    def create_websocket_connection(self, websocket_handler, config=None):
        return self.wrapped_kernel_manager.create_websocket_connection(
            websocket_handler=websocket_handler, config=config
        )

    @property
    def session(self):
        return self.wrapped_kernel_manager.session

    @property
    def has_kernel(self):
        if not self.kernel_id:
            return False
        return self.wrapped_kernel_manager.has_kernel

    async def is_alive(self):
        if not self.has_kernel:
            return False
        return await self.wrapped_kernel_manager.is_alive()

    def client(self, *args, **kwargs):
        if not self.kernel_id:
            return None
        return self.wrapped_kernel_manager.client(*args, **kwargs)

    @in_pending_state
    async def start_kernel(self, *args, **kwargs):
        km = self.wrapped_multi_kernel_manager
        if isinstance(km, GatewayMappingKernelManager):
            kwargs.pop("kernel_id", None)
        self.kernel_id: str = await ensure_async(
            km.start_kernel(kernel_name=self.kernel_name, **kwargs)
        )
        self.log.debug(f"Created kernel {self.kernel_id} in {km}")

    async def shutdown_kernel(self, now=False, restart=False):
        km = self.wrapped_multi_kernel_manager
        await ensure_async(km.shutdown_kernel(self.kernel_id, now=now, restart=restart))

    async def restart_kernel(self, now=False):
        km = self.wrapped_multi_kernel_manager
        return await ensure_async(km.restart_kernel(self.kernel_id, now=now))

    async def interrupt_kernel(self):
        km = self.wrapped_kernel_manager
        return await ensure_async(km.interrupt_kernel())

    async def model(self):
        wrapped_model = await ensure_async(
            self.wrapped_multi_kernel_manager.kernel_model(self.kernel_id)
        )
        model = copy.deepcopy(wrapped_model)
        model["id"] = self.kernel_id
        return model


class RoutingMappingKernelManager(AsyncMappingKernelManager):
    # We have to completely override the kernel management from the super classes so that
    # we can effectively keep the set of kernels in sync with the nested managers.
    _kernels: dict[str, RoutingKernelManager]

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

    def remove_kernel(self, kernel_id):
        return self._kernels.pop(kernel_id, None)

    async def shutdown_kernel(self, kernel_id, now=False, restart=False):
        km = self.get_kernel(kernel_id)
        await ensure_async(km.shutdown_kernel(now=now, restart=restart))
        self.remove_kernel(kernel_id)
        return

    async def shutdown_all(self, now=False):
        kernels_to_shutdown = [kid for kid in self._kernels]
        self.log.debug(f"Shutting down the kernels {kernels_to_shutdown}...")
        for kid in kernels_to_shutdown:
            await self.shutdown_kernel(kid, now=now)
        return

    async def restart_kernel(self, kernel_id, now=False, **kwargs):
        km = self.get_kernel(kernel_id)
        return await km.restart_kernel(now=now, **kwargs)

    async def interrupt_kernel(self, kernel_id, **kwargs):
        km = self.get_kernel(kernel_id)
        return await km.interrupt_kernel()

    async def list_kernels(self):
        # We have might remote kernels, so we must call `list_kernels` on the
        # wrapped Gateway kernel managers to update our kernel models.
        updated_kernels = await ensure_async(self.routing_provider.primary_manager.list_kernels())
        try:
            for wrapped in self.routing_provider.additional_managers:
                updated_kernels.extend(await ensure_async(wrapped.list_kernels()))
        except Exception as ex:
            self.log.exception("Failure listing kernels: %s", ex)
            # Ignore the exception listing remote kernels, so that local kernels are still usable.
        self.log.debug(f"Updated kernels: {updated_kernels}...")
        updated_kernel_ids = [k.get("id", None) for k in updated_kernels]
        for kid in [kid for kid in self._kernels]:
            if kid not in updated_kernel_ids:
                # The kernel may have been culled by the nested manager
                self.log.debug(f"Kernel {kid} missing from the nested managers; possibly culled...")
                self._kernels.pop(kid, None)
        filtered_kernels = [
            kernel for kernel in updated_kernels if kernel.get("id", None) in self._kernels
        ]
        return filtered_kernels

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

    def _using_pending_kernels(self):
        return False

    async def start_kernel(self, kernel_name=None, kernel_id=None, **kwargs):
        km, kernel_name, _ = self.pre_start_kernel(kernel_name, kwargs)
        await km.start_kernel(kernel_id=kernel_id, **kwargs)
        self._kernels[km.kernel_id] = km
        return km.kernel_id

    @property
    def info(self):
        return self.routing_provider.info


KernelManagerABC.register(RoutingKernelManager)
