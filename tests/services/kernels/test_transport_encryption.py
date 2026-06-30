"""End-to-end tests for MappingKernelManager.transport_encryption."""

import json
import sys
import warnings

import jupyter_client
import pytest
import zmq
from traitlets.config import Config

TEST_TIMEOUT = 60

pytestmark = [
    pytest.mark.skipif(
        jupyter_client._version.version_info < (8, 9),
        reason="transport_encryption requires jupyter-client >= 8.9",
    ),
    pytest.mark.skipif(
        not zmq.has("curve"),
        reason="CurveZMQ not available in this environment (zmq.has('curve') is False)",
    ),
]


@pytest.fixture(autouse=True)
def suppress_deprecation_warnings():
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message="The synchronous MappingKernelManager",
            category=DeprecationWarning,
        )
        yield


@pytest.fixture
def non_curve_kernel_spec(jp_data_dir):
    """Install a minimal kernel spec that does not declare curve encryption support."""
    kernel_dir = jp_data_dir / "kernels" / "no_curve"
    kernel_dir.mkdir(parents=True)
    (kernel_dir / "kernel.json").write_text(
        json.dumps(
            {
                "argv": [sys.executable, "-c", "pass"],
                "display_name": "No Curve",
                "language": "python",
            }
        )
    )
    return "no_curve"


@pytest.mark.timeout(TEST_TIMEOUT)
async def test_transport_encryption_disabled_no_curve_keys(jp_configurable_serverapp):
    """Default 'disabled' policy never provisions curve keys, even for kernels that support them."""
    app = jp_configurable_serverapp()
    km = app.kernel_manager
    kernel_id = await km.start_kernel()
    try:
        kernel = km.get_kernel(kernel_id)
        info = kernel.get_connection_info()
        assert "curve_publickey" not in info
        assert "curve_secretkey" not in info
    finally:
        await km.shutdown_kernel(kernel_id, now=True)


@pytest.mark.timeout(TEST_TIMEOUT)
@pytest.mark.parametrize("policy", ["auto", "required"])
async def test_transport_encryption_provisions_curve_keys(jp_configurable_serverapp, policy):
    """'auto' and 'required' both provision curve keys for kernelspecs that declare curve support."""
    config = Config({"MappingKernelManager": {"transport_encryption": policy}})
    app = jp_configurable_serverapp(config=config)
    km = app.kernel_manager
    kernel_id = await km.start_kernel()
    try:
        kernel = km.get_kernel(kernel_id)
        info = kernel.get_connection_info()
        assert "curve_publickey" in info
        assert "curve_secretkey" in info
    finally:
        await km.shutdown_kernel(kernel_id, now=True)


@pytest.mark.timeout(TEST_TIMEOUT)
async def test_transport_encryption_auto_skips_keys_for_non_curve_kernel(
    non_curve_kernel_spec, jp_configurable_serverapp
):
    """'auto' silently skips key provisioning when the kernelspec lacks curve support metadata."""
    config = Config({"MappingKernelManager": {"transport_encryption": "auto"}})
    app = jp_configurable_serverapp(config=config)
    km = app.kernel_manager
    kernel_id = await km.start_kernel(kernel_name=non_curve_kernel_spec)
    try:
        kernel = km.get_kernel(kernel_id)
        info = kernel.get_connection_info()
        assert "curve_publickey" not in info
        assert "curve_secretkey" not in info
    finally:
        await km.shutdown_kernel(kernel_id, now=True)


async def test_transport_encryption_required_raises_for_non_curve_kernel(
    non_curve_kernel_spec, jp_configurable_serverapp
):
    """'required' raises RuntimeError at startup when the kernelspec lacks curve support metadata."""
    config = Config({"MappingKernelManager": {"transport_encryption": "required"}})
    app = jp_configurable_serverapp(config=config)
    with pytest.raises(RuntimeError, match=r"metadata\.supported_encryption"):
        await app.kernel_manager.start_kernel(kernel_name=non_curve_kernel_spec)
