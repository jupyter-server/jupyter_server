"""KernelSpec watchdog monitor used by KernelspecCache."""
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

import json
from hashlib import md5

from overrides import overrides
from traitlets.traitlets import Float

from ..kernelspec_cache import KernelSpecCache, KernelSpecMonitorBase


class KernelSpecPollingMonitor(KernelSpecMonitorBase):
    """Polling monitor that uses a periodic poll period to reload the kernelspec cache."""

    interval = Float(
        default_value=30.0,
        config=True,
        help="""The interval (in seconds) at which kernelspecs are updated in the cache.""",
    )

    _pcallback = None

    # Keep track of hash values for each entry placed into the cache.  This will lessen
    # the churn and noise when publishing events
    hash_values: dict[str, str]

    def __init__(self, kernel_spec_cache: KernelSpecCache, **kwargs):
        """Initialize the handler."""
        super().__init__(**kwargs)
        self.kernel_spec_cache: KernelSpecCache = kernel_spec_cache
        self.kernel_spec_manager = self.kernel_spec_cache.kernel_spec_manager
        self.hash_values = {}
        self.log.info(f"Starting {self.__class__.__name__} with interval: {self.interval} ...")

    @overrides
    def initialize(self):
        """Initializes the cache and starts the registers the periodic poller."""

        # Seed the cache and start the observer
        if self.kernel_spec_cache.cache_enabled:
            self.poll()
            self.start()

    @overrides
    def destroy(self) -> None:
        self.stop()

    def poll(self):
        diff_kernelspecs = {}
        kernelspecs = self.kernel_spec_manager.get_all_specs()
        for kernel_name, entry in kernelspecs.items():
            hash_val = md5(json.dumps(entry).encode("utf-8")).hexdigest()
            cached_hash_val = self.hash_values.get(kernel_name, "")
            if hash_val != cached_hash_val:
                diff_kernelspecs[kernel_name] = entry
                self.hash_values[kernel_name] = hash_val

        self.log.debug(
            f"{self.__class__.__name__} num fetched: {len(kernelspecs.keys())}, "
            f"num cached: {len(diff_kernelspecs.keys())}"
        )
        self.kernel_spec_cache.put_all_items(diff_kernelspecs)

        # Determine items to remove by calculating what kernelspec names are in the previous
        # set and not in the current set
        current_set: set = set(kernelspecs.keys())
        previous_set: set = set(self.hash_values.keys())
        to_be_removed = previous_set.difference(current_set)
        for kernel_name in to_be_removed:
            self.hash_values.pop(kernel_name, None)
            self.kernel_spec_cache.remove_item(kernel_name)

    def start(self):
        """Start the polling of the kernel."""
        if self._pcallback is None:
            from tornado.ioloop import PeriodicCallback

            self._pcallback = PeriodicCallback(
                self.poll,
                1000 * self.interval,
            )
            self._pcallback.start()

    def stop(self):
        """Stop the kernel polling."""
        if self._pcallback is not None:
            self._pcallback.stop()
            self._pcallback = None
