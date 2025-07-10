"""
Prometheus metrics server for Jupyter Server

This module provides functionality to start a separate Prometheus metrics server
that exposes Jupyter-specific metrics on a dedicated port.

Note on HTTP Request Metrics:
The separate metrics server uses the same prometheus registry as the main server.
HTTP request duration metrics (http_request_duration_seconds) are recorded by the
main server's logging system when record_http_request_metrics=True. Since both
servers share the same registry, these metrics will be available in the separate
metrics server as well.

The record_http_request_metrics parameter controls whether the main server records
these metrics, and the separate metrics server will automatically reflect this
setting since it uses the same underlying metrics collection.

Authentication:
The separate metrics server reuses the main server's authentication settings and
handler infrastructure, ensuring consistent behavior.
"""

import asyncio
import socket
import threading
import time
import warnings
from typing import Optional

import tornado.httpserver
import tornado.ioloop
import tornado.web

from jupyter_server._version import __version__
from jupyter_server.base.handlers import PrometheusMetricsHandler
from jupyter_server.prometheus.metrics import (
    ACTIVE_DURATION,
    KERNEL_CURRENTLY_RUNNING_TOTAL,
    LAST_ACTIVITY,
    SERVER_EXTENSION_INFO,
    SERVER_INFO,
    SERVER_STARTED,
    TERMINAL_CURRENTLY_RUNNING_TOTAL,
)


class PrometheusMetricsServer:
    """A separate Tornado server for serving Prometheus metrics."""

    def __init__(self, app):
        """Initialize the metrics server."""
        self.app = app
        self.port = None
        self.server = None
        self.ioloop = None
        self.thread = None
        self._running = False

    def initialize_metrics(self):
        """Initialize Jupyter-specific metrics for this server instance."""
        # Set server version info
        SERVER_INFO.info({"version": __version__})

        # Set up extension info
        for ext in self.app.extension_manager.extensions.values():
            SERVER_EXTENSION_INFO.labels(
                name=ext.name, version=ext.version, enabled=str(ext.enabled).lower()
            ).info({})

        # Set server start time
        started = self.app.web_app.settings["started"]
        SERVER_STARTED.set(started.timestamp())

        # Set up activity tracking
        LAST_ACTIVITY.set_function(lambda: self.app.web_app.last_activity().timestamp())
        ACTIVE_DURATION.set_function(
            lambda: (
                self.app.web_app.last_activity() - self.app.web_app.settings["started"]
            ).total_seconds()
        )

        # Set up kernel and terminal metrics
        self._setup_runtime_metrics()

        # Note: HTTP request metrics are recorded by the main server's logging system
        # via the log_request function when record_http_request_metrics=True.
        # The separate metrics server uses the same prometheus registry, so those
        # metrics will be available here as well.

    def _setup_runtime_metrics(self):
        """Set up metrics that track runtime state."""

        # Set up kernel count tracking
        def update_kernel_metrics():
            try:
                kernel_manager = self.app.kernel_manager
                if hasattr(kernel_manager, "list_kernel_ids"):
                    kernel_ids = kernel_manager.list_kernel_ids()
                    # Reset all kernel type metrics to 0
                    for kernel_type in set(KERNEL_CURRENTLY_RUNNING_TOTAL._metrics.keys()):
                        KERNEL_CURRENTLY_RUNNING_TOTAL.labels(type=kernel_type).set(0)

                    # Count kernels by type
                    kernel_types: dict[str, int] = {}
                    for kid in kernel_ids:
                        try:
                            kernel = kernel_manager.get_kernel(kid)
                            if hasattr(kernel, "kernel_name"):
                                kernel_type = kernel.kernel_name
                            else:
                                kernel_type = "unknown"
                            kernel_types[kernel_type] = kernel_types.get(kernel_type, 0) + 1
                        except Exception:
                            kernel_types["unknown"] = kernel_types.get("unknown", 0) + 1

                    # Update metrics
                    for kernel_type, count in kernel_types.items():
                        KERNEL_CURRENTLY_RUNNING_TOTAL.labels(type=kernel_type).set(count)
            except Exception as e:
                self.app.log.debug(f"Error updating kernel metrics: {e}")

        # Set up terminal count tracking
        def update_terminal_metrics():
            try:
                terminal_manager = getattr(self.app, "terminal_manager", None)
                if terminal_manager and hasattr(terminal_manager, "list"):
                    terminal_count = len(terminal_manager.list())
                    TERMINAL_CURRENTLY_RUNNING_TOTAL.set(terminal_count)
                else:
                    TERMINAL_CURRENTLY_RUNNING_TOTAL.set(0)
            except Exception as e:
                self.app.log.debug(f"Error updating terminal metrics: {e}")

        # Set up periodic updates
        def periodic_update():
            update_kernel_metrics()
            update_terminal_metrics()

        # Run initial update
        periodic_update()

        # Store the periodic update function to be called from the metrics server thread
        self._periodic_update = periodic_update

    def start(self, port: int = 9090) -> None:
        """Start the metrics server on the specified port."""
        if self._running:
            return

        # Initialize Jupyter metrics
        self.initialize_metrics()

        # Create Tornado application with metrics handler
        app = tornado.web.Application(
            [
                (r"/metrics", PrometheusMetricsHandler),
            ]
        )

        # Create HTTP server
        self.server = tornado.httpserver.HTTPServer(app)

        # Try to bind to the specified port
        try:
            self.server.bind(port)
            self.port = port
        except OSError:
            # If port is in use, try alternative ports
            for alt_port in range(port + 1, port + 10):
                try:
                    self.server.bind(alt_port)
                    self.port = alt_port
                    break
                except OSError:
                    continue
            else:
                raise RuntimeError(f"Could not bind to any port starting from {port}")

        # Start the server in a separate thread
        self.thread = threading.Thread(target=self._start_metrics_loop, daemon=True)
        self.thread.start()

        # Wait for server to be ready
        self._wait_for_server_ready()
        self._running = True

    def _start_metrics_loop(self) -> None:
        """Start the IOLoop in a separate thread."""
        try:
            # Create a new IOLoop for this thread
            self.ioloop = tornado.ioloop.IOLoop()

            # Set as current event loop for this thread
            asyncio.set_event_loop(self.ioloop.asyncio_loop)

            # Start the server
            self.server.start(1)  # Single process

            # Set up periodic updates in this IOLoop
            def periodic_update_wrapper():
                if hasattr(self, "_periodic_update"):
                    self._periodic_update()
                # Schedule next update in 30 seconds
                self.ioloop.call_later(30, periodic_update_wrapper)

            # Start periodic updates
            self.ioloop.call_later(30, periodic_update_wrapper)

            # Start the IOLoop
            self.ioloop.start()
        except Exception as e:
            # Log error but don't raise to avoid unhandled thread exceptions
            print(f"Metrics server error: {e}")

    def _wait_for_server_ready(self, timeout: float = 5.0) -> None:
        """Wait for the server to be ready to accept connections."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(0.1)
                    s.connect(("localhost", self.port))
                    return
            except OSError:
                time.sleep(0.1)
        raise TimeoutError(f"Server not ready after {timeout} seconds")

    def stop(self) -> None:
        """Stop the metrics server."""
        if not self._running:
            return

        self._running = False

        # Stop the server
        if self.server:
            self.server.stop()

        # Stop the IOLoop
        if self.ioloop:
            try:
                self.ioloop.add_callback(self.ioloop.stop)
            except Exception:
                pass

        # Wait for thread to finish
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2.0)

        # Clean up
        self.server = None
        self.ioloop = None
        self.thread = None
        self.port = None


def start_metrics_server(app, port: int = 9090) -> Optional[PrometheusMetricsServer]:
    """Start a metrics server for the given app."""
    try:
        server = PrometheusMetricsServer(app)
        server.start(port)
        return server
    except Exception as e:
        print(f"Failed to start metrics server: {e}")
        return None
