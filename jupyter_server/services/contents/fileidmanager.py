import os
import sqlite3
import stat
from typing import Optional

from jupyter_core.paths import jupyter_data_dir
from traitlets import TraitError, Unicode, validate
from traitlets.config.configurable import LoggingConfigurable


class StatStruct:
    empty = True
    ino: int
    crtime: Optional[int]
    mtime: int
    is_dir: bool


class FileIdManager(LoggingConfigurable):
    """
    Manager that supports tracks files across their lifetime by associating
    each with a unique file ID, which is maintained across filesystem operations.

    Notes
    -----

    All private helper methods prefixed with an underscore (except `__init__()`)
    do NOT commit their SQL statements in a transaction via `self.con.commit()`.
    This responsibility is delegated to the public method calling them to
    increase performance. Committing multiple SQL transactions in serial is much
    slower than committing a single SQL transaction wrapping all SQL statements
    performed during a method's procedure body.
    """

    root_dir = Unicode(
        help=("The root being served by Jupyter server. Must be an absolute path."), config=True
    )

    db_path = Unicode(
        default_value=os.path.join(jupyter_data_dir(), "file_id_manager.db"),
        help=(
            "The path of the DB file used by `FileIdManager`. "
            "Defaults to `jupyter_data_dir()/file_id_manager.db`."
        ),
        config=True,
    )

    def __init__(self, *args, **kwargs):
        # pass args and kwargs to parent Configurable
        super().__init__(*args, **kwargs)
        # initialize connection with db
        self.con = sqlite3.connect(self.db_path)
        self.log.debug("FileIdManager : Creating File ID tables and indices")
        self.con.execute(
            "CREATE TABLE IF NOT EXISTS Files("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            # uniqueness constraint relaxed here because we need to keep records
            # of deleted files which may occupy same path
            "path TEXT NOT NULL, "
            "ino INTEGER NOT NULL UNIQUE, "
            "crtime INTEGER, "
            "mtime INTEGER NOT NULL, "
            "is_dir TINYINT NOT NULL"
            ")"
        )
        self._index_all()
        self.con.execute("CREATE INDEX IF NOT EXISTS ix_Files_path ON Files (path)")
        self.con.execute("CREATE INDEX IF NOT EXISTS ix_Files_ino ON Files (ino)")
        self.con.execute("CREATE INDEX IF NOT EXISTS ix_Files_is_dir ON Files (is_dir)")
        self.con.commit()

    @validate("root_dir", "db_path")
    def _validate_abspath_traits(self, proposal):
        if proposal["value"] is None:
            raise TraitError("FileIdManager : %s must not be None" % proposal["trait"].name)
        if not os.path.isabs(proposal["value"]):
            raise TraitError("FileIdManager : %s must be an absolute path" % proposal["trait"].name)
        return self._normalize_path(proposal["value"])

    def _index_all(self):
        """Recursively indexes all directories under the server root."""
        self._index_dir_recursively(self.root_dir, self._stat(self.root_dir))

    def _index_dir_recursively(self, dir_path, stat_info):
        """Recursively indexes all directories under a given path."""
        self.index(dir_path, stat_info=stat_info, commit=False)

        with os.scandir(dir_path) as scan_iter:
            for entry in scan_iter:
                if entry.is_dir():
                    self._index_dir_recursively(entry.path, self._parse_raw_stat(entry.stat()))
        scan_iter.close()

    def _sync_all(self):
        """Syncs Files table with the filesystem and ensures that the correct
        path is associated with each file ID. Does so by traversing the file
        tree recursively, looking for dirty directories. A dirty directory is a
        directory that possibly contains previously indexed files which were
        moved into it.  An unindexed directory is always dirty, whereas an
        indexed directory is dirty only if the `mtime` in the record and the
        current `mtime` differ."""
        cursor = self.con.execute("SELECT id, path, mtime FROM Files WHERE is_dir = 1")
        for dir in cursor:
            id, path, old_mtime = dir
            stat_info = self._stat(path)

            # ignore directories that no longer exist
            if stat_info is None:
                continue

            new_mtime = stat_info.mtime
            dir_dirty = new_mtime != old_mtime
            if dir_dirty:
                self._sync_dir(path)
                self._update(id, stat_info)

    def _sync_dir(self, dir_path):
        """Syncs the contents of a directory. Indexes previously unindexed
        directories and recursively syncs their contents."""
        with os.scandir(dir_path) as scan_iter:
            for entry in scan_iter:
                stat_info = self._parse_raw_stat(entry.stat())
                id = self._sync_file(entry.path, stat_info)

                # treat unindexed directories as dirty. create a new record and
                # recursive sync dir contents.
                if stat_info.is_dir and id is None:
                    self._create(entry.path, stat_info)
                    self._sync_dir(entry.path)
        scan_iter.close()

    def _sync_file(self, path, stat_info):
        """Syncs the file at path with the Files table by detecting whether the
        file was previously indexed but moved. Updates the record with the new
        path and returns the file ID if the file was previously indexed. Returns
        None otherwise."""
        src = self.con.execute(
            "SELECT id, crtime, mtime FROM Files WHERE ino = ?", (stat_info.ino,)
        ).fetchone()

        # if no record with matching ino, then return None
        if not src:
            return None

        id, src_crtime, src_mtime = src
        src_timestamp = src_crtime if src_crtime is not None else src_mtime
        dst_timestamp = stat_info.crtime if stat_info.crtime is not None else stat_info.mtime

        # if record has identical ino and crtime/mtime to an existing record,
        # update it with new destination path and stat info, returning its id
        if src_timestamp == dst_timestamp:
            self._update(id, stat_info, path)
            return id

        # otherwise delete the existing record with identical `ino`, since inos
        # must be unique. then return None
        self.con.execute("DELETE FROM Files WHERE id = ?", (id,))
        return None

    def _normalize_path(self, path):
        """Normalizes a given file path."""
        if not os.path.isabs(path):
            path = os.path.join(self.root_dir, path)
        path = os.path.normcase(path)
        path = os.path.normpath(path)
        return path

    def _parse_raw_stat(self, raw_stat, stat_info=None):
        """Accepts an `os.stat_result` object and returns a `StatStruct`
        object. Writes to `stat_info` argument if passed."""
        if stat_info is None:
            stat_info = StatStruct()

        stat_info.empty = False
        stat_info.ino = raw_stat.st_ino
        stat_info.crtime = (
            raw_stat.st_ctime_ns
            if os.name == "nt"
            # st_birthtime_ns is not supported, so we have to compute it manually
            else int(raw_stat.st_birthtime * 1e9)
            if hasattr(raw_stat, "st_birthtime")
            else None
        )
        stat_info.mtime = raw_stat.st_mtime_ns
        stat_info.is_dir = stat.S_ISDIR(raw_stat.st_mode)

        return stat_info

    def _stat(self, path):
        """Returns stat info on a path in a StatStruct object. Writes to
        `stat_info` StatStruct arg if passed. Returns None if file does not
        exist at path."""
        stat_info = StatStruct()

        try:
            raw_stat = os.stat(path)
        except OSError:
            return None

        return self._parse_raw_stat(raw_stat, stat_info)

    def _create(self, path, stat_info):
        """Creates a record given its stat info and path. Returns the new file
        ID."""
        cursor = self.con.execute(
            "INSERT INTO Files (path, ino, crtime, mtime, is_dir) VALUES (?, ?, ?, ?, ?)",
            (path, stat_info.ino, stat_info.crtime, stat_info.mtime, stat_info.is_dir),
        )

        return cursor.lastrowid

    def _update(self, id, stat_info, path=None):
        """Updates a record given its file ID."""
        if path is not None:
            self.con.execute(
                "UPDATE Files SET path = ?, ino = ?, crtime = ?, mtime = ? WHERE id = ?",
                (path, stat_info.ino, stat_info.crtime, stat_info.mtime, id),
            )
        else:
            self.con.execute(
                # updating `ino` and `crtime` is a conscious design decision because
                # this method is called by `move()`. these values are only preserved
                # by fs moves done via the `rename()` syscall, like `mv`. we don't
                # care how the contents manager moves a file; it could be deleting
                # and creating a new file (which will change the stat info).
                "UPDATE Files SET ino = ?, crtime = ?, mtime = ? WHERE id = ?",
                (stat_info.ino, stat_info.crtime, stat_info.mtime, id),
            )

    def index(self, path, stat_info=None, commit=True):
        """Returns the file ID for the file at `path`, creating a new file ID if
        one does not exist. Returns None only if file does not exist at path."""
        path = self._normalize_path(path)
        stat_info = stat_info or self._stat(path)
        if not stat_info:
            return None

        # sync file at path and return file ID if it exists
        id = self._sync_file(path, stat_info)
        if id is not None:
            return id

        # otherwise, create a new record and return the file ID
        id = self._create(path, stat_info)
        if commit:
            self.con.commit()
        return id

    def get_id(self, path):
        """Retrieves the file ID associated with a file path. Returns None if
        the file has not yet been indexed or does not exist at the given
        path."""
        path = self._normalize_path(path)
        stat_info = self._stat(path)
        if not stat_info:
            return None

        # then sync file at path and retrieve id, if any
        id = self._sync_file(path, stat_info)
        self.con.commit()
        return id

    def get_path(self, id):
        """Retrieves the file path associated with a file ID. Returns None if
        the ID does not exist in the Files table or if the corresponding path no
        longer has a file."""
        self._sync_all()
        row = self.con.execute("SELECT path FROM Files WHERE id = ?", (id,)).fetchone()
        return row[0] if row else None

    def move(self, old_path, new_path, recursive=False):
        """Handles file moves by updating the file path of the associated file
        ID.  Returns the file ID. Returns None if file does not exist at new_path."""
        old_path = self._normalize_path(old_path)
        new_path = self._normalize_path(new_path)

        # verify file exists at new_path
        stat_info = self._stat(new_path)
        if stat_info is None:
            return None

        self.log.debug(f"FileIdManager : Moving file from ${old_path} to ${new_path}")

        if recursive:
            old_path_glob = os.path.join(old_path, "*")
            records = self.con.execute(
                "SELECT id, path FROM Files WHERE path GLOB ?", (old_path_glob,)
            ).fetchall()
            for record in records:
                if not record:
                    continue
                id, old_recpath = record
                new_recpath = os.path.join(new_path, os.path.basename(old_recpath))
                rec_stat_info = self._stat(new_recpath)
                if not rec_stat_info:
                    continue
                self.con.execute(
                    "UPDATE Files SET path = ?, mtime = ? WHERE id = ?",
                    (new_recpath, rec_stat_info.mtime, id),
                )

        # attempt to fetch ID associated with old path
        # we avoid using get_id() here since that will always return None as file no longer exists at old path
        row = self.con.execute("SELECT id FROM Files WHERE path = ?", (old_path,)).fetchone()
        if row is None:
            # if no existing record, create a new one
            id = self._create(new_path, stat_info)
            self.con.commit()
            return id
        else:
            # update existing record with new path and stat info
            # TODO: make sure is_dir for existing record matches that of file at new_path
            id = row[0]
            self._update(id, stat_info, new_path)
            self.con.commit()
            return id

    def copy(self, from_path, to_path, recursive=False):
        """Handles file copies by creating a new record in the Files table.
        Returns the file ID associated with `new_path`. Also indexes `old_path`
        if record does not exist in Files table. TODO: emit to event bus to
        inform client extensions to copy records associated with old file ID to
        the new file ID."""
        from_path = self._normalize_path(from_path)
        to_path = self._normalize_path(to_path)
        self.log.debug(f"FileIdManager : Copying file from ${from_path} to ${to_path}")

        if recursive:
            from_path_glob = os.path.join(from_path, "*")
            records = self.con.execute(
                "SELECT path FROM Files WHERE path GLOB ?", (from_path_glob,)
            ).fetchall()
            for record in records:
                if not record:
                    continue
                (from_recpath,) = record
                to_recpath = os.path.join(to_path, os.path.basename(from_recpath))
                stat_info = self._stat(to_recpath)
                if not stat_info:
                    continue
                self.con.execute(
                    "INSERT INTO FILES (path, ino, crtime, mtime, is_dir) VALUES (?, ?, ?, ?, ?)",
                    (
                        to_recpath,
                        stat_info.ino,
                        stat_info.crtime,
                        stat_info.mtime,
                        stat_info.is_dir,
                    ),
                )

        # transaction committed in index()
        self.index(from_path)
        return self.index(to_path)

    def delete(self, path, recursive=False):
        """Handles file deletions by deleting the associated record in the File
        table. Returns None."""
        path = self._normalize_path(path)
        self.log.debug(f"FileIdManager : Deleting file {path}")

        if recursive:
            path_glob = os.path.join(path, "*")
            self.con.execute("DELETE FROM Files WHERE path GLOB ?", (path_glob,))

        self.con.execute("DELETE FROM Files WHERE path = ?", (path,))
        self.con.commit()

    def _cleanup(self):
        """Cleans up `FileIdManager` by committing any pending transactions and
        closing the connection."""
        self.con.commit()
        self.con.close()
