"""
Prometheus metrics exported by Jupyter Server

Read https://prometheus.io/docs/practices/naming/ for naming
conventions for metrics & labels.
"""
from prometheus_client import Info, Gauge, Histogram

try:
    from notebook._version import version_info as notebook_version_info
except ImportError:
    notebook_version_info = None

if notebook_version_info is not None and notebook_version_info < (7,):
    # Jupyter Notebook v6 also defined these metrics.  Re-defining them results in a ValueError,
    # so we simply re-export them if we are co-existing with the notebook v6 package.
    # See https://github.com/jupyter/jupyter_server/issues/209
    from notebook.prometheus.metrics import (
        HTTP_REQUEST_DURATION_SECONDS,
        KERNEL_CURRENTLY_RUNNING_TOTAL,
        TERMINAL_CURRENTLY_RUNNING_TOTAL,
    )
else:
    HTTP_REQUEST_DURATION_SECONDS = Histogram(
        "http_request_duration_seconds",
        "duration in seconds for all HTTP requests",
        ["method", "handler", "status_code"],
    )

    TERMINAL_CURRENTLY_RUNNING_TOTAL = Gauge(
        "terminal_currently_running_total",
        "counter for how many terminals are running",
    )

    KERNEL_CURRENTLY_RUNNING_TOTAL = Gauge(
        "kernel_currently_running_total",
        "counter for how many kernels are running labeled by type",
        ["type"],
    )

# New prometheus metrics that do not exist in notebook v6 go here
SERVER_INFO = Info("jupyter_server", "Jupyter Server Version information")

__all__ = [
    "HTTP_REQUEST_DURATION_SECONDS",
    "TERMINAL_CURRENTLY_RUNNING_TOTAL",
    "KERNEL_CURRENTLY_RUNNING_TOTAL",
    "SERVER_INFO",
]
