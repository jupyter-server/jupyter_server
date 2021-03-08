# coding: utf-8
import json

import tornado

from nbformat import writes
from nbformat.v4 import (
    new_notebook, new_markdown_cell, new_code_cell, new_output,
)

from shutil import which


from base64 import encodebytes

import pytest

from ..utils import expected_http_error


png_green_pixel = encodebytes(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00'
b'\x00\x00\x01\x00\x00x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDAT'
b'\x08\xd7c\x90\xfb\xcf\x00\x00\x02\\\x01\x1e.~d\x87\x00\x00\x00\x00IEND\xaeB`\x82'
).decode('ascii')


@pytest.fixture
def notebook(jp_root_dir):
    # Build sub directory.
    subdir = jp_root_dir / 'foo'
    if not jp_root_dir.joinpath('foo').is_dir():
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


pytestmark = pytest.mark.skipif(not which('pandoc'), reason="Command 'pandoc' is not available")


async def test_from_file(jp_fetch, notebook):
    r = await jp_fetch(
        'nbconvert', 'html', 'foo', 'testnb.ipynb',
        method='GET',
        params={'download': False}
    )

    assert r.code == 200
    assert 'text/html' in r.headers['Content-Type']
    assert 'Created by test' in r.body.decode()
    assert 'print' in r.body.decode()

    r = await jp_fetch(
        'nbconvert', 'python', 'foo', 'testnb.ipynb',
        method='GET',
        params={'download': False}
    )

    assert r.code == 200
    assert 'text/x-python' in r.headers['Content-Type']
    assert 'print(2*6)' in r.body.decode()


async def test_from_file_404(jp_fetch, notebook):
    with pytest.raises(tornado.httpclient.HTTPClientError) as e:
        await jp_fetch(
            'nbconvert', 'html', 'foo', 'thisdoesntexist.ipynb',
            method='GET',
            params={'download': False}
        )
    assert expected_http_error(e, 404)


async def test_from_file_download(jp_fetch, notebook):
    r = await jp_fetch(
        'nbconvert', 'python', 'foo', 'testnb.ipynb',
        method='GET',
        params={'download': True}
    )
    content_disposition = r.headers['Content-Disposition']
    assert 'attachment' in content_disposition
    assert 'testnb.py' in content_disposition


async def test_from_file_zip(jp_fetch, notebook):
    r = await jp_fetch(
        'nbconvert', 'latex', 'foo', 'testnb.ipynb',
        method='GET',
        params={'download': True}
    )
    assert 'application/zip' in r.headers['Content-Type']
    assert '.zip' in r.headers['Content-Disposition']


async def test_from_post(jp_fetch, notebook):
    r = await jp_fetch(
        'api/contents/foo/testnb.ipynb',
        method='GET',
    )
    nbmodel = json.loads(r.body.decode())

    r = await jp_fetch(
        'nbconvert', 'html',
        method='POST',
        body=json.dumps(nbmodel)
    )
    assert r.code == 200
    assert 'text/html' in r.headers['Content-Type']
    assert 'Created by test' in r.body.decode()
    assert 'print' in r.body.decode()

    r = await jp_fetch(
        'nbconvert', 'python',
        method='POST',
        body=json.dumps(nbmodel)
    )
    assert r.code == 200
    assert u'text/x-python' in r.headers['Content-Type']
    assert 'print(2*6)'in r.body.decode()


async def test_from_post_zip(jp_fetch, notebook):
    r = await jp_fetch(
        'api/contents/foo/testnb.ipynb',
        method='GET',
    )
    nbmodel = json.loads(r.body.decode())

    r = await jp_fetch(
        'nbconvert', 'latex',
        method='POST',
        body=json.dumps(nbmodel)
    )
    assert 'application/zip' in r.headers['Content-Type']
    assert '.zip' in r.headers['Content-Disposition']
