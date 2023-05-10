# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
"""Tests for KernelSpecCache."""

import asyncio
import json
import os
import shutil

import pytest
from jupyter_client.kernelspec import NoSuchKernel
from pytest_jupyter.utils import mkdir
from traitlets.config import Config

from jupyter_server.services.kernelspecs.kernelspec_cache import KernelSpecCache

kernelspec_json = {
    "argv": ["cat", "{connection_file}"],
    "display_name": "Test kernel: {kernel_name}",
}


def _install_kernelspec(kernels_dir, kernel_name):
    """install a sample kernel in a kernels directory"""
    kernelspec_dir = os.path.join(kernels_dir, kernel_name)
    os.makedirs(kernelspec_dir)
    json_file = os.path.join(kernelspec_dir, "kernel.json")
    named_json = kernelspec_json.copy()
    named_json["display_name"] = named_json["display_name"].format(kernel_name=kernel_name)
    with open(json_file, "w") as f:
        json.dump(named_json, f)
    return kernelspec_dir


def _modify_kernelspec(kernelspec_dir, kernel_name):
    json_file = os.path.join(kernelspec_dir, "kernel.json")
    kernel_json = kernelspec_json.copy()
    kernel_json["display_name"] = f"{kernel_name} modified!"
    with open(json_file, "w") as f:
        json.dump(kernel_json, f)


kernelspec_location = pytest.fixture(lambda jp_data_dir: mkdir(jp_data_dir, "kernels"))
other_kernelspec_location = pytest.fixture(
    lambda jp_env_jupyter_path: mkdir(jp_env_jupyter_path, "kernels")
)


@pytest.fixture
def setup_kernelspecs(jp_environ, kernelspec_location):
    # Only populate factory info
    _install_kernelspec(str(kernelspec_location), "test1")
    _install_kernelspec(str(kernelspec_location), "test2")
    _install_kernelspec(str(kernelspec_location), "test3")


MONITORS = ["watchdog-monitor", "polling-monitor"]


@pytest.fixture(params=MONITORS)
def kernel_spec_cache(
    jp_environ, setup_kernelspecs, request, is_enabled, jp_configurable_serverapp
):
    config = Config(
        {
            "ServerApp": {
                "KernelSpecManager": {
                    "ensure_native_kernel": False,
                },
                "KernelSpecCache": {
                    "cache_enabled": is_enabled,
                    "monitor_entry_point": request.param,
                },
                "KernelSpecPollingMonitor": {
                    "interval": 1.0 if request.param == "polling-monitor" else 30.0,
                },
            }
        }
    )
    app = jp_configurable_serverapp(config=config)
    yield app.kernel_spec_cache


def get_delay_factor(kernel_spec_cache: KernelSpecCache):
    if kernel_spec_cache.cache_enabled:
        if kernel_spec_cache.monitor_entry_point == "polling-monitor":
            return 2.0
        return 1.0
    return 0.5


@pytest.fixture(params=[False, True])  # Add types as needed
def is_enabled(request):
    return request.param


async def test_get_all_specs(kernel_spec_cache):
    kspecs = await kernel_spec_cache.get_all_specs()
    assert len(kspecs) == 4  # The 3 we create, plus the echo kernel that jupyter_core adds


async def test_get_named_spec(kernel_spec_cache):
    kspec = await kernel_spec_cache.get_kernel_spec("test2")
    assert kspec.display_name == "Test kernel: test2"


async def test_get_modified_spec(kernel_spec_cache):
    kspec = await kernel_spec_cache.get_kernel_spec("test2")
    assert kspec.display_name == "Test kernel: test2"

    # Modify entry
    _modify_kernelspec(kspec.resource_dir, "test2")
    await asyncio.sleep(get_delay_factor(kernel_spec_cache))  # sleep to allow cache to update item
    kspec = await kernel_spec_cache.get_kernel_spec("test2")
    assert kspec.display_name == "test2 modified!"


async def test_add_spec(kernel_spec_cache, kernelspec_location, other_kernelspec_location):
    with pytest.raises(NoSuchKernel):
        await kernel_spec_cache.get_kernel_spec("added")  # this will increment cache_miss

    _install_kernelspec(str(other_kernelspec_location), "added")
    # this will increment cache_miss prior to load
    kspec = await kernel_spec_cache.get_kernel_spec("added")

    assert kspec.display_name == "Test kernel: added"
    # Cache misses should be 2, one for prior to adding the spec, the other after discovering its addition
    assert kernel_spec_cache.cache_misses == (2 if kernel_spec_cache.cache_enabled else 0)

    # Add another to an existing observed directory, no cache miss here
    _install_kernelspec(str(kernelspec_location), "added2")
    await asyncio.sleep(
        get_delay_factor(kernel_spec_cache)
    )  # sleep to allow cache to add item (no cache miss in this case)
    kspec = await kernel_spec_cache.get_kernel_spec("added2")

    assert kspec.display_name == "Test kernel: added2"
    assert kernel_spec_cache.cache_misses == (2 if kernel_spec_cache.cache_enabled else 0)


async def test_remove_spec(kernel_spec_cache):
    kspec = await kernel_spec_cache.get_kernel_spec("test2")
    assert kspec.display_name == "Test kernel: test2"

    assert kernel_spec_cache.cache_misses == 0
    shutil.rmtree(kspec.resource_dir)
    await asyncio.sleep(get_delay_factor(kernel_spec_cache))  # sleep to allow cache to remove item
    with pytest.raises(NoSuchKernel):
        await kernel_spec_cache.get_kernel_spec("test2")

    assert kernel_spec_cache.cache_misses == (1 if kernel_spec_cache.cache_enabled else 0)


async def test_get_missing(kernel_spec_cache):
    with pytest.raises(NoSuchKernel):
        await kernel_spec_cache.get_kernel_spec("missing")

    assert kernel_spec_cache.cache_misses == (1 if kernel_spec_cache.cache_enabled else 0)
