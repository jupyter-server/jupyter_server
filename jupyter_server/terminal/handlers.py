# encoding: utf-8
"""Tornado handlers for the terminal emulator."""
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
import json

import terminado
from tornado import web

from jupyter_server._tz import utcnow
from ..base.handlers import JupyterHandler
from ..base.zmqhandlers import WebSocketMixin


class TermSocket(WebSocketMixin, JupyterHandler, terminado.TermSocket):
    def initialize(self, *args, **kwargs):
        super(TermSocket, self).initialize(*args, **kwargs)
        self._first_stdout = ''

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
        self._set_state_busy()

    def write_message(self, message, binary=False):
        super(TermSocket, self).write_message(message, binary=binary)
        message_seg = json.loads(message)
        if not self._first_stdout and message_seg[0] == 'stdout':
            # Record the first output to identify the terminal return
            # It works well for jupyterhub-singleuser and should also work for other debian-based mirrors
            # fixme: May fail if terminal is not properly separated with ':' or change user after connect
            #        (Any change to the user, hostname or environment may render it invalid)
            self._first_stdout = message_seg[1].split(':')[0].lstrip()
            self.log.debug(f'take "{self._first_stdout}" as terminal returned')
        if isinstance(message_seg[1], str) and message_seg[1].lstrip().startswith(self._first_stdout):
            self._set_state_idle()

    def _update_activity(self):
        self.application.settings["terminal_last_activity"] = utcnow()
        # terminal may not be around on deletion/cull
        if self.term_name in self.terminal_manager.terminals:
            self.terminal_manager.terminals[self.term_name].last_activity = utcnow()

    def _set_state_busy(self):
        if self.term_name in self.terminal_manager.terminals:
            self.terminal_manager.terminals[self.term_name].execution_state = 'busy'

    def _set_state_idle(self):
        if self.term_name in self.terminal_manager.terminals:
            self.log.debug('set terminal execution_state as idle')
            self.terminal_manager.terminals[self.term_name].execution_state = 'idle'
