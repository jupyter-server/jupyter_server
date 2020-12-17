#encoding: utf-8
"""Tornado handlers for the terminal emulator."""

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

from tornado import web
import terminado
from jupyter_server._tz import utcnow
from ..base.handlers import JupyterHandler
from ..base.zmqhandlers import WebSocketMixin


class TermSocket(WebSocketMixin, JupyterHandler, terminado.TermSocket):

    def origin_check(self):
        """Terminado adds redundant origin_check
        Tornado already calls check_origin, so don't do anything here.
        """
        return True

    def get(self, *args, **kwargs):
        if not self.get_current_user():
            raise web.HTTPError(403)
        return super(TermSocket, self).get(*args, **kwargs)

    def on_message(self, message):
        super(TermSocket, self).on_message(message)
        self.application.settings['terminal_last_activity'] = utcnow()

    def write_message(self, message, binary=False):
        super(TermSocket, self).write_message(message, binary=binary)
        self.application.settings['terminal_last_activity'] = utcnow()