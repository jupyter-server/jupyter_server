import pathlib
from setuptools import setup
from setupbase import (
    get_version, find_packages
)

here = pathlib.Path('.')
version_path = here.joinpath('jupyter_server', '_version.py')
VERSION = get_version(str(version_path))

readme_path = here.joinpath('README.md')
README = readme_path.read_text()

setup_args = dict(
    name             = 'jupyter_server',
    description      = 'The backend—i.e. core services, APIs, and REST endpoints—to Jupyter web applications.',
    long_description = README,
    version          = VERSION,
    packages         = find_packages('.'),
    package_data     = {
        'notebook' : ['templates/*'],
        'notebook.i18n': ['*/LC_MESSAGES/*.*'],
        'notebook.services.api': ['api.yaml'],
    },
    author           = 'Jupyter Development Team',
    author_email     = 'jupyter@googlegroups.com',
    url              = 'http://jupyter.org',
    license          = 'BSD',
    platforms        = "Linux, Mac OS X, Windows",
    keywords         = ['ipython', 'jupyter'],
    classifiers      = [
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    install_requires = [
        'jinja2',
        'tornado>=5.0',
        'pyzmq>=17',
        'ipython_genutils',
        'traitlets>=4.2.1',
        'jupyter_core>=4.4.0',
        'jupyter_client>=6.1.1',
        'nbformat',
        'nbconvert',
        'Send2Trash',
        'terminado>=0.8.3',
        'prometheus_client',
        "pywin32>=1.0 ; sys_platform == 'win32'"
    ],
    extras_require = {
        'test': ['nose', 'coverage', 'requests', 'nose_warnings_filters',
                 'pytest', 'pytest-cov', 'pytest-tornasync',
                 'pytest-console-scripts', 'ipykernel'],
        'test:sys_platform == "win32"': ['nose-exclude'],
    },
    entry_points = {
        'console_scripts': [
            'jupyter-server = jupyter_server.serverapp:main',
        ],
        'pytest11': [
            'pytest_jupyter_server = jupyter_server.pytest_plugin'
        ]
    },
)

if __name__ == '__main__':
    setup(**setup_args)
