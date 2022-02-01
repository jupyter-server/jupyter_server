# Authorization in a simple Jupyter Notebook Server

This folder contains the following examples:

1. a "read-only" Jupyter Notebook Server
2. a read/write Server without the ability to execute code on kernels.
3. a "temporary notebook server", i.e. read and execute notebooks but cannot save/write files.

## How does it work?

To add a custom authorization system to the Jupyter Server, you will need to write your own `Authorizer` subclass and pass it to Jupyter's configuration system (i.e. by file or CLI).

The examples below demonstrate some basic implementations of an `Authorizer`.

```python
from jupyter_server.auth import Authorizer


class MyCustomAuthorizer(Authorizer):
    """Custom authorization manager."""

    # Define my own method here for handling authorization.
    # The argument signature must have `self`, `handler`, `user`, `action`, and `resource`.
    def is_authorized(self, handler, user, action, resource):
        """My override for handling authorization in Jupyter services."""

        # Add logic here to check if user is allowed.
        # For example, here is an example of a read-only server
        if action != "read":
            return False

        return True

# Pass this custom class to Jupyter Server
c.ServerApp.authorizer_class = MyCustomAuthorizer
```

In the `jupyter_nbclassic_readonly_config.py`

## Try it out!

### Read-only example

1. Install nbclassic using `pip`.

   pip install nbclassic

2. Navigate to the jupyter_authorized_server `examples/` folder.

3. Launch nbclassic and load `jupyter_nbclassic_readonly_config.py`:

   jupyter nbclassic --config=jupyter_nbclassic_readonly_config.py

4. Try creating a notebook, running a notebook in a cell, etc. You should see a `403: Forbidden` error.

### Read+Write example

1. Install nbclassic using `pip`.

   pip install nbclassic

2. Navigate to the jupyter_authorized_server `examples/` folder.

3. Launch nbclassic and load `jupyter_nbclassic_rw_config.py`:

   jupyter nbclassic --config=jupyter_nbclassic_rw_config.py

4. Try running a cell in a notebook. You should see a `403: Forbidden` error.

### Temporary notebook server example

This configuration allows everything except saving files.

1. Install nbclassic using `pip`.

   pip install nbclassic

2. Navigate to the jupyter_authorized_server `examples/` folder.

3. Launch nbclassic and load `jupyter_temporary_config.py`:

   jupyter nbclassic --config=jupyter_temporary_config.py

4. Edit a notebook, run a cell, etc. Everything works fine. Then try to save your changes... you should see a `403: Forbidden` error.
