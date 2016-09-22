"""The Jupyter HTML Server"""

import os

DEFAULT_STATIC_FILES_PATH = os.path.join(os.path.dirname(__file__), "static")

# Packagers: modify the next line if you store the template files elsewhere

# Include both jupyter_server/ and jupyter_server/templates/.  This makes it
# possible for users to override a template with a file that inherits from that
# template.
#
# For example, if you want to override a specific block of notebook.html, you
# can create a file called notebook.html that inherits from
# templates/notebook.html, and the latter will resolve correctly to the base
# implementation.
DEFAULT_TEMPLATE_PATH_LIST = [
    os.path.dirname(__file__),
    os.path.join(os.path.dirname(__file__), "templates"),
]

del os

from ._version import version_info, __version__
