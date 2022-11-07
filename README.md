# Jupyter Server

The Jupyter Server provides the backend (i.e. the core services, APIs, and REST endpoints) for Jupyter web applications like Jupyter notebook, JupyterLab, and Voila.

For more information, read our [documentation here](http://jupyter-server.readthedocs.io/en/stable/?badge=latest).

## Installation and Basic usage

To install the latest release locally, make sure you have
[pip installed](https://pip.readthedocs.io/en/stable/installing/) and run:

    pip install jupyter_server

Jupyter Server currently supports Python>=3.6 on Linux, OSX and Windows.

### Versioning and Branches

If Jupyter Server is a dependency of your project/application, it is important that you pin it to a version that works for your application. Currently, Jupyter Server only has minor and patch versions. Different minor versions likely include API-changes while patch versions do not change API.

When a new minor version is released on PyPI, a branch for that version will be created in this repository, and the version of the main branch will be bumped to the next minor version number. That way, the main branch always reflects the latest un-released version.

To see the changes between releases, checkout the [CHANGELOG](https://github.com/jupyter/jupyter_server/blob/1.x/CHANGELOG.md).

## Usage - Running Jupyter Server

### Running in a local installation

Launch with:

    jupyter server

### Testing

See [CONTRIBUTING](https://github.com/jupyter-server/jupyter_server/blob/1.x/CONTRIBUTING.rst#running-tests).

## Contributing

If you are interested in contributing to the project, see [`CONTRIBUTING.rst`](CONTRIBUTING.rst).

## Team Meetings and Roadmap

- When: Thursdays [8:00am, Pacific time](https://www.thetimezoneconverter.com/?t=8%3A00%20am&tz=San%20Francisco&)
- Where: [Jovyan Zoom](https://zoom.us/my/jovyan?pwd=c0JZTHlNdS9Sek9vdzR3aTJ4SzFTQT09)
- What: [Meeting notes](https://github.com/jupyter-server/team-compass/issues/4)

See our tentative [roadmap here](https://github.com/jupyter/jupyter_server/issues/127).
