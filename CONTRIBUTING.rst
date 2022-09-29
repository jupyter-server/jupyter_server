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

The development version of the server requires `node <https://nodejs.org/en/download/>`_ and `pip <https://pip.pypa.io/en/stable/installing/>`_.

Once you have installed the dependencies mentioned above, use the following
steps::

    pip install --upgrade pip
    git clone https://github.com/jupyter/jupyter_server
    cd jupyter_server
    pip install -e ".[test]"

If you are using a system-wide Python installation and you only want to install the server for you,
you can add ``--user`` to the install commands.

Once you have done this, you can launch the main branch of Jupyter server
from any directory in your system with::

    jupyter server


Code Styling
-----------------------------
`jupyter_server` has adopted automatic code formatting so you shouldn't
need to worry too much about your code style.
As long as your code is valid,
the pre-commit hook should take care of how it should look.
`pre-commit` and its associated hooks will automatically be installed when
you run ``pip install -e ".[test]"``

To install ``pre-commit`` hook manually, run the following::

    pre-commit install


You can invoke the pre-commit hook by hand at any time with::

    pre-commit run

which should run any autoformatting on your code
and tell you about any errors it couldn't fix automatically.
You may also install `black integration <https://github.com/psf/black#editor-integration>`_
into your text editor to format code automatically.

If you have already committed files before setting up the pre-commit
hook with ``pre-commit install``, you can fix everything up using
``pre-commit run --all-files``. You need to make the fixing commit
yourself after that.

Some of the hooks only run on CI by default, but you can invoke them by
running with the ``--hook-stage manual`` argument.

Troubleshooting the Installation
--------------------------------

If you do not see that your Jupyter Server is not running on dev mode, it's possible that you are
running other instances of Jupyter Server. You can try the following steps:

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

Install dependencies::

    pip install -e .[test]
    pip install -e examples/simple  # to test the examples

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

Install the docs requirements using ``pip``::

    pip install .[doc]

Once you have installed the required packages, you can build the docs with::

    cd docs
    make html

You can also run the tests using ``hatch`` without installing test dependencies
in your local environment.

    pip install hatch
    hatch run docs:build

You can also drop into a shell in the docs environment by running::

    hatch -e docs shell

After that, the generated HTML files will be available at
``build/html/index.html``. You may view the docs in your browser.

Windows users can find ``make.bat`` in the ``docs`` folder.

You should also have a look at the `Project Jupyter Documentation Guide`__.

__ https://jupyter.readthedocs.io/en/latest/contributing/content-contributor.html
