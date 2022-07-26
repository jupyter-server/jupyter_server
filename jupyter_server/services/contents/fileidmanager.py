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
            "path TEXT NOT NULL UNIQUE, "
            "ino INTEGER NOT NULL UNIQUE, "
            "crtime INTEGER, "
            "mtime INTEGER NOT NULL, "
            "is_dir TINYINT NOT NULL"
            ")"
        )
        self._index_dirs(self.root_dir)
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

    def _index_dirs(self, dir_path):
        """Recursively indexes all directories under a given path. Used in
        __init__() to recursively index all directories under the server
        root."""
        self.index(dir_path)
        for entry in os.scandir(dir_path):
            if entry.is_dir():
                self._index_dirs(entry.path)

    def _normalize_path(self, path):
        """Normalizes a given file path."""
        if not os.path.isabs(path):
            path = os.path.join(self.root_dir, path)
        path = os.path.normcase(path)
        path = os.path.normpath(path)
        return path

    def _stat(self, path, stat_info=StatStruct()):
        """Returns stat info on a path in a StatStruct object. Writes to
        `stat_info` StatStruct arg if passed. Returns None if file does not
        exist at path."""
        try:
            raw_stat = os.stat(path)
        except OSError:
            return None

        stat_info.empty = False
        stat_info.ino = raw_stat.st_ino
        stat_info.crtime = (
            raw_stat.st_ctime
            if os.name == "nt"
            else raw_stat.st_birthtime  # type: ignore
            if hasattr(raw_stat, "st_birthtime")
            else None
        )
        stat_info.mtime = raw_stat.st_mtime
        stat_info.is_dir = stat.S_ISDIR(raw_stat.st_mode)

        return stat_info

    def _update(self, id, stat_info, path=None):
        """Updates stat info associated with a ID."""
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
                # and creating a new file (which will change both values).
                "UPDATE Files SET ino = ?, crtime = ?, mtime = ? WHERE id = ?",
                (stat_info.ino, stat_info.crtime, stat_info.mtime, id),
            )
        self.con.commit()

    def index(self, path):
        """Returns the file ID for the file at `path`, creating a new file ID if
        one does not exist. Returns None only if file does not exist at path.
        Note that this essentially just wraps `get_id()` and creates a new
        record if it returns None and the file exists."""
        stat_info = StatStruct()
        existing_id = self.get_id(path, stat_info)
        if existing_id is not None:
            return existing_id
        if stat_info.empty:
            return None

        # if path does not exist in the DB and an out-of-band move is not indicated, create a new record
        path = self._normalize_path(path)
        cursor = self.con.execute(
            "INSERT INTO Files (path, ino, crtime, mtime, is_dir) VALUES (?, ?, ?, ?, ?)",
            (path, stat_info.ino, stat_info.crtime, stat_info.mtime, stat_info.is_dir),
        )
        self.con.commit()
        return cursor.lastrowid

    def get_id(self, path, stat_info=StatStruct()):
        """Retrieves the file ID associated with a file path. Tracks out-of-band
        moves by searching the table for a record with an identical `ino` and
        `crtime` (falling back to `mtime` if `crtime` is not supported on the
        current platform). Updates the file's stat info on invocation and caches
        this in the `stat_info` arg if passed.  Returns None if the file has not
        yet been indexed or does not exist at the given path."""
        path = self._normalize_path(path)
        stat_info = self._stat(path, stat_info)
        if not stat_info:
            return None

        # if file at already exists, just update the stat info and return id
        row = self.con.execute("SELECT id FROM Files WHERE path = ?", (path,)).fetchone()
        if row:
            (existing_id,) = row
            self._update(existing_id, stat_info)
            return existing_id

        # then check if file at path was indexed but moved out-of-band
        src = self.con.execute(
            "SELECT id, crtime, mtime FROM Files WHERE ino = ?", (stat_info.ino,)
        ).fetchone()

        ## if no matching ino, then return None
        if not src:
            return None

        id, src_crtime, src_mtime = src
        src_timestamp = src_crtime if src_crtime is not None else src_mtime
        dst_timestamp = stat_info.crtime if stat_info.crtime is not None else stat_info.mtime

        ## if identical ino and crtime/mtime to an existing record, update it with new destination path and stat info, returning its id
        if src_timestamp == dst_timestamp:
            self._update(id, stat_info, path)
            return id

        ## otherwise delete the existing record with identical `ino`, since inos must be unique. then return None
        self.con.execute("DELETE FROM Files WHERE id = ?", (id,))
        self.con.commit()
        return None

    def get_path(self, id):
        """Retrieves the file path associated with a file ID. Returns None if
        the ID does not exist in the Files table or if the corresponding path no
        longer has a file."""
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
                stat_info = self._stat(new_recpath)
                if not stat_info:
                    continue
                self.con.execute(
                    "UPDATE Files SET path = ?, mtime = ? WHERE id = ?",
                    (new_recpath, stat_info.mtime, id),
                )
            self.con.commit()

        # attempt to fetch ID associated with old path
        # we avoid using get_id() here since that will always return None as file no longer exists at old path
        row = self.con.execute("SELECT id FROM Files where path = ?", (old_path,)).fetchone()
        if row is None:
            # if no existing record, create a new one
            # TODO: pass stat info to avoid useless syscall
            return self.index(new_path)
        else:
            # update existing record with new path and stat info
            # TODO: make sure is_dir for existing record matches that of file at new_path
            id = row[0]
            self._update(id, stat_info, new_path)
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
            self.con.commit()

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
            self.con.commit()

        self.con.execute("DELETE FROM Files WHERE path = ?", (path,))
        self.con.commit()

    def _cleanup(self):
        """Cleans up `FileIdManager` by committing any pending transactions and
        closing the connection."""
        self.con.commit()
        self.con.close()
