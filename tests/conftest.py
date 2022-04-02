import os

import pytest

from tests.extension.mockextensions.app import MockExtensionApp

# Enforce WinPTY for Windows terminals, since the ConPTY backend
# dones not work in CI.
os.environ["PYWINPTY_BACKEND"] = "1"

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


mock_html = """
<!DOCTYPE HTML>
<html>
<head>
    <meta charset="utf-8">
    <title>{% block title %}Jupyter Server 1{% endblock %}</title>
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    {% block meta %}
    {% endblock %}
</head>
<body>
  <div id="site">
    {% block site %}
    {% endblock site %}
  </div>
  {% block after_site %}
  {% endblock after_site %}
</body>
</html>
"""


@pytest.fixture
def mock_template(jp_template_dir):
    index = jp_template_dir.joinpath("index.html")
    index.write_text(mock_html)


@pytest.fixture
def extension_manager(jp_serverapp):
    return jp_serverapp.extension_manager


@pytest.fixture
def config_file(jp_config_dir):
    """"""
    f = jp_config_dir.joinpath("jupyter_mockextension_config.py")
    f.write_text("c.MockExtensionApp.mock_trait ='config from file'")
    return f


@pytest.fixture(autouse=True)
def jp_mockextension_cleanup():
    yield
    MockExtensionApp.clear_instance()
