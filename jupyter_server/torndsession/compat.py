#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2014 Mitchell Chu

import sys

# __all__ = (
#     'text_type', 'string_types', 'izip', 'iteritems', 'itervalues',
#     'with_metaclass',
# )

PY3 = sys.version_info >= (3,)

if PY3:
    text_type = str
    string_types = (str, )
    integer_types = int
    izip = zip
    _xrange = range
    MAXSIZE = sys.maxsize

    def iteritems(o):
        return iter(o.items())

    def itervalues(o):
        return iter(o.values())

    def bytes_from_hex(h):
        return bytes.fromhex(h)

    def reraise(exctype, value, trace=None):
        raise exctype(str(value)).with_traceback(trace)

    def _unicode(s):
        return s
else:
    text_type = unicode
    string_types = (basestring, )
    integer_types = (int, long)
    from itertools import izip
    _xrange = xrange
    MAXSIZE = sys.maxint

    def b(s):
        # See comments above. In python 2.x b('foo') is just 'foo'.
        return s

    def iteritems(o):
        return o.iteritems()

    def itervalues(o):
        return o.itervalues()

    def bytes_from_hex(h):
        return h.decode('hex')

    # "raise x, y, z" raises SyntaxError in Python 3
    exec("""def reraise(exctype, value, trace=None):
    raise exctype, str(value), trace
""")

    _unicode = unicode


def with_metaclass(meta, base=object):
    return meta("NewBase", (base,), {})
