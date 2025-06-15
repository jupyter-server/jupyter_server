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

import threading
from typing import Optional

import prometheus_client
import tornado.httpserver
import tornado.ioloop

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
    """A separate server for exposing Prometheus metrics."""

    def __init__(self, server_app):
        """Initialize the metrics server.

        Parameters
        ----------
        server_app : ServerApp
            The main Jupyter server application instance
        """
        self.server_app = server_app
        self.port = None
        self.http_server = None
        self.thread = None

    def initialize_metrics(self):
        """Initialize Jupyter-specific metrics for this server instance."""
        # Set server version info
        SERVER_INFO.info({"version": __version__})

        # Set up extension info
        for ext in self.server_app.extension_manager.extensions.values():
            SERVER_EXTENSION_INFO.labels(
                name=ext.name, version=ext.version, enabled=str(ext.enabled).lower()
            ).info({})

        # Set server start time
        started = self.server_app.web_app.settings["started"]
        SERVER_STARTED.set(started.timestamp())

        # Set up activity tracking
        LAST_ACTIVITY.set_function(lambda: self.server_app.web_app.last_activity().timestamp())
        ACTIVE_DURATION.set_function(
            lambda: (
                self.server_app.web_app.last_activity()
                - self.server_app.web_app.settings["started"]
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
                kernel_manager = self.server_app.kernel_manager
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
                self.server_app.log.debug(f"Error updating kernel metrics: {e}")

        # Set up terminal count tracking
        def update_terminal_metrics():
            try:
                terminal_manager = getattr(self.server_app, "terminal_manager", None)
                if terminal_manager and hasattr(terminal_manager, "list"):
                    terminal_count = len(terminal_manager.list())
                    TERMINAL_CURRENTLY_RUNNING_TOTAL.set(terminal_count)
                else:
                    TERMINAL_CURRENTLY_RUNNING_TOTAL.set(0)
            except Exception as e:
                self.server_app.log.debug(f"Error updating terminal metrics: {e}")

        # Set up periodic updates
        def periodic_update():
            update_kernel_metrics()
            update_terminal_metrics()

        # Run initial update
        periodic_update()

        # Store the periodic update function to be called from the metrics server thread
        self._periodic_update = periodic_update

    def start(self, port: int) -> None:
        """Start the metrics server on the specified port.

        Parameters
        ----------
        port : int
            The port to listen on for metrics requests
        """
        # Initialize Jupyter metrics
        self.initialize_metrics()

        # Reuse the main server's web application and settings
        # This ensures identical behavior and eliminates duplication
        main_app = self.server_app.web_app

        # Create a new application that shares the same settings and handlers
        # but only serves the metrics endpoint
        metrics_app = tornado.web.Application(
            [
                (r"/metrics", PrometheusMetricsHandler),
            ],
            **main_app.settings,
        )

        # Determine authentication status for logging
        authenticate_metrics = main_app.settings.get("authenticate_prometheus", True)
        auth_info = "with authentication" if authenticate_metrics else "without authentication"

        # Create and start the HTTP server with port retry logic
        self.http_server = tornado.httpserver.HTTPServer(metrics_app)

        # Try to bind to the requested port, with fallback to random ports
        actual_port = port
        max_retries = 10

        for attempt in range(max_retries):
            try:
                self.http_server.listen(actual_port)
                self.port = actual_port
                break
            except OSError as e:
                if e.errno == 98:  # Address already in use
                    if attempt == 0:
                        # First attempt failed, try random ports
                        import random

                        actual_port = random.randint(49152, 65535)  # Use dynamic port range
                    else:
                        # Subsequent attempts, try next random port
                        actual_port = random.randint(49152, 65535)

                    if attempt == max_retries - 1:
                        # Last attempt failed
                        self.server_app.log.warning(
                            f"Could not start metrics server on any port after {max_retries} attempts. "
                        )
                        return
                else:
                    # Non-port-related error, re-raise
                    raise

        # Start the IOLoop in a separate thread
        def start_metrics_loop():
            self.ioloop = tornado.ioloop.IOLoop()
            self.ioloop.make_current()

            # Set up periodic updates in this IOLoop
            def periodic_update_wrapper():
                if hasattr(self, "_periodic_update"):
                    self._periodic_update()
                # Schedule next update in 30 seconds
                self.ioloop.call_later(30, periodic_update_wrapper)

            # Start periodic updates
            self.ioloop.call_later(30, periodic_update_wrapper)

            self.ioloop.start()

        self.thread = threading.Thread(target=start_metrics_loop, daemon=True)
        self.thread.start()

        self.server_app.log.info(
            f"Metrics server started on port {self.port} {auth_info} (using Jupyter Prometheus integration)"
        )

    def stop(self) -> None:
        """Stop the metrics server."""
        if self.http_server:
            self.http_server.stop()
            self.http_server = None

        if hasattr(self, "ioloop") and self.ioloop:
            # Stop the IOLoop
            self.ioloop.add_callback(self.ioloop.stop)
            self.ioloop = None

        if self.thread and self.thread.is_alive():
            # Wait for thread to finish (with timeout)
            self.thread.join(timeout=1.0)

        self.server_app.log.info(
            f"Metrics server stopped on port {getattr(self, 'port', 'unknown')}"
        )


def start_metrics_server(server_app, port: int) -> PrometheusMetricsServer:
    """Start a Prometheus metrics server for the given Jupyter server.

    Parameters
    ----------
    server_app : ServerApp
        The main Jupyter server application instance
    port : int
        The port to listen on for metrics requests

    Returns
    -------
    PrometheusMetricsServer
        The metrics server instance
    """
    metrics_server = PrometheusMetricsServer(server_app)
    metrics_server.start(port)
    return metrics_server
