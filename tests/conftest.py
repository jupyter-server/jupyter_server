import os

import pytest
from nbformat import writes
from nbformat.v4 import new_notebook

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


@pytest.fixture
def contents_dir(tmp_path, jp_serverapp):
    return tmp_path / jp_serverapp.root_dir


dirs = [
    ("", "inroot"),
    ("Directory with spaces in", "inspace"),
    ("unicodé", "innonascii"),
    ("foo", "a"),
    ("foo", "b"),
    ("foo", "name with spaces"),
    ("foo", "unicodé"),
    ("foo/bar", "baz"),
    ("ordering", "A"),
    ("ordering", "b"),
    ("ordering", "C"),
    ("å b", "ç d"),
]


@pytest.fixture
def contents(contents_dir):
    # Create files in temporary directory
    paths: dict = {"notebooks": [], "textfiles": [], "blobs": [], "contents_dir": contents_dir}
    for d, name in dirs:
        p = contents_dir / d
        p.mkdir(parents=True, exist_ok=True)

        # Create a notebook
        nb = writes(new_notebook(), version=4)
        nbname = p.joinpath(f"{name}.ipynb")
        nbname.write_text(nb, encoding="utf-8")
        paths["notebooks"].append(nbname.relative_to(contents_dir))

        # Create a text file
        txt = f"{name} text file"
        txtname = p.joinpath(f"{name}.txt")
        txtname.write_text(txt, encoding="utf-8")
        paths["textfiles"].append(txtname.relative_to(contents_dir))

        # Create a random blob
        blob = name.encode("utf-8") + b"\xFF"
        blobname = p.joinpath(f"{name}.blob")
        blobname.write_bytes(blob)
        paths["blobs"].append(blobname.relative_to(contents_dir))
    paths["all"] = list(paths.values())
    return paths


@pytest.fixture
def folders():
    return list({item[0] for item in dirs})
