import setuptools

VERSION = '0.0.1'

setuptools.setup(
    name = 'jupyter_simple_ext',
    version = VERSION,
    description = 'Datalayer',
    long_description = open('README.md').read(),
    packages = [
        'jupyter_simple_ext',
    ],
    package_data = {
        'jupyter_simple_ext': [
            '*',
        ],
    },
    setup_requires = [
    ],
    install_requires = [
        'jupyter_server==0.1.1',
        'jinja2',
    ],
    tests_requires = [
        'pytest',
        'pytest-cov',
        'pylint',
    ],
    python_requires = '>=3.5',
    data_files = [
        ('etc/jupyter/jupyter_server_config.d', ['etc/jupyter/jupyter_server_config.d/simple_ext.json']),
    ],
    entry_points = {
        'console_scripts': [
             'jupyter-simple-ext = jupyter_simple_ext.application:main'
        ]
    },
)
