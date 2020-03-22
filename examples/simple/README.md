# Jupyter Server Simple Extension Example

This folder contains example of simple extensions on top of Jupyter Server and review configuration aspects.

## Install

You need `python3` to build and run the server extensions.

```bash
# Clone, create a conda env and install from source.
git clone https://github.com/jupyter/jupyter_server && \
  cd examples/simple && \
  conda create -y -n jupyter-server-example python=3.7 && \
  conda activate jupyter-server-example && \
  pip install -e .
```

**OPTIONAL** If you want to build the Typescript code, you need [npm](https://www.npmjs.com) on your local environement. Compiled javascript is provided as artifact in this repository, so this Typescript build step is optional. The Typescript source and configuration have been taken from https://github.com/markellekelly/jupyter-server-example.

```bash
npm install && \
  npm run build
```

## No Extension

Ensure Jupyter Server is starting without any extension enabled.

```bash
# Run this command from a shell.
jupyter server
```

Browse the default home page, it should show a white page in your browser with the following content: `A Jupyter Server is running.`

```bash
# Jupyter Server default Home Page.
open http://localhost:8888
```

## Extension 1

```bash
# Start the jupyter server activating simple_ext1 extension.
jupyter server --ServerApp.jpserver_extensions="{'simple_ext1': True}"
```

Now you can render `Extension 1` Server content in your browser.

```bash
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

You can also start the server extension with python modules.

```bash
python -m simple_ext1
```

## Extension 1 and Extension 2

The following command starts both the `simple_ext1` and `simple_ext2` extensions.

```bash
# Start the jupyter server, it will load both simple_ext1 and simple_ext2 based on the provided trait.
jupyter server --ServerApp.jpserver_extensions="{'simple_ext1': True, 'simple_ext2': True}"
```

Check that the previous `Extension 1` content is still available ant that you can also render `Extension 2` Server content in your browser.

```bash
# HTML static page.
open http://localhost:8888/static/simple_ext2/test.html
# Content from Handlers.
open http://localhost:8888/simple_ext2/params/test?var1=foo
```

## Work with Entrypoints

Optionally, you can copy `simple_ext1.json` and `simple_ext2.json` configuration to your env `etc` folder and start only Extension 1, which will also start Extension 2.

```bash
pip uninstall -y jupyter_server_example && \
  python setup.py install && \
  cp -r ./etc $(dirname $(which jupyter))/..
```

```bash
# Start the jupyter server extension simple_ext1, it will also load simple_ext2 because of load_other_extensions = True..
# When you invoke with the entrypoint, the default url will be opened in your browser.
jupyter simple-ext1
```

## Configuration

Stop any running server (with `CTRL+C`) and start with additional configuration on the command line.

The provided settings via CLI will override the configuration that reside in the files (`jupyter_server_example1_config.py`...)

```bash
jupyter simple-ext1 --SimpleApp1.configA="ConfigA from command line"
```

Check the log, it should return on startup print the Config object.

The content of the Config is based on the trait you have defined via the `CLI` and in the `jupyter_server_example1_config.py`.

```
[SimpleApp1] Config {'SimpleApp1': {'configA': 'ConfigA from file', 'configB': 'ConfigB from file', 'configC': 'ConfigC from file'}}
[SimpleApp1] Config {'SimpleApp1': {'configA': 'ConfigA from file', 'configB': 'ConfigB from file', 'configC': 'ConfigC from file'}}
[SimpleApp2] WARNING | Config option `configD` not recognized by `SimpleApp2`.  Did you mean one of: `configA, configB, configC`?
[SimpleApp2] Config {'SimpleApp2': {'configD': 'ConfigD from file'}}
[SimpleApp1] Config {'SimpleApp1': {'configA': 'ConfigA from command line', 'configB': 'ConfigB from file', 'configC': 'ConfigC from file'}}
```

## Only Extension 2

Now stop agin the server and start with only `Extension 2`.

```bash
# Start the jupyter server extension simple_ext2, it will NOT load simple_ext1 because of load_other_extensions = False.
jupyter simple-ext2
```

Try with the above links to check that only Extension 2 is responding (Extension 1 URLs should give you an 404 error).

## Extension 11 extends Extension 1

`Extension 11` extends `Extension 1` and brings a few more configs.

```bash
# TODO `--generate-config` returns an exception `"The ExtensionApp has not ServerApp "`
jupyter simple-ext11 --generate-config && vi ~/.jupyter/jupyter_config.py`.
```

The generated configuration should contains the following.

```bash
# TODO
```

The `hello`, `ignore_js` and `simple11_dir` are traits defined on the SimpleApp11 class.

It also implements additional flags and aliases for these traits.

- The `--hello` flag will log on startup `Hello Simple11 - You have provided the --hello flag or defined a c.SimpleApp1.hello == True`
- The `ignore_js` flag
- The `--simple11-dir` alias will set `SimpleExt11.simple11_dir` settings

Stop any running server and then start the simple-ext11.

```bash
jupyter simple-ext11 --hello --simple11-dir any_folder
# You can also launch with a module
python -m simple_ext11 --hello
# TODO FIX the following command, simple11 does not work launching with jpserver_extensions parameter.
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
