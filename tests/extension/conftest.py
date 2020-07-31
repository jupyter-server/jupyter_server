import pytest


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
def mock_template(template_dir):
    index = template_dir.joinpath('index.html')
    index.write_text(mock_html)


@pytest.fixture
def extension_manager(serverapp):
    return serverapp.extension_manager


@pytest.fixture
def config_file(config_dir):
    """"""
    f = config_dir.joinpath("jupyter_mockextension_config.py")
    f.write_text("c.MockExtensionApp.mock_trait ='config from file'")
    return f