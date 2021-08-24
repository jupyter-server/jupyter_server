import pytest


pytest_plugins = ["jupyter_server.pytest_plugin"]


def pytest_addoption(parser):
    parser.addoption(
        "--integration_tests",
        default=False,
        type=bool,
        help="only run tests with the 'integration_test' pytest mark.",
    )


def pytest_configure(config):
    # register an additional marker
    config.addinivalue_line("markers", "integration_test")


def pytest_runtest_setup(item):
    is_integration_test = any(mark for mark in item.iter_markers(name="integration_test"))

    if item.config.getoption("--integration_tests") is True:
        if not is_integration_test:
            pytest.skip("Only running tests marked as 'integration_test'.")
    else:
        if is_integration_test:
            pytest.skip(
                "Skipping this test because it's marked 'integration_test'. Run integration tests using the `--integration_tests` flag."
            )
