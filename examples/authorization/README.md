# Authorization in a simple Jupyter Notebook Server

This folder contains the following examples:
1. a "read-only" Jupyter Notebook Server
2. a read/write Server without the ability to execute code on kernels.
3. a "temporary notebook server", i.e. read and execute notebooks but cannot save/write notebooks.

## How does it work?

To add a custom authorization system to the Jupyter Server, you simply override (i.e. patch) the `user_is_authorized()` method in the `JupyterHandler`.

In the examples here, we do this by patching this method in our Jupyter configuration files. It looks something like this:

```python
from jupyter_server.base import JupyterHandler


# Define my own method here for handling authorization.
# The argument signature must have `self`, `user`, `action`, and `resource`.

def my_authorization_method(self, user, action, resource):
    """My override for handling authorization in Jupyter services."""

    # Add logic here to check if user is allowed.
    # For example, here is an example of a read-only server
    if action in ['write', 'execute']:
        return False

    return True

# Patch the user_is_authorized method with my own method.
JupyterHandler.user_is_authorized = my_authorization_method
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