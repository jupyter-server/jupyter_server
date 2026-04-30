General Jupyter contributor guidelines
======================================

If you're reading this section, you're probably interested in contributing to
Jupyter.  Welcome and thanks for your interest in contributing!

Please take a look at the Contributor documentation, familiarize yourself with
using the Jupyter Server, and introduce yourself on the mailing list and
share what area of the project you are interested in working on.

For general documentation about contributing to Jupyter projects, see the
`Project Jupyter Contributor Documentation`__.

__ https://jupyter.readthedocs.io/en/latest/contributing/content-contributor.html

Setting Up a Development Environment
====================================

Installing the Jupyter Server
-----------------------------

Developing on Jupyter Server requires Python, pip, and Git to be installed on your system.
The minimum supported Python version for Jupyter Server can be found in the ``pyproject.toml``.


First clone your fork of the repository::

    git clone https://github.com/<your_org_name>/jupyter_server
    cd jupyter_server

Then choose one of the following environment setup options. Any of them will work. Picking one is a matter of
personal preference.

Option 1: ``pip`` + ``venv``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the most direct setup, avoiding any additional tool installations::

    python -m venv .venv
    source .venv/bin/activate
    python -m pip install --upgrade pip
    python -m pip install -e ".[test]"

On Windows, activate the environment with::

    .venv\Scripts\activate

Option 2: ``conda``
~~~~~~~~~~~~~~~~~~~

Many Jupyter projects and contributors use ``conda`` or ``mamba`` for local
development instead::

    conda create -n jupyter-server-dev python=3.12 pip
    conda activate jupyter-server-dev
    python -m pip install -e ".[test]"


With your ``venv`` or ``conda`` environment activated, you can run the server with::

    jupyter server

Option 3: ``uv``
~~~~~~~~~~~~~~~~

`uv <https://docs.astral.sh/uv/>`_ is a more recent option for Python project management.
It can set up your environment with a single command::

    uv sync --extra test

This creates a local ``.venv`` automatically if needed. To activate it
yourself, run::

    source .venv/bin/activate

On Windows, use::

    .venv\Scripts\activate


When using ``uv`` you can run the server with::

    uv run jupyter server


Code Styling and Quality Checks
-------------------------------
``jupyter_server`` has adopted automatic code formatting so you shouldn't
need to worry too much about your code style.
As long as your code is valid,
the pre-commit hook should take care of how it should look.
``pre-commit`` and its associated hooks are included in the ``test`` dependency group
and therefore, would be installed in any of the three installation options above.

To install ``pre-commit`` hook manually, run the following::

    pre-commit install


You can invoke the pre-commit hook by hand at any time with::

    pre-commit run

which will run any autoformatting on your code
and tell you about any errors it couldn't fix automatically.
You may also install `black integration <https://github.com/psf/black#editor-integration>`_
into your text editor to format code automatically.

If you have already committed files before setting up the pre-commit
hook with ``pre-commit install``, you can fix everything up using
``pre-commit run --all-files``. You need to make the fixing commit
yourself after that.

Some of the hooks only run on CI by default, but you can invoke them by
running with the ``--hook-stage manual`` argument.

There are three hatch scripts that can be run locally as well:
``hatch run lint:build`` will enforce styling.  ``hatch run typing:test`` will
run the type checker.

Troubleshooting the Installation
--------------------------------

If you do not see that your Jupyter Server is running in dev mode, it's possible that you are
running other instances of Jupyter Server elsewhere on your system. You can try the following steps:

1. Uninstall all instances of the jupyter_server package. These include any installations you made using
   pip or conda
2. Run ``python -m pip install -e .`` in the jupyter_server repository to install the jupyter_server from there
3. Run ``npm run build`` to make sure the Javascript and CSS are updated and compiled
4. Launch with ``python -m jupyter_server --port 8989``, and check that the browser is pointing to ``localhost:8989``
   (rather than the default 8888). You don't necessarily have to launch with port 8989, as long as you use
   a port that is neither the default nor in use, then it should be fine.
5. Verify the installation with the steps in the previous section.

Running Tests
=============

If you used one of the environment setup options above, the test dependencies
are already installed. Otherwise install them with::

    python -m pip install -e ".[test]"
    python -m pip install -e examples/simple  # to test the examples

To run the Python tests, use::

    pytest
    pytest examples/simple  # to test the examples

You can also run the tests using ``hatch`` without installing test dependencies in your local environment::

    pip install hatch
    hatch run test:test

The command takes any argument that you can give to ``pytest``, e.g.::

    hatch run test:test -k name_of_method_to_test

You can also drop into a shell in the test environment by running::

    hatch -e test shell

Building the Docs
=================

Install the docs requirements into your active environment using ``pip``::

    python -m pip install -e ".[docs]"

Once you have installed the required packages, you can build the docs with::

    cd docs
    make html

You can also run the tests using ``hatch`` without installing test dependencies
in your local environment::

    pip install hatch
    hatch run docs:build

You can also drop into a shell in the docs environment by running::

    hatch -e docs shell

After that, the generated HTML files will be available at
``build/html/index.html``. You may view the docs in your browser.

Windows users can find ``make.bat`` in the ``docs`` folder.

You should also have a look at the `Project Jupyter Documentation Guide`__.

__ https://jupyter.readthedocs.io/en/latest/contributing/content-contributor.html
