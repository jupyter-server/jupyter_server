# coding: utf-8
"""Tornado handlers for WebSocket <-> ZMQ sockets."""
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
import json
import re
import struct
import sys
from urllib.parse import urlparse

import tornado
from ipython_genutils.py3compat import cast_unicode

try:
    from jupyter_client.jsonutil import json_default
except ImportError:
    from jupyter_client.jsonutil import date_default as json_default
from jupyter_client.jsonutil import extract_dates
from jupyter_client.session import Session
from tornado import ioloop
from tornado import web
from tornado.websocket import WebSocketHandler

from .handlers import JupyterHandler


# ping interval for keeping websockets alive (30 seconds)
WS_PING_INTERVAL = 30000


class WebSocketMixin(object):
    """Mixin for common websocket options"""

    ping_callback = None
    last_ping = 0
    last_pong = 0
    stream = None

    @property
    def ping_interval(self):
        """The interval for websocket keep-alive pings.

        Set ws_ping_interval = 0 to disable pings.
        """
        return self.settings.get("ws_ping_interval", WS_PING_INTERVAL)

    @property
    def ping_timeout(self):
        """If no ping is received in this many milliseconds,
        close the websocket connection (VPNs, etc. can fail to cleanly close ws connections).
        Default is max of 3 pings or 30 seconds.
        """
        return self.settings.get("ws_ping_timeout", max(3 * self.ping_interval, WS_PING_INTERVAL))

    def check_origin(self, origin=None):
        """Check Origin == Host or Access-Control-Allow-Origin.

        Tornado >= 4 calls this method automatically, raising 403 if it returns False.
        """

        if self.allow_origin == "*" or (
            hasattr(self, "skip_check_origin") and self.skip_check_origin()
        ):
            return True

        host = self.request.headers.get("Host")
        if origin is None:
            origin = self.get_origin()

        # If no origin or host header is provided, assume from script
        if origin is None or host is None:
            return True

        origin = origin.lower()
        origin_host = urlparse(origin).netloc

        # OK if origin matches host
        if origin_host == host:
            return True

        # Check CORS headers
        if self.allow_origin:
            allow = self.allow_origin == origin
        elif self.allow_origin_pat:
            allow = bool(re.match(self.allow_origin_pat, origin))
        else:
            # No CORS headers deny the request
            allow = False
        if not allow:
            self.log.warning(
                "Blocking Cross Origin WebSocket Attempt.  Origin: %s, Host: %s",
                origin,
                host,
            )
        return allow

    def clear_cookie(self, *args, **kwargs):
        """meaningless for websockets"""
        pass

    def open(self, *args, **kwargs):
        self.log.debug("Opening websocket %s", self.request.path)

        # start the pinging
        if self.ping_interval > 0:
            loop = ioloop.IOLoop.current()
            self.last_ping = loop.time()  # Remember time of last ping
            self.last_pong = self.last_ping
            self.ping_callback = ioloop.PeriodicCallback(
                self.send_ping,
                self.ping_interval,
            )
            self.ping_callback.start()
        return super(WebSocketMixin, self).open(*args, **kwargs)

    def send_ping(self):
        """send a ping to keep the websocket alive"""
        if self.ws_connection is None and self.ping_callback is not None:
            self.ping_callback.stop()
            return

        if self.ws_connection.client_terminated:
            self.close()
            return

        # check for timeout on pong.  Make sure that we really have sent a recent ping in
        # case the machine with both server and client has been suspended since the last ping.
        now = ioloop.IOLoop.current().time()
        since_last_pong = 1e3 * (now - self.last_pong)
        since_last_ping = 1e3 * (now - self.last_ping)
        if since_last_ping < 2 * self.ping_interval and since_last_pong > self.ping_timeout:
            self.log.warning("WebSocket ping timeout after %i ms.", since_last_pong)
            self.close()
            return

        self.ping(b"")
        self.last_ping = now

    def on_pong(self, data):
        self.last_pong = ioloop.IOLoop.current().time()


class ZMQStreamHandler(WebSocketMixin, WebSocketHandler):

    if tornado.version_info < (4, 1):
        """Backport send_error from tornado 4.1 to 4.0"""

        def send_error(self, *args, **kwargs):
            if self.stream is None:
                super(WebSocketHandler, self).send_error(*args, **kwargs)
            else:
                # If we get an uncaught exception during the handshake,
                # we have no choice but to abruptly close the connection.
                # TODO: for uncaught exceptions after the handshake,
                # we can close the connection more gracefully.
                self.stream.close()

    def _on_zmq_reply(self, stream, msg_list):
        # Sometimes this gets triggered when the on_close method is scheduled in the
        # eventloop but hasn't been called.
        if self.ws_connection is None or stream.closed():
            self.log.warning("zmq message arrived on closed channel")
            self.close()
            return
        layout = json.dumps({
            "channel": getattr(stream, "channel", None),
            "offsets": [0] + [len(msg) for msg in msg_list] + [0],
        }).encode("utf-8")
        layout_length = len(layout).to_bytes(2, byteorder="little")
        bin_msg = b"".join([layout_length, layout] + msg_list)
        self.write_message(bin_msg, binary=True)


class AuthenticatedZMQStreamHandler(ZMQStreamHandler, JupyterHandler):
    def set_default_headers(self):
        """Undo the set_default_headers in JupyterHandler

        which doesn't make sense for websockets
        """
        pass

    def pre_get(self):
        """Run before finishing the GET request

        Extend this method to add logic that should fire before
        the websocket finishes completing.
        """
        # authenticate the request before opening the websocket
        if self.get_current_user() is None:
            self.log.warning("Couldn't authenticate WebSocket connection")
            raise web.HTTPError(403)

        if self.get_argument("session_id", False):
            self.session.session = cast_unicode(self.get_argument("session_id"))
        else:
            self.log.warning("No session ID specified")

    async def get(self, *args, **kwargs):
        # pre_get can be a coroutine in subclasses
        # assign and yield in two step to avoid tornado 3 issues
        res = self.pre_get()
        await res
        res = super(AuthenticatedZMQStreamHandler, self).get(*args, **kwargs)
        await res

    def initialize(self):
        self.log.debug("Initializing websocket connection %s", self.request.path)
        self.session = Session(config=self.config)

    def get_compression_options(self):
        return self.settings.get("websocket_compression_options", None)
