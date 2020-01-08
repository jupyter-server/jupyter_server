# coding: utf-8
import io
import json
import os
from os.path import join as pjoin
import shutil

import tornado

from nbformat import writes
from nbformat.v4 import (
    new_notebook, new_markdown_cell, new_code_cell, new_output,
)

from ipython_genutils.testing.decorators import onlyif_cmds_exist

from base64 import encodebytes

import pytest

from ..utils import expected_http_error


png_green_pixel = encodebytes(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00'
b'\x00\x00\x01\x00\x00x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDAT'
b'\x08\xd7c\x90\xfb\xcf\x00\x00\x02\\\x01\x1e.~d\x87\x00\x00\x00\x00IEND\xaeB`\x82'
).decode('ascii')


@pytest.fixture
def notebook(root_dir):
    # Build sub directory.
    if not root_dir.joinpath('foo').is_dir():
        subdir = root_dir / 'foo'
        subdir.mkdir()

    # Build a notebook programmatically.
    nb = new_notebook()
    nb.cells.append(new_markdown_cell(u'Created by test ³'))
    cc1 = new_code_cell(source=u'print(2*6)')
    cc1.outputs.append(new_output(output_type="stream", text=u'12'))
    cc1.outputs.append(new_output(output_type="execute_result",
        data={'image/png' : png_green_pixel},
        execution_count=1,
    ))
    nb.cells.append(cc1)

    # Write file to tmp dir.
    nbfile = subdir / 'testnb.ipynb'
    nbfile.write_text(writes(nb, version=4), encoding='utf-8')


@onlyif_cmds_exist('pandoc')
async def test_from_file(fetch, notebook):
    r = await fetch(
        'nbconvert', 'html', 'foo', 'testnb.ipynb',
        method='GET',
        params={'download': False}
    )

    assert r.code == 200
    assert 'text/html' in r.headers['Content-Type']
    assert 'Created by test' in r.body.decode()
    assert 'print' in r.body.decode()

    r = await fetch(
        'nbconvert', 'python', 'foo', 'testnb.ipynb',
        method='GET',
        params={'download': False}
    )

    assert r.code == 200
    assert 'text/x-python' in r.headers['Content-Type']
    assert 'print(2*6)' in r.body.decode()


@onlyif_cmds_exist('pandoc')
async def test_from_file_404(fetch, notebook):
    with pytest.raises(tornado.httpclient.HTTPClientError) as e:
        await fetch(
            'nbconvert', 'html', 'foo', 'thisdoesntexist.ipynb',
            method='GET',
            params={'download': False}
        )
    assert expected_http_error(e, 404)


@onlyif_cmds_exist('pandoc')
async def test_from_file_download(fetch, notebook):
    r = await fetch(
        'nbconvert', 'python', 'foo', 'testnb.ipynb',
        method='GET',
        params={'download': True}
    )
    content_disposition = r.headers['Content-Disposition']
    assert 'attachment' in content_disposition
    assert 'testnb.py' in content_disposition


@onlyif_cmds_exist('pandoc')
async def test_from_file_zip(fetch, notebook):
    r = await fetch(
        'nbconvert', 'latex', 'foo', 'testnb.ipynb',
        method='GET',
        params={'download': True}
    )
    assert 'application/zip' in r.headers['Content-Type']
    assert '.zip' in r.headers['Content-Disposition']


@onlyif_cmds_exist('pandoc')
async def test_from_post(fetch, notebook):
    r = await fetch(
        'api/contents/foo/testnb.ipynb',
        method='GET',
    )
    nbmodel = json.loads(r.body.decode())

    r = await fetch(
        'nbconvert', 'html',
        method='POST',
        body=json.dumps(nbmodel)
    )
    assert r.code == 200
    assert 'text/html' in r.headers['Content-Type']
    assert 'Created by test' in r.body.decode()
    assert 'print' in r.body.decode()

    r = await fetch(
        'nbconvert', 'python',
        method='POST',
        body=json.dumps(nbmodel)
    )
    assert r.code == 200
    assert u'text/x-python' in r.headers['Content-Type']
    assert 'print(2*6)'in r.body.decode()


@onlyif_cmds_exist('pandoc')
async def test_from_post_zip(fetch, notebook):
    r = await fetch(
        'api/contents/foo/testnb.ipynb',
        method='GET',
    )
    nbmodel = json.loads(r.body.decode())

    r = await fetch(
        'nbconvert', 'latex',
        method='POST',
        body=json.dumps(nbmodel)
    )
    assert 'application/zip' in r.headers['Content-Type']
    assert '.zip' in r.headers['Content-Disposition']