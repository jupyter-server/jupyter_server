#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright @ 2014 Mitchell Chu

from __future__ import (absolute_import, division, print_function,
                        with_statement)

import tornado.web
import SessionMixin from .session


class SessionBaseHandler(tornado.web.RequestHandler, SessionMixin):
    """
    This is a tornado web request handler which is base on torndsession.
    Generally, user must persistent session object with manual operation when force_persistence is False.
    but when the handler is inherit from SessionBaseHandler, in your handler, you just need to add/update/delete session values, SessionBaseHandler will auto save it.
    """

    def prepare(self):
        """
        Overwrite tornado.web.RequestHandler prepare.
        """
        pass

    def on_finish(self):
        """
        Overwrite tornado.web.RequestHandler on_finish.
        """
        self.web_session.flush()    # try to save session
