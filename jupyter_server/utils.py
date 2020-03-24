"""Notebook related utilities"""

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

from __future__ import print_function

import asyncio
import concurrent.futures
import ctypes
import errno
import inspect
import os
import stat
import sys
from distutils.version import LooseVersion
from contextlib import contextmanager


from urllib.parse import quote, unquote, urlparse, urljoin
from urllib.request import pathname2url


# tornado.concurrent.Future is asyncio.Future
# in tornado >=5 with Python 3
from tornado.concurrent import Future as TornadoFuture
from tornado import gen
from ipython_genutils import py3compat

# UF_HIDDEN is a stat flag not defined in the stat module.
# It is used by BSD to indicate hidden files.
UF_HIDDEN = getattr(stat, 'UF_HIDDEN', 32768)


def exists(path):
    """Replacement for `os.path.exists` which works for host mapped volumes
    on Windows containers
    """
    try:
        os.lstat(path)
    except OSError:
        return False
    return True


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


def is_file_hidden_win(abs_path, stat_res=None):
    """Is a file hidden?

    This only checks the file itself; it should be called in combination with
    checking the directory containing the file.

    Use is_hidden() instead to check the file and its parent directories.

    Parameters
    ----------
    abs_path : unicode
        The absolute path to check.
    stat_res : os.stat_result, optional
        Ignored on Windows, exists for compatibility with POSIX version of the
        function.
    """
    if os.path.basename(abs_path).startswith('.'):
        return True

    win32_FILE_ATTRIBUTE_HIDDEN = 0x02
    try:
        attrs = ctypes.windll.kernel32.GetFileAttributesW(
            py3compat.cast_unicode(abs_path)
        )
    except AttributeError:
        pass
    else:
        if attrs > 0 and attrs & win32_FILE_ATTRIBUTE_HIDDEN:
            return True

    return False

def is_file_hidden_posix(abs_path, stat_res=None):
    """Is a file hidden?

    This only checks the file itself; it should be called in combination with
    checking the directory containing the file.

    Use is_hidden() instead to check the file and its parent directories.

    Parameters
    ----------
    abs_path : unicode
        The absolute path to check.
    stat_res : os.stat_result, optional
        The result of calling stat() on abs_path. If not passed, this function
        will call stat() internally.
    """
    if os.path.basename(abs_path).startswith('.'):
        return True

    if stat_res is None or stat.S_ISLNK(stat_res.st_mode):
        try:
            stat_res = os.stat(abs_path)
        except OSError as e:
            if e.errno == errno.ENOENT:
                return False
            raise

    # check that dirs can be listed
    if stat.S_ISDIR(stat_res.st_mode):
        # use x-access, not actual listing, in case of slow/large listings
        if not os.access(abs_path, os.X_OK | os.R_OK):
            return True

    # check UF_HIDDEN
    if getattr(stat_res, 'st_flags', 0) & UF_HIDDEN:
        return True

    return False

if sys.platform == 'win32':
    is_file_hidden = is_file_hidden_win
else:
    is_file_hidden = is_file_hidden_posix

def is_hidden(abs_path, abs_root=''):
    """Is a file hidden or contained in a hidden directory?

    This will start with the rightmost path element and work backwards to the
    given root to see if a path is hidden or in a hidden directory. Hidden is
    determined by either name starting with '.' or the UF_HIDDEN flag as
    reported by stat.

    If abs_path is the same directory as abs_root, it will be visible even if
    that is a hidden folder. This only checks the visibility of files
    and directories *within* abs_root.

    Parameters
    ----------
    abs_path : unicode
        The absolute path to check for hidden directories.
    abs_root : unicode
        The absolute path of the root directory in which hidden directories
        should be checked for.
    """
    if os.path.normpath(abs_path) == os.path.normpath(abs_root):
        return False

    if is_file_hidden(abs_path):
        return True

    if not abs_root:
        abs_root = abs_path.split(os.sep, 1)[0] + os.sep
    inside_root = abs_path[len(abs_root):]
    if any(part.startswith('.') for part in inside_root.split(os.sep)):
        return True

    # check UF_HIDDEN on any location up to root.
    # is_file_hidden() already checked the file, so start from its parent dir
    path = os.path.dirname(abs_path)
    while path and path.startswith(abs_root) and path != abs_root:
        if not exists(path):
            path = os.path.dirname(path)
            continue
        try:
            # may fail on Windows junctions
            st = os.lstat(path)
        except OSError:
            return True
        if getattr(st, 'st_flags', 0) & UF_HIDDEN:
            return True
        path = os.path.dirname(path)

    return False

# TODO: Move to jupyter_core
def win32_restrict_file_to_user(fname):
    """Secure a windows file to read-only access for the user.
    Follows guidance from win32 library creator:
    http://timgolden.me.uk/python/win32_how_do_i/add-security-to-a-file.html

    This method should be executed against an already generated file which
    has no secrets written to it yet.

    Parameters
    ----------

    fname : unicode
        The path to the file to secure
    """
    import win32api
    import win32security
    import ntsecuritycon as con

    # everyone, _domain, _type = win32security.LookupAccountName("", "Everyone")
    admins = win32security.CreateWellKnownSid(win32security.WinBuiltinAdministratorsSid)
    user, _domain, _type = win32security.LookupAccountName("", win32api.GetUserName())

    sd = win32security.GetFileSecurity(fname, win32security.DACL_SECURITY_INFORMATION)

    dacl = win32security.ACL()
    # dacl.AddAccessAllowedAce(win32security.ACL_REVISION, con.FILE_ALL_ACCESS, everyone)
    dacl.AddAccessAllowedAce(win32security.ACL_REVISION, con.FILE_GENERIC_READ | con.FILE_GENERIC_WRITE, user)
    dacl.AddAccessAllowedAce(win32security.ACL_REVISION, con.FILE_ALL_ACCESS, admins)

    sd.SetSecurityDescriptorDacl(1, dacl, 0)
    win32security.SetFileSecurity(fname, win32security.DACL_SECURITY_INFORMATION, sd)

# TODO: Move to jupyter_core
@contextmanager
def secure_write(fname, binary=False):
    """Opens a file in the most restricted pattern available for
    writing content. This limits the file mode to `600` and yields
    the resulting opened filed handle.

    Parameters
    ----------

    fname : unicode
        The path to the file to write
    """
    mode = 'wb' if binary else 'w'
    open_flag = os.O_CREAT | os.O_WRONLY | os.O_TRUNC
    try:
        os.remove(fname)
    except (IOError, OSError):
        # Skip any issues with the file not existing
        pass

    if os.name == 'nt':
        # Python on windows does not respect the group and public bits for chmod, so we need
        # to take additional steps to secure the contents.
        # Touch file pre-emptively to avoid editing permissions in open files in Windows
        fd = os.open(fname, os.O_CREAT | os.O_WRONLY | os.O_TRUNC, 0o600)
        os.close(fd)
        open_flag = os.O_WRONLY | os.O_TRUNC
        win32_restrict_file_to_user(fname)

    with os.fdopen(os.open(fname, open_flag, 0o600), mode) as f:
        if os.name != 'nt':
            # Enforce that the file got the requested permissions before writing
            assert '0600' == oct(stat.S_IMODE(os.stat(fname).st_mode)).replace('0o', '0')
        yield f

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
        return result
    return wrapped()
