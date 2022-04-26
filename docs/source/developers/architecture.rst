.. _architecture:

Architecture Diagrams
=====================

This page describes the Jupyter Server architecture and the main workflows.
This information is useful for developers who want to understand how Jupyter
Server components are connected and how the principal workflows look like.

To make changes for these diagrams, use `the Draw.io <https://app.diagrams.net/>`_
open source tool to edit the png file.


Jupyter Server Architecture
---------------------------

The Jupyter Server system can be seen in figure below:

.. image:: ../images/jupyter-server-architecture.drawio.png
   :alt: Jupyter Server Architecture
   :width: 100%
   :align: center

Jupyter Server contains the following components:

- **ServerApp** is the main Tornado-based application which connects all
  components together.

- **Config Manager** initializes configuration for the ServerApp. You can define
  custom classes for the Jupyter Server managers using this config and change
  SererApp settings. Follow :ref:`the Config File Guide <other-full-config>` to
  learn about configuration settings and how to build custom config.

- **Custom Extensions** allow you to create the custom Server's REST API endpoints.
  Follow :ref:`the Extension Guide <extensions>` to know more about extending
  ServerApp with extra request handlers.

- **Gateway Server** is a web server that, when configured, provides access to
  Jupyter Kernels running on other hosts. There are different ways to create a
  gateway server. If your ServerApp needs to communicate with remote Kernels
  residing within resource-managed clusters, you can use
  `Enterprise Gateway <https://github.com/jupyter-server/enterprise_gateway>`_,
  otherwise, you can use
  `Kernel Gateway <https://github.com/jupyter-server/kernel_gateway>`_, where
  Kernels run locally to the gateway server.

- **Contents Manager and File Contents Manager** are responsible for serving
  Notebook on the file system. Session Manager uses Contents Manager to receive
  Kernel path. Follow :ref:`the Contents API guide <contents_api>` to learn
  about Contents Manager.

- **Session Manager** processes users' Sessions. When a user starts a new Kernel,
  Session Manager starts a process to provision Kernel for the user and generates
  a new Session ID. Each opened Notebook has a separate Session, but different
  Notebook Kernels can use the same Session. That is useful if the user wants to
  share data across various opened Notebooks. Session Manager uses SQLite3
  DataBase to store the Session information. The database is stored in memory by
  default, but can be configured to save to disk.

- **Mapping Kernel Manager** is responsible for managing the lifecycles of the
  Kernels running within the ServerApp. It starts a new Kernel for a user's Session
  and facilitates interrupt, restart, and shutdown operations against the Kernel.

- **Jupyter Client** library is used by Jupyter Server to work with the Notebook
  Kernels.

  - **Kernel Manager** manages a single Kernel for the Notebook. To know more about
    Kernel Manager, follow
    `the Jupyter Client APIs documentation <https://jupyter-client.readthedocs.io/en/latest/api/manager.html#jupyter_client.KernelManager>`_.

  - **Kernel Spec Manager** parses files with JSON specification for a Kernels,
    and provides a list of available Kernel configurations. To learn about
    Kernel Spec, check `the Jupyter Client guide <https://jupyter-client.readthedocs.io/en/stable/kernels.html#kernel-specs>`_.
