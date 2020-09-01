"""Serve files directly from the ContentsManager."""

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

import os
import pathlib
import mimetypes
import json
import zipfile
import tarfile
from base64 import decodebytes
from tornado import web
from tornado import ioloop
from jupyter_server.base.handlers import JupyterHandler
from jupyter_server.utils import url2path


class FilesHandler(JupyterHandler):
    """serve files via ContentsManager

    Normally used when ContentsManager is not a FileContentsManager.

    FileContentsManager subclasses use AuthenticatedFilesHandler by default,
    a subclass of StaticFileHandler.
    """

    @property
    def content_security_policy(self):
        # In case we're serving HTML/SVG, confine any Javascript to a unique
        # origin so it can't interact with the notebook server.
        return (
            super(FilesHandler, self).content_security_policy
            + "; sandbox allow-scripts"
        )

    @web.authenticated
    def head(self, path):
        self.get(path, include_body=False)

    @web.authenticated
    async def get(self, path, include_body=True):
        cm = self.contents_manager

        if cm.is_hidden(path) and not cm.allow_hidden:
            self.log.info("Refusing to serve hidden file, via 404 Error")
            raise web.HTTPError(404)

        path = path.strip("/")
        if "/" in path:
            _, name = path.rsplit("/", 1)
        else:
            name = path

        model = await cm.get(path, type="file", content=include_body)

        if self.get_argument("download", False):
            self.set_attachment_header(name)

        # get mimetype from filename
        if name.lower().endswith(".ipynb"):
            self.set_header("Content-Type", "application/x-ipynb+json")
        else:
            cur_mime = mimetypes.guess_type(name)[0]
            if cur_mime == "text/plain":
                self.set_header("Content-Type", "text/plain; charset=UTF-8")
            elif cur_mime is not None:
                self.set_header("Content-Type", cur_mime)
            else:
                if model["format"] == "base64":
                    self.set_header("Content-Type", "application/octet-stream")
                else:
                    self.set_header("Content-Type", "text/plain; charset=UTF-8")

        if include_body:
            if model["format"] == "base64":
                b64_bytes = model["content"].encode("ascii")
                self.write(decodebytes(b64_bytes))
            elif model["format"] == "json":
                self.write(json.dumps(model["content"]))
            else:
                self.write(model["content"])
            self.flush()


# The delay in ms at which we send the chunk of data
# to the client.
ARCHIVE_DOWNLOAD_FLUSH_DELAY = 100

# Supported archive format
SUPPORTED_FORMAT = [
    "zip",
    "tgz",
    "tar.gz",
    "tbz",
    "tbz2",
    "tar.bz",
    "tar.bz2",
    "txz",
    "tar.xz",
]


DEFAULT_DIRECTORY_SIZE_LIMIT = 1073741824  # 1GB
DEFAULT_ARCHIVE_FORMAT = "zip"


class ArchiveStream:
    """ArchiveStream is an abstraction layer to a Python archive allowing
    to stream archive files.
    """

    def __init__(self, handler):
        self.handler = handler
        self.position = 0

    def write(self, data):
        self.position += len(data)
        self.handler.write(data)
        del data

    def tell(self):
        return self.position

    def flush(self):
        # Note: Flushing is done elsewhere, in the main thread
        # because `write()` is called in a background thread.
        # self.handler.flush()
        pass


def make_writer(handler, archive_format="zip"):
    """Given an handler object, create an `ArchiveStream` instance
    and setup an archive file object using the specified archive format.
    """
    fileobj = ArchiveStream(handler)

    if archive_format == "zip":
        archive_file = zipfile.ZipFile(
            fileobj, mode="w", compression=zipfile.ZIP_DEFLATED
        )
        archive_file.add = archive_file.write
    elif archive_format in ["tgz", "tar.gz"]:
        archive_file = tarfile.open(fileobj=fileobj, mode="w|gz")
    elif archive_format in ["tbz", "tbz2", "tar.bz", "tar.bz2"]:
        archive_file = tarfile.open(fileobj=fileobj, mode="w|bz2")
    elif archive_format in ["txz", "tar.xz"]:
        archive_file = tarfile.open(fileobj=fileobj, mode="w|xz")
    else:
        raise ValueError("'{}' is not a valid archive format.".format(archive_format))
    return archive_file


def get_folder_size(dir_path):
    """Return the size in bytes of a given directory.
    """
    dir_path = pathlib.Path(dir_path)
    return sum(f.stat().st_size for f in dir_path.glob("**/*") if f.is_file())


def make_reader(archive_path):
    """Return the appropriate archive file instance given
    the extension's path of `archive_path`.
    """

    archive_format = "".join(archive_path.suffixes)[1:]

    if archive_format == "zip":
        archive_file = zipfile.ZipFile(archive_path, mode="r")
    elif archive_format in ["tgz", "tar.gz"]:
        archive_file = tarfile.open(archive_path, mode="r|gz")
    elif archive_format in ["tbz", "tbz2", "tar.bz", "tar.bz2"]:
        archive_file = tarfile.open(archive_path, mode="r|bz2")
    elif archive_format in ["txz", "tar.xz"]:
        archive_file = tarfile.open(archive_path, mode="r|xz")
    else:
        raise ValueError("'{}' is not a valid archive format.".format(archive_format))
    return archive_file


class DirectoryHandler(JupyterHandler):
    """Download a directory. Since a folder can't be directly downloaded,
    it is first archived with or without compression before being downloaded from the client.
    The archive format (zip, tar.gz, etc) can be configured within the request.
    """

    @web.authenticated
    async def get(self, archive_path, include_body=False):

        # /directories/ requests must originate from the same site
        self.check_xsrf_cookie()
        cm = self.contents_manager

        if cm.is_hidden(archive_path) and not cm.allow_hidden:
            self.log.info("Refusing to serve hidden file, via 404 Error")
            raise web.HTTPError(404)

        archive_token = self.get_argument("archiveToken")
        archive_format = self.get_argument("archiveFormat", DEFAULT_ARCHIVE_FORMAT)
        folder_size_limit = self.get_argument("folderSizeLimit", None)

        # Check whether the specified archive format is supported.
        if archive_format not in SUPPORTED_FORMAT:
            self.log.error("Unsupported format {}.".format(archive_format))
            raise web.HTTPError(404)

        # If the folder size limit is not specified in the request, a
        # default size limit is used.
        try:
            folder_size_limit_num = int(folder_size_limit)

        except (ValueError, TypeError):
            self.log.warning(
                "folderSizeLimit is a not a valid number: {}.".format(folder_size_limit)
            )
            folder_size_limit_num = DEFAULT_DIRECTORY_SIZE_LIMIT

        root_dir = pathlib.Path(cm.root_dir)
        archive_path = root_dir / url2path(archive_path)
        archive_filename = archive_path.with_suffix(".{}".format(archive_format)).name

        # Check whether the archive folder is not larger than the size limit.
        folder_size = get_folder_size(archive_path)
        print(folder_size)
        if folder_size > folder_size_limit_num:
            self.log.error(
                "Archive folder size is larger than the size limit: {} bytes with a size limit of {}.".format(
                    folder_size, folder_size_limit_num
                )
            )
            raise web.HTTPError(413)

        self.log.info(
            "Prepare {} for archiving and downloading.".format(archive_filename)
        )
        self.set_header("content-type", "application/octet-stream")
        self.set_header("cache-control", "no-cache")
        self.set_header(
            "content-disposition", "attachment; filename={}".format(archive_filename)
        )

        self.canceled = False
        self.flush_cb = ioloop.PeriodicCallback(
            self.flush, ARCHIVE_DOWNLOAD_FLUSH_DELAY
        )
        self.flush_cb.start()

        args = (archive_path, archive_format, archive_token)
        await ioloop.IOLoop.current().run_in_executor(
            None, self.archive_and_download, *args
        )

        if self.canceled:
            self.log.info("Download canceled.")
        else:
            self.flush()
            self.log.info("Finished downloading {}.".format(archive_filename))

        self.set_cookie("archiveToken", archive_token)
        self.flush_cb.stop()
        self.finish()

    def archive_and_download(self, archive_path, archive_format, archive_token):

        with make_writer(self, archive_format) as archive:
            prefix = len(str(archive_path.parent)) + len(os.path.sep)
            for root, _, files in os.walk(archive_path):
                for file_ in files:
                    file_name = os.path.join(root, file_)
                    if not self.canceled:
                        self.log.debug("{}\n".format(file_name))
                        archive.add(file_name, os.path.join(root[prefix:], file_))
                    else:
                        break

    def on_connection_close(self):
        super().on_connection_close()
        self.canceled = True
        self.flush_cb.stop()


class ExtractDirectoryHandler(JupyterHandler):
    """Extract the content of an archive on the server side. Given an archive on
    the server side, this class allows to request extracting the content of the archive.
    The archive format is detected from the extension of the archive.
    """

    @web.authenticated
    async def get(self, archive_path, include_body=False):

        # /extract-archive/ requests must originate from the same site
        self.check_xsrf_cookie()
        cm = self.contents_manager

        if cm.is_hidden(archive_path) and not cm.allow_hidden:
            self.log.info("Refusing to serve hidden file, via 404 Error")
            raise web.HTTPError(404)

        root_dir = pathlib.Path(cm.root_dir)
        archive_path = root_dir / url2path(archive_path)

        await ioloop.IOLoop.current().run_in_executor(
            None, self.extract_archive, archive_path
        )

        self.finish()

    def extract_archive(self, archive_path):

        archive_destination = archive_path.parent
        self.log.info(
            "Begin extraction of {} to {}.".format(archive_path, archive_destination)
        )

        archive_reader = make_reader(archive_path)
        with archive_reader as archive:
            archive.extractall(archive_destination)

        self.log.info(
            "Finished extracting {} to {}.".format(archive_path, archive_destination)
        )


default_handlers = []
