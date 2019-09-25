
import re
import nose.tools as nt

from jupyter_server.base.handlers import path_regex


# build regexps that tornado uses:
path_pat = re.compile('^' + '/x%s' % path_regex + '$')

def test_path_regex():
    for path in (
        '/x',
        '/x/',
        '/x/foo',
        '/x/foo.ipynb',
        '/x/foo/bar',
        '/x/foo/bar.txt',
    ):
        nt.assert_regex(path, path_pat)

def test_path_regex_bad():
    for path in (
        '/xfoo',
        '/xfoo/',
        '/xfoo/bar',
        '/xfoo/bar/',
        '/x/foo/bar/',
        '/x//foo',
        '/y',
        '/y/x/foo',
    ):
        nt.assert_not_regex(path, path_pat)
