# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3] - 2020-4-22

### Added

- ([#191](https://github.com/jupyter/jupyter_server/pull/191)) Async kernel managment is now possible using the `AsyncKernelManager` from `jupyter_client`
- ([#201](https://github.com/jupyter/jupyter_server/pull/201)) Parameters can now be passed to new terminals created by the `terminals` REST API.


### Changed

- ([#196](https://github.com/jupyter/jupyter_server/pull/196)) Documentation was rewritten + refactored to use pydata_sphinx_theme.
- ([#174](https://github.com/jupyter/jupyter_server/pull/174)) `ExtensionHandler` was changed to an Mixin class, i.e. `ExtensionHandlerMixin`

### Removed

- ([#194](https://github.com/jupyter/jupyter_server/pull/194)) The bundlerextension entry point was removed.


## [0.2.1] - 2020-1-10

### Added

- **pytest-plugin** for Jupyter Server.
    - Allows one to write async/await syntax in tests functions.
    - Some particularly useful fixtures include:
        - `serverapp`: a default ServerApp instance that handles setup+teardown.
        - `configurable_serverapp`: a function that returns a ServerApp instance.
        - `fetch`: an awaitable function that tests makes requests to the server API
        - `create_notebook`: a function that writes a notebook to a given temporary file path.

## [0.2.0] - 2019-12-19

### Added
- `extension` submodule ([#48](https://github.com/jupyter/jupyter_server/pull/48))
    - ExtensionApp - configurable JupyterApp-subclass for server extensions
        - Most useful for Jupyter frontends, like Notebook, JupyterLab, nteract, voila etc.
        - Launch with entrypoints
        - Configure from file or CLI
        - Add custom templates, static assets, handlers, etc.
        - Static assets are served behind a `/static/<extension_name>` endpoint.
        - Run server extensions in "standalone mode" ([#70](https://github.com/jupyter/jupyter_server/pull/70) and [#76](https://github.com/jupyter/jupyter_server/pull/76))
    - ExtensionHandler - tornado handlers for extensions.
        - Finds static assets at `/static/<extension_name>`

### Changed
- `jupyter serverextension <command>` entrypoint has been changed to `jupyter server extension <command>`.
- `toggle_jupyter_server` and `validate_jupyter_server` function no longer take a Logger object as an argument.
- Changed testing framework from nosetests to pytest ([#152](https://github.com/jupyter/jupyter_server/pull/152))
    - Depend on pytest-tornasync extension for handling tornado/asyncio eventloop
    - Depend on pytest-console-scripts for testing CLI entrypoints
- Added Github actions as a testing framework along side Travis and Azure ([#146](https://github.com/jupyter/jupyter_server/pull/146))

### Removed
- Removed the option to update `root_dir` trait in FileContentsManager and MappingKernelManager in ServerApp ([#135](https://github.com/jupyter/jupyter_server/pull/135))

### Fixed
- Synced Jupyter Server with Notebook PRs in batches (ended on 2019-09-27)
    - [Batch 1](https://github.com/jupyter/jupyter_server/pull/95)
    - [Batch 2](https://github.com/jupyter/jupyter_server/pull/97)
    - [Batch 3](https://github.com/jupyter/jupyter_server/pull/98)
    - [Batch 4](https://github.com/jupyter/jupyter_server/pull/99)
    - [Batch 5](https://github.com/jupyter/jupyter_server/pull/103)
    - [Batch 6](https://github.com/jupyter/jupyter_server/pull/104)
    - [Batch 7](https://github.com/jupyter/jupyter_server/pull/105)
    - [Batch 8](https://github.com/jupyter/jupyter_server/pull/106)

### Security
- Added a "secure_write to function for cookie/token saves ([#77](https://github.com/jupyter/jupyter_server/pull/77))