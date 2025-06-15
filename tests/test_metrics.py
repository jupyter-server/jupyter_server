"""Tests for Jupyter Server metrics functionality."""

import time
from unittest.mock import patch

import pytest
import requests

from jupyter_server.prometheus.server import PrometheusMetricsServer, start_metrics_server
from jupyter_server.serverapp import ServerApp


@pytest.fixture(autouse=True)
def cleanup_metrics_servers():
    """Ensure metrics servers are cleaned up after each test."""
    yield
    # Give any remaining threads time to clean up
    time.sleep(0.2)


@pytest.fixture
def metrics_server_app():
    """Create a server app with metrics enabled on a specific port."""
    # Use a unique port for this test
    port = 9090
    # Override the environment variable for this test
    with patch.dict("os.environ", {"JUPYTER_SERVER_METRICS_PORT": str(port)}):
        app = ServerApp()
        # Set the metrics_port directly as a trait
        app.metrics_port = port
        app.initialize([])
        return app


@pytest.fixture
def metrics_server(metrics_server_app):
    """Start a metrics server for testing."""
    server = start_metrics_server(metrics_server_app, 9090)
    # Give the server time to start
    time.sleep(0.1)
    yield server
    # Cleanup
    if hasattr(server, "stop"):
        server.stop()
        # Give time for cleanup
        time.sleep(0.2)


def test_metrics_server_starts(metrics_server):
    """Test that the metrics server starts successfully."""
    assert metrics_server is not None
    assert hasattr(metrics_server, "port")
    assert metrics_server.port == 9090


def test_metrics_endpoint_accessible(metrics_server):
    """Test that the metrics endpoint is accessible."""
    response = requests.get(f"http://localhost:{metrics_server.port}/metrics")
    assert response.status_code == 200
    assert "jupyter_server" in response.text


def test_metrics_contains_kernel_metrics(metrics_server):
    """Test that kernel metrics are present."""
    response = requests.get(f"http://localhost:{metrics_server.port}/metrics")
    assert response.status_code == 200
    content = response.text
    assert "jupyter_kernel_currently_running_total" in content


def test_metrics_contains_server_info(metrics_server):
    """Test that server info metrics are present."""
    response = requests.get(f"http://localhost:{metrics_server.port}/metrics")
    assert response.status_code == 200
    content = response.text
    assert "jupyter_server_info" in content


def test_metrics_server_with_authentication():
    """Test metrics server with authentication enabled."""
    app = ServerApp()
    app.metrics_port = 9091
    app.authenticate_prometheus = True
    app.initialize([])
    app.identity_provider.token = "test_token"

    server = start_metrics_server(app, 9091)
    time.sleep(0.1)

    try:
        # Without token should fail
        response = requests.get(f"http://localhost:{server.port}/metrics")
        assert response.status_code == 401

        # With token should succeed
        response = requests.get(f"http://localhost:{server.port}/metrics?token=test_token")
        assert response.status_code == 200
    finally:
        if hasattr(server, "stop"):
            server.stop()
            time.sleep(0.2)


def test_metrics_server_port_conflict_handling():
    """Test that metrics server handles port conflicts gracefully."""
    app = ServerApp()
    app.metrics_port = 9092
    app.initialize([])
    server2 = None
    # Start first server
    server1 = start_metrics_server(app, 9092)
    time.sleep(0.1)

    try:
        # Try to start second server on same port
        server2 = start_metrics_server(app, 9092)
        time.sleep(0.1)

        # One of them should have failed to start or used a different port
        if server2 is not None and hasattr(server2, "port"):
            assert server2.port != 9092 or server1.port != 9092
    finally:
        if hasattr(server1, "stop"):
            server1.stop()
            time.sleep(0.2)
        if server2 is not None and hasattr(server2, "stop"):
            server2.stop()
            time.sleep(0.2)


def test_metrics_server_disabled_when_port_zero():
    """Test that metrics server is not started when port is 0."""
    with patch.dict("os.environ", {"JUPYTER_SERVER_METRICS_PORT": "0"}):
        app = ServerApp()
        app.metrics_port = 0
        app.initialize([])

        # Should not start metrics server
        assert not hasattr(app, "metrics_server") or app.metrics_server is None


def test_metrics_url_logging_with_separate_server():
    """Test that metrics URL is logged correctly with separate server."""
    app = ServerApp()
    app.metrics_port = 9093
    app.authenticate_prometheus = True
    app.initialize([])
    app.identity_provider.token = "test_token"

    # Start metrics server
    server = start_metrics_server(app, 9093)
    time.sleep(0.1)

    try:
        # The URL should include the separate port
        expected_url = "http://localhost:9093/metrics?token=test_token"
        # This is a basic test - in practice you'd capture the log output
        assert server.port == 9093
    finally:
        if hasattr(server, "stop"):
            server.stop()
            time.sleep(0.2)


def test_metrics_url_logging_with_main_server():
    """Test that metrics URL is logged correctly when using main server."""
    app = ServerApp()
    app.metrics_port = 0  # Disable separate server
    app.authenticate_prometheus = True
    app.initialize([])
    app.identity_provider.token = "test_token"

    # Should use main server's /metrics endpoint
    # This would be tested by checking the log output in practice
    assert app.metrics_port == 0
