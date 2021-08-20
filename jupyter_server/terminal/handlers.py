# encoding: utf-8
"""Tornado handlers for the terminal emulator."""
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
import terminado
from tornado import web

from ..base.handlers import JupyterHandler
from ..base.zmqhandlers import WebSocketMixin
from jupyter_server._tz import utcnow


class TermSocket(WebSocketMixin, JupyterHandler, terminado.TermSocket):
    def origin_check(self):
        """Terminado adds redundant origin_check
        Tornado already calls check_origin, so don't do anything here.
        """
        return True

    def get(self, *args, **kwargs):
        if not self.get_current_user():
            raise web.HTTPError(403)
        if not args[0] in self.term_manager.terminals:
            raise web.HTTPError(404)
        return super(TermSocket, self).get(*args, **kwargs)

    def on_message(self, message):
        super(TermSocket, self).on_message(message)
        self._update_activity()

    def write_message(self, message, binary=False):
        super(TermSocket, self).write_message(message, binary=binary)
        self._update_activity()

    def _update_activity(self):
        self.application.settings["terminal_last_activity"] = utcnow()
        # terminal may not be around on deletion/cull
        if self.term_name in self.terminal_manager.terminals:
            self.terminal_manager.terminals[self.term_name].last_activity = utcnow()
