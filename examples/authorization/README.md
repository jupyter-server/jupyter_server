# Authorization in a simple Jupyter Notebook Server

This folder contains the following examples:

1. a "read-only" Jupyter Notebook Server
2. a read/write Server without the ability to execute code on kernels.
3. a "temporary notebook server", i.e. read and execute notebooks but cannot save/write notebooks.

## How does it work?

To add a custom authorization system to the Jupyter Server, you will need to write your own `AuthorizationManager` subclass and pass it to Jupyter's configuration system (i.e. by file or CLI).

The examples below demonstrate some basic implementations of an `AuthorizationManager`.

```python
from jupyter_server.services.auth.manager import AuthorizationManager


class MyCustomAuthorizationManager(AuthorizationManager):
    """Custom authorization manager."""

    # Define my own method here for handling authorization.
    # The argument signature must have `self`, `handler`, `subject`, `action`, and `resource`.
    def is_authorized(self, handler, subject, action, resource):
        """My override for handling authorization in Jupyter services."""

        # Add logic here to check if user is allowed.
        # For example, here is an example of a read-only server
        if action in ['write', 'execute']:
            return False

        return True

# Pass this custom class to Jupyter Server
c.ServerApp.authorization_manager_class = MyCustomAuthorizationManager
```

In the `jupyter_nbclassic_readonly_config.py`

## Try it out!

### Read-only example

1. Clone and install nbclassic using `pip`.

   git clone https://github.com/Zsailer/nbclassic
   cd nbclassic
   pip install .

2. Navigate to the jupyter_authorized_server `examples/` folder.

3. Launch nbclassic and load `jupyter_nbclassic_readonly_config.py`:

   jupyter nbclassic --config=jupyter_nbclassic_readonly_config.py

4. Try creating a notebook, running a notebook in a cell, etc. You should see a `401: Unauthorized` error.

### Read+Write example

1. Clone and install nbclassic using `pip`.

   git clone https://github.com/Zsailer/nbclassic
   cd nbclassic
   pip install .

2. Navigate to the jupyter_authorized_server `examples/` folder.

3. Launch nbclassic and load `jupyter_nbclassic_rw_config.py`:

   jupyter nbclassic --config=jupyter_nbclassic_rw_config.py

4. Try running a cell in a notebook. You should see a `401: Unauthorized` error.

### Temporary notebook server example

1. Clone and install nbclassic using `pip`.

   git clone https://github.com/Zsailer/nbclassic
   cd nbclassic
   pip install .

2. Navigate to the jupyter_authorized_server `examples/` folder.

3. Launch nbclassic and load `jupyter_temporary_config.py`:

   jupyter nbclassic --config=jupyter_temporary_config.py

4. Edit a notebook, run a cell, etc. Everything works fine. Then try to save your changes... you should see a `401: Unauthorized` error.
