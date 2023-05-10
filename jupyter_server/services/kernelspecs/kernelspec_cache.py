"""Cache handling for kernel specs."""
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.


import os
import sys
from abc import ABC, ABCMeta, abstractmethod
from typing import Dict, Optional, Union

# See compatibility note on `group` keyword in https://docs.python.org/3/library/importlib.metadata.html#entry-points
if sys.version_info < (3, 10):  # pragma: no cover
    from importlib_metadata import EntryPoint, entry_points
else:  # pragma: no cover
    from importlib.metadata import EntryPoint, entry_points

from jupyter_client.kernelspec import KernelSpec
from traitlets.config import LoggingConfigurable
from traitlets.traitlets import CBool, Instance, Unicode, default

from jupyter_server.utils import ensure_async

# Simplify the typing.  Cache items are essentially dictionaries of strings
# to either strings or dictionaries.  The items themselves are indexed by
# the kernel_name (case-insensitive).
CacheItemType = Dict[str, Union[str, Dict]]


class KernelSpecCache(LoggingConfigurable):
    """The primary (singleton) instance for managing KernelSpecs.

    This class contains the configured KernelSpecManager instance upon
    which it uses to populate the cache (when enabled) or as a pass-thru
    (when disabled).

    Note that the KernelSpecManager returns different formats from methods
    get_all_specs() and get_kernel_spec().  The format in which cache entries
    are stored is that of the get_all_specs() results.  As a result, some
    conversion between formats is necessary, depending on which method is called.
    """

    cache_enabled_env = "JUPYTER_KERNELSPEC_CACHE_ENABLED"
    cache_enabled = CBool(
        config=True,
        help="""Enable Kernel Specification caching. (JUPYTER_KERNELSPEC_CACHE_ENABLED env var)""",
    )

    @default("cache_enabled")
    def _cache_enabled_default(self):
        return os.getenv(self.cache_enabled_env, "false").lower() in ("true", "1")

    kernel_spec_manager = Instance("jupyter_client.kernelspec.KernelSpecManager")

    monitor_entry_point = Unicode(
        help="""The monitor entry_point to use to capture kernelspecs updates.""",
    ).tag(config=True)

    @default("monitor_entry_point")
    def _monitor_entry_point_default(self):
        return "polling-monitor"

    # The kernelspec cache consists of a dictionary mapping the kernel name to the actual
    # kernelspec data (CacheItemType).
    cache_items: Dict = {}
    cache_misses: int = 0

    def __init__(self, kernel_spec_manager, **kwargs) -> None:
        """Initialize the cache."""
        super().__init__(**kwargs)
        self.kernel_spec_manager = kernel_spec_manager
        self.kernel_spec_monitor = None
        if self.cache_enabled:
            # Remove configurable traits that have no bearing on monitors
            kwargs.pop("cache_enabled", None)
            kwargs.pop("monitor_entry_point", None)
            self.kernel_spec_monitor = KernelSpecMonitorBase.create_instance(self, **kwargs)

    async def get_kernel_spec(self, kernel_name: str) -> KernelSpec:
        """Get the named kernel specification.

        This method is equivalent to calling KernelSpecManager.get_kernel_spec().  If
        caching is enabled, it will pull the item from the cache.  If no item is
        returned (as will be the case if caching is disabled) it will defer to the
        currently configured KernelSpecManager.  If an item is returned (and caching
        is enabled), it will be added to the cache.
        """
        kernelspec = self.get_item(kernel_name)
        if not kernelspec:
            kernelspec = await ensure_async(self.kernel_spec_manager.get_kernel_spec(kernel_name))
            if kernelspec:
                self.put_item(kernel_name, kernelspec)
        return kernelspec

    async def get_all_specs(self) -> Dict[str, CacheItemType]:
        """Get all available kernel specifications.

        This method is equivalent to calling KernelSpecManager.get_all_specs().  If
        caching is enabled, it will pull all items from the cache.  If no items are
        returned (as will be the case if caching is disabled) it will defer to the
        currently configured KernelSpecManager.  If items are returned (and caching
        is enabled), they will be added to the cache.

        Note that the return type of this method is not a dictionary or list of
        KernelSpec instances, but rather a dictionary of kernel-name to kernel-info
        dictionaries are returned - as is the case with the respective return values
        of the KernelSpecManager methods.
        """
        kernelspecs = self.get_all_items()
        if not kernelspecs:
            kernelspecs = await ensure_async(self.kernel_spec_manager.get_all_specs())
            if kernelspecs:
                self.put_all_items(kernelspecs)
        return kernelspecs

    # Cache-related methods
    def get_item(self, kernel_name: str) -> Optional[KernelSpec]:
        """Retrieves a named kernel specification from the cache.

        If cache is disabled or the item is not in the cache, None is returned;
        otherwise, a KernelSpec instance of the item is returned.
        """
        kernelspec = None
        if self.cache_enabled:
            cache_item = self.cache_items.get(kernel_name.lower())
            if cache_item:  # Convert to KernelSpec
                # In certain conditions, like when the kernelspec is fetched prior to its removal from the cache,
                # we can encounter a FileNotFoundError.  In those cases, treat as a cache miss as well.
                try:
                    kernelspec = KernelSpecCache.cache_item_to_kernel_spec(cache_item)
                except FileNotFoundError:
                    pass
            if not kernelspec:
                self.cache_misses += 1
                self.log.debug(
                    "Cache miss ({misses}) for kernelspec: {kernel_name}".format(
                        misses=self.cache_misses, kernel_name=kernel_name
                    )
                )
        return kernelspec

    def get_all_items(self) -> Dict[str, CacheItemType]:
        """Retrieves all kernel specification from the cache.

        If cache is disabled or no items are in the cache, an empty dictionary is returned;
        otherwise, a dictionary of kernel-name to specifications (kernel infos) are returned.
        """
        items = {}
        if self.cache_enabled:
            for kernel_name in self.cache_items:
                cache_item = self.cache_items.get(kernel_name)
                items[kernel_name] = cache_item
            if not items:
                self.cache_misses += 1
        return items

    def put_item(self, kernel_name: str, cache_item: Union[KernelSpec, CacheItemType]) -> None:
        """Adds or updates a kernel specification in the cache.

        This method can take either a KernelSpec (if called directly from the `get_kernel_spec()`
        method, or a CacheItemItem (if called from a cache-related method) as that is the type
        in which the cache items are stored.
        """
        if self.cache_enabled:
            self.log.info(f"KernelSpecCache: adding/updating kernelspec: {kernel_name}")
            if type(cache_item) is KernelSpec:
                cache_item = KernelSpecCache.kernel_spec_to_cache_item(cache_item)
            self.cache_items[kernel_name.lower()] = cache_item

    def put_all_items(self, kernelspecs: Dict[str, CacheItemType]) -> None:
        """Adds or updates a dictionary of kernel specification in the cache."""
        for kernel_name, cache_item in kernelspecs.items():
            self.put_item(kernel_name, cache_item)

    def remove_item(self, kernel_name: str) -> Optional[CacheItemType]:
        """Removes the cache item corresponding to kernel_name from the cache."""
        cache_item = None
        if self.cache_enabled and kernel_name.lower() in self.cache_items:
            cache_item = self.cache_items.pop(kernel_name.lower())
            self.log.info(f"KernelSpecCache: removed kernelspec: {kernel_name}")
        return cache_item

    def remove_all_items(self) -> None:
        """Removes all items from the cache."""
        if self.cache_enabled:
            self.cache_items.clear()
            self.log.info("KernelSpecCache: all items removed from cache")

    @staticmethod
    def kernel_spec_to_cache_item(kernelspec: KernelSpec) -> CacheItemType:
        """Converts a KernelSpec instance to a CacheItemType for storage into the cache."""
        cache_item = {"spec": kernelspec.to_dict(), "resource_dir": kernelspec.resource_dir}
        return cache_item

    @staticmethod
    def cache_item_to_kernel_spec(cache_item: CacheItemType) -> KernelSpec:
        """Converts a CacheItemType to a KernelSpec instance for user consumption."""
        kernel_spec = KernelSpec(resource_dir=cache_item["resource_dir"], **cache_item["spec"])
        return kernel_spec


class KernelSpecMonitorMeta(ABCMeta, type(LoggingConfigurable)):  # type: ignore
    pass


class KernelSpecMonitorBase(  # type:ignore[misc]
    ABC, LoggingConfigurable, metaclass=KernelSpecMonitorMeta
):
    GROUP_NAME = "jupyter_server.kernelspec_monitors"

    @classmethod
    def create_instance(
        cls, kernel_spec_cache: KernelSpecCache, **kwargs
    ) -> "KernelSpecMonitorBase":
        """Creates an instance of the monitor class configured on the KernelSpecCache instance."""

        kernel_spec_cache = kernel_spec_cache
        entry_point_name = kernel_spec_cache.monitor_entry_point
        eps = entry_points(group=KernelSpecMonitorBase.GROUP_NAME, name=entry_point_name)
        if eps:
            ep: EntryPoint = eps[entry_point_name]
            monitor_class = ep.load()
            monitor_instance: KernelSpecMonitorBase = monitor_class(kernel_spec_cache, **kwargs)
            if not isinstance(monitor_instance, KernelSpecMonitorBase):
                msg = (
                    f"Entrypoint '{kernel_spec_cache.monitor_entry_point}' of "
                    f"group '{KernelSpecMonitorBase.GROUP_NAME}' is not a "
                    f"subclass of '{KernelSpecMonitorBase.__name__}'"
                )
                raise RuntimeError(msg)

            monitor_instance.initialize()
            return monitor_instance
        else:
            msg = (
                f"Entrypoint '{kernel_spec_cache.monitor_entry_point}' of "
                f"group '{KernelSpecMonitorBase.GROUP_NAME}' cannot be located."
            )
            raise RuntimeError(msg)

    @abstractmethod
    def initialize(self) -> None:
        """Initializes the monitor."""
        pass

    @abstractmethod
    def destroy(self) -> None:
        """Destroys the monitor."""
        pass
