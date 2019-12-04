# Jupyter Server Simple Extension Example

This folder contains example of simple extensions on top of Jupyter Server and review configuration aspects.

## Install

You need `python3` to build and run the server extensions.

```bash
git clone https://github.com/jupyter/jupyter_server && \
  cd examples/simple && \
  conda create -y -n jupyter_server_example python=3.7 && \
  conda activate jupyter_server_example && \
  pip install -e .
```

**OPTIONAL** If you want to build the Typescript code, you need `npm` on your local env. Compiled javascript is provided as artifact in this repository, so this Typescript build step is optional. The Typescript source and configuration has been taken from https://github.com/markellekelly/jupyter-server-example.

```bash
npm install && \
  npm run build
```

## Start Extension 1

```bash
# Start the jupyter server activating simple_ext1 extension.
jupyter server --ServerApp.jpserver_extensions="{'simple_ext1': True}"
```

Now you can render `Extension 1` Server content in your browser.

```bash
# Jupyter Server Home Page.
open http://localhost:8888/
# Home page as defined by default_url = '/default'.
open http://localhost:8888/simple_ext1/default
# HTML static page.
open http://localhost:8888/static/simple_ext1/home.html
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

## Start Extension 2

The following command starts both `simple_ext1` and `simple_ext2` extensions.

```bash
# Start the jupyter server, it will load both simple_ext1 and simple_ext2 based on the provided trait.
jupyter server --ServerApp.jpserver_extensions="{'simple_ext1': True, 'simple_ext2': True}"
```

You can also render `Extension 2` Server content in your browser.

```bash
# HTML static page.
open http://localhost:8888/static/simple_ext2/test.html
# Content from Handlers.
open http://localhost:8888/simple_ext2/params/test?var1=foo
```

## Start with Entrypoints

Optionally, you can copy `simple_ext1.json` and `simple_ext2.json` configuration to your env `etc` folder and start only Extension 1, which will also start Extension 2.

```bash
pip uninstall -y jupyter_simple_ext && \
  python setup.py install && \
  cp -r ./etc $(dirname $(which jupyter))/..
# Start the jupyter server extension simple_ext1, it will also load simple_ext2 because of load_other_extensions = True..
# When you invoke with the entrypoint, the default url will be opened in your browser.
jupyter simple-ext1
```

## Configuration

Stop any running server (with `CTRL+C`) and start with additional configuration on the command line.

The provided settings via CLI will override the configuration that reside in the files (`jupyter_simple_ext1_config.py`...)

```bash
jupyter server \ 
  --ServerApp.jpserver_extensions="{'simple_ext1': True, 'simple_ext2': True}" \
  --SimpleApp1.cli=OK
```

Check the log, it should return on startup something like the following base on the trait you have defined in the CLI and in the `jupyter_server_config.py`.

```
[SimpleApp1] SimpleApp1.app OK
[SimpleApp1] SimpleApp1.file OK
[SimpleApp1] SimpleApp1.cli OK
```

## Start only Extension 2

Now stop agin the server and start with only `Extension 2`.

```bash
# Start the jupyter server extension simple_ext2, it will NOT load simple_ext1 because of load_other_extensions = False.
jupyter simple-ext2
```

Try with the above links to check that only Extension 2 is responding (Extension 1 URLs should give you an 404 error).

## Extension 11 extending Extension 1

`Extension 11` extends `Extension 1` and brings a few more configs.

Run `jupyter simple-ext11 --generate-config && vi ~/.jupyter/jupyter_config.py`.

The generated configuration should contains the following.

```bash
...
#  Can be used to override templates from notebook.templates.
#c.ExtensionApp.template_paths = []

#------------------------------------------------------------------------------
# SimpleApp1(ExtensionApp) configuration
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# SimpleApp11(SimpleApp1) configuration
#------------------------------------------------------------------------------

## Say hello
#c.SimpleApp11.hello = False

## Ignore Javascript
#c.SimpleApp11.ignore_js = False

## Simple directory
#c.SimpleApp11.simple11_dir = ''

#------------------------------------------------------------------------------
# ServerApp(JupyterApp) configuration
#------------------------------------------------------------------------------

## Set the Access-Control-Allow-Credentials: true header
#c.ServerApp.allow_credentials = False
...
```

The `hello`, `ignore_js` and `simple11_dir` are traits defined on the SimpleApp11 class.

It also implements additional flags and aliases for these traits.

+ The `--hello` flag will log on startup `Hello Simple11 - You have provided the --hello flag or defined a c.SimpleApp1.hello == True`.
+ The `--simple11-dir` alias will set `SimpleExt11.simple11_dir` settings.

Stop any running server and then start the simple-ext11.

```bash
jupyter simple-ext11 --hello --simple11-dir any_folder
# or...
jupyter server --ServerApp.jpserver_extensions="{'simple_ext11': True}" --hello --simple11-dir any_folder
```

Ensure the following URLs respond correctly.

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
