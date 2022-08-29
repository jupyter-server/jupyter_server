"""Scheduling API for JupyterLab"""
from .extension import SchedulerApp
__version__ = "0.1.0"


def _jupyter_server_extension_points():
    return [{
        "module": "jupyter_scheduling",
        "app": SchedulerApp
    }]
