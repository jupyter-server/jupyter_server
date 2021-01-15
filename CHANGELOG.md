# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]


## [1.2.2](https://github.com/jupyter-server/jupyter_server/tree/1.2.2) (2021-01-14)

**Merged pull requests:**

- Apply missing ensure\_async to root session handler methods [\#386](https://github.com/jupyter-server/jupyter_server/pull/386) ([kevin-bates](https://github.com/kevin-bates))
- Update changelog to 1.2.1 [\#385](https://github.com/jupyter-server/jupyter_server/pull/385) ([Zsailer](https://github.com/Zsailer))
- Fix application exit [\#384](https://github.com/jupyter-server/jupyter_server/pull/384) ([afshin](https://github.com/afshin))
- Replace secure\_write, is\_hidden, exists with jupyter\_core's [\#382](https://github.com/jupyter-server/jupyter_server/pull/382) ([kevin-bates](https://github.com/kevin-bates))
- Add --autoreload flag [\#380](https://github.com/jupyter-server/jupyter_server/pull/380) ([afshin](https://github.com/afshin))


## [1.2.1](https://github.com/jupyter-server/jupyter_server/tree/1.2.1) (2021-01-08)

[Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/1.2.0...1.2.1)

**Merged pull requests:**

- Enable extensions to set debug and open-browser flags [\#379](https://github.com/jupyter-server/jupyter_server/pull/379) ([afshin](https://github.com/afshin))
- Add reconnection to Gateway [\#378](https://github.com/jupyter-server/jupyter_server/pull/378) ([oyvsyo](https://github.com/oyvsyo))

## [1.2.0](https://github.com/jupyter-server/jupyter_server/tree/1.2.0) (2021-01-07)

[Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/1.1.4...1.2.0)

**Merged pull requests:**

- Flip default value for open\_browser in extensions [\#377](https://github.com/jupyter-server/jupyter_server/pull/377) ([ajbozarth](https://github.com/ajbozarth))
- Improve Handling of the soft limit on open file handles [\#376](https://github.com/jupyter-server/jupyter_server/pull/376) ([afshin](https://github.com/afshin))
- Handle open\_browser trait in ServerApp and ExtensionApp differently [\#375](https://github.com/jupyter-server/jupyter_server/pull/375) ([afshin](https://github.com/afshin))
- Add setting to disable redirect file browser launch [\#374](https://github.com/jupyter-server/jupyter_server/pull/374) ([afshin](https://github.com/afshin))
- Make trust handle use ensure\_async [\#373](https://github.com/jupyter-server/jupyter_server/pull/373) ([vidartf](https://github.com/vidartf))

## [1.1.4](https://github.com/jupyter-server/jupyter_server/tree/1.1.4) (2021-01-04)

[Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/1.1.3...1.1.4)

**Merged pull requests:**

- Update the link to paths documentation [\#371](https://github.com/jupyter-server/jupyter_server/pull/371) ([krassowski](https://github.com/krassowski))
- IPythonHandler -\> JupyterHandler [\#370](https://github.com/jupyter-server/jupyter_server/pull/370) ([krassowski](https://github.com/krassowski))
- use setuptools find\_packages, exclude tests, docs and examples from dist [\#368](https://github.com/jupyter-server/jupyter_server/pull/368) ([bollwyvl](https://github.com/bollwyvl))
- Update serverapp.py [\#367](https://github.com/jupyter-server/jupyter_server/pull/367) ([michaelaye](https://github.com/michaelaye))

## [1.1.3](https://github.com/jupyter-server/jupyter_server/tree/1.1.3) (2020-12-23)

[Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/1.1.2...1.1.3)

**Merged pull requests:**

- Culling: ensure last\_activity attr exists before use [\#365](https://github.com/jupyter-server/jupyter_server/pull/365) ([afshin](https://github.com/afshin))

## [1.1.2](https://github.com/jupyter-server/jupyter_server/tree/1.1.2) (2020-12-21)

[Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/1.0.11...1.1.2)

**Merged pull requests:**

- Nudge kernel with info request until we receive IOPub messages [\#361](https://github.com/jupyter-server/jupyter_server/pull/361) ([SylvainCorlay](https://github.com/SylvainCorlay))


## [1.1.1](https://github.com/jupyter-server/jupyter_server/tree/1.1.1) (2020-12-16)

[Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/1.1.0...1.1.1)

**Merged pull requests:**

- Fix: await possible async dir\_exists method [\#363](https://github.com/jupyter-server/jupyter_server/pull/363) ([mwakaba2](https://github.com/mwakaba2))


## 1.1.0 (2020-12-11)

[Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/1.0.10...1.1.0)

**Merged pull requests:**

- Restore pytest plugin from pytest-jupyter [\#360](https://github.com/jupyter-server/jupyter_server/pull/360) ([kevin-bates](https://github.com/kevin-bates))
- Fix upgrade packaging dependencies build step [\#354](https://github.com/jupyter-server/jupyter_server/pull/354) ([mwakaba2](https://github.com/mwakaba2))
- Await \_connect and inline read\_messages callback to \_connect [\#350](https://github.com/jupyter-server/jupyter_server/pull/350) ([ricklamers](https://github.com/ricklamers))
- Update release instructions and dev version [\#348](https://github.com/jupyter-server/jupyter_server/pull/348) ([kevin-bates](https://github.com/kevin-bates))
- Fix test\_trailing\_slash  [\#346](https://github.com/jupyter-server/jupyter_server/pull/346) ([kevin-bates](https://github.com/kevin-bates))
- Apply security advisory fix to master [\#345](https://github.com/jupyter-server/jupyter_server/pull/345) ([kevin-bates](https://github.com/kevin-bates))
- Allow toggling auth for prometheus metrics [\#344](https://github.com/jupyter-server/jupyter_server/pull/344) ([yuvipanda](https://github.com/yuvipanda))
- Port Notebook PRs 5565 and 5588 - terminal shell heuristics [\#343](https://github.com/jupyter-server/jupyter_server/pull/343) ([kevin-bates](https://github.com/kevin-bates))
- Port gateway updates from notebook \(PRs 5317 and 5484\) [\#341](https://github.com/jupyter-server/jupyter_server/pull/341) ([kevin-bates](https://github.com/kevin-bates))
- add check\_origin handler to gateway WebSocketChannelsHandler [\#340](https://github.com/jupyter-server/jupyter_server/pull/340) ([ricklamers](https://github.com/ricklamers))
- Remove pytest11 entrypoint and plugin, require tornado 6.1, remove asyncio patch, CI work [\#339](https://github.com/jupyter-server/jupyter_server/pull/339) ([bollwyvl](https://github.com/bollwyvl))
- Switch fixtures to use those in pytest-jupyter to avoid collisions [\#335](https://github.com/jupyter-server/jupyter_server/pull/335) ([kevin-bates](https://github.com/kevin-bates))
- Enable CodeQL runs on all pushed branches [\#333](https://github.com/jupyter-server/jupyter_server/pull/333) ([kevin-bates](https://github.com/kevin-bates))
- Asynchronous Contents API [\#324](https://github.com/jupyter-server/jupyter_server/pull/324) ([mwakaba2](https://github.com/mwakaba2))


## 1.0.6 (2020-11-18)

1.0.6 is a security release, fixing one vulnerability:

### Changed

- Fix open redirect vulnerability GHSA-grfj-wjv9-4f9v (CVE-2020-26232)


## 1.0 (2020-9-18)

### Added.

* Added a basic, styled `login.html` template. ([220](https://github.com/jupyter/jupyter_server/pull/220), [295](https://github.com/jupyter/jupyter_server/pull/295))
* Added new extension manager API for handling server extensions. ([248](https://github.com/jupyter/jupyter_server/pull/248), [265](https://github.com/jupyter/jupyter_server/pull/265), [275](https://github.com/jupyter/jupyter_server/pull/275), [303](https://github.com/jupyter/jupyter_server/pull/303))
* The favicon and Jupyter logo are now available under jupyter_server's static namespace. ([284](https://github.com/jupyter/jupyter_server/pull/284))

### Changed.

* `load_jupyter_server_extension` should be renamed to `_load_jupyter_server_extension` in server extensions. Server now throws a warning when the old name is used. ([213](https://github.com/jupyter/jupyter_server/pull/213))
* Docs for server extensions now recommend using `authenticated` decorator for handlers. ([219](https://github.com/jupyter/jupyter_server/pull/219))
* `_load_jupyter_server_paths` should be renamed to `_load_jupyter_server_points` in server extensions. ([277](https://github.com/jupyter/jupyter_server/pull/277))
* `static_url_prefix` in ExtensionApps is now a configurable trait. ([289](https://github.com/jupyter/jupyter_server/pull/289))
* `extension_name` trait was removed in favor of `name`. ([232](https://github.com/jupyter/jupyter_server/pull/232))
* Dropped support for Python 3.5. ([296](https://github.com/jupyter/jupyter_server/pull/296))
* Made the `config_dir_name` trait configurable in `ConfigManager`. ([297](https://github.com/jupyter/jupyter_server/pull/297))

### Removed for now removed features.

* Removed ipykernel as a dependency of jupyter_server. ([255](https://github.com/jupyter/jupyter_server/pull/255))

### Fixed for any bug fixes.
* Prevent a re-definition of prometheus metrics if `notebook` package already imports them. ([#210](https://github.com/jupyter/jupyter_server/pull/210))
* Fixed `terminals` REST API unit tests that weren't shutting down properly. ([221](https://github.com/jupyter/jupyter_server/pull/221))
* Fixed jupyter_server on Windows for Python < 3.7. Added patch to handle subprocess cleanup. ([240](https://github.com/jupyter/jupyter_server/pull/240))
* `base_url` was being duplicated when getting a url path from the `ServerApp`. ([280](https://github.com/jupyter/jupyter_server/pull/280))
* Extension URLs are now properly prefixed with `base_url`. Previously, all `static` paths were not. ([285](https://github.com/jupyter/jupyter_server/pull/285))
* Changed ExtensionApp mixin to inherit from `HasTraits`. This broke in traitlets 5.0 ([294](https://github.com/jupyter/jupyter_server/pull/294))
* Replaces `urlparse` with `url_path_join` to prevent URL squashing issues. ([304](https://github.com/jupyter/jupyter_server/pull/304))


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
