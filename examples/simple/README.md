# Jupyter Server Simple Extension Example

This folder contains an example of 2 simple extensions on top of Jupyter Server.

## Install

You need `python3` to build and run the server extensions.

```bash
conda create -y -n jext python=3.7
conda activate jext
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

Now you can render Server content in your browser.

```bash
# Default server page should redirect to `/static/simple_ext1/favicon.ico`.
open http://localhost:8888
```

Render Extension 1 Server content in your browser.
x
```bash
# Jupyter Server Home Page
open http://localhost:8888/
# TODO Fix Default URL.
# Home page as defined by default_url = '/template1/home'.
open http://localhost:8888/simple_ext1/
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

Render Extension 2 Server content in your browser.

```bash
# HTML static page.
open http://localhost:8888/static/simple_ext2/test.html
# Content from Handlers.
open http://localhost:8888/simple_ext2/params/test?var1=foo
```

## Start only Extension 2

Now stop the server and start again with only Extension 2.

```bash
# Start the jupyter server extension simple_ext2, it will NOT load simple_ext1 because of load_other_extensions = False.
jupyter simple-ext2
```

Try with the above links to check that only Extension 2 is responding (Extension 1 URLs should give you an 404 error).
