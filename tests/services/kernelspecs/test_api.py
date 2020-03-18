import pytest
import json

import tornado

from jupyter_server.pytest_plugin import some_resource

from ...utils import expected_http_error


async def test_list_kernelspecs_bad(fetch, kernelspecs, data_dir):
    bad_kernel_dir = data_dir.joinpath(data_dir, 'kernels', 'bad')
    bad_kernel_dir.mkdir(parents=True)
    bad_kernel_json = bad_kernel_dir.joinpath('kernel.json')
    bad_kernel_json.write_text('garbage')

    r = await fetch(
        'api', 'kernelspecs',
        method='GET'
    )
    model = json.loads(r.body.decode())
    assert isinstance(model, dict)
    assert model['default'] == 'pyimport/kernel'
    specs = model['kernelspecs']
    assert isinstance(specs, dict)
    assert len(specs) > 2


async def test_list_kernelspecs(fetch, kernelspecs):
    r = await fetch(
        'api', 'kernelspecs',
        method='GET'
    )
    model = json.loads(r.body.decode())
    assert isinstance(model, dict)
    assert model['default'] == 'pyimport/kernel'
    specs = model['kernelspecs']
    assert isinstance(specs, dict)
    assert len(specs) > 2

    def is_sample_kernelspec(s):
        return s['name'] == 'spec/sample' and s['spec']['display_name'] == 'Test kernel'

    def is_default_kernelspec(s):
        return s['name'] == 'pyimport/kernel' and s['spec']['display_name'].startswith("Python")

    assert any(is_sample_kernelspec(s) for s in specs.values()), specs
    assert any(is_default_kernelspec(s) for s in specs.values()), specs


async def test_get_kernelspecs(fetch, kernelspecs):
    r = await fetch(
        'api', 'kernelspecs', 'spec%2FSample',
        method='GET'
    )
    model = json.loads(r.body.decode())
    assert model['name'].lower() == 'spec/sample'
    assert isinstance(model['spec'], dict)
    assert model['spec']['display_name'] == 'Test kernel'
    assert isinstance(model['resources'], dict)


async def test_get_kernelspec_spaces(fetch, kernelspecs):
    r = await fetch(
        'api', 'kernelspecs', 'spec%2Fsample%202',
        method='GET'
    )
    model = json.loads(r.body.decode())
    assert model['name'].lower() == 'spec/sample 2'


async def test_get_nonexistant_kernelspec(fetch, kernelspecs):
    with pytest.raises(tornado.httpclient.HTTPClientError) as e:
        await fetch(
            'api', 'kernelspecs', 'spec/nonexistant',
            method='GET'
        )
    assert expected_http_error(e, 404)


async def test_get_kernel_resource_file(fetch, kernelspecs):
    r = await fetch(
        'kernelspecs', 'spec%2FsAmple', 'resource.txt',
        method='GET'
    )
    res = r.body.decode('utf-8')
    assert res == some_resource


async def test_get_nonexistant_resource(fetch, kernelspecs):
    with pytest.raises(tornado.httpclient.HTTPClientError) as e:
        await fetch(
            'kernelspecs', 'spec%2Fnonexistant', 'resource.txt',
            method='GET'
        )
    assert expected_http_error(e, 404)

    with pytest.raises(tornado.httpclient.HTTPClientError) as e:
        await fetch(
            'kernelspecs', 'spec%2Fsample', 'nonexistant.txt',
            method='GET'
        )
    assert expected_http_error(e, 404)
