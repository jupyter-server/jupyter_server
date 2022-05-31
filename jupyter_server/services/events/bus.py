"""An EventBus for use in the Jupyter server.

.. versionadded:: 2.0
"""
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
from jupyter_events.logger import EventLogger
from traitlets.config import SingletonConfigurable


class EventBus(EventLogger, SingletonConfigurable):
    """A singleton eventlog that behaves as an event
    bus for emitting Jupyter Server (and extension)
    event data.
    """
