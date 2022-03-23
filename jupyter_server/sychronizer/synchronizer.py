import asyncio
import uuid
from dataclasses import dataclass
from dataclasses import fields
from typing import Union

from tornado.escape import json_decode
from traitlets import Any
from traitlets import default
from traitlets import Float
from traitlets import Instance
from traitlets.config import LoggingConfigurable

from .remote_kernel_table import RemoteKernelTable


class KernelRecordConflict(Exception):
    """An exception raised when"""

    pass


@dataclass
class KernelRecord:
    """A dataclass that keeps a record of kernels maintained
    by Jupyter Server's synchronizer.

    Two records are considered equivalent if their
    kernel ID or remote ID are equal. In this case, calling
    `.update(...)` will merge the data of two records
    """

    remote_id: Union[None, str] = None
    kernel_id: Union[None, str] = None
    alive: Union[None, bool] = None
    recorded: Union[None, bool] = None
    managed: Union[None, bool] = None

    def __eq__(self, other: "KernelRecord") -> bool:
        if isinstance(other, KernelRecord):
            if any(
                [
                    # Check if the Kernel ID matches
                    self.kernel_id and other.kernel_id and self.kernel_id == other.kernel_id,
                    # Check if the remote ID matches.
                    self.remote_id and other.remote_id and self.remote_id == other.remote_id,
                ]
            ):
                return True
        return False

    def update(self, other: "KernelRecord") -> None:
        """Updates in-place a kernel from other (only accepts positive updates"""
        if not isinstance(other, KernelRecord):
            raise TypeError("'other' must be an instance of KernelRecord.")

        if other.kernel_id and self.kernel_id and other.kernel_id != self.kernel_id:
            raise KernelRecordConflict(
                "Could not update the record from 'other' because the two records conflict."
            )

        for field in fields(self):
            if hasattr(other, field.name) and getattr(other, field.name):
                setattr(self, field.name, getattr(other, field.name))


class KernelRecordList:
    """Handy object for storing and managing a list of KernelRecords.
    When adding a record to the list, first checks if the record
    already exists. If it does, the record will be updated with
    the new information.
    """

    def __init__(self, *records):
        self._records = []
        for record in records:
            self.update(record)

    def __str__(self):
        return str(self._records)

    def __contains__(self, record: Union[KernelRecord, str]):
        """Search for records by kernel_id and session_id"""
        if isinstance(record, KernelRecord) and record in self._records:
            return True

        if isinstance(record, str):
            for r in self._records:
                if record in [r.remote_id, r.kernel_id]:
                    return True
        return False

    def __len__(self):
        return len(self._records)

    def get(self, record: Union[KernelRecord, str]) -> KernelRecord:
        if isinstance(record, str):
            for r in self._records:
                if record == r.kernel_id or record == r.remote_id:
                    return r
        elif isinstance(record, KernelRecord):
            for r in self._records:
                if record == r:
                    return record
        raise ValueError(f"{record} not found in KernelRecordList.")

    def update(self, record: KernelRecord) -> None:
        """Update a record in-place or append it if not in the list."""
        try:
            idx = self._records.index(record)
            self._records[idx].update(record)
        except ValueError:
            self._records.append(record)

    def remove(self, record: KernelRecord) -> None:
        """Remove a record if its found in the list. If it's not found,
        do nothing.
        """
        if record in self._records:
            self._records.remove(record)


class Synchronizer(LoggingConfigurable):
    """A configurable class for syncing all managers in Jupyter Server."""

    syncing_interval = Float(
        default_value=5.0,
        help="Interval (in seconds) for each call to the periodic syncing method.",
    )

    _kernel_records = KernelRecordList()

    remote_kernel_table = Instance(RemoteKernelTable)

    @default("remote_kernel_table")
    def _default_kernel_remote_table(self):  # pragma: no cover
        return RemoteKernelTable()

    # Remote Client
    fetch_remote_kernels = Any(allow_none=True)

    multi_kernel_manager = Instance(
        klass="jupyter_server.services.kernels.kernelmanager.MappingKernelManager"
    )
    session_manager = Instance(
        klass="jupyter_server.services.sessions.sessionmanager.SessionManager"
    )
    contents_manager = Instance(klass="jupyter_server.services.contents.manager.ContentsManager")

    async def call_fetch_remote_kernels(self) -> None:
        """Fetch kernels from the remote kernel service"""
        r = await self.fetch_remote_kernels()
        response = json_decode(r.body)
        # Hydrate kernelmanager for all remote kernels
        for item in response:
            kernel = KernelRecord(remote_id=item["id"], alive=True)
            self._kernel_records.update(kernel)

    def fetch_recorded_kernels(self) -> None:
        for k in self.remote_kernel_table.list():
            kernel = KernelRecord(kernel_id=k.kernel_id, remote_id=k.remote_id, recorded=True)
            self._kernel_records.update(kernel)

    def fetch_managed_kernels(self) -> None:
        for kernel_id, km in self.multi_kernel_manager._kernels.items():
            kernel = KernelRecord(remote_id=km.remote_id, kernel_id=kernel_id, managed=True)
            self._kernel_records.update(kernel)

    async def fetch_kernel_records(self):
        if self.fetch_kernel_records:
            await self.call_fetch_remote_kernels()
        self.fetch_recorded_kernels()
        self.fetch_managed_kernels()

    def record_kernels(self):
        for kernel in self._kernel_records._records:
            if not kernel.recorded and kernel.kernel_id and kernel.remote_id and kernel.alive:
                self.remote_kernel_table.save(
                    kernel_id=kernel.kernel_id, remote_id=kernel.remote_id
                )
                kernel.recorded = True

    def remove_stale_kernels(self):
        for k in self._kernel_records._records:
            if not k.alive:
                self._kernel_records.remove(k)
                if k.recorded:
                    self.remote_kernel_table.delete(kernel_id=k.kernel_id)

    async def hydrate_kernel_managers(self):
        for k in self._kernel_records._records:
            if not k.managed and k.remote_id and k.alive:
                if not k.kernel_id:
                    kernel_id = str(uuid.uuid4())
                    k.kernel_id = kernel_id
                await self.multi_kernel_manager.start_kernel(
                    kernel_id=k.kernel_id, remote_id=k.remote_id
                )
                k.managed = True

    async def delete_stale_sessions(self):
        """Delete sessions that either have no kernel or no content
        found in the server.
        """
        session_list = await self.session_manager.list_sessions()
        mkm = self.multi_kernel_manager
        for session in session_list:
            kid = session["kernel"]["id"]
            known_kids = list(mkm._kernels.keys()) + list(mkm._pending_kernels.keys())
            if kid not in known_kids:
                self.log.info(
                    (
                        f"Kernel {kid} found in the session_manager but "
                        f"not in the kernel_manager. Deleting this session."
                    )
                )
                # session = await self.get_session(kernel_id=kid)
                self.session_manager.cursor.execute("DELETE FROM session WHERE kernel_id=?", (kid,))
            # Check the contents manager for documents.
            file_exists = self.contents_manager.exists(path=session["path"])
            if not file_exists:
                session_id = session["id"]
                self.log.info(
                    (
                        f"The document path for {session_id} was not found. "
                        f"Deleting this session."
                    )
                )
                await self.session_manager.delete_session(session_id)

    async def shutdown_kernels_without_sessions(self):
        """Shutdown 'unknown' kernels (found in kernelmanager but
        not the session manager).
        """
        for kernel_id in self.multi_kernel_manager.list_kernel_ids():
            try:
                kernel = await self.session_manager.get_session(kernel_id=kernel_id)
            except Exception:
                try:
                    kernel = self.multi_kernel_manager.get_kernel(kernel_id)
                    if (
                        not kernel.ready.done()
                        or kernel_id in self.session_manager._pending_sessions
                    ):
                        continue
                    self.log.info(
                        (
                            f"Kernel {kernel_id} found in the kernel_manager is not "
                            f"found in the session database. Shutting down the kernel."
                        )
                    )
                    await self.multi_kernel_manager.shutdown_kernel(kernel_id)
                # Log any failures, but don't raise exceptions.
                except Exception as err2:
                    self.log.info(err2)
                    pass

    async def sync_kernels(self):
        """Synchronize the kernel manager, kernel database, and
        remote kernel service.
        """
        self._kernel_records = KernelRecordList()
        await self.fetch_kernel_records()

        self.remove_stale_kernels()
        await self.hydrate_kernel_managers()
        self.record_kernels()

    async def sync_sessions(self):
        """Synchronize the session database and with the
        multi-kernel_manager by:

        1. Deleting sessions that do not have running
            kernels in the kernel manager
        2. Shutting down kernels in the kernel manager
            that do not have a session associated with them.
        3. Deleting sessions+kernels that do not have content
            found by the contents manager.
        """
        await self.delete_stale_sessions()
        await self.shutdown_kernels_without_sessions()

    async def sync_managers(self):
        """Rehydrate sessions and kernels managers from the remote
        kernel service.
        """
        self.log.info("Syncing ")
        await self.sync_kernels()
        await self.sync_sessions()

    async def _regular_syncing(self, interval=5.0):
        """Start regular syncing on a defined interval."""
        while True:
            self.log.debug("Syncing with Remote Service.")
            await self.sync_managers()
            await asyncio.sleep(interval)

    def start_regular_syncing(self):
        """Run regular syncing in a background task."""
        return asyncio.ensure_future(self._regular_syncing(interval=self.syncing_interval))
