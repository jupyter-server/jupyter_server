"""
Prometheus metrics integration for Jupyter Server.

This module provides Prometheus metrics collection and exposure for Jupyter Server.
"""

from .metrics import (
    KERNEL_CURRENTLY_RUNNING_TOTAL,
    LAST_ACTIVITY,
    SERVER_EXTENSION_INFO,
    SERVER_INFO,
    SERVER_STARTED,
    TERMINAL_CURRENTLY_RUNNING_TOTAL,
)
from .server import PrometheusMetricsServer, start_metrics_server

__all__ = [
    "KERNEL_CURRENTLY_RUNNING_TOTAL", 
    "TERMINAL_CURRENTLY_RUNNING_TOTAL",
    "SERVER_INFO",
    "SERVER_EXTENSION_INFO",
    "LAST_ACTIVITY",
    "SERVER_STARTED",
    "ACTIVE_DURATION",
    "PrometheusMetricsServer",
    "start_metrics_server",
]
