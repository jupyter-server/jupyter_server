==================================
Jupyter Server (Developer Preview)
==================================

Jupyter Server is a fork of the `Jupyter Notebook`_'s Tornado_ Server. It provides all the core services, APIs and `REST endpoints`_ from the classic Notebook Server without the Jupyter Notebook (Javascript) frontend. In fact, the Jupyter Server provides no frontend out-of-the-box; rather, it exposes `hooks <frontends.html>`_ for Jupyter frontend creators to register their frontends with the Server. 

Before the Jupyter Server project, the `Jupyter Notebook`_ was the only first-class frontend to the Tornado Server. As a consequence, other Jupyter frontends had to include Jupyter Notebook (and all of its Javascript code) as a dependency. The Jupyter Server project views all frontends—including the `Jupyter Notebook`_—as equal and separate . 

.. _Tornado: https://www.tornadoweb.org/en/stable/
.. _Jupyter Notebook: https://github.com/jupyter/notebook
.. _REST endpoints: http://petstore.swagger.io/?url=https://raw.githubusercontent.com/jupyter/notebook/master/notebook/services/api/api.yaml

Installation
------------

To install the latest release of ``jupyter_server``, use *pip*:

.. code-block:: bash

    pip install jupyter_server


.. toctree::
   :maxdepth: 1
   :caption: Table of Contents

   frontends
   changelog

.. toctree::
   :maxdepth: 1
   :caption: Configuration

   config_overview
   config
   migrate_from_notebook
   public_server
   security
   extending/index.rst

.. toctree::
   :maxdepth: 1
   :caption: Contributor Documentation

   contributing