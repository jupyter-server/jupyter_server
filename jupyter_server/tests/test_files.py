# coding: utf-8
"""Test the /files/ handler."""

import json
import io
import os
from os.path import join as pjoin

from nbformat import write
from nbformat.v4 import (new_notebook,
                         new_markdown_cell, new_code_cell,
                         new_output)

from jupyter_server.utils import url_path_join
from .launchserver import ServerTestBase


class FilesTest(ServerTestBase):

    def test_hidden_files(self):
        not_hidden = [
            u'å b',
            u'å b/ç. d',
        ]
        hidden = [
            u'.å b',
            u'å b/.ç d',
        ]
        dirs = not_hidden + hidden

        rootdir = self.root_dir
        for d in dirs:
            path = pjoin(rootdir, d.replace('/', os.sep))
            if not os.path.exists(path):
                os.mkdir(path)
            with open(pjoin(path, 'foo'), 'w') as f:
                f.write('foo')
            with open(pjoin(path, '.foo'), 'w') as f:
                f.write('.foo')

        for d in not_hidden:
            path = pjoin(rootdir, d.replace('/', os.sep))
            r = self.request('GET', url_path_join('files', d, 'foo'))
            r.raise_for_status()
            self.assertEqual(r.text, 'foo')
            r = self.request('GET', url_path_join('files', d, '.foo'))
            self.assertEqual(r.status_code, 404)

        for d in hidden:
            path = pjoin(rootdir, d.replace('/', os.sep))
            for foo in ('foo', '.foo'):
                r = self.request('GET', url_path_join('files', d, foo))
                self.assertEqual(r.status_code, 404)

        self.server.contents_manager.allow_hidden = True
        try:
            for d in not_hidden:
                path = pjoin(rootdir, d.replace('/', os.sep))
                r = self.request('GET', url_path_join('files', d, 'foo'))
                r.raise_for_status()
                self.assertEqual(r.text, 'foo')
                r = self.request('GET', url_path_join('files', d, '.foo'))
                r.raise_for_status()
                self.assertEqual(r.text, '.foo')

            for d in hidden:
                path = pjoin(rootdir, d.replace('/', os.sep))
                for foo in ('foo', '.foo'):
                    r = self.request('GET', url_path_join('files', d, foo))
                    r.raise_for_status()
                    self.assertEqual(r.text, foo)
        finally:
            self.server.contents_manager.allow_hidden = False

    def test_contents_manager(self):
        "make sure ContentsManager returns right files (ipynb, bin, txt)."

        rootdir = self.root_dir

        nb = new_notebook(
            cells=[
                new_markdown_cell(u'Created by test ³'),
                new_code_cell("print(2*6)", outputs=[
                    new_output("stream", text="12"),
                ])
            ]
        )

        with io.open(pjoin(rootdir, 'testnb.ipynb'), 'w',
            encoding='utf-8') as f:
            write(nb, f, version=4)

        with io.open(pjoin(rootdir, 'test.bin'), 'wb') as f:
            f.write(b'\xff' + os.urandom(5))
            f.close()

        with io.open(pjoin(rootdir, 'test.txt'), 'w') as f:
            f.write(u'foobar')
            f.close()

        r = self.request('GET', 'files/testnb.ipynb')
        self.assertEqual(r.status_code, 200)
        self.assertIn('print(2*6)', r.text)
        json.loads(r.text)

        r = self.request('GET', 'files/test.bin')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.headers['content-type'], 'application/octet-stream')
        self.assertEqual(r.content[:1], b'\xff')
        self.assertEqual(len(r.content), 6)

        r = self.request('GET', 'files/test.txt')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.headers['content-type'], 'text/plain; charset=UTF-8')
        self.assertEqual(r.text, 'foobar')

    def test_download(self):
        rootdir = self.root_dir

        text = 'hello'
        with open(pjoin(rootdir, 'test.txt'), 'w') as f:
            f.write(text)

        r = self.request('GET', 'files/test.txt')
        disposition = r.headers.get('Content-Disposition', '')
        self.assertNotIn('attachment', disposition)

        r = self.request('GET', 'files/test.txt?download=1')
        disposition = r.headers.get('Content-Disposition', '')
        self.assertIn('attachment', disposition)
        self.assertIn("filename*=utf-8''test.txt", disposition)

    def test_view_html(self):
        rootdir = self.root_dir

        html = '<div>Test test</div>'
        with open(pjoin(rootdir, 'test.html'), 'w') as f:
            f.write(html)

        r = self.request('GET', 'view/test.html')
        self.assertEqual(r.status_code, 200)

    def test_old_files_redirect(self):
        """pre-2.0 'files/' prefixed links are properly redirected"""
        rootdir = self.root_dir

        os.mkdir(pjoin(rootdir, 'files'))
        os.makedirs(pjoin(rootdir, 'sub', 'files'))

        for prefix in ('', 'sub'):
            with open(pjoin(rootdir, prefix, 'files', 'f1.txt'), 'w') as f:
                f.write(prefix + '/files/f1')
            with open(pjoin(rootdir, prefix, 'files', 'f2.txt'), 'w') as f:
                f.write(prefix + '/files/f2')
            with open(pjoin(rootdir, prefix, 'f2.txt'), 'w') as f:
                f.write(prefix + '/f2')
            with open(pjoin(rootdir, prefix, 'f3.txt'), 'w') as f:
                f.write(prefix + '/f3')

            # These depend on the tree handlers
            #
            #url = url_path_join('notebooks', prefix, 'files', 'f1.txt')
            #r = self.request('GET', url)
            #self.assertEqual(r.status_code, 200)
            #self.assertEqual(r.text, prefix + '/files/f1')

            #url = url_path_join('notebooks', prefix, 'files', 'f2.txt')
            #r = self.request('GET', url)
            #self.assertEqual(r.status_code, 200)
            #self.assertEqual(r.text, prefix + '/files/f2')

            #url = url_path_join('notebooks', prefix, 'files', 'f3.txt')
            #r = self.request('GET', url)
            #self.assertEqual(r.status_code, 200)
            #self.assertEqual(r.text, prefix + '/f3')

