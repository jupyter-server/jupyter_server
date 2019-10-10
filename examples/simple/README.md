# Jupyter Server Simple Extension Example

This folder contains an example to develop an simple extension on top of Jupyter Server.

```bash
# Install the server simple extension.
python setup.py develop
```

```bash
# Start the jupyter server simple extension.
jupyter server-simple
```

Render server content in your browser.

```bash
# Default server page.
open http://localhost:8888
# Default favicon.
open http://localhost:8888/favicon.ico
# HTML static page.
open http://localhost:8888/static/server_simple/test.html
# Content from Handlers.
open http://localhost:8888/server_simple
open http://localhost:8888/server_simple/something?var1=foo
# Content from Template.
open http://localhost:8888/template
```

## TO FIX

+ The token created in `browser-open.html` is `None` - http://localhost:8888/?token=None
+ This static favicon request fails with `403 : Forbidden - favicon.ico is not in root static directory` - http://localhost:8888/static/server_simple/favicon.ico
