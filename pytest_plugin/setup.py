from pathlib import Path

import setuptools
from re import findall


here = Path(__file__).parent
name = "pytest_jupyter_server"
version = findall(r'__version__ = "(.+)"', (here / f"{name}.py").read_text())[0]

if __name__ == "__main__":
    setuptools.setup(name=name, version=version)
