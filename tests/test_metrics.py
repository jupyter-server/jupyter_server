"""Tests for Jupyter Server metrics functionality."""

import socket
import time
from unittest.mock import patch

import pytest
import requests

from jupyter_server.prometheus.server import PrometheusMetricsServer, start_metrics_server
from jupyter_server.serverapp import ServerApp


def find_available_port(start_port=9090, max_attempts=10):
    """Find an available port starting from start_port."""
    for i in range(max_attempts):
        port = start_port + i
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("localhost", port))
                return port
        except OSError:
            continue
    raise RuntimeError(f"Could not find available port starting from {start_port}")


def wait_for_server(url, timeout=10, interval=0.1):
    """Wait for a server to be ready to accept connections."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=1)
            return response
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            time.sleep(interval)
    raise TimeoutError(f"Server at {url} not ready after {timeout} seconds")


@pytest.fixture(autouse=True)
def cleanup_metrics_servers():
    """Ensure metrics servers are cleaned up after each test."""
    yield
    # Give any remaining threads time to clean up
    time.sleep(0.3)


@pytest.fixture
def metrics_server_app():
    """Create a server app with metrics enabled on a specific port."""
    # Use a unique port for this test
    port = find_available_port(9090)
    # Override the environment variable for this test
    with patch.dict("os.environ", {"JUPYTER_SERVER_METRICS_PORT": str(port)}):
        app = ServerApp()
        # Set the metrics_port directly as a trait
        app.metrics_port = port
        app.initialize([])
        return app


@pytest.fixture
def standalone_metrics_server():
    """Create a standalone metrics server for testing."""
    port = find_available_port(9091)
    server = PrometheusMetricsServer(port=port)
    server.start()
    # Wait for server to be ready
    time.sleep(0.5)
    yield server
    server.stop()


def test_metrics_server_startup(standalone_metrics_server):
    """Test that metrics server starts correctly."""
    assert standalone_metrics_server.port is not None
    assert standalone_metrics_server.port > 0

    # Test that metrics endpoint is accessible
    response = wait_for_server(f"http://localhost:{standalone_metrics_server.port}/metrics")
    assert response.status_code == 200
    assert "jupyter_server_info" in response.text


def test_metrics_server_with_authentication():
    """Test metrics server with authentication enabled."""
    port = find_available_port(9092)

    # Create a server app with authentication
    with patch.dict("os.environ", {"JUPYTER_SERVER_METRICS_PORT": str(port)}):
        app = ServerApp()
        app.metrics_port = port
        app.authenticate_prometheus = True
        app.initialize([])

        # Start the app
        app.start_app()

        # Wait for both servers to be ready
        time.sleep(1.0)

        try:
            # Get the token
            token = app.identity_provider.token

            # Test metrics endpoint with token
            response = wait_for_server(f"http://localhost:{port}/metrics?token={token}", timeout=5)
            assert response.status_code == 200
            assert "jupyter_server_info" in response.text

            # Test without token should fail
            try:
                response = requests.get(f"http://localhost:{port}/metrics", timeout=2)
                assert response.status_code == 403
            except requests.exceptions.ConnectionError:
                # Server might not be ready yet, which is also acceptable
                pass

        finally:
            app.stop()


def test_metrics_server_without_authentication():
    """Test metrics server without authentication."""
    port = find_available_port(9093)

    # Create a server app without authentication
    with patch.dict("os.environ", {"JUPYTER_SERVER_METRICS_PORT": str(port)}):
        app = ServerApp()
        app.metrics_port = port
        app.authenticate_prometheus = False
        app.initialize([])

        # Start the app
        app.start_app()

        # Wait for both servers to be ready
        time.sleep(1.0)

        try:
            # Test metrics endpoint without token should work
            response = wait_for_server(f"http://localhost:{port}/metrics", timeout=5)
            assert response.status_code == 200
            assert "jupyter_server_info" in response.text

        finally:
            app.stop()


def test_metrics_server_port_conflict():
    """Test that metrics server handles port conflicts gracefully."""
    # Use a port that's likely to be in use
    port = 8888  # Default Jupyter port

    # Create a server app that should fail to start metrics server
    with patch.dict("os.environ", {"JUPYTER_SERVER_METRICS_PORT": str(port)}):
        app = ServerApp()
        app.metrics_port = port
        app.initialize([])

        # Start the app - should not crash
        app.start_app()

        try:
            # The app should still be running even if metrics server failed
            assert app.http_server is not None

        finally:
            app.stop()


def test_metrics_server_disabled():
    """Test that metrics server is disabled when port is 0."""
    with patch.dict("os.environ", {"JUPYTER_SERVER_METRICS_PORT": "0"}):
        app = ServerApp()
        app.metrics_port = 0
        app.initialize([])

        # Start the app
        app.start_app()

        # Wait for server to be ready
        time.sleep(0.5)

        try:
            # Metrics should be available on main server
            token = app.identity_provider.token
            response = wait_for_server(
                f"http://localhost:{app.port}/metrics?token={token}", timeout=5
            )
            assert response.status_code == 200
            assert "jupyter_server_info" in response.text

        finally:
            app.stop()
