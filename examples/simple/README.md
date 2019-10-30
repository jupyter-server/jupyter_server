# Jupyter Server Simple Extension Example

This folder contains an example of 2 simple extensions on top of Jupyter Server.

## Install

You need `python3` to build and run the server extensions.

```bash
conda create -y -n jext python=3.7 && \
  conda activate jext && \
  pip install -e .
```

**OPTIONAL** If you want to build the Typescript code, you need `npm` on your local env. Compiled javascript is provided as artifact in this repository, so this Typescript build step is optional. The Typescript source and configuration has been taken from https://github.com/markellekelly/jupyter-server-example.

```bash
npm install
npm run build
```

## Start Extension 1 and Extension 2

```bash
# Start the jupyter server, it will load both simple_ext1 and simple_ext2 based on the provided trait.
jupyter server --ServerApp.jpserver_extensions="{'simple_ext1': True, 'simple_ext2': True}"
```

Optionally, you can copy `simple_ext1.json` and `simple_ext2.json` configuration to your env `etc` folder and start only Extension 1, which will also start Extension 2.

```bash
pip uninstall -y simple_ext
python setup.py install
cp -r ./etc $(dirname $(which jupyter))/..
# Start the jupyter server extension simple_ext1, it will also load simple_ext2 because of load_other_extensions = True..
jupyter simple-ext1
```

Now you can render Extension 1 Server content in your browser.

```bash
# Jupyter Server Home Page.
open http://localhost:8888/
# TODO Fix Default URL, it does not show on startup.
# Home page as defined by default_url = '/default'.
open http://localhost:8888/simple_ext1/default
# HTML static page.
open http://localhost:8888/static/simple_ext1/test.html
# Content from Handlers.
open http://localhost:8888/simple_ext1/params/test?var1=foo
# Content from Template.
open http://localhost:8888/simple_ext1/template1/test
# Content from Template with Typescript.
open http://localhost:8888/simple_ext1/typescript
# Error content.
open http://localhost:8888/simple_ext1/nope
# Redirect.
open http://localhost:8888/simple_ext1/redirect
# Favicon static content.
open http://localhost:8888/static/simple_ext1/favicon.ico
```

You can also render Extension 2 Server content in your browser.

```bash
# HTML static page.
open http://localhost:8888/static/simple_ext2/test.html
# Content from Handlers.
open http://localhost:8888/simple_ext2/params/test?var1=foo
```

## Settings

Start with additional settings.

```bash
jupyter server --ServerApp.jpserver_extensions="{'simple_ext1': True, 'simple_ext2': True}" --SimpleApp1.cli=OK
```

Check the log, it should return on startup something like the following base on the trait you have defined in the CLI and in the `jupyter_server_config.py`.

```
[SimpleApp1] SimpleApp1.app OK
[SimpleApp1] SimpleApp1.file OK
[SimpleApp1] SimpleApp1.cli OK
[SimpleApp1] Complete Settings {'simple_ext1_config': {}, 'simple_ext1_template_paths': ['/home/datalayer/repos/jupyter-server/examples/simple/simple_ext1/templates'], 'simple_ext1_jinja2_env': <jinja2.environment.Environment object at 0x105ed7438>, 'log_function': <function log_request at 0x105e2d950>, 'base_url': '/', 'default_url': '/', 'template_path': ['/opt/datalayer/opt/miniconda3/envs/datalayer/lib/python3.7/site-packages/jupyter_server', '/opt/datalayer/opt/miniconda3/envs/datalayer/lib/python3.7/site-packages/jupyter_server/templates'], 'static_path': ['/opt/datalayer/opt/miniconda3/envs/datalayer/lib/python3.7/site-packages/jupyter_server/static'], 'static_custom_path': ['/home/datalayer/.jupyter/custom', '/opt/datalayer/opt/miniconda3/envs/datalayer/lib/python3.7/site-packages/jupyter_server/static/custom'], 'static_handler_class': <class 'jupyter_server.base.handlers.FileFindHandler'>, 'static_url_prefix': ...
```

## Start only Extension 2
`
Now stop the server and start again with only Extension 2.

```bash
# Start the jupyter server extension simple_ext2, it will NOT load simple_ext1 because of load_other_extensions = False.
jupyter simple-ext2
```

Try with the above links to check that only Extension 2 is responding (Extension 1 URLs should give you an 404 error).

## Extension 11 extending Extension 1

```bash
jupyter simple-ext11
# or...
jupyter server --ServerApp.jpserver_extensions="{'simple_ext11': True}"
```

```bash
# Jupyter Server Home Page.
open http://localhost:8888/
# TODO Fix Default URL, it does not show on startup.
# Home page as defined by default_url = '/default'.
open http://localhost:8888/simple_ext11/default
# HTML static page.
open http://localhost:8888/static/simple_ext11/test.html
# Content from Handlers.
open http://localhost:8888/simple_ext11/params/test?var1=foo
# Content from Template.
open http://localhost:8888/simple_ext11/template1/test
# Content from Template with Typescript.
open http://localhost:8888/simple_ext11/typescript
# Error content.
open http://localhost:8888/simple_ext11/nope
# Redirect.
open http://localhost:8888/simple_ext11/redirect
# Favicon static content.
open http://localhost:8888/static/simple_ext11/favicon.ico
```
