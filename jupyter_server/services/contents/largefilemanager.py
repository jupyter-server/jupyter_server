import base64
import os

from anyio.to_thread import run_sync
from tornado import web

from jupyter_server.services.contents.filemanager import (
    AsyncFileContentsManager,
    FileContentsManager,
)


class LargeFileManager(FileContentsManager):
    """Handle large file upload."""
    pass

class AsyncLargeFileManager(AsyncFileContentsManager):
    """Handle large file upload asynchronously"""
    pass