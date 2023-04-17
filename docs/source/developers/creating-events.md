# Emitting events

Jupyter Server comes equipped with an `event_logger` for capturing structured events from a running server.

## Emit a custom event from an extension

The core EventLogger in Jupyter Server's `ServerApp` can be used to emit events from extensions.

First, define an event schema. We recommend that you make the `$id` field
a valid URI and incorporate the version as part of the URI, e.g.:

```yaml
$id: https://my.extension.org/myextension/myevent/v1.yaml
version: 1
title: My Event
description: |
  Some information about my event
type: object
properties:
  thing:
    title: Thing
    description: A random thing.
    type: string
required:
  - thing
```

We also recommend that you write this schema to a file in your extension repository in a logical location, e.g. `myextension/events/myevent/v1.yaml`.

Then, you can easily register your event on the core serverapp's event logger:

```python
import pathlib

def _load_jupyter_server_extension(serverapp: ServerApp):
    ...
    # Register the event schema from its local filepath.
    schema = pathlib.Path("myextension/events/myevent/v1.yaml")
    serverapp.event_logger.register_event_schema(schema)
    ...
```

Once the event schema is registered, it is ready to be emitted. Note that the core `event_logger` is included in Jupyter Server's tornado settings and listed as a property of `JupyterHandler` API.

As an example, you can emit an event from custom request handler by calling `self.event_logger.emit(...)`:

```python
from jupyter_server.base.handlers import JupyterHandler

class MyExtensionHandler(JupyterHandler):

    def get(self):
        ...
        self.event_logger.emit(
            schema_id="https://my.extension.org/myextension/myevent/v1.yaml",
            data={
                "thing": "`GET` method was called."
            }
        )
```
