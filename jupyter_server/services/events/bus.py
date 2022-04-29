from jupyter_telemetry.eventlog import EventLog
from traitlets.config import SingletonConfigurable


class EventBus(EventLog, SingletonConfigurable):
    """A Jupyter EventLog as a Singleton, making it easy to
    access from anywhere and log events.
    """

    def record_event(self, *args, **kwargs):

        super().record_event(*args, **kwargs)
