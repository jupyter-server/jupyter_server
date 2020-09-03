Depending on Jupyter Server
===========================

If your project depends directly on Jupyter Server, be sure to watch Jupyter Server's :ref:`Change Log <changelog>` and pin your project to a version that works for your application. Major releases represent possible backwards-compatibility breaking API changes or features.

When a new major version in released on PyPI, a branch for that version will be created in this repository, and the version of the master branch will be bumped to the next major version number. That way, the master branch always reflects the latest un-released version.

To see the changes between releases, checkout the :ref:`Change Log <changelog>`.

To install the latest patch of a given version:

.. code-block:: console

    > pip install jupyter_server --upgrade


To pin your jupyter_server install to a specific version:

.. code-block:: console

    > pip install jupyter_server==1.0.0
