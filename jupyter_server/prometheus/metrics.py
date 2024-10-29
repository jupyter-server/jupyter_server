"""
Prometheus metrics exported by Jupyter Server

Read https://prometheus.io/docs/practices/naming/ for naming
conventions for metrics & labels.
"""

from prometheus_client import Gauge, Histogram, Info
from jupyter_server._version import version_info as server_version_info

try:
    from notebook._version import version_info as notebook_version_info
    v6_notebook_present = notebook_version_info != server_version_info
except ImportError:
    # notebook._version is not present, so notebook v6 can not be present
    v6_notebook_present = False


if v6_notebook_present:
    print("yes, we think we have an unshimmed notebook package")
    print(notebook_version_info)
    print(server_version_info)
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
