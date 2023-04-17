#!/usr/bin/env python3
#
# Jupyter Server documentation build configuration file, created by
# sphinx-quickstart on Mon Apr 13 09:51:11 2015.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.
import os
import os.path as osp
import shutil
import sys

HERE = osp.abspath(osp.dirname(__file__))
sys.path.insert(0, osp.join(HERE, "..", ""))
from jupyter_server import JUPYTER_SERVER_EVENTS
from jupyter_server._version import version_info

# -- General configuration ------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autosummary",
    "sphinx.ext.mathjax",
    "sphinx.ext.napoleon",
    "IPython.sphinxext.ipython_console_highlighting",
    "sphinxcontrib_github_alt",
    "sphinxcontrib.openapi",
    "sphinxemoji.sphinxemoji",
    "sphinx_autodoc_typehints",
]

try:
    import enchant  # type:ignore  # noqa

    extensions += ["sphinxcontrib.spelling"]
except ImportError:
    pass

myst_enable_extensions = ["html_image", "substitution"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
# source_suffix = ['.rst', '.md']
source_suffix = [".rst", ".ipynb"]

# The encoding of source files.
# source_encoding = 'utf-8-sig'

# The master toctree document.
master_doc = "index"

# General information about the project.
project = "Jupyter Server"
copyright = "2020, Jupyter Team, https://jupyter.org"
author = "The Jupyter Team"

# ghissue config
github_project_url = "https://github.com/jupyter/jupyter_server"

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = f"{version_info[0]}.{version_info[1]}"

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = "en"

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
# today = ''
# Else, today_fmt is used as the format for a strftime call.
# today_fmt = '%B %d, %Y'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# exclude_patterns = []

# The reST default role (used for this markup: `text`) to use for all
# documents.
default_role = "literal"

# If true, '()' will be appended to :func: etc. cross-reference text.
# add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
# add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
# show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "default"
# highlight_language = 'python3'

# A list of ignored prefixes for module index sorting.
# modindex_common_prefix = []

# If true, keep warnings as "system message" paragraphs in the built documents.
# keep_warnings = False

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False

# # Add custom note for each doc page

# rst_prolog = ""

# rst_prolog += """
# .. important::
#     This documentation covers Jupyter Server, an **early developer preview**,
#     and is not suitable for general usage yet. Features and implementation are
#     subject to change.

#     For production use cases, please use the stable notebook server in the
#     `Jupyter Notebook repo <https://github.com/jupyter/notebook>`_
#     and `Jupyter Notebook documentation <https://jupyter-notebook.readthedocs.io/en/stable/public_server.html>`_.
# """

# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
# html_theme = 'sphinx_rtd_theme'
html_theme = "pydata_sphinx_theme"
html_logo = "_static/jupyter_server_logo.svg"

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
# html_theme_options = {}

# Add any paths that contain custom themes here, relative to this directory.
# html_theme_path = []

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
# html_title = None

# A shorter title for the navigation bar.  Default is the same as html_title.
# html_short_title = None

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
# html_logo = None

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
# html_favicon = None

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# NOTE: Sphinx's 'make html' builder will throw a warning about an unfound
#       _static directory. Do not remove or comment out html_static_path
#       since it is needed to properly generate _static in the build directory
html_static_path = ["_static"]

# Add any extra paths that contain custom files (such as robots.txt or
# .htaccess) here, relative to this directory. These files are copied
# directly to the root of the documentation.
# html_extra_path = []

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
# html_last_updated_fmt = '%b %d, %Y'

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
# html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.
# html_sidebars = {}

# Additional templates that should be rendered to pages, maps page names to
# template names.
# html_additional_pages = {}

# If false, no module index is generated.
# html_domain_indices = True

# If false, no index is generated.
# html_use_index = True

# If true, the index is split into individual pages for each letter.
# html_split_index = False

# If true, links to the reST sources are added to the pages.
# html_show_sourcelink = True

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
# html_show_sphinx = True

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
# html_show_copyright = True

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
# html_use_opensearch = ''

# This is the file name suffix for HTML files (e.g. ".xhtml").
# html_file_suffix = None

# Language to be used for generating the HTML full-text search index.
# Sphinx supports the following languages:
#   'da', 'de', 'en', 'es', 'fi', 'fr', 'h', 'it', 'ja'
#   'nl', 'no', 'pt', 'ro', 'r', 'sv', 'tr'
# html_search_language = 'en'

# A dictionary with options for the search language support, empty by default.
# Now only 'ja' uses this config value
# html_search_options = {'type': 'default'}

# The name of a javascript file (relative to the configuration directory) that
# implements a search results scorer. If empty, the default will be used.
# html_search_scorer = 'scorer.js'

# Output file base name for HTML help builder.
htmlhelp_basename = "JupyterServerdoc"

# -- Options for LaTeX output ---------------------------------------------

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (
        master_doc,
        "JupyterServer.tex",
        "Jupyter Server Documentation",
        "https://jupyter.org",
        "manual",
    ),
]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
# latex_logo = None

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
# latex_use_parts = False

# If true, show page references after internal links.
# latex_show_pagerefs = False

# If true, show URL addresses after external links.
# latex_show_urls = False

# Documents to append as an appendix to all manuals.
# latex_appendices = []

# If false, no module index is generated.
# latex_domain_indices = True


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [(master_doc, "jupyterserver", "Jupyter Server Documentation", [author], 1)]

# If true, show URL addresses after external links.
# man_show_urls = False


# -- Options for link checks ----------------------------------------------

linkcheck_ignore = [r"http://127\.0\.0\.1/*"]


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        master_doc,
        "JupyterServer",
        "Jupyter Server Documentation",
        author,
        "JupyterServer",
        "One line description of project.",
        "Miscellaneous",
    ),
]

# Documents to append as an appendix to all manuals.
# texinfo_appendices = []

# If false, no module index is generated.
# texinfo_domain_indices = True

# How to display URL addresses: 'footnote', 'no', or 'inline'.
# texinfo_show_urls = 'footnote'

# If true, do not generate a @detailmenu in the "Top" node's menu.
# texinfo_no_detailmenu = False

intersphinx_mapping = {
    "python": ("https://docs.python.org/", None),
    "ipython": ("https://ipython.readthedocs.io/en/stable/", None),
    "nbconvert": ("https://nbconvert.readthedocs.io/en/stable/", None),
    "nbformat": ("https://nbformat.readthedocs.io/en/stable/", None),
    "jupyter_core": ("https://jupyter-core.readthedocs.io/en/stable/", None),
    "tornado": ("https://www.tornadoweb.org/en/stable/", None),
    "traitlets": ("https://traitlets.readthedocs.io/en/stable/", None),
}

spelling_lang = "en_US"
spelling_word_list_filename = "spelling_wordlist.txt"

# import before any doc is built, so _ is guaranteed to be injected
import jupyter_server.transutils  # noqa: F401

CONFIG_HEADER = """\
.. _other-full-config:


Config file and command line options
====================================

The Jupyter Server can be run with a variety of command line arguments.
A list of available options can be found below in the :ref:`options section
<options>`.

Defaults for these options can also be set by creating a file named
``jupyter_server_config.py`` in your Jupyter folder. The Jupyter
folder is in your home directory, ``~/.jupyter``.

To create a ``jupyter_server_config.py`` file, with all the defaults
commented out, you can use the following command line::

  $ jupyter server --generate-config


.. _options:

Options
-------

This list of options can be generated by running the following and hitting
enter::

  $ jupyter server --help-all

"""


def setup(app):
    dest = osp.join(HERE, "other", "changelog.md")
    shutil.copy(osp.join(HERE, "..", "..", "CHANGELOG.md"), dest)

    # Generate full-config docs.
    from jupyter_server.serverapp import ServerApp

    destination = os.path.join(HERE, "other/full-config.rst")
    with open(destination, "w") as f:
        f.write(CONFIG_HEADER)
        f.write(ServerApp().document_config_options())


# Create a markdown list of the core events emitted by Jupyter Server.
event_list_md = ""
for event in JUPYTER_SERVER_EVENTS:
    event_list_md += f"* `{event}`\n"

myst_substitutions = {"jupyter_server_events": event_list_md}
