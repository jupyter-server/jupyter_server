import sys
import time
import json
import shutil
import pytest

import tornado

from nbformat.v4 import new_notebook
from nbformat import writes

from ...utils import expected_http_error

j = lambda r: json.loads(r.body.decode())


@pytest.fixture(params=["MappingKernelManager", "AsyncMappingKernelManager"])
def argv(request):
    if request.param == "AsyncMappingKernelManager" and sys.version_info < (3, 6):
        pytest.skip("Kernel manager is AsyncMappingKernelManager, Python version < 3.6")
    return ["--ServerApp.kernel_manager_class=jupyter_server.services.kernels.kernelmanager." + request.param]


class SessionClient:

    def __init__(self, fetch_callable):
        self.fetch = fetch_callable

    async def _req(self, *args, method, body=None):
        if body is not None:
            body = json.dumps(body)

        r = await self.fetch(
            'api', 'sessions', *args,
            method=method,
            body=body,
            allow_nonstandard_methods=True
        )
        return r

    async def list(self):
        return await self._req(method='GET')

    async def get(self, id):
        return await self._req(id, method='GET')

    async def create(
        self,
        path,
        type='notebook',
        kernel_name='python',
        kernel_id=None):
        body = {
            'path': path,
            'type': type,
            'kernel': {
                'name': kernel_name,
                'id': kernel_id
            }
        }
        return await self._req(method='POST', body=body)

    def create_deprecated(self, path):
        body = {
            'notebook': {
                'path': path
            },
            'kernel': {
                'name': 'python',
                'id': 'foo'
            }
        }
        return self._req(method='POST', body=body)

    def modify_path(self, id, path):
        body = {'path': path}
        return self._req(id, method='PATCH', body=body)

    def modify_path_deprecated(self, id, path):
        body = {'notebook': {'path': path}}
        return self._req(id, method='PATCH', body=body)

    def modify_type(self, id, type):
        body = {'type': type}
        return self._req(id, method='PATCH', body=body)

    def modify_kernel_name(self, id, kernel_name):
        body = {'kernel': {'name': kernel_name}}
        return self._req(id, method='PATCH', body=body)

    def modify_kernel_id(self, id, kernel_id):
        # Also send a dummy name to show that id takes precedence.
        body = {'kernel': {'id': kernel_id, 'name': 'foo'}}
        return self._req(id, method='PATCH', body=body)

    async def delete(self, id):
        return await self._req(id, method='DELETE')

    async def cleanup(self):
        resp = await self.list()
        sessions = j(resp)
        for session in sessions:
            await self.delete(session['id'])
        time.sleep(0.1)



@pytest.fixture
def session_client(root_dir, fetch):
    subdir = root_dir.joinpath('foo')
    subdir.mkdir()

    # Write a notebook to subdir.
    nb = new_notebook()
    nb_str = writes(nb, version=4)
    nbpath = subdir.joinpath('nb1.ipynb')
    nbpath.write_text(nb_str, encoding='utf-8')

    # Yield a session client
    client = SessionClient(fetch)
    yield client

    # Remove subdir
    shutil.rmtree(str(subdir), ignore_errors=True)


def assert_kernel_equality(actual, expected):
    """ Compares kernel models after taking into account that execution_states
        may differ from 'starting' to 'idle'.  The 'actual' argument is the
        current state (which may have an 'idle' status) while the 'expected'
        argument is the previous state (which may have a 'starting' status).
    """
    actual.pop('execution_state', None)
    actual.pop('last_activity', None)
    expected.pop('execution_state', None)
    expected.pop('last_activity', None)
    assert actual == expected


def assert_session_equality(actual, expected):
    """ Compares session models.  `actual` is the most current session,
        while `expected` is the target of the comparison.  This order
        matters when comparing the kernel sub-models.
    """
    assert actual['id'] == expected['id']
    assert actual['path'] == expected['path']
    assert actual['type'] == expected['type']
    assert_kernel_equality(actual['kernel'], expected['kernel'])


async def test_create(session_client):
    # Make sure no sessions exist.
    resp = await session_client.list()
    sessions = j(resp)
    assert len(sessions) == 0

    # Create a session.
    resp = await session_client.create('foo/nb1.ipynb')
    assert resp.code == 201
    new_session = j(resp)
    assert 'id' in new_session
    assert new_session['path'] == 'foo/nb1.ipynb'
    assert new_session['type'] == 'notebook'
    assert resp.headers['Location'] == '/api/sessions/' + new_session['id']

    # Check that the new session appears in list.
    resp = await session_client.list()
    sessions = j(resp)
    assert len(sessions) == 1
    assert_session_equality(sessions[0], new_session)

    # Retrieve that session.
    sid = new_session['id']
    resp = await session_client.get(sid)
    got = j(resp)
    assert_session_equality(got, new_session)

    # Need to find a better solution to this.
    await session_client.cleanup()


async def test_create_file_session(session_client):
    resp = await session_client.create('foo/nb1.py', type='file')
    assert resp.code == 201
    newsession = j(resp)
    assert newsession['path'] == 'foo/nb1.py'
    assert newsession['type'] == 'file'
    await session_client.cleanup()


async def test_create_console_session(session_client):
    resp = await session_client.create('foo/abc123', type='console')
    assert resp.code == 201
    newsession = j(resp)
    assert newsession['path'] == 'foo/abc123'
    assert newsession['type'] == 'console'
    # Need to find a better solution to this.
    await session_client.cleanup()


async def test_create_deprecated(session_client):
    resp = await session_client.create_deprecated('foo/nb1.ipynb')
    assert resp.code == 201
    newsession = j(resp)
    assert newsession['path'] == 'foo/nb1.ipynb'
    assert newsession['type'] == 'notebook'
    assert newsession['notebook']['path'] == 'foo/nb1.ipynb'
    # Need to find a better solution to this.
    await session_client.cleanup()


async def test_create_with_kernel_id(session_client, fetch):
    # create a new kernel
    resp = await fetch('api/kernels', method='POST', allow_nonstandard_methods=True)
    kernel = j(resp)

    resp = await session_client.create('foo/nb1.ipynb', kernel_id=kernel['id'])
    assert resp.code == 201
    new_session = j(resp)
    assert 'id' in new_session
    assert new_session['path'] == 'foo/nb1.ipynb'
    assert new_session['kernel']['id'] == kernel['id']
    assert resp.headers['Location'] == '/api/sessions/{0}'.format(new_session['id'])

    resp = await session_client.list()
    sessions = j(resp)
    assert len(sessions) == 1
    assert_session_equality(sessions[0], new_session)

    # Retrieve it
    sid = new_session['id']
    resp = await session_client.get(sid)
    got = j(resp)
    assert_session_equality(got, new_session)
    # Need to find a better solution to this.
    await session_client.cleanup()

async def test_delete(session_client):
    resp = await session_client.create('foo/nb1.ipynb')
    newsession = j(resp)
    sid = newsession['id']

    resp = await session_client.delete(sid)
    assert resp.code == 204

    resp = await session_client.list()
    sessions = j(resp)
    assert sessions == []

    with pytest.raises(tornado.httpclient.HTTPClientError) as e:
        await session_client.get(sid)
    assert expected_http_error(e, 404)
    # Need to find a better solution to this.
    await session_client.cleanup()

async def test_modify_path(session_client):
    resp = await session_client.create('foo/nb1.ipynb')
    newsession = j(resp)
    sid = newsession['id']

    resp = await session_client.modify_path(sid, 'nb2.ipynb')
    changed = j(resp)
    assert changed['id'] == sid
    assert changed['path'] == 'nb2.ipynb'
    # Need to find a better solution to this.
    await session_client.cleanup()

async def test_modify_path_deprecated(session_client):
    resp = await session_client.create('foo/nb1.ipynb')
    newsession = j(resp)
    sid = newsession['id']

    resp = await session_client.modify_path_deprecated(sid, 'nb2.ipynb')
    changed = j(resp)
    assert changed['id'] == sid
    assert changed['notebook']['path'] == 'nb2.ipynb'
    # Need to find a better solution to this.
    await session_client.cleanup()

async def test_modify_type(session_client):
    resp = await session_client.create('foo/nb1.ipynb')
    newsession = j(resp)
    sid = newsession['id']

    resp = await session_client.modify_type(sid, 'console')
    changed = j(resp)
    assert changed['id'] == sid
    assert changed['type'] == 'console'
    # Need to find a better solution to this.
    await session_client.cleanup()

async def test_modify_kernel_name(session_client, fetch):
    resp = await session_client.create('foo/nb1.ipynb')
    before = j(resp)
    sid = before['id']

    resp = await session_client.modify_kernel_name(sid, before['kernel']['name'])
    after = j(resp)
    assert after['id'] == sid
    assert after['path'] == before['path']
    assert after['type'] == before['type']
    assert after['kernel']['id'] != before['kernel']['id']

    # check kernel list, to be sure previous kernel was cleaned up
    resp = await fetch('api/kernels', method='GET')
    kernel_list = j(resp)
    after['kernel'].pop('last_activity')
    [ k.pop('last_activity') for k in kernel_list ]
    assert kernel_list == [after['kernel']]
    # Need to find a better solution to this.
    await session_client.cleanup()


async def test_modify_kernel_id(session_client, fetch):
    resp = await session_client.create('foo/nb1.ipynb')
    before = j(resp)
    sid = before['id']

    # create a new kernel
    resp = await fetch('api/kernels', method='POST', allow_nonstandard_methods=True)
    kernel = j(resp)

    # Attach our session to the existing kernel
    resp = await session_client.modify_kernel_id(sid, kernel['id'])
    after = j(resp)
    assert after['id'] == sid
    assert after['path'] == before['path']
    assert after['type'] == before['type']
    assert after['kernel']['id'] != before['kernel']['id']
    assert after['kernel']['id'] == kernel['id']

    # check kernel list, to be sure previous kernel was cleaned up
    resp = await fetch('api/kernels', method='GET')
    kernel_list = j(resp)

    kernel.pop('last_activity')
    [ k.pop('last_activity') for k in kernel_list ]
    assert kernel_list == [kernel]

    # Need to find a better solution to this.
    await session_client.cleanup()
