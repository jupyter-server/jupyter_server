# Changelog

All notable changes to this project will be documented in this file.

<!-- <START NEW CHANGELOG ENTRY> -->

## 1.9.0

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/v1.8.0...f712734c4f7005f6a844abec9f57b993e7b004b0))

### Enhancements made

- enable a way to run a task when an io_loop is created [#531](https://github.com/jupyter-server/jupyter_server/pull/531) ([@eastonsuo](https://github.com/eastonsuo))
- adds `GatewayClient.auth_scheme` configurable [#529](https://github.com/jupyter-server/jupyter_server/pull/529) ([@telamonian](https://github.com/telamonian))
- [Notebook port 4835] Add UNIX socket support to notebook server [#525](https://github.com/jupyter-server/jupyter_server/pull/525) ([@jtpio](https://github.com/jtpio))

### Bugs fixed

- Fix nbconvert handler [#545](https://github.com/jupyter-server/jupyter_server/pull/545) ([@davidbrochart](https://github.com/davidbrochart))
- Fixes AsyncContentsManager#exists [#542](https://github.com/jupyter-server/jupyter_server/pull/542) ([@icankeep](https://github.com/icankeep))

### Maintenance and upkeep improvements

- argon2 as an optional dependency [#532](https://github.com/jupyter-server/jupyter_server/pull/532) ([@vidartf](https://github.com/vidartf))
- Test Downstream Packages [#528](https://github.com/jupyter-server/jupyter_server/pull/528) ([@blink1073](https://github.com/blink1073))
- fix jp_ws_fetch not work by its own #441 [#527](https://github.com/jupyter-server/jupyter_server/pull/527) ([@eastonsuo](https://github.com/eastonsuo))

### Documentation improvements

- Update link to meeting notes [#535](https://github.com/jupyter-server/jupyter_server/pull/535) ([@krassowski](https://github.com/krassowski))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2021-05-20&to=2021-06-24&type=c))

[@blink1073](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ablink1073+updated%3A2021-05-20..2021-06-24&type=Issues) | [@codecov-commenter](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Acodecov-commenter+updated%3A2021-05-20..2021-06-24&type=Issues) | [@davidbrochart](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Adavidbrochart+updated%3A2021-05-20..2021-06-24&type=Issues) | [@eastonsuo](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aeastonsuo+updated%3A2021-05-20..2021-06-24&type=Issues) | [@icankeep](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aicankeep+updated%3A2021-05-20..2021-06-24&type=Issues) | [@jtpio](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ajtpio+updated%3A2021-05-20..2021-06-24&type=Issues) | [@kevin-bates](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Akevin-bates+updated%3A2021-05-20..2021-06-24&type=Issues) | [@krassowski](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Akrassowski+updated%3A2021-05-20..2021-06-24&type=Issues) | [@telamonian](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Atelamonian+updated%3A2021-05-20..2021-06-24&type=Issues) | [@vidartf](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Avidartf+updated%3A2021-05-20..2021-06-24&type=Issues) | [@welcome](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Awelcome+updated%3A2021-05-20..2021-06-24&type=Issues) | [@Zsailer](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3AZsailer+updated%3A2021-05-20..2021-06-24&type=Issues)

<!-- <END NEW CHANGELOG ENTRY> -->

## 1.8.0

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/v1.7.0...b063117a3a48ea67371c62e492f4637e44157586))

### Enhancements made

- Expose a public property to sort extensions deterministically. [#522](https://github.com/jupyter-server/jupyter_server/pull/522) ([@Zsailer](https://github.com/Zsailer))

### Bugs fixed

- init_httpserver at the end of initialize [#517](https://github.com/jupyter-server/jupyter_server/pull/517) ([@minrk](https://github.com/minrk))

### Maintenance and upkeep improvements

- Upgrade anyio to 3.1 for all py versions [#521](https://github.com/jupyter-server/jupyter_server/pull/521) ([@mwakaba2](https://github.com/mwakaba2))
- Enable Server Tests on Windows [#519](https://github.com/jupyter-server/jupyter_server/pull/519) ([@jtpio](https://github.com/jtpio))
- restore preference for SelectorEventLoop on Windows [#513](https://github.com/jupyter-server/jupyter_server/pull/513) ([@minrk](https://github.com/minrk))
- set default config dir name [#504](https://github.com/jupyter-server/jupyter_server/pull/504) ([@minrk](https://github.com/minrk))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2021-05-10&to=2021-05-20&type=c))

[@codecov-commenter](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Acodecov-commenter+updated%3A2021-05-10..2021-05-20&type=Issues) | [@jtpio](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ajtpio+updated%3A2021-05-10..2021-05-20&type=Issues) | [@minrk](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aminrk+updated%3A2021-05-10..2021-05-20&type=Issues) | [@mwakaba2](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Amwakaba2+updated%3A2021-05-10..2021-05-20&type=Issues) | [@vidartf](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Avidartf+updated%3A2021-05-10..2021-05-20&type=Issues) | [@welcome](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Awelcome+updated%3A2021-05-10..2021-05-20&type=Issues) | [@Zsailer](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3AZsailer+updated%3A2021-05-10..2021-05-20&type=Issues)

## 1.7.0

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/v1.7.0a2...afae85a7bb8c45f7610cd38b60d6075bb623490b))

### Bugs fixed

- Fix for recursive symlink - (port Notebook 4670) [#497](https://github.com/jupyter-server/jupyter_server/pull/497) ([@kevin-bates](https://github.com/kevin-bates))

### Enhancements made

- Make nbconvert root handler asynchronous [#512](https://github.com/jupyter-server/jupyter_server/pull/512) ([@hMED22](https://github.com/hMED22))
- Refactor gateway kernel management to achieve a degree of consistency [#483](https://github.com/jupyter-server/jupyter_server/pull/483) ([@kevin-bates](https://github.com/kevin-bates))

### Maintenance and upkeep improvements

- Remove Packaging Dependency [#515](https://github.com/jupyter-server/jupyter_server/pull/515) ([@jtpio](https://github.com/jtpio))
- Use kernel_id for new kernel if it doesn't exist in MappingKernelManager.start_kernel [#511](https://github.com/jupyter-server/jupyter_server/pull/511) ([@the-higgs](https://github.com/the-higgs))
- Include backtrace in debug output when extension fails to load [#506](https://github.com/jupyter-server/jupyter_server/pull/506) ([@candlerb](https://github.com/candlerb))
- ExtensionPoint: return True on successful validate() [#503](https://github.com/jupyter-server/jupyter_server/pull/503) ([@minrk](https://github.com/minrk))
- ExtensionManager: load default config manager by default [#502](https://github.com/jupyter-server/jupyter_server/pull/502) ([@minrk](https://github.com/minrk))
- Prep for Release Helper Usage [#494](https://github.com/jupyter-server/jupyter_server/pull/494) ([@jtpio](https://github.com/jtpio))
- Typo in shutdown with answer_yes [#491](https://github.com/jupyter-server/jupyter_server/pull/491) ([@kiendang](https://github.com/kiendang))
- Remove some of ipython_genutils no-op. [#440](https://github.com/jupyter-server/jupyter_server/pull/440) ([@Carreau](https://github.com/Carreau))
- Drop dependency on pywin32 [#514](https://github.com/jupyter-server/jupyter_server/pull/514) ([@kevin-bates](https://github.com/kevin-bates))
- Upgrade anyio to v3 [#492](https://github.com/jupyter-server/jupyter_server/pull/492) ([@mwakaba2](https://github.com/mwakaba2))
- Add Appropriate Token Permission for CodeQL Workflow [#489](https://github.com/jupyter-server/jupyter_server/pull/489) ([@afshin](https://github.com/afshin))

### Documentation improvements

- DOC: Autoreformat docstrings. [#493](https://github.com/jupyter-server/jupyter_server/pull/493) ([@Carreau](https://github.com/Carreau))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2021-04-22&to=2021-05-10&type=c))

[@codecov-commenter](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Acodecov-commenter+updated%3A2021-05-06..2021-05-10&type=Issues) | [@hMED22](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3AhMED22+updated%3A2021-05-06..2021-05-10&type=Issues) | [@jtpio](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ajtpio+updated%3A2021-05-06..2021-05-10&type=Issues) | [@kevin-bates](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Akevin-bates+updated%3A2021-05-06..2021-05-10&type=Issues) | [@the-higgs](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Athe-higgs+updated%3A2021-05-06..2021-05-10&type=Issues) | [@welcome](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Awelcome+updated%3A2021-05-06..2021-05-10&type=Issues)
[@blink1073](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ablink1073+updated%3A2021-05-01..2021-05-05&type=Issues) | [@candlerb](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Acandlerb+updated%3A2021-05-01..2021-05-05&type=Issues) | [@kevin-bates](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Akevin-bates+updated%3A2021-05-01..2021-05-05&type=Issues) | [@minrk](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aminrk+updated%3A2021-05-01..2021-05-05&type=Issues) | [@mwakaba2](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Amwakaba2+updated%3A2021-05-01..2021-05-05&type=Issues) | [@Zsailer](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3AZsailer+updated%3A2021-05-01..2021-05-05&type=Issues) | [@kiendang](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Akiendang+updated%3A2021-04-21..2021-05-01&type=Issues) | [@Carreau]
(https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3ACarreau+updated%3A2021-04-21..2021-05-01&type=Issues)

## 1.6.4

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/v1.6.3...68a64ea13be5d0d86460f04e0c47eb0b6662a0af))

### Bugs fixed

- Fix loading of sibling extensions [#485](https://github.com/jupyter-server/jupyter_server/pull/485) ([@afshin](https://github.com/afshin))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2021-04-21&to=2021-04-21&type=c))

[@afshin](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aafshin+updated%3A2021-04-21..2021-04-21&type=Issues)

## 1.6.3

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/v1.6.2...aa2636795ae1d87e3055febb3931f891dd6b4451))

### Merges

- Gate anyio version. [2b51ee3](https://github.com/jupyter-server/jupyter_server/commit/2b51ee37bdad305cb349e246c8ba94381cdb2048)
- Fix activity tracking and nudge issues when kernel ports change on restarts [#482](https://github.com/jupyter-server/jupyter_server/pull/482) ([@kevin-bates](https://github.com/kevin-bates))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2021-04-16&to=2021-04-21&type=c))

[@kevin-bates](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Akevin-bates+updated%3A2021-04-16..2021-04-21&type=Issues)

## 1.6.2

### Enhancements made

- Tighten xsrf checks [#478](https://github.com/jupyter-server/jupyter_server/pull/478) ([@jtpio](https://github.com/jtpio))

### Bugs fixed

- Re-enable support for answer_yes flag [#479](https://github.com/jupyter-server/jupyter_server/pull/479) ([@jtpio](https://github.com/jtpio))

### Maintenance and upkeep improvements

- Use Jupyter Packaging [#477](https://github.com/jupyter-server/jupyter_server/pull/477) ([@jtpio](https://github.com/jtpio))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2021-04-12&to=2021-04-16&type=c))

[@jtpio](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ajtpio+updated%3A2021-04-12..2021-04-16&type=Issues)

## 1.6.1

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/1.6.0...2756a29c5fdcfa62a3492004627541089d53d14f))

### Merged PRs

- Fix race condition with async kernel management [#472](https://github.com/jupyter-server/jupyter_server/pull/472) ([@jtpio](https://github.com/jtpio))
- Fix kernel lookup [#475](https://github.com/jupyter-server/jupyter_server/pull/475) ([@davidbrochart](https://github.com/davidbrochart))
- Add Extension App Aliases to Server App [#473](https://github.com/jupyter-server/jupyter_server/pull/473) ([@jtpio](https://github.com/jtpio))
- Correct 'Content-Type' headers [#471](https://github.com/jupyter-server/jupyter_server/pull/471) ([@faucct](https://github.com/faucct))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2021-04-08&to=2021-04-12&type=c))

[@codecov-io](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Acodecov-io+updated%3A2021-04-08..2021-04-12&type=Issues) | [@davidbrochart](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Adavidbrochart+updated%3A2021-04-08..2021-04-12&type=Issues) | [@echarles](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aecharles+updated%3A2021-04-08..2021-04-12&type=Issues) | [@faucct](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Afaucct+updated%3A2021-04-08..2021-04-12&type=Issues) | [@jtpio](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ajtpio+updated%3A2021-04-08..2021-04-12&type=Issues) | [@welcome](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Awelcome+updated%3A2021-04-08..2021-04-12&type=Issues)

## 1.6.0

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/1.5.1...724c38ec08c15cf1ed3c2efb2ad5c11f684f2cda))

### New features added

- Add env variable support for port options [#461](https://github.com/jupyter-server/jupyter_server/pull/461) ([@afshin](https://github.com/afshin))

### Enhancements made

- Add support for JUPYTER_TOKEN_FILE [#462](https://github.com/jupyter-server/jupyter_server/pull/462) ([@afshin](https://github.com/afshin))

### Maintenance and upkeep improvements

- Remove unnecessary future imports [#464](https://github.com/jupyter-server/jupyter_server/pull/464) ([@afshin](https://github.com/afshin))

### Documentation improvements

- Add Changelog to Sphinx Docs [#465](https://github.com/jupyter-server/jupyter_server/pull/465) ([@afshin](https://github.com/afshin))
- Update description for kernel restarted in the API docs [#463](https://github.com/jupyter-server/jupyter_server/pull/463) ([@jtpio](https://github.com/jtpio))
- Delete the extra “or” that prevents easy cut-and-paste of URLs. [#460](https://github.com/jupyter-server/jupyter_server/pull/460) ([@jasongrout](https://github.com/jasongrout))
- Add descriptive log for port unavailable and port-retries=0 [#459](https://github.com/jupyter-server/jupyter_server/pull/459) ([@afshin](https://github.com/afshin))

### Other merged PRs

- Add ReadTheDocs config [#468](https://github.com/jupyter-server/jupyter_server/pull/468) ([@jtpio](https://github.com/jtpio))
- Update MappingKM.restart_kernel to accept now kwarg [#404](https://github.com/jupyter-server/jupyter_server/pull/404) ([@vidartf](https://github.com/vidartf))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2021-03-24&to=2021-04-08&type=c))

[@afshin](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aafshin+updated%3A2021-03-24..2021-04-08&type=Issues) | [@codecov-io](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Acodecov-io+updated%3A2021-03-24..2021-04-08&type=Issues) | [@echarles](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aecharles+updated%3A2021-03-24..2021-04-08&type=Issues) | [@jasongrout](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ajasongrout+updated%3A2021-03-24..2021-04-08&type=Issues) | [@jtpio](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ajtpio+updated%3A2021-03-24..2021-04-08&type=Issues) | [@kevin-bates](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Akevin-bates+updated%3A2021-03-24..2021-04-08&type=Issues) | [@vidartf](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Avidartf+updated%3A2021-03-24..2021-04-08&type=Issues)

## 1.5.1

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/1.5.0...c3303cde880ecd1103118b8c7f9e5ebc19f0d1ba))

**Merged pull requests:**

* Ensure jupyter config dir exists [#454](https://github.com/jupyter-server/jupyter_server/pull/454) ([@afshin](https://github.com/afshin))
* Allow `pre_save_hook` to cancel save with `HTTPError` [#456](https://github.com/jupyter-server/jupyter_server/pull/456) ([@minrk](https://github.com/minrk))

**Contributors to this release:**

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2021-03-23&to=2021-03-24&type=c))

[@afshin](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aafshin+updated%3A2021-03-23..2021-03-24&type=Issues) | [@minrk](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aminrk+updated%3A2021-03-23..2021-03-24&type=Issues)

## 1.5.0

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/1.4.1...74801f479d7bb89c5afd4c020c52e614cc566da5))

**Merged pull requests:**

- Add Styling to the HTML Pages [#452](https://github.com/jupyter-server/jupyter_server/pull/452) ([@afshin](https://github.com/afshin))
- Implement password hashing with `argon2-cffi` [#450](https://github.com/jupyter-server/jupyter_server/pull/450) ([@afshin](https://github.com/afshin))
- Escape user input in handlers flagged during code scans [#449](https://github.com/jupyter-server/jupyter_server/pull/449) ([@kevin-bates](https://github.com/kevin-bates))
- Fix for the terminal shutdown issue [#446](https://github.com/jupyter-server/jupyter_server/pull/446) ([@afshin](https://github.com/afshin))
- Update the branch filter for the CI badge [#445](https://github.com/jupyter-server/jupyter_server/pull/445) ([@jtpio](https://github.com/jtpio))
- Fix for `UnboundLocalError` in shutdown [#444](https://github.com/jupyter-server/jupyter_server/pull/444) ([@afshin](https://github.com/afshin))
- Update CI badge and fix broken link [#443](https://github.com/jupyter-server/jupyter_server/pull/443) ([@blink1073](https://github.com/blink1073))
- Fix syntax typo [#442](https://github.com/jupyter-server/jupyter_server/pull/442) ([@kiendang](https://github.com/kiendang))
- Port terminal culling from Notebook [#438](https://github.com/jupyter-server/jupyter_server/pull/438) ([@kevin-bates](https://github.com/kevin-bates))
- More complex handling of `open_browser` from extension applications [#433](https://github.com/jupyter-server/jupyter_server/pull/433) ([@afshin](https://github.com/afshin))
- Correction in Changelog [#429](https://github.com/jupyter-server/jupyter_server/pull/429) ([@Zsailer](https://github.com/Zsailer))
- Rename translation function alias [#428](https://github.com/jupyter-server/jupyter_server/pull/428) ([@sngyo](https://github.com/sngyo))

**Contributors to this release:**

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2021-02-22&to=2021-03-23&type=c))

[@afshin](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aafshin+updated%3A2021-02-22..2021-03-23&type=Issues) | [@blink1073](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ablink1073+updated%3A2021-02-22..2021-03-23&type=Issues) | [@codecov-io](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Acodecov-io+updated%3A2021-02-22..2021-03-23&type=Issues) | [@jtpio](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ajtpio+updated%3A2021-02-22..2021-03-23&type=Issues) | [@kevin-bates](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Akevin-bates+updated%3A2021-02-22..2021-03-23&type=Issues) | [@kiendang](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Akiendang+updated%3A2021-02-22..2021-03-23&type=Issues) | [@minrk](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aminrk+updated%3A2021-02-22..2021-03-23&type=Issues) | [@sngyo](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Asngyo+updated%3A2021-02-22..2021-03-23&type=Issues) | [@Zsailer](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3AZsailer+updated%3A2021-02-22..2021-03-23&type=Issues)

## [1.4.1](https://github.com/jupyter-server/jupyter_server/tree/1.4.1) (2021-02-22)

[Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/1.4.0...bc252d33de2f647f98d048dc32888f0a83f005ac)

**Merged pull requests:**

* Update README.md [#425](https://github.com/jupyter-server/jupyter_server/pull/425) ([@BobinMathew](https://github.com/BobinMathew))
* Solve UnboundLocalError in launch_browser() [#421](https://github.com/jupyter-server/jupyter_server/pull/421) ([@jamesmishra](https://github.com/jamesmishra))
* Add file_to_run to server extension docs [#420](https://github.com/jupyter-server/jupyter_server/pull/420) ([@Zsailer](https://github.com/Zsailer))
* Remove outdated reference to _jupyter_server_extension_paths in docs [#419](https://github.com/jupyter-server/jupyter_server/pull/419) ([@Zsailer](https://github.com/Zsailer))

**Contributors to this release:**

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2021-02-18&to=2021-02-22&type=c))

[@jamesmishra](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ajamesmishra+updated%3A2021-02-18..2021-02-22&type=Issues) | [@Zsailer](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3AZsailer+updated%3A2021-02-18..2021-02-22&type=Issues)

## [1.4.0](https://github.com/jupyter-server/jupyter_server/tree/1.4.0) (2021-02-18)

[Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/1.3.0...HEAD)

**Merged pull requests:**

- Add Tests to Distribution [\#416](https://github.com/jupyter-server/jupyter_server/pull/416) ([afshin](https://github.com/afshin))
- Enable extensions to control the file\_to\_run [\#415](https://github.com/jupyter-server/jupyter_server/pull/415) ([afshin](https://github.com/afshin))
- add missing template for view.html [\#414](https://github.com/jupyter-server/jupyter_server/pull/414) ([minrk](https://github.com/minrk))
- Remove obsoleted asyncio-patch fixture [\#412](https://github.com/jupyter-server/jupyter_server/pull/412) ([kevin-bates](https://github.com/kevin-bates))
- Emit deprecation warning on old name [\#411](https://github.com/jupyter-server/jupyter_server/pull/411) ([fcollonval](https://github.com/fcollonval))
- Correct logging message position [\#410](https://github.com/jupyter-server/jupyter_server/pull/410) ([fcollonval](https://github.com/fcollonval))
- Update 1.3.0 Changelog to include broken 1.2.3 PRs [\#408](https://github.com/jupyter-server/jupyter_server/pull/408) ([kevin-bates](https://github.com/kevin-bates))
- \[Gateway\] Track only this server's kernels [\#407](https://github.com/jupyter-server/jupyter_server/pull/407) ([kevin-bates](https://github.com/kevin-bates))
- Update manager.py: more descriptive warnings when extensions fail to load [\#396](https://github.com/jupyter-server/jupyter_server/pull/396) ([alberti42](https://github.com/alberti42))

## [1.3.0](https://github.com/jupyter-server/jupyter_server/tree/1.3.0) (2021-02-04)

[Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/1.2.2...HEAD)

**Merged pull requests (includes those from broken 1.2.3 release):**

- Special case ExtensionApp that starts the ServerApp [\#401](https://github.com/jupyter-server/jupyter_server/pull/401) ([afshin](https://github.com/afshin))
- only use deprecated notebook\_dir config if root\_dir is not set [\#400](https://github.com/jupyter-server/jupyter_server/pull/400) ([minrk](https://github.com/minrk))
- Use async kernel manager by default [\#399](https://github.com/jupyter-server/jupyter_server/pull/399) ([kevin-bates](https://github.com/kevin-bates))
- Revert Session.username default value change [\#398](https://github.com/jupyter-server/jupyter_server/pull/398) ([mwakaba2](https://github.com/mwakaba2))
- Re-enable default\_url in ExtensionApp [\#393](https://github.com/jupyter-server/jupyter_server/pull/393) ([afshin](https://github.com/afshin))
- Enable notebook ContentsManager in jupyter\_server [\#392](https://github.com/jupyter-server/jupyter_server/pull/392) ([afshin](https://github.com/afshin))
- Use jupyter\_server\_config.json as config file in the update password api [\#390](https://github.com/jupyter-server/jupyter_server/pull/390) ([echarles](https://github.com/echarles))
- Increase culling test idle timeout [\#388](https://github.com/jupyter-server/jupyter_server/pull/388) ([kevin-bates](https://github.com/kevin-bates))
- update changelog for 1.2.2 [\#387](https://github.com/jupyter-server/jupyter_server/pull/387) ([Zsailer](https://github.com/Zsailer))

## [1.2.3](https://github.com/jupyter-server/jupyter_server/tree/1.2.3) (2021-01-29)

This was a broken release and was yanked from PyPI.

[Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/1.2.2...HEAD)

**Merged pull requests:**

- Re-enable default\_url in ExtensionApp [\#393](https://github.com/jupyter-server/jupyter_server/pull/393) ([afshin](https://github.com/afshin))
- Enable notebook ContentsManager in jupyter\_server [\#392](https://github.com/jupyter-server/jupyter_server/pull/392) ([afshin](https://github.com/afshin))
- Use jupyter\_server\_config.json as config file in the update password api [\#390](https://github.com/jupyter-server/jupyter_server/pull/390) ([echarles](https://github.com/echarles))
- Increase culling test idle timeout [\#388](https://github.com/jupyter-server/jupyter_server/pull/388) ([kevin-bates](https://github.com/kevin-bates))
- update changelog for 1.2.2 [\#387](https://github.com/jupyter-server/jupyter_server/pull/387) ([Zsailer](https://github.com/Zsailer))

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
