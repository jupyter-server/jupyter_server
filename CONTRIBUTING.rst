Contributing to the Jupyter
===========================

If you're reading this section, you're probably interested in contributing to
Jupyter.  Welcome and thanks for your interest in contributing!

Please take a look at the Contributor documentation, familiarize yourself with
using the Jupyter Server, and introduce yourself on the mailing list and share
what area of the project you are interested in working on.

General Guidelines
------------------

For general documentation about contributing to Jupyter projects, see the
`Project Jupyter Contributor Documentation`__.

__ http://jupyter.readthedocs.io/en/latest/contributor/content-contributor.html


Setting Up a Development Environment
------------------------------------

Installing the Jupyter Server
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Once you have installed the dependencies mentioned above, use the following
steps::

    pip install setuptools pip --upgrade --user
    git clone https://github.com/jupyter/jupyter_server
    cd jupyter_server
    pip install -e . 

Once you have done this, you can launch the master branch of Jupyter Server
from any directory in your system with::

    jupyter server

Running Tests
-------------

Install dependencies::

    pip install -e .[test] --user

To run the Python tests, use::

    nosetests

If you want coverage statistics as well, you can run::

    nosetests --with-coverage --cover-package=jupyter_server jupyter_server

Building the Documentation
--------------------------

To build the documentation you'll need `Sphinx <http://www.sphinx-doc.org/>`_, `pandoc <http://pandoc.org/>`_
and a few other packages.

To install (and activate) a `conda environment`_ named ``jupyter_server_docs``
containing all the necessary packages (except pandoc), use::

    conda env create -f docs/environment.yml
    source activate jupyter_server_docs  # Linux and OS X
    activate jupyter_server_docs         # Windows

.. _conda environment:
    http://conda.pydata.org/docs/using/envs.html#use-environment-from-file

If you want to install the necessary packages with ``pip`` instead, use
(omitting --user if working in a virtual environment)::

    pip install -r docs/doc-requirements.txt --user

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
