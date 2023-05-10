"""KernelSpec watchdog monitor used by KernelspecCache."""
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
import os

from overrides import overrides
from watchdog.events import FileMovedEvent, FileSystemEventHandler
from watchdog.observers import Observer

from ..kernelspec_cache import KernelSpecCache, KernelSpecMonitorBase


class KernelSpecWatchdogMonitor(KernelSpecMonitorBase):
    """Watchdog handler that filters on specific files deemed representative of a kernel specification."""

    def __init__(self, kernel_spec_cache: KernelSpecCache, **kwargs):
        """Initialize the handler."""
        super().__init__(**kwargs)
        self.kernel_spec_cache: KernelSpecCache = kernel_spec_cache
        self.kernel_spec_manager = self.kernel_spec_cache.kernel_spec_manager
        self.observed_dirs = set()  # Tracks which directories are being watched
        self.observer = None

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

    def __init__(self, monitor: "KernelSpecWatchdogMonitor", **kwargs):
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
            src_resource_dir = os.path.dirname(event.src_path)
            event.src_resource_dir = src_resource_dir
            event.src_kernel_name = os.path.basename(src_resource_dir)
            if type(event) is FileMovedEvent:
                dest_resource_dir = os.path.dirname(event.dest_path)
                event.dest_resource_dir = dest_resource_dir
                event.dest_kernel_name = os.path.basename(dest_resource_dir)

            super().dispatch(event)

    def on_created(self, event):
        """Fires when a watched file is created.

        This will trigger a call to the configured KernelSpecManager to fetch the instance
        associated with the created file, which is then added to the cache.
        """
        kernel_name = event.src_kernel_name
        try:
            kernelspec = self.kernel_spec_cache.kernel_spec_manager.get_kernel_spec(kernel_name)
            self.kernel_spec_cache.put_item(kernel_name, kernelspec)
        except Exception as e:
            self.log.warning(
                "The following exception occurred creating cache entry for: {src_resource_dir} "
                "- continuing...  ({e})".format(src_resource_dir=event.src_resource_dir, e=e)
            )

    def on_deleted(self, event):
        """Fires when a watched file is deleted, triggering a removal of the corresponding item from the cache."""
        kernel_name = event.src_kernel_name
        self.kernel_spec_cache.remove_item(kernel_name)

    def on_modified(self, event):
        """Fires when a watched file is modified.

        This will trigger a call to the configured KernelSpecManager to fetch the instance
        associated with the modified file, which is then replaced in the cache.
        """
        kernel_name = event.src_kernel_name
        try:
            kernelspec = self.kernel_spec_cache.kernel_spec_manager.get_kernel_spec(kernel_name)
            self.kernel_spec_cache.put_item(kernel_name, kernelspec)
        except Exception as e:
            self.log.warning(
                "The following exception occurred updating cache entry for: {src_resource_dir} "
                "- continuing...  ({e})".format(src_resource_dir=event.src_resource_dir, e=e)
            )

    def on_moved(self, event):
        """Fires when a watched file is moved.

        This will trigger the update of the existing cached item, replacing its resource_dir entry
        with that of the new destination.
        """
        src_kernel_name = event.src_kernel_name
        dest_kernel_name = event.dest_kernel_name
        cache_item = self.kernel_spec_cache.remove_item(src_kernel_name)
        cache_item["resource_dir"] = event.dest_resource_dir
        self.kernel_spec_cache.put_item(dest_kernel_name, cache_item)
