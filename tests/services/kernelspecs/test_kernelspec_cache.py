# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
"""Tests for KernelSpecCache."""

import asyncio
import json
import shutil
import sys
from pathlib import Path

import pytest
from jupyter_client.kernelspec import NoSuchKernel
from traitlets.config import Config

from jupyter_server.services.kernelspecs.kernelspec_cache import KernelSpecCache

kernelspec_json = {
    "argv": ["cat", "{connection_file}"],
    "display_name": "Test kernel: {kernel_name}",
}


def _install_kernelspec(kernels_dir: Path, kernel_name: str) -> Path:
    """install a sample kernel in a kernels directory"""
    kernelspec_dir = kernels_dir / kernel_name
    kernelspec_dir.mkdir(parents=True)
    json_file = Path(kernelspec_dir) / "kernel.json"
    named_json = kernelspec_json.copy()
    named_json["display_name"] = str(named_json["display_name"]).format(kernel_name=kernel_name)
    with open(str(json_file), "w") as f:
        json.dump(named_json, f)
    return kernelspec_dir


def _modify_kernelspec(kernelspec_dir: str, kernel_name: str) -> None:
    json_file = Path(kernelspec_dir) / "kernel.json"
    kernel_json = kernelspec_json.copy()
    kernel_json["display_name"] = f"{kernel_name} modified!"
    with open(str(json_file), "w") as f:
        json.dump(kernel_json, f)


@pytest.fixture
def other_kernelspec_location(jp_env_jupyter_path):
    other_location = Path(jp_env_jupyter_path) / "kernels"
    other_location.mkdir()
    return other_location


@pytest.fixture
def setup_kernelspecs(jp_environ, jp_kernel_dir):
    # Only populate factory info
    _install_kernelspec(jp_kernel_dir, "test1")
    _install_kernelspec(jp_kernel_dir, "test2")
    _install_kernelspec(jp_kernel_dir, "test3")


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
                    "monitor_name": request.param,
                },
            }
        }
    )
    # Increase polling frequency to avoid long test delays
    if request.param == "polling-monitor" and is_enabled:
        config["ServerApp"]["KernelSpecPollingMonitor"]["interval"] = 1.0

    app = jp_configurable_serverapp(config=config)
    yield app.kernel_spec_cache
    app.kernel_spec_cache = None
    app.clear_instance()


def get_delay_factor(kernel_spec_cache: KernelSpecCache) -> float:
    if kernel_spec_cache.cache_enabled:
        if kernel_spec_cache.monitor_name == "polling-monitor":
            return 2.0
        elif kernel_spec_cache.monitor_name == "watchdog-monitor":
            # watchdog on Windows appears to be a bit slower
            return 2.0 if sys.platform.startswith("win") else 1.0
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


async def test_add_spec(kernel_spec_cache, jp_kernel_dir, other_kernelspec_location):
    with pytest.raises(NoSuchKernel):
        await kernel_spec_cache.get_kernel_spec("added")  # this will increment cache_miss

    _install_kernelspec(other_kernelspec_location, "added")
    # this will increment cache_miss prior to load
    kspec = await kernel_spec_cache.get_kernel_spec("added")

    assert kspec.display_name == "Test kernel: added"
    # Cache misses should be 2, one for prior to adding the spec, the other after discovering its addition
    assert kernel_spec_cache.cache_misses == (2 if kernel_spec_cache.cache_enabled else 0)

    # Add another to an existing observed directory, no cache miss here
    _install_kernelspec(jp_kernel_dir, "added2")
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
