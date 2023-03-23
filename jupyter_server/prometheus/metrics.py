"""
Prometheus metrics exported by Jupyter Server

Read https://prometheus.io/docs/practices/naming/ for naming
conventions for metrics & labels.
"""

from prometheus_client import Counter

try:
    import notebook  # type: ignore

    if notebook.__name__ != "notebook":
        # avoid double-importing myself if nbclassic is shimming jupyter_server into notebook,
        # in which case notebook.__name__ will be 'jupyter_server'
        _msg = "Not importing jupyter_server metrics under two names"
        raise ImportError(_msg)
    # Jupyter Notebook also defines these metrics.  Re-defining them results in a ValueError.
    # Try to de-duplicate by using the ones in Notebook if available.
    # See https://github.com/jupyter/jupyter_server/issues/209
    from notebook.prometheus.metrics import (  # type:ignore
        HTTP_REQUEST_DURATION_SECONDS,
        KERNEL_CURRENTLY_RUNNING_TOTAL,
        TERMINAL_CURRENTLY_RUNNING_TOTAL,
    )

except ImportError:
    from prometheus_client import Gauge, Histogram

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

KERNEL_RESTARTS = Counter(
    "jupyter_kernel_restarts",
    "counter for how many kernel restarts, labeled by kernel_name and source (user or restarter)",
    ["kernel_name", "source"],
)
