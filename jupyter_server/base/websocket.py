import re
from typing import Optional, no_type_check
from urllib.parse import urlparse

from tornado import ioloop
from tornado.iostream import IOStream

# ping interval for keeping websockets alive (30 seconds)
WS_PING_INTERVAL = 30000


class WebSocketMixin:
    """Mixin for common websocket options"""

    ping_callback = None
    last_ping = 0.0
    last_pong = 0.0
    stream = None  # type: Optional[IOStream]

    @property
    def ping_interval(self):
        """The interval for websocket keep-alive pings.

        Set ws_ping_interval = 0 to disable pings.
        """
        return self.settings.get("ws_ping_interval", WS_PING_INTERVAL)  # type:ignore[attr-defined]

    @property
    def ping_timeout(self):
        """If no ping is received in this many milliseconds,
        close the websocket connection (VPNs, etc. can fail to cleanly close ws connections).
        Default is max of 3 pings or 30 seconds.
        """
        return self.settings.get(  # type:ignore[attr-defined]
            "ws_ping_timeout", max(3 * self.ping_interval, WS_PING_INTERVAL)
        )

    @no_type_check
    def check_origin(self, origin: Optional[str] = None) -> bool:
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

    @no_type_check
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
        return super().open(*args, **kwargs)

    @no_type_check
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
