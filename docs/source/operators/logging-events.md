# Event logging

Jupyter Server emits the following list of events (via [`jupyter_events`](https://jupyter-events.readthedocs.io/en/latest/))

{{ jupyter_server_events }}

## Collecting emitted events

Configure the `EventLogger` to begin emitting events from Jupyter Server

```python
from logging import FileHandler

event_handler = FileHandler("events.log")

c.EventLogger.handlers = [event_handler]
```

## Filtering events

By default, all events are emitted to all handlers. If you would like to filter a specific set of
events to a handler, use Python's `logging.Filter`.

See the following example:

```python
from logging import Filter
from logging import FileHandler


class ContentsFilter(Filter):

    contents_events = [
        "https://events.jupyter.org/jupyter_server/contents_service/v1"
    ]

    def filter(self, record):
        if record.msg['__schema__'] in self.contents_events:
            return True
        return False


contents_filter = ContentsFilter()
event_handler = FileHandler("events.log")
event_handler.addFilter(contents_filter)

c.EventLogger.handlers = [event_handler]
```
