import os
import sqlite3
from typing import Optional

from jupyter_core.paths import jupyter_data_dir
from traitlets import Unicode
from traitlets.config.configurable import LoggingConfigurable


class StatStruct:
    empty = True
    ino: int
    crtime: Optional[int]
    mtime: int


class FileIdManager(LoggingConfigurable):
    root_dir = Unicode(help=("The root being served by Jupyter server."), config=True)

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
        self.log.debug("Creating File ID tables and indices")
        self.con.execute(
            "CREATE TABLE IF NOT EXISTS Files("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "path TEXT NOT NULL UNIQUE, "
            "ino INTEGER NOT NULL UNIQUE, "
            "crtime INTEGER, "
            "mtime INTEGER NOT NULL"
            ")"
        )
        self.con.execute("CREATE INDEX IF NOT EXISTS ix_Files_path ON FILES (path)")
        self.con.execute("CREATE INDEX IF NOT EXISTS ix_Files_ino ON FILES (ino)")
        self.con.commit()

    def _normalize_path(self, path):
        """Normalizes a given file path."""
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

        return stat_info

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
            "INSERT INTO Files (path, ino, crtime, mtime) VALUES (?, ?, ?, ?)",
            (path, stat_info.ino, stat_info.crtime, stat_info.mtime),
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

        # if id already exists, just update the stat info and return id
        row = self.con.execute("SELECT id FROM Files WHERE path = ?", (path,)).fetchone()
        if row:
            (existing_id,) = row
            self.con.execute(
                "UPDATE Files SET ino = ?, crtime = ?, mtime = ? WHERE id = ?",
                (stat_info.ino, stat_info.crtime, stat_info.mtime, existing_id),
            )
            self.con.commit()
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
            self.con.execute(
                "UPDATE Files SET path = ?, crtime = ?, mtime = ? WHERE id = ?",
                (path, stat_info.crtime, stat_info.mtime, id),
            )
            self.con.commit()
            return id

        ## otherwise delete the existing record with identical `ino`, since inos must be unique. then return None
        self.con.execute("DELETE FROM Files WHERE id = ?", (id,))
        self.con.commit()
        return None

    def get_path(self, id):
        """Retrieves the file path associated with a file ID. Returns None if
        the ID does not exist in the Files table."""
        row = self.con.execute("SELECT path FROM Files WHERE id = ?", (id,)).fetchone()
        return row[0] if row else None

    def move(self, old_path, new_path, recursive=False):
        """Handles file moves by updating the file path of the associated file
        ID.  Returns the file ID."""
        old_path = self._normalize_path(old_path)
        new_path = self._normalize_path(new_path)
        self.log.debug(f"Moving file from ${old_path} to ${new_path}")

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
                    (id, stat_info.mtime, new_recpath),
                )
            self.con.commit()

        id = self.get_id(old_path)
        if id is None:
            return self.index(new_path)
        else:
            self.con.execute("UPDATE Files SET path = ? WHERE id = ?", (new_path, id))
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
        self.log.debug(f"Copying file from ${from_path} to ${to_path}")

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
                    "INSERT INTO FILES (path, ino, crtime, mtime) VALUES (?, ?, ?, ?)",
                    (to_recpath, stat_info.ino, stat_info.crtime, stat_info.mtime),
                )
            self.con.commit()

        self.index(from_path)
        return self.index(to_path)

    def delete(self, path, recursive=False):
        """Handles file deletions by deleting the associated record in the File
        table. Returns None."""
        path = self._normalize_path(path)
        self.log.debug(f"Deleting file {path}")

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
