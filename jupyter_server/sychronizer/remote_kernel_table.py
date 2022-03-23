import os
import sqlite3
from collections import namedtuple
from typing import List

from jupyter_core.paths import jupyter_runtime_dir


KernelMap = namedtuple("KernelMap", ["kernel_id", "remote_id"])


class RemoteKernelTable:
    """An SQLite database that stores the map between
    Kernel ID (from Jupyter) and remote ID.
    """

    _table_name = "kernelmap"
    _table_columns = ("kernel_id", "remote_id")
    _db_name = "jupyter-session.db"
    _connection = None
    _cursor = None

    @property
    def cursor(self):
        """Start a cursor and create a database called 'session'"""
        if self._cursor is None:
            self._cursor = self.connection.cursor()
            self._cursor.execute(
                f"""CREATE TABLE IF NOT EXISTS {self._table_name}
                ({', '.join(self._table_columns)})"""
            )
        return self._cursor

    @property
    def connection(self):
        """Start a database connection"""
        session_db_path = os.path.join(jupyter_runtime_dir(), self._db_name)
        if self._connection is None:
            self._connection = sqlite3.connect(session_db_path, isolation_level=None)
            self._connection.row_factory = sqlite3.Row
        return self._connection

    def query(self, query_string, **identifiers):
        """Build and execute a query."""
        if any(key in identifiers for key in self._table_columns):
            query = query_string.format(
                *list(identifiers.keys()),
                table=self._table_name,
            )
            print(query, tuple(identifiers.values()))
            self.cursor.execute(query, tuple(identifiers.values()))
        else:
            raise Exception("No kernel_id or remote_id given.")

    def save(self, kernel_id: str = None, remote_id: str = None) -> None:
        self.cursor.execute(f"INSERT INTO {self._table_name} VALUES (?,?)", (kernel_id, remote_id))

    def exists(self, **identifier) -> bool:
        """Check to see if the session of a given name exists"""
        self.query("SELECT * FROM {table} WHERE {0}=?", **identifier)
        row = self.cursor.fetchone()
        if row is not None:
            return True
        return False

    def update(self, kernel_id=None, remote_id=None) -> None:
        if self.exists(kernel_id=kernel_id):
            self.query(
                "UPDATE {table} SET {0}=? WHERE {1}=?",
                remote_id=remote_id,
                kernel_id=kernel_id,
            )
        elif self.exists(remote_id=remote_id):
            self.query(
                "UPDATE {table} SET {0}=? WHERE {1}=?",
                kernel_id=kernel_id,
                remote_id=remote_id,
            )
        else:
            raise Exception("Couldn't find a matching entry in the kernelmap database.")

    def delete(self, **identifier) -> None:
        self.query("DELETE FROM {table} WHERE {0}=?", **identifier)

    def row_to_model(self, row: sqlite3.Row) -> KernelMap:
        return KernelMap(kernel_id=row["kernel_id"], remote_id=row["remote_id"])

    def list(self) -> List[KernelMap]:
        self.cursor.execute(f"SELECT * FROM {self._table_name}")
        rows = self.cursor.fetchall()
        return [self.row_to_model(row) for row in rows]

    def get_remote_map(self) -> dict:
        models = self.list()
        return {m.remote_id: m.kernel_id for m in models}

    def get_kernel_map(self) -> dict:
        models = self.list()
        return {m.kernel_id: m.remote_id for m in models}

    def get(self, **identifier) -> KernelMap:
        self.query("SELECT * FROM {table} WHERE {0}=?", **identifier)
        row = self.cursor.fetchone()
        if not row:
            raise Exception("No match was found in database.")
        return self.row_to_model(row)
