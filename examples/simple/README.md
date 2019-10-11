# Jupyter Server Simple Extension Example

This folder contains an example of a simple extension on top of Jupyter Server.

You need yarn and python3.

```bash
# Install and build.
make install
make build
```

```bash
# Start the jupyter server simple extension.
make start
```

Render server content in your browser.

```bash
# Default server page.
open http://localhost:8888
# Favicon static content.
open http://localhost:8888/static/simple_ext/favicon.ico
# HTML static page.
open http://localhost:8888/static/simple_ext/test.html
# Content from Handlers.
open http://localhost:8888/simple_ext/params/test?var1=foo
# Content from Template.
open http://localhost:8888/simple_ext/page1/test
# Content from Template with Typescript.
open http://localhost:8888/simple_ext
open http://localhost:8888/simple_ext/template
# Error content.
open http://localhost:8888/simple_ext/nope
```
