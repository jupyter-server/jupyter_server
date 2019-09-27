#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup script for Jupyter Server"""

#-----------------------------------------------------------------------------
#  Copyright (c) 2015-, Jupyter Development Team.
#  Copyright (c) 2008-2015, IPython Development Team.
#
#  Distributed under the terms of the Modified BSD License.
#
#  The full license is in the file COPYING.md, distributed with this software.
#-----------------------------------------------------------------------------

from __future__ import print_function

import os
import sys

name = "jupyter_server"

# Minimal Python version sanity check
if sys.version_info < (3,5):
    error = "ERROR: %s requires Python version 3.5 or above." % name
    print(error, file=sys.stderr)
    sys.exit(1)

# At least we're on the python version we need, move on.

# BEFORE importing distutils, remove MANIFEST. distutils doesn't properly
# update it when the contents of directories change.
if os.path.exists('MANIFEST'): os.remove('MANIFEST')

from setuptools import setup

from setupbase import (
    version,
    find_packages,
    find_package_data,
    check_package_data_first,
)

setup_args = dict(
    name            = name,
    description     = "The Jupyter Server",
    long_description = """
The Jupyter Server is a web application that allows you to create and
share documents that contain live code, equations, visualizations, and
explanatory text. The Notebook has support for multiple programming
languages, sharing, and interactive widgets.

Read `the documentation <https://jupyter-server.readthedocs.io>`_
for more information.
    """,
    version         = version,
    packages        = find_packages(),
    package_data    = find_package_data(),
    author          = 'Jupyter Development Team',
    author_email    = 'jupyter@googlegroups.com',
    url             = 'http://jupyter.org',
    license         = 'BSD',
    platforms       = "Linux, Mac OS X, Windows",
    keywords        = ['Interactive', 'Interpreter', 'Shell', 'Web'],
    classifiers     = [
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    zip_safe = False,
    install_requires = [
        'jinja2',
        'tornado>=4, <6',
        # pyzmq>=17 is not technically necessary,
        # but hopefully avoids incompatibilities with Tornado 5. April 2018
        'pyzmq>=17',
        'ipython_genutils',
        'traitlets>=4.2.1',
        'jupyter_core>=4.4.0',
        'jupyter_client>=5.3.1',
        'nbformat',
        'nbconvert',
        'ipykernel', # bless IPython kernel for now
        'Send2Trash',
        'terminado>=0.8.1',
        'prometheus_client',
        "pywin32>=1.0 ; sys_platform == 'win32'"
    ],
    extras_require = {
        'test': ['nose', 'coverage', 'requests', 'nose_warnings_filters',
                 'nbval', 'nose-exclude', 'selenium', 'pytest', 'pytest-cov'],
        'test:sys_platform == "win32"': ['nose-exclude'],
    },
    python_requires='>=3.5',
    entry_points = {
        'console_scripts': [
            'jupyter-server = jupyter_server.serverapp:main',
            'jupyter-extension = jupyter_server.extensions:main',
            'jupyter-bundlerextension = jupyter_server.bundler.bundlerextensions:main',
        ]
    },
)

try:
    from wheel.bdist_wheel import bdist_wheel
except ImportError:
    pass

# Run setup --------------------
def main():
    setup(**setup_args)

if __name__ == '__main__':
    main()
