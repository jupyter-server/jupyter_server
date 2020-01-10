import os
import pytest
import tornado

from .utils import expected_http_error

from nbformat import writes
from nbformat.v4 import (new_notebook,
                         new_markdown_cell, new_code_cell,
                         new_output)


async def test_hidden_files(fetch, serverapp, root_dir):
    not_hidden = [
        u'å b',
        u'å b/ç. d',
    ]
    hidden = [
        u'.å b',
        u'å b/.ç d',
    ]
    dirs = not_hidden + hidden

    for d in dirs:
        path  = root_dir / d.replace('/', os.sep)
        path.mkdir(parents=True, exist_ok=True)
        path.joinpath('foo').write_text('foo')
        path.joinpath('.foo').write_text('.foo')


    for d in not_hidden:
        path = root_dir / d.replace('/', os.sep)

        r = await fetch(
            'files', d, 'foo',
            method='GET'
        )
        assert r.body.decode() == 'foo'

        with pytest.raises(tornado.httpclient.HTTPClientError) as e:
            r = await fetch(
                'files', d, '.foo',
                method='GET'
            )
        assert expected_http_error(e, 404)


    for d in hidden:
        path = root_dir / d.replace('/', os.sep)
        for foo in ('foo', '.foo'):
            with pytest.raises(tornado.httpclient.HTTPClientError) as e:
                r = await fetch(
                    'files', d, foo,
                    method='GET'
                )
            assert expected_http_error(e, 404)

    serverapp.contents_manager.allow_hidden = True

    for d in not_hidden:
        path = root_dir / d.replace('/', os.sep)

        r = await fetch(
            'files', d, 'foo',
            method='GET'
        )
        assert r.body.decode() == 'foo'

        r = await fetch(
            'files', d, '.foo',
            method='GET'
        )
        assert r.body.decode() == '.foo'

        for d in hidden:
            path = root_dir / d.replace('/', os.sep)

            for foo in ('foo', '.foo'):
                r = await fetch(
                    'files', d, foo,
                    method='GET'
                )
                assert r.body.decode() == foo


async def test_contents_manager(fetch, serverapp, root_dir):
    "make sure ContentsManager returns right files (ipynb, bin, txt)."
    nb = new_notebook(
        cells=[
            new_markdown_cell(u'Created by test ³'),
            new_code_cell("print(2*6)", outputs=[
                new_output("stream", text="12"),
            ])
        ]
    )
    root_dir.joinpath('testnb.ipynb').write_text(writes(nb, version=4), encoding='utf-8')
    root_dir.joinpath('test.bin').write_bytes(b'\xff' + os.urandom(5))
    root_dir.joinpath('test.txt').write_text('foobar')

    r = await fetch(
        'files/testnb.ipynb',
        method='GET'
    )
    assert r.code == 200
    assert 'print(2*6)' in r.body.decode('utf-8')

    r = await fetch(
        'files/test.bin',
        method='GET'
    )
    assert r.code == 200
    assert r.headers['content-type'] == 'application/octet-stream'
    assert r.body[:1] == b'\xff'
    assert len(r.body) == 6

    r = await fetch(
        'files/test.txt',
        method='GET'
    )
    assert r.code == 200
    assert r.headers['content-type'] == 'text/plain; charset=UTF-8'
    assert r.body.decode() == 'foobar'


async def test_download(fetch, serverapp, root_dir):
    text = 'hello'
    root_dir.joinpath('test.txt').write_text(text)

    r = await fetch(
        'files', 'test.txt',
        method='GET'
    )
    disposition = r.headers.get('Content-Disposition', '')
    assert 'attachment' not in disposition

    r = await fetch(
        'files', 'test.txt',
        method='GET',
        params={'download': True}
    )
    disposition = r.headers.get('Content-Disposition', '')
    assert 'attachment' in disposition
    assert "filename*=utf-8''test.txt" in disposition


async def test_old_files_redirect(fetch, serverapp, root_dir):
    """pre-2.0 'files/' prefixed links are properly redirected"""
    root_dir.joinpath('files').mkdir(parents=True, exist_ok=True)
    root_dir.joinpath('sub', 'files').mkdir(parents=True, exist_ok=True)


    for prefix in ('', 'sub'):
        root_dir.joinpath(prefix, 'files', 'f1.txt').write_text(prefix + '/files/f1')
        root_dir.joinpath(prefix, 'files', 'f2.txt').write_text(prefix + '/files/f2')
        root_dir.joinpath(prefix, 'f2.txt').write_text(prefix + '/f2')
        root_dir.joinpath(prefix, 'f3.txt').write_text(prefix + '/f3')

    # These depend on the tree handlers
    #
    # def test_download(self):
    #     rootdir = self.root_dir

    #     text = 'hello'
    #     with open(pjoin(rootdir, 'test.txt'), 'w') as f:
    #         f.write(text)

    #     r = self.request('GET', 'files/test.txt')
    #     disposition = r.headers.get('Content-Disposition', '')
    #     self.assertNotIn('attachment', disposition)

    #     r = self.request('GET', 'files/test.txt?download=1')
    #     disposition = r.headers.get('Content-Disposition', '')
    #     self.assertIn('attachment', disposition)
    #     self.assertIn("filename*=utf-8''test.txt", disposition)