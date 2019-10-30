import os, setuptools
from setuptools import find_packages

VERSION = '0.0.1'

def get_data_files():
    """Get the data files for the package.
    """
    data_files = [
        ('etc/jupyter/jupyter_server_config.d', ['etc/jupyter/jupyter_server_config.d/simple_ext.json']),
    ]
    def add_data_files(path):
        for (dirpath, dirnames, filenames) in os.walk(path):
            if filenames:
                data_files.append((dirpath, [os.path.join(dirpath, filename) for filename in filenames]))
    # Add all static and templates folders.
    add_data_files('simple_ext1/static')
    add_data_files('simple_ext1/templates')
    add_data_files('simple_ext2/static')
    add_data_files('simple_ext2/templates')
    return data_files

setuptools.setup(
    name = 'simple_ext',
    version = VERSION,
    description = 'Jupyter Simple Extension',
    long_description = open('README.md').read(),
    packages = find_packages(),
    python_requires = '>=3.5',
    install_requires = [
        'jupyter_server',
        'jinja2',
    ],
    tests_requires = [
        'pytest',
        'pytest-cov',
        'pylint',
    ],
    data_files = get_data_files(),
    entry_points = {
        'console_scripts': [
             'jupyter-simple-ext1 = simple_ext1.application:main',
             'jupyter-simple-ext11 = simple_ext11.application:main',
             'jupyter-simple-ext2 = simple_ext2.application:main'
        ]
    },
)
