"""Notebook related utilities"""

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

from __future__ import print_function

import asyncio
import errno
import inspect
import os
import sys
from distutils.version import LooseVersion

from urllib.parse import quote, unquote, urlparse, urljoin
from urllib.request import pathname2url

from ipython_genutils import py3compat


def url_path_join(*pieces):
    """Join components of url into a relative url

    Use to prevent double slash when joining subpath. This will leave the
    initial and final / in place
    """
    initial = pieces[0].startswith('/')
    final = pieces[-1].endswith('/')
    stripped = [s.strip('/') for s in pieces]
    result = '/'.join(s for s in stripped if s)
    if initial: result = '/' + result
    if final: result = result + '/'
    if result == '//': result = '/'
    return result


def url_is_absolute(url):
    """Determine whether a given URL is absolute"""
    return urlparse(url).path.startswith("/")


def path2url(path):
    """Convert a local file path to a URL"""
    pieces = [ quote(p) for p in path.split(os.sep) ]
    # preserve trailing /
    if pieces[-1] == '':
        pieces[-1] = '/'
    url = url_path_join(*pieces)
    return url


def url2path(url):
    """Convert a URL to a local file path"""
    pieces = [ unquote(p) for p in url.split('/') ]
    path = os.path.join(*pieces)
    return path


def url_escape(path):
    """Escape special characters in a URL path

    Turns '/foo bar/' into '/foo%20bar/'
    """
    parts = py3compat.unicode_to_str(path, encoding='utf8').split('/')
    return u'/'.join([quote(p) for p in parts])


def url_unescape(path):
    """Unescape special characters in a URL path

    Turns '/foo%20bar/' into '/foo bar/'
    """
    return u'/'.join([
        py3compat.str_to_unicode(unquote(p), encoding='utf8')
        for p in py3compat.unicode_to_str(path, encoding='utf8').split('/')
    ])


def samefile_simple(path, other_path):
    """
    Fill in for os.path.samefile when it is unavailable (Windows+py2).

    Do a case-insensitive string comparison in this case
    plus comparing the full stat result (including times)
    because Windows + py2 doesn't support the stat fields
    needed for identifying if it's the same file (st_ino, st_dev).

    Only to be used if os.path.samefile is not available.

    Parameters
    -----------
    path:       String representing a path to a file
    other_path: String representing a path to another file

    Returns
    -----------
    same:   Boolean that is True if both path and other path are the same
    """
    path_stat = os.stat(path)
    other_path_stat = os.stat(other_path)
    return (path.lower() == other_path.lower()
        and path_stat == other_path_stat)


def to_os_path(path, root=''):
    """Convert an API path to a filesystem path

    If given, root will be prepended to the path.
    root must be a filesystem path already.
    """
    parts = path.strip('/').split('/')
    parts = [p for p in parts if p != ''] # remove duplicate splits
    path = os.path.join(root, *parts)
    return path


def to_api_path(os_path, root=''):
    """Convert a filesystem path to an API path

    If given, root will be removed from the path.
    root must be a filesystem path already.
    """
    if os_path.startswith(root):
        os_path = os_path[len(root):]
    parts = os_path.strip(os.path.sep).split(os.path.sep)
    parts = [p for p in parts if p != ''] # remove duplicate splits
    path = '/'.join(parts)
    return path


def check_version(v, check):
    """check version string v >= check

    If dev/prerelease tags result in TypeError for string-number comparison,
    it is assumed that the dependency is satisfied.
    Users on dev branches are responsible for keeping their own packages up to date.
    """
    try:
        return LooseVersion(v) >= LooseVersion(check)
    except TypeError:
        return True


# Copy of IPython.utils.process.check_pid:

def _check_pid_win32(pid):
    import ctypes
    # OpenProcess returns 0 if no such process (of ours) exists
    # positive int otherwise
    return bool(ctypes.windll.kernel32.OpenProcess(1,0,pid))

def _check_pid_posix(pid):
    """Copy of IPython.utils.process.check_pid"""
    try:
        os.kill(pid, 0)
    except OSError as err:
        if err.errno == errno.ESRCH:
            return False
        elif err.errno == errno.EPERM:
            # Don't have permission to signal the process - probably means it exists
            return True
        raise
    else:
        return True

if sys.platform == 'win32':
    check_pid = _check_pid_win32
else:
    check_pid = _check_pid_posix


async def ensure_async(obj):
    """Convert a non-awaitable object to a coroutine if needed,
    and await it if it was not already awaited.
    """
    if inspect.isawaitable(obj):
        try:
            result = await obj
        except RuntimeError as e:
            if str(e) == 'cannot reuse already awaited coroutine':
                # obj is already the coroutine's result
                return obj
            raise
        return result
    # obj doesn't need to be awaited
    return obj


def run_sync(maybe_async):
    """If async, runs maybe_async and blocks until it has executed,
    possibly creating an event loop.
    If not async, just returns maybe_async as it is the result of something
    that has already executed.

    Parameters
    ----------
    maybe_async : async or non-async object
        The object to be executed, if it is async.

    Returns
    -------
    result :
        Whatever the async object returns, or the object itself.
    """
    if not inspect.isawaitable(maybe_async):
        # that was not something async, just return it
        return maybe_async
    # it is async, we need to run it in an event loop
    def wrapped():
        create_new_event_loop = False
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            create_new_event_loop = True
        else:
            if loop.is_closed():
                create_new_event_loop = True
        if create_new_event_loop:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(maybe_async)
        except RuntimeError as e:
            if str(e) == 'This event loop is already running':
                # just return a Future, hoping that it will be awaited
                result = asyncio.ensure_future(maybe_async)
            else:
                raise e
        return result
    return wrapped()
