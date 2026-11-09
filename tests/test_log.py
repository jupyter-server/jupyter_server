"""Tests for log utilities."""

from unittest.mock import Mock

import pytest

from jupyter_server.log import log_request
from jupyter_server.serverapp import ServerApp


@pytest.fixture
def server_app_with_extra_scrub_keys():
    """Fixture that returns a ServerApp with custom extra_log_scrub_param_keys."""
    app = ServerApp()
    app.extra_log_scrub_param_keys = ["password", "secret"]
    return app


@pytest.fixture
def server_app_with_default_scrub_keys():
    """Fixture that returns a ServerApp with default extra_log_scrub_param_keys."""
    app = ServerApp()
    return app


def test_log_request_scrubs_sensitive_params_default(server_app_with_default_scrub_keys, caplog):
    """Test that log_request scrubs sensitive parameters using default configuration."""
    handler = Mock()
    handler.get_status.return_value = 200
    handler.request.method = "GET"
    handler.request.remote_ip = "127.0.0.1"
    handler.request.uri = "http://example.com/path?token=secret123&normal=value"
    handler.request.request_time.return_value = 0.1
    handler.settings = {
        "extra_log_scrub_param_keys": server_app_with_default_scrub_keys.extra_log_scrub_param_keys
    }
    handler.log = Mock()
    handler.current_user = None

    log_request(handler, record_prometheus_metrics=False)

    handler.log.debug.assert_called_once()
    call_args = handler.log.debug.call_args[0][0]

    assert "secret123" not in call_args
    assert "[secret]" in call_args
    assert "normal=value" in call_args


def test_log_request_scrubs_sensitive_params_extra(server_app_with_extra_scrub_keys, caplog):
    """Test that log_request scrubs sensitive parameters using extra configuration."""
    handler = Mock()
    handler.get_status.return_value = 200
    handler.request.method = "GET"
    handler.request.remote_ip = "127.0.0.1"
    handler.request.uri = (
        "http://example.com/path?password=secret123&token=default_token&normal=value"
    )
    handler.request.request_time.return_value = 0.1
    handler.settings = {
        "extra_log_scrub_param_keys": server_app_with_extra_scrub_keys.extra_log_scrub_param_keys
    }
    handler.log = Mock()
    handler.current_user = None

    log_request(handler, record_prometheus_metrics=False)

    handler.log.debug.assert_called_once()
    call_args = handler.log.debug.call_args[0][0]

    assert "secret123" not in call_args
    assert "default_token" not in call_args
    assert "[secret]" in call_args
    assert "normal=value" in call_args


def test_log_request_scrubs_referer_in_5xx_header_dump(server_app_with_default_scrub_keys, caplog):
    """Test that the 5xx JSON header dump scrubs sensitive params from the Referer header. GHSA-c3mw-737p-c7g2"""
    handler = Mock()
    handler.get_status.return_value = 500
    handler.request.method = "POST"
    handler.request.remote_ip = "127.0.0.1"
    handler.request.uri = "http://example.com/api/kernels"
    handler.request.request_time.return_value = 0.1
    handler.request.headers = {"Referer": "http://example.com/tree?token=REFERTOKEN"}
    handler.settings = {
        "extra_log_scrub_param_keys": server_app_with_default_scrub_keys.extra_log_scrub_param_keys
    }
    handler.log = Mock()
    handler.current_user = None

    log_request(handler, record_prometheus_metrics=False)

    call_args = handler.log.error.call_args_list[0][0][0]

    assert "REFERTOKEN" not in call_args
    assert "[secret]" in call_args
