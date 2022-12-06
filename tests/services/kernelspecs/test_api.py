import json

import pytest
from tornado.httpclient import HTTPClientError

from jupyter_server.serverapp import ServerApp

from ...utils import expected_http_error, some_resource


async def test_list_kernelspecs_bad(jp_fetch, jp_kernelspecs, jp_data_dir, jp_serverapp):
    app: ServerApp = jp_serverapp
    default = app.kernel_manager.default_kernel_name
    bad_kernel_dir = jp_data_dir.joinpath(jp_data_dir, "kernels", "bad2")
    bad_kernel_dir.mkdir(parents=True)
    bad_kernel_json = bad_kernel_dir.joinpath("kernel.json")
    bad_kernel_json.write_text("garbage")

    r = await jp_fetch("api", "kernelspecs", method="GET")
    model = json.loads(r.body.decode())
    assert isinstance(model, dict)
    assert model["default"] == default
    specs = model["kernelspecs"]
    assert isinstance(specs, dict)
    assert len(specs) > 2


async def test_list_kernelspecs(jp_fetch, jp_kernelspecs, jp_serverapp):
    app: ServerApp = jp_serverapp
    default = app.kernel_manager.default_kernel_name
    r = await jp_fetch("api", "kernelspecs", method="GET")
    model = json.loads(r.body.decode())
    assert isinstance(model, dict)
    assert model["default"] == default
    specs = model["kernelspecs"]
    assert isinstance(specs, dict)
    assert len(specs) > 2

    def is_sample_kernelspec(s):
        return s["name"] == "sample" and s["spec"]["display_name"] == "Test kernel"

    def is_default_kernelspec(s):
        return s["name"] == default

    assert any(is_sample_kernelspec(s) for s in specs.values()), specs
    assert any(is_default_kernelspec(s) for s in specs.values()), specs


async def test_get_kernelspecs(jp_fetch, jp_kernelspecs):
    r = await jp_fetch("api", "kernelspecs", "Sample", method="GET")
    model = json.loads(r.body.decode())
    assert model["name"].lower() == "sample"
    assert isinstance(model["spec"], dict)
    assert model["spec"]["display_name"] == "Test kernel"
    assert isinstance(model["resources"], dict)


async def test_get_nonexistant_kernelspec(jp_fetch, jp_kernelspecs):
    with pytest.raises(HTTPClientError) as e:
        await jp_fetch("api", "kernelspecs", "nonexistant", method="GET")
    assert expected_http_error(e, 404)


async def test_get_kernel_resource_file(jp_fetch, jp_kernelspecs):
    r = await jp_fetch("kernelspecs", "sAmple", "resource.txt", method="GET")
    res = r.body.decode("utf-8")
    assert res == some_resource


async def test_get_nonexistant_resource(jp_fetch, jp_kernelspecs):
    with pytest.raises(HTTPClientError) as e:
        await jp_fetch("kernelspecs", "nonexistant", "resource.txt", method="GET")
    assert expected_http_error(e, 404)

    with pytest.raises(HTTPClientError) as e:
        await jp_fetch("kernelspecs", "sample", "nonexistant.txt", method="GET")
    assert expected_http_error(e, 404)
