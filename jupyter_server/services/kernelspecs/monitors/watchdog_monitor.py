"""KernelSpec watchdog monitor used by KernelspecCache."""
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
import os
from typing import Any, Set, Tuple

from overrides import overrides
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from ..kernelspec_cache import KernelSpecCache, KernelSpecMonitorBase


class KernelSpecWatchdogMonitor(KernelSpecMonitorBase):  # type:ignore[misc]
    """Watchdog handler that filters on specific files deemed representative of a kernel specification."""

    def __init__(self, kernel_spec_cache: KernelSpecCache, **kwargs: Any):
        """Initialize the handler."""
        super().__init__(**kwargs)
        self.kernel_spec_cache: KernelSpecCache = kernel_spec_cache
        self.kernel_spec_manager = self.kernel_spec_cache.kernel_spec_manager
        self.observed_dirs: Set[str] = set()  # Tracks which directories are being watched
        self.observer: Any = None

    @overrides
    def initialize(self) -> None:
        """Initializes the cache and starts the observer."""

        if self.kernel_spec_cache.cache_enabled:
            self.observer = Observer()
            kernelspecs = self.kernel_spec_manager.get_all_specs()
            self.kernel_spec_cache.put_all_items(kernelspecs)
            # Following adds, see if any of the manager's kernel dirs are not observed and add them
            for kernel_dir in self.kernel_spec_manager.kernel_dirs:
                if kernel_dir not in self.observed_dirs:
                    if os.path.exists(kernel_dir):
                        self.log.info(
                            "KernelSpecCache: observing directory: {kernel_dir}".format(
                                kernel_dir=kernel_dir
                            )
                        )
                        self.observed_dirs.add(kernel_dir)
                        self.observer.schedule(WatchDogHandler(self), kernel_dir, recursive=True)
                    else:
                        self.log.warning(
                            "KernelSpecCache: kernel_dir '{kernel_dir}' does not exist"
                            " and will not be observed.".format(kernel_dir=kernel_dir)
                        )
            self.observer.start()

    @overrides
    def destroy(self) -> None:
        self.observer = None


class WatchDogHandler(FileSystemEventHandler):
    # Events related to these files trigger the management of the KernelSpec cache.  Should we find
    # other files qualify as indicators of a kernel specification's state (like perhaps detached parameter
    # files in the future) should be added to this list - at which time it should become configurable.
    watched_files = ["kernel.json"]

    def __init__(self, monitor: "KernelSpecWatchdogMonitor", **kwargs: Any):
        """Initialize the handler."""
        super().__init__(**kwargs)
        self.kernel_spec_cache = monitor.kernel_spec_cache
        self.log = monitor.kernel_spec_cache.log

    def dispatch(self, event):
        """Dispatches events pertaining to kernelspecs to the appropriate methods.

        The primary purpose of this method is to ensure the action is occurring against
        a file in the list of watched files and adds some additional attributes to
        the event instance to make the actual event handling method easier.
        """

        if os.path.basename(event.src_path) in self.watched_files:
            super().dispatch(event)

    def on_created(self, event):
        """Fires when a watched file is created.

        This will trigger a call to the configured KernelSpecManager to fetch the instance
        associated with the created file, which is then added to the cache.
        """
        resource_dir, kernel_name = WatchDogHandler._extract_info(event.src_path)
        try:
            kernelspec = self.kernel_spec_cache.kernel_spec_manager.get_kernel_spec(kernel_name)
            self.kernel_spec_cache.put_item(kernel_name, kernelspec)
        except Exception as e:
            self.log.warning(
                f"The following exception occurred creating cache entry for: {resource_dir} - continuing...  ({e})"
            )

    def on_deleted(self, event):
        """Fires when a watched file is deleted, triggering a removal of the corresponding item from the cache."""
        _, kernel_name = WatchDogHandler._extract_info(event.src_path)
        self.kernel_spec_cache.remove_item(kernel_name)

    def on_modified(self, event):
        """Fires when a watched file is modified.

        This will trigger a call to the configured KernelSpecManager to fetch the instance
        associated with the modified file, which is then replaced in the cache.
        """
        resource_dir, kernel_name = WatchDogHandler._extract_info(event.src_path)
        try:
            kernelspec = self.kernel_spec_cache.kernel_spec_manager.get_kernel_spec(kernel_name)
            self.kernel_spec_cache.put_item(kernel_name, kernelspec)
        except Exception as e:
            self.log.warning(
                f"The following exception occurred updating cache entry for: {resource_dir} - continuing...  ({e})"
            )

    def on_moved(self, event):
        """Fires when a watched file is moved.

        This will trigger the update of the existing cached item, replacing its resource_dir entry
        with that of the new destination.
        """
        _, src_kernel_name = WatchDogHandler._extract_info(event.src_path)
        dest_resource_dir, dest_kernel_name = WatchDogHandler._extract_info(event.dest_path)
        cache_item = self.kernel_spec_cache.remove_item(src_kernel_name)
        if cache_item is not None:
            cache_item["resource_dir"] = dest_resource_dir
            self.kernel_spec_cache.put_item(dest_kernel_name, cache_item)

    @staticmethod
    def _extract_info(dir_name: str) -> Tuple[str, str]:
        """Extracts the resource directory and kernel_name from the given dir_name."""
        resource_dir: str = os.path.dirname(dir_name)  # includes kernel_name
        return resource_dir, os.path.basename(resource_dir)
