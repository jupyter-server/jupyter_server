"""KernelSpec watchdog monitor used by KernelspecCache."""
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

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

    def __init__(self, **kwargs):
        """Initialize the handler."""
        super().__init__(**kwargs)
        self.kernel_spec_cache: KernelSpecCache = kwargs["parent"]
        self.kernel_spec_manager = self.kernel_spec_cache.kernel_spec_manager
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
        self.kernel_spec_cache.remove_all_items()
        kernelspecs = self.kernel_spec_manager.get_all_specs()
        self.kernel_spec_cache.put_all_items(kernelspecs)

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
