import os

from jupyter_packaging import create_cmdclass
from setuptools import setup

VERSION = "0.0.1"


def get_data_files():
    """Get the data files for the package."""
    data_files = [
        ("etc/jupyter/jupyter_server_config.d", "etc/jupyter/jupyter_server_config.d/", "*.json"),
    ]

    def add_data_files(path):
        for (dirpath, dirnames, filenames) in os.walk(path):
            if filenames:
                paths = [(dirpath, dirpath, filename) for filename in filenames]
                data_files.extend(paths)

    # Add all static and templates folders.
    add_data_files("simple_ext1/static")
    add_data_files("simple_ext1/templates")
    add_data_files("simple_ext2/static")
    add_data_files("simple_ext2/templates")
    return data_files


cmdclass = create_cmdclass(data_files_spec=get_data_files())

setup_args = dict(
    name="jupyter_server_example",
    version=VERSION,
    description="Jupyter Server Example",
    long_description=open("README.md").read(),
    python_requires=">=3.7",
    install_requires=[
        "jupyter_server",
        "jinja2",
    ],
    extras_require={
        "test": ["pytest"],
    },
    include_package_data=True,
    cmdclass=cmdclass,
    entry_points={
        "console_scripts": [
            "jupyter-simple-ext1 = simple_ext1.application:main",
            "jupyter-simple-ext11 = simple_ext11.application:main",
            "jupyter-simple-ext2 = simple_ext2.application:main",
        ]
    },
)


if __name__ == "__main__":
    setup(**setup_args)
