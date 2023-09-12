import json

import pytest
from tornado.httpclient import HTTPClientError

from jupyter_server.serverapp import ServerApp

from ...utils import expected_http_error, some_resource


@pytest.fixture(params=[False, True])
def jp_rename_kernels(request):
    return request.param


@pytest.fixture
def jp_argv(jp_rename_kernels):
    argv = []
    if jp_rename_kernels:
        argv.extend(
            [
                "--ServerApp.kernel_spec_manager_class=jupyter_server.services.kernelspecs.renaming.RenamingKernelSpecManager",
            ]
        )
    return argv


async def test_list_kernelspecs_bad(
    jp_rename_kernels, jp_fetch, jp_kernelspecs, jp_data_dir, jp_serverapp
):
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


async def test_list_kernelspecs(jp_rename_kernels, jp_fetch, jp_kernelspecs, jp_serverapp):
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
        if jp_rename_kernels:
            return (
                s["name"] == "local-sample" and s["spec"]["display_name"] == "Test kernel (Local)"
            )
        else:
            return s["name"] == "sample" and s["spec"]["display_name"] == "Test kernel"

    def is_default_kernelspec(s):
        return s["name"] == default

    assert any(is_sample_kernelspec(s) for s in specs.values()), specs
    assert any(
        is_default_kernelspec(s) for s in specs.values()
    ), f"Default kernel name {default} not found in {specs}"


async def test_get_kernelspecs(jp_rename_kernels, jp_fetch, jp_kernelspecs):
    kernel_name = "Sample"
    if jp_rename_kernels:
        kernel_name = "local-sample"
    r = await jp_fetch("api", "kernelspecs", kernel_name, method="GET")
    model = json.loads(r.body.decode())
    if jp_rename_kernels:
        assert model["name"].lower() == "local-sample"
    else:
        assert model["name"].lower() == "sample"

    assert isinstance(model["spec"], dict)
    if jp_rename_kernels:
        assert model["spec"]["display_name"] == "Test kernel (Local)"
    else:
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
