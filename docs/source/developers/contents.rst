.. _contents_api:

Contents API
============

.. currentmodule:: jupyter_server.services.contents

The Jupyter Notebook web application provides a graphical interface for
creating, opening, renaming, and deleting files in a virtual filesystem.

The :class:`~manager.ContentsManager` class defines an abstract
API for translating these interactions into operations on a particular storage
medium. The default implementation,
:class:`~filemanager.FileContentsManager`, uses the local
filesystem of the server for storage and straightforwardly serializes notebooks
into JSON.  Users can override these behaviors by supplying custom subclasses
of ContentsManager.

This section describes the interface implemented by ContentsManager subclasses.
We refer to this interface as the **Contents API**.

Data Model
----------

.. currentmodule:: jupyter_server.services.contents.manager

Filesystem Entities
~~~~~~~~~~~~~~~~~~~
.. _notebook models:

ContentsManager methods represent virtual filesystem entities as dictionaries,
which we refer to as **models**.

Models may contain the following entries:

+--------------------+-----------+------------------------------+
| Key                | Type      |Info                          |
+====================+===========+==============================+
|**name**            |unicode    |Basename of the entity.       |
+--------------------+-----------+------------------------------+
|**path**            |unicode    |Full                          |
|                    |           |(:ref:`API-style<apipaths>`)  |
|                    |           |path to the entity.           |
+--------------------+-----------+------------------------------+
|**type**            |unicode    |The entity type. One of       |
|                    |           |``"notebook"``, ``"file"`` or |
|                    |           |``"directory"``.              |
+--------------------+-----------+------------------------------+
|**created**         |datetime   |Creation date of the entity.  |
+--------------------+-----------+------------------------------+
|**last_modified**   |datetime   |Last modified date of the     |
|                    |           |entity.                       |
+--------------------+-----------+------------------------------+
|**content**         |variable   |The "content" of the entity.  |
|                    |           |(:ref:`See                    |
|                    |           |Below<modelcontent>`)         |
+--------------------+-----------+------------------------------+
|**mimetype**        |unicode or |The mimetype of ``content``,  |
|                    |``None``   |if any.  (:ref:`See           |
|                    |           |Below<modelcontent>`)         |
+--------------------+-----------+------------------------------+
|**format**          |unicode or |The format of ``content``,    |
|                    |``None``   |if any. (:ref:`See            |
|                    |           |Below<modelcontent>`)         |
+--------------------+-----------+------------------------------+

.. _modelcontent:

Certain model fields vary in structure depending on the ``type`` field of the
model. There are three model types: **notebook**, **file**, and **directory**.

- ``notebook`` models
    - The ``format`` field is always ``"json"``.
    - The ``mimetype`` field is always ``None``.
    - The ``content`` field contains a
      :class:`nbformat.notebooknode.NotebookNode` representing the .ipynb file
      represented by the model.  See the `NBFormat`_ documentation for a full
      description.

- ``file`` models
    - The ``format`` field is either ``"text"`` or ``"base64"``.
    - The ``mimetype`` field is ``text/plain`` for text-format models and
      ``application/octet-stream`` for base64-format models.
    - The ``content`` field is always of type ``unicode``.  For text-format
      file models, ``content`` simply contains the file's bytes after decoding
      as UTF-8.  Non-text (``base64``) files are read as bytes, base64 encoded,
      and then decoded as UTF-8.

- ``directory`` models
    - The ``format`` field is always ``"json"``.
    - The ``mimetype`` field is always ``None``.
    - The ``content`` field contains a list of :ref:`content-free<contentfree>`
      models representing the entities in the directory.

.. note::

   .. _contentfree:

   In certain circumstances, we don't need the full content of an entity to
   complete a Contents API request.  In such cases, we omit the ``mimetype``,
   ``content``, and ``format`` keys from the model. This most commonly occurs
   when listing a directory, in which circumstance we represent files within
   the directory as content-less models to avoid having to recursively traverse
   and serialize the entire filesystem.

**Sample Models**

.. code-block:: python

    # Notebook Model with Content
    {
        'content': {
            'metadata': {},
            'nbformat': 4,
            'nbformat_minor': 0,
            'cells': [
                {
                    'cell_type': 'markdown',
                    'metadata': {},
                    'source': 'Some **Markdown**',
                },
            ],
        },
        'created': datetime(2015, 7, 25, 19, 50, 19, 19865),
        'format': 'json',
        'last_modified': datetime(2015, 7, 25, 19, 50, 19, 19865),
        'mimetype': None,
        'name': 'a.ipynb',
        'path': 'foo/a.ipynb',
        'type': 'notebook',
        'writable': True,
    }

    # Notebook Model without Content
    {
        'content': None,
        'created': datetime.datetime(2015, 7, 25, 20, 17, 33, 271931),
        'format': None,
        'last_modified': datetime.datetime(2015, 7, 25, 20, 17, 33, 271931),
        'mimetype': None,
        'name': 'a.ipynb',
        'path': 'foo/a.ipynb',
        'type': 'notebook',
        'writable': True
    }


API Paths
~~~~~~~~~
.. _apipaths:

ContentsManager methods represent the locations of filesystem resources as
**API-style paths**.  Such paths are interpreted as relative to the root
directory of the notebook server.  For compatibility across systems, the
following guarantees are made:

* Paths are always ``unicode``, not ``bytes``.
* Paths are not URL-escaped.
* Paths are always forward-slash (/) delimited, even on Windows.
* Leading and trailing slashes are stripped.  For example, ``/foo/bar/buzz/``
  becomes ``foo/bar/buzz``.
* The empty string (``""``) represents the root directory.


Writing a Custom ContentsManager
--------------------------------

The default ContentsManager is designed for users running the notebook as an
application on a personal computer.  It stores notebooks as .ipynb files on the
local filesystem, and it maps files and directories in the Notebook UI to files
and directories on disk.  It is possible to override how notebooks are stored
by implementing your own custom subclass of ``ContentsManager``. For example,
if you deploy the notebook in a context where you don't trust or don't have
access to the filesystem of the notebook server, it's possible to write your
own ContentsManager that stores notebooks and files in a database.


Required Methods
~~~~~~~~~~~~~~~~

A minimal complete implementation of a custom
:class:`~manager.ContentsManager` must implement the following
methods:

.. autosummary::
   ContentsManager.get
   ContentsManager.save
   ContentsManager.delete_file
   ContentsManager.rename_file
   ContentsManager.file_exists
   ContentsManager.dir_exists
   ContentsManager.is_hidden

You may be required to specify a Checkpoints object, as the default one,
``FileCheckpoints``, could be incompatible with your custom
ContentsManager.

Customizing Checkpoints
-----------------------
.. currentmodule:: jupyter_server.services.contents.checkpoints

Customized Checkpoint definitions allows behavior to be
altered and extended.

The ``Checkpoints`` and ``GenericCheckpointsMixin`` classes
(from :mod:`jupyter_server.services.contents.checkpoints`)
have reusable code and are intended to be used together,
but require the following methods to be implemented.

.. autosummary::
   Checkpoints.rename_checkpoint
   Checkpoints.list_checkpoints
   Checkpoints.delete_checkpoint
   GenericCheckpointsMixin.create_file_checkpoint
   GenericCheckpointsMixin.create_notebook_checkpoint
   GenericCheckpointsMixin.get_file_checkpoint
   GenericCheckpointsMixin.get_notebook_checkpoint

No-op example
~~~~~~~~~~~~~

Here is an example of a no-op checkpoints object - note the mixin
comes first. The docstrings indicate what each method should do or
return for a more complete implementation.

.. code-block:: python

    class NoOpCheckpoints(GenericCheckpointsMixin, Checkpoints):
        """requires the following methods:"""
        def create_file_checkpoint(self, content, format, path):
            """ -> checkpoint model"""
        def create_notebook_checkpoint(self, nb, path):
            """ -> checkpoint model"""
        def get_file_checkpoint(self, checkpoint_id, path):
            """ -> {'type': 'file', 'content': <str>, 'format': {'text', 'base64'}}"""
        def get_notebook_checkpoint(self, checkpoint_id, path):
            """ -> {'type': 'notebook', 'content': <output of nbformat.read>}"""
        def delete_checkpoint(self, checkpoint_id, path):
            """deletes a checkpoint for a file"""
        def list_checkpoints(self, path):
            """returns a list of checkpoint models for a given file,
            default just does one per file
            """
            return []
        def rename_checkpoint(self, checkpoint_id, old_path, new_path):
            """renames checkpoint from old path to new path"""

See ``GenericFileCheckpoints`` in :mod:`notebook.services.contents.filecheckpoints`
for a more complete example.

Testing
-------
.. currentmodule:: jupyter_server.services.contents.tests

:mod:`jupyter_server.services.contents.tests` includes several test suites written
against the abstract Contents API.  This means that an excellent way to test a
new ContentsManager subclass is to subclass our tests to make them use your
ContentsManager.

.. note::

   PGContents_ is an example of a complete implementation of a custom
   ``ContentsManager``.  It stores notebooks and files in PostgreSQL_ and encodes
   directories as SQL relations.  PGContents also provides an example of how to
   re-use the notebook's tests.

.. _NBFormat: https://nbformat.readthedocs.io/en/latest/index.html
.. _PGContents: https://github.com/quantopian/pgcontents
.. _PostgreSQL: https://www.postgresql.org/

Asynchronous Support
--------------------

An asynchronous version of the Contents API is available to run slow IO processes concurrently.

- :class:`~manager.AsyncContentsManager`
- :class:`~filemanager.AsyncFileContentsManager`
- :class:`~largefilemanager.AsyncLargeFileManager`
- :class:`~checkpoints.AsyncCheckpoints`
- :class:`~checkpoints.AsyncGenericCheckpointsMixin`

.. note::

   .. _asynccontents:

   In most cases, the non-asynchronous Contents API is performant for local filesystems.
   However, if the Jupyter Notebook web application is interacting with a high-latent virtual filesystem, you may see performance gains by using the asynchronous version.
   For example, if you're experiencing terminal lag in the web application due to the slow and blocking file operations, the asynchronous version can reduce the lag.
   Before opting in, comparing both non-async and async options' performances is recommended.
