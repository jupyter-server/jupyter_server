"""Gateway connection classes."""
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

import asyncio
import random
from typing import cast

from tornado.concurrent import Future
from tornado.escape import url_escape
from tornado.httpclient import HTTPRequest
from tornado.ioloop import IOLoop
from tornado.websocket import websocket_connect

from ..services.kernels.connection.base import BaseKernelWebsocketConnection
from ..utils import url_path_join
from .managers import GatewayClient


class GatewayWebSocketConnection(BaseKernelWebsocketConnection):
    """Web socket connection that proxies to a kernel/enterprise gateway."""

    kernel_ws_protocol = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ws = None
        self.ws_future: Future = Future()
        self.disconnected = False
        self.retry = 0

    async def connect(self):
        """Connect to the socket."""
        # websocket is initialized before connection
        self.ws = None
        ws_url = url_path_join(
            GatewayClient.instance().ws_url,
            GatewayClient.instance().kernels_endpoint,
            url_escape(self.kernel_id),
            "channels",
        )
        self.log.info(f"Connecting to {ws_url}")
        kwargs: dict = {}
        kwargs = GatewayClient.instance().load_connection_args(**kwargs)

        request = HTTPRequest(ws_url, **kwargs)
        self.ws_future = cast(Future, websocket_connect(request))
        self.ws_future.add_done_callback(self._connection_done)

        loop = IOLoop.current()
        loop.add_future(self.ws_future, lambda future: self._read_messages())

    def _connection_done(self, fut):
        """Handle a finished connection."""
        if (
            not self.disconnected and fut.exception() is None
        ):  # prevent concurrent.futures._base.CancelledError
            self.ws = fut.result()
            self.retry = 0
            self.log.debug(f"Connection is ready: ws: {self.ws}")
        else:
            self.log.warning(
                "Websocket connection has been closed via client disconnect or due to error.  "
                "Kernel with ID '{}' may not be terminated on GatewayClient: {}".format(
                    self.kernel_id, GatewayClient.instance().url
                )
            )

    def disconnect(self):
        """Handle a disconnect."""
        self.disconnected = True
        if self.ws is not None:
            # Close connection
            self.ws.close()
        elif not self.ws_future.done():
            # Cancel pending connection.  Since future.cancel() is a noop on tornado, we'll track cancellation locally
            self.ws_future.cancel()
            self.log.debug(f"_disconnect: future cancelled, disconnected: {self.disconnected}")

    async def _read_messages(self):
        """Read messages from gateway server."""
        while self.ws is not None:
            message = None
            if not self.disconnected:
                try:
                    message = await self.ws.read_message()
                except Exception as e:
                    self.log.error(
                        f"Exception reading message from websocket: {e}"
                    )  # , exc_info=True)
                if message is None:
                    if not self.disconnected:
                        self.log.warning(f"Lost connection to Gateway: {self.kernel_id}")
                    break
                self.handle_outgoing_message(
                    message
                )  # pass back to notebook client (see self.on_open and WebSocketChannelsHandler.open)
            else:  # ws cancelled - stop reading
                break

        # NOTE(esevan): if websocket is not disconnected by client, try to reconnect.
        if not self.disconnected and self.retry < GatewayClient.instance().gateway_retry_max:
            jitter = random.randint(10, 100) * 0.01  # noqa
            retry_interval = (
                min(
                    GatewayClient.instance().gateway_retry_interval * (2**self.retry),
                    GatewayClient.instance().gateway_retry_interval_max,
                )
                + jitter
            )
            self.retry += 1
            self.log.info(
                "Attempting to re-establish the connection to Gateway in %s secs (%s/%s): %s",
                retry_interval,
                self.retry,
                GatewayClient.instance().gateway_retry_max,
                self.kernel_id,
            )
            await asyncio.sleep(retry_interval)
            loop = IOLoop.current()
            loop.spawn_callback(self.connect)

    def handle_outgoing_message(self, *args, **kwargs):
        """Send message to the notebook client."""
        self.websocket_handler.write_message(*args, **kwargs)

    def handle_incoming_message(self, message: str) -> None:
        """Send message to gateway server."""
        if self.ws is None:
            loop = IOLoop.current()
            loop.add_future(self.ws_future, lambda future: self.handle_incoming_message(message))
        else:
            self._write_message(message)

    def _write_message(self, message):
        """Send message to gateway server."""
        try:
            if not self.disconnected and self.ws is not None:
                self.ws.write_message(message)
        except Exception as e:
            self.log.error(f"Exception writing message to websocket: {e}")  # , exc_info=True)
