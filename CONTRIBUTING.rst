Contributing to the Jupyter Server
==================================

If you're reading this section, you're probably interested in contributing to
Jupyter.  Welcome and thanks for your interest in contributing!

Please take a look at the Contributor documentation, familiarize yourself with
using the Jupyter Server, and introduce yourself on the mailing list and
share what area of the project you are interested in working on.

General Guidelines
------------------

For general documentation about contributing to Jupyter projects, see the
`Project Jupyter Contributor Documentation`__.

__ https://jupyter.readthedocs.io/en/latest/contributor/content-contributor.html

Setting Up a Development Environment
------------------------------------

Installing the Jupyter Server
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Once you have installed the dependencies mentioned above, use the following
steps::

    pip install --upgrade setuptools pip
    git clone https://github.com/jupyter/jupyter_server
    cd jupyter_server
    pip install -e .

If you are using a system-wide Python installation and you only want to install the server for you,
you can add ``--user`` to the install commands.

Once you have done this, you can launch the master branch of Jupyter server
from any directory in your system with::

    jupyter server

Troubleshooting the Installation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you do not see that your Jupyter Server is not running on dev mode, it's possible that you are
running other instances of Jupyter Server. You can try the following steps:

1. Uninstall all instances of the jupyter_server package. These include any installations you made using
   pip or conda
2. Run ``python3 -m pip install -e .`` in the jupyter_server repository to install the jupyter_server from there
3. Run ``npm run build`` to make sure the Javascript and CSS are updated and compiled
4. Launch with ``python3 -m jupyter_server --port 8989``, and check that the browser is pointing to ``localhost:8989``
   (rather than the default 8888). You don't necessarily have to launch with port 8989, as long as you use
   a port that is neither the default nor in use, then it should be fine.
5. Verify the installation with the steps in the previous section.

Running Tests
-------------

Python Tests
^^^^^^^^^^^^

Install dependencies::

    pip install -e .[test]

To run the Python tests, use::

    pytest

If you want coverage statistics as well, you can run::

    py.test --cov notebook -v --pyargs jupyter_server

Building the Documentation
--------------------------

To build the documentation you'll need `Sphinx <http://www.sphinx-doc.org/>`_,
`pandoc <http://pandoc.org/>`_ and a few other packages.

To install (and activate) a `conda environment`_ named ``server_docs``
containing all the necessary packages (except pandoc), use::

    conda env create -f docs/environment.yml
    source activate server_docs  # Linux and OS X
    activate notebook_docs         # Windows

.. _conda environment:
    https://conda.io/docs/user-guide/tasks/manage-environments.html#creating-an-environment-from-an-environment-yml-file

If you want to install the necessary packages with ``pip`` instead::

    pip install -r docs/doc-requirements.txt

Once you have installed the required packages, you can build the docs with::

    cd docs
    make html

After that, the generated HTML files will be available at
``build/html/index.html``. You may view the docs in your browser.

You can automatically check if all hyperlinks are still valid::

    make linkcheck

Windows users can find ``make.bat`` in the ``docs`` folder.

You should also have a look at the `Project Jupyter Documentation Guide`__.

__ https://jupyter.readthedocs.io/en/latest/contrib_docs/index.html
