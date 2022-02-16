import pytest

from .mockextensions.app import MockExtensionApp


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
