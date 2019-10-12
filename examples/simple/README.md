# Jupyter Server Simple Extension Example

This folder contains an example of 2 simple extensions on top of Jupyter Server.

OPTIONAL (compiled js is provided) If you want to build the typescript code, you need npm installed.

```bash
make install-ts
make build-ts
```

You need python3 to build and run the extensions.

```bash
conda create -y -n jext python=3.7
conda activate jext
make build
```

```bash
# Start the jupyter server, it will load both simple_ext1 and simple_ext2 based on the provided trait.
make start1+2
```

Optionally, you can copy `simple_ext.json` configuration to your env `etc` folder and start only App 1.

```bash
make uninstall
make install
cp -r ./etc $(dirname $(which jupyter))/..
# Start the jupyter server extension simple_ext1, it will also load simple_ext2 because of load_other_extensions = True..
make start1
```

Render default Server content in your browser.

```bash
# Default server page.
open http://localhost:8888
```

Render Extension 1 Server content in your browser.

```bash
# Favicon static content.
open http://localhost:8888/static/simple_ext1/favicon.ico
# HTML static page.
open http://localhost:8888/static/simple_ext1/test.html
# Content from Handlers.
open http://localhost:8888/simple_ext1/params/test?var1=foo
# Content from Template.
open http://localhost:8888/simple_ext1/page1/test
# Content from Template with Typescript.
open http://localhost:8888/simple_ext1
open http://localhost:8888/simple_ext1/template
# Error content.
open http://localhost:8888/simple_ext1/nope
```

Render Extension 2 Server content in your browser.

```bash
# HTML static page.
open http://localhost:8888/static/simple_ext2/test.html
# Content from Handlers.
open http://localhost:8888/simple_ext2/params/test?var1=foo
```

Now stop the server and start again with only Extension 2.

```bash
# Start the jupyter server extension simple_ext2, it will NOT load simple_ext1 because of load_other_extensions = False.
make start2
```

Try with the above links to check that only Extension 2 is responding.

## TODO

+ Automatic redirect on the default home page.
