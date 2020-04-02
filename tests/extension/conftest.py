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
def enabled_extensions(serverapp):
    return serverapp._enabled_extensions
