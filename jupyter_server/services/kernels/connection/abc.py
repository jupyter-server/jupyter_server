from abc import ABC, abstractmethod
from typing import Callable


class KernelWebsocketConnectionABC(ABC):
    """
    This class defines a minimal interface that should
    be used to bridge the connection between Jupyter
    Server's websocket API and a kernel's ZMQ socket
    interface.
    """

    write_message: Callable

    @abstractmethod
    async def connect(self):
        ...

    @abstractmethod
    async def disconnect(self):
        ...

    @abstractmethod
    def handle_incoming_message(self, incoming_msg: str) -> None:
        ...

    @abstractmethod
    def handle_outgoing_message(self, stream: str, outgoing_msg: list) -> None:
        ...
