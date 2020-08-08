.. _user-installation:

Installation
============

Most Jupyter users will **never need to install Jupyter Server manually**. Jupyter Web applications will include the (correct version) of Jupyter Server as a dependency. It's best to let those applications handle installation, because they may require a specific version of Jupyter Server.

If you decide to install manually, run:

.. code-block:: bash

    pip install jupyter_server


You upgrade or downgrade to a specific version of Jupyter Server by adding an operator to the command above:

.. code-block:: bash

    pip install jupyter_server==1.0


To see what each version has to offer, checkout our :ref:`changelog`.
