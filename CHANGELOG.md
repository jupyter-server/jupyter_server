# Changelog

All notable changes to this project will be documented in this file.

<!-- <START NEW CHANGELOG ENTRY> -->

## 2.6.0

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/v2.5.0...35b8e9cb68eec48fe9a017ac128cb776c2ead195))

### New features added

- Emit events from the kernels service and gateway client [#1252](https://github.com/jupyter-server/jupyter_server/pull/1252) ([@rajmusuku](https://github.com/rajmusuku))

### Enhancements made

- Allows immutable cache for static files in a directory [#1268](https://github.com/jupyter-server/jupyter_server/pull/1268) ([@brichet](https://github.com/brichet))
- Merge the gateway handlers into the standard handlers. [#1261](https://github.com/jupyter-server/jupyter_server/pull/1261) ([@ojarjur](https://github.com/ojarjur))
- Gateway manager retry kernel updates [#1256](https://github.com/jupyter-server/jupyter_server/pull/1256) ([@ojarjur](https://github.com/ojarjur))
- Use debug-level messages for generating anonymous users [#1254](https://github.com/jupyter-server/jupyter_server/pull/1254) ([@hbcarlos](https://github.com/hbcarlos))
- Define a CURRENT_JUPYTER_HANDLER context var [#1251](https://github.com/jupyter-server/jupyter_server/pull/1251) ([@Zsailer](https://github.com/Zsailer))

### Bugs fixed

- Don't instantiate an unused Future in gateway connection trait [#1276](https://github.com/jupyter-server/jupyter_server/pull/1276) ([@minrk](https://github.com/minrk))
- Write server list to stdout [#1275](https://github.com/jupyter-server/jupyter_server/pull/1275) ([@minrk](https://github.com/minrk))
- Make the kernel_websocket_protocol flag reusable. [#1264](https://github.com/jupyter-server/jupyter_server/pull/1264) ([@ojarjur](https://github.com/ojarjur))
- Register websocket handler from same module as kernel handlers [#1249](https://github.com/jupyter-server/jupyter_server/pull/1249) ([@kevin-bates](https://github.com/kevin-bates))
- Re-enable websocket ping/pong from the server [#1243](https://github.com/jupyter-server/jupyter_server/pull/1243) ([@Zsailer](https://github.com/Zsailer))
- Fix italics in operators security sections [#1242](https://github.com/jupyter-server/jupyter_server/pull/1242) ([@kevin-bates](https://github.com/kevin-bates))
- Fix calculation of schema location [#1239](https://github.com/jupyter-server/jupyter_server/pull/1239) ([@lresende](https://github.com/lresende))

### Maintenance and upkeep improvements

- Fix DeprecationWarning from pytest-console-scripts [#1281](https://github.com/jupyter-server/jupyter_server/pull/1281) ([@frenzymadness](https://github.com/frenzymadness))
- Remove docutils and mistune pins [#1278](https://github.com/jupyter-server/jupyter_server/pull/1278) ([@blink1073](https://github.com/blink1073))
- Update docutils requirement from \<0.20 to \<0.21 [#1277](https://github.com/jupyter-server/jupyter_server/pull/1277) ([@dependabot](https://github.com/dependabot))
- Use Python 3.9 for the readthedocs builds [#1269](https://github.com/jupyter-server/jupyter_server/pull/1269) ([@ojarjur](https://github.com/ojarjur))
- Fix coverage handling [#1257](https://github.com/jupyter-server/jupyter_server/pull/1257) ([@blink1073](https://github.com/blink1073))
- chore: delete `.gitmodules` [#1248](https://github.com/jupyter-server/jupyter_server/pull/1248) ([@SauravMaheshkar](https://github.com/SauravMaheshkar))
- chore: move `babel` and `eslint` configuration under `package.json` [#1246](https://github.com/jupyter-server/jupyter_server/pull/1246) ([@SauravMaheshkar](https://github.com/SauravMaheshkar))

### Documentation improvements

- Fix typo in docs [#1270](https://github.com/jupyter-server/jupyter_server/pull/1270) ([@davidbrochart](https://github.com/davidbrochart))
- Fix typo [#1262](https://github.com/jupyter-server/jupyter_server/pull/1262) ([@davidbrochart](https://github.com/davidbrochart))
- Extends the IP documentation [#1258](https://github.com/jupyter-server/jupyter_server/pull/1258) ([@hbcarlos](https://github.com/hbcarlos))
- Fix italics in operators security sections [#1242](https://github.com/jupyter-server/jupyter_server/pull/1242) ([@kevin-bates](https://github.com/kevin-bates))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2023-03-16&to=2023-05-25&type=c))

[@blink1073](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ablink1073+updated%3A2023-03-16..2023-05-25&type=Issues) | [@brichet](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Abrichet+updated%3A2023-03-16..2023-05-25&type=Issues) | [@codecov](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Acodecov+updated%3A2023-03-16..2023-05-25&type=Issues) | [@davidbrochart](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Adavidbrochart+updated%3A2023-03-16..2023-05-25&type=Issues) | [@dependabot](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Adependabot+updated%3A2023-03-16..2023-05-25&type=Issues) | [@echarles](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aecharles+updated%3A2023-03-16..2023-05-25&type=Issues) | [@frenzymadness](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Afrenzymadness+updated%3A2023-03-16..2023-05-25&type=Issues) | [@hbcarlos](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ahbcarlos+updated%3A2023-03-16..2023-05-25&type=Issues) | [@kevin-bates](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Akevin-bates+updated%3A2023-03-16..2023-05-25&type=Issues) | [@lresende](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Alresende+updated%3A2023-03-16..2023-05-25&type=Issues) | [@minrk](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aminrk+updated%3A2023-03-16..2023-05-25&type=Issues) | [@ojarjur](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aojarjur+updated%3A2023-03-16..2023-05-25&type=Issues) | [@pre-commit-ci](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Apre-commit-ci+updated%3A2023-03-16..2023-05-25&type=Issues) | [@rajmusuku](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Arajmusuku+updated%3A2023-03-16..2023-05-25&type=Issues) | [@SauravMaheshkar](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3ASauravMaheshkar+updated%3A2023-03-16..2023-05-25&type=Issues) | [@welcome](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Awelcome+updated%3A2023-03-16..2023-05-25&type=Issues) | [@yuvipanda](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ayuvipanda+updated%3A2023-03-16..2023-05-25&type=Issues) | [@Zsailer](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3AZsailer+updated%3A2023-03-16..2023-05-25&type=Issues)

<!-- <END NEW CHANGELOG ENTRY> -->

## 2.5.0

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/v2.4.0...dc1eee8715dfe674560789caa5123dc895717ca1))

### Enhancements made

- Enable KernelSpecResourceHandler to be async [#1236](https://github.com/jupyter-server/jupyter_server/pull/1236) ([@Zsailer](https://github.com/Zsailer))
- Added error propagation to gateway_request function [#1233](https://github.com/jupyter-server/jupyter_server/pull/1233) ([@broden-wanner](https://github.com/broden-wanner))

### Maintenance and upkeep improvements

- Update ruff [#1230](https://github.com/jupyter-server/jupyter_server/pull/1230) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2023-03-06&to=2023-03-16&type=c))

[@blink1073](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ablink1073+updated%3A2023-03-06..2023-03-16&type=Issues) | [@broden-wanner](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Abroden-wanner+updated%3A2023-03-06..2023-03-16&type=Issues) | [@codecov](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Acodecov+updated%3A2023-03-06..2023-03-16&type=Issues) | [@welcome](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Awelcome+updated%3A2023-03-06..2023-03-16&type=Issues) | [@Zsailer](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3AZsailer+updated%3A2023-03-06..2023-03-16&type=Issues)

## 2.4.0

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/v2.3.0...4d311b2c91e055e7b4690d8100f7fe85381f06da))

### Enhancements made

- Skip dir size check if not enumerable [#1227](https://github.com/jupyter-server/jupyter_server/pull/1227) ([@vidartf](https://github.com/vidartf))
- Optimize hidden checks [#1226](https://github.com/jupyter-server/jupyter_server/pull/1226) ([@vidartf](https://github.com/vidartf))
- Enable users to copy both files and directories [#1190](https://github.com/jupyter-server/jupyter_server/pull/1190) ([@kenyaachon](https://github.com/kenyaachon))

### Bugs fixed

- Fix port selection [#1229](https://github.com/jupyter-server/jupyter_server/pull/1229) ([@blink1073](https://github.com/blink1073))
- Fix priority of deprecated NotebookApp.notebook_dir behind ServerApp.root_dir (#1223 [#1223](https://github.com/jupyter-server/jupyter_server/pull/1223) ([@minrk](https://github.com/minrk))
- Ensure content-type properly reflects gateway kernelspec resources [#1219](https://github.com/jupyter-server/jupyter_server/pull/1219) ([@kevin-bates](https://github.com/kevin-bates))

### Maintenance and upkeep improvements

- fix docs build [#1225](https://github.com/jupyter-server/jupyter_server/pull/1225) ([@blink1073](https://github.com/blink1073))
- Fix ci failures [#1222](https://github.com/jupyter-server/jupyter_server/pull/1222) ([@blink1073](https://github.com/blink1073))
- Clean up license [#1218](https://github.com/jupyter-server/jupyter_server/pull/1218) ([@dcsaba89](https://github.com/dcsaba89))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2023-02-15&to=2023-03-06&type=c))

[@blink1073](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ablink1073+updated%3A2023-02-15..2023-03-06&type=Issues) | [@Carreau](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3ACarreau+updated%3A2023-02-15..2023-03-06&type=Issues) | [@codecov](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Acodecov+updated%3A2023-02-15..2023-03-06&type=Issues) | [@codecov-commenter](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Acodecov-commenter+updated%3A2023-02-15..2023-03-06&type=Issues) | [@davidbrochart](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Adavidbrochart+updated%3A2023-02-15..2023-03-06&type=Issues) | [@dcsaba89](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Adcsaba89+updated%3A2023-02-15..2023-03-06&type=Issues) | [@echarles](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aecharles+updated%3A2023-02-15..2023-03-06&type=Issues) | [@kenyaachon](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Akenyaachon+updated%3A2023-02-15..2023-03-06&type=Issues) | [@kevin-bates](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Akevin-bates+updated%3A2023-02-15..2023-03-06&type=Issues) | [@minrk](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aminrk+updated%3A2023-02-15..2023-03-06&type=Issues) | [@vidartf](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Avidartf+updated%3A2023-02-15..2023-03-06&type=Issues) | [@welcome](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Awelcome+updated%3A2023-02-15..2023-03-06&type=Issues) | [@Zsailer](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3AZsailer+updated%3A2023-02-15..2023-03-06&type=Issues)

## 2.3.0

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/v2.2.1...968c56c8c69aa545f7fe93243331fe140dac7c90))

### Enhancements made

- Support IPV6 in \_find_http_port() [#1207](https://github.com/jupyter-server/jupyter_server/pull/1207) ([@schnell18](https://github.com/schnell18))

### Bugs fixed

- Redact tokens, etc. in url parameters from request logs [#1212](https://github.com/jupyter-server/jupyter_server/pull/1212) ([@minrk](https://github.com/minrk))
- Fix get_loader returning None when load_jupyter_server_extension is not found (#1193)Co-authored-by: pre-commit-ci\[bot\] \<66853113+pre-commit-ci\[bot\]@users.noreply.github.com> [#1193](https://github.com/jupyter-server/jupyter_server/pull/1193) ([@cmd-ntrf](https://github.com/cmd-ntrf))

### Maintenance and upkeep improvements

- update LICENSE [#1197](https://github.com/jupyter-server/jupyter_server/pull/1197) ([@dcsaba89](https://github.com/dcsaba89))
- Add license 2 (#1196 [#1196](https://github.com/jupyter-server/jupyter_server/pull/1196) ([@dcsaba89](https://github.com/dcsaba89))

### Documentation improvements

- Update jupyterhub security link [#1200](https://github.com/jupyter-server/jupyter_server/pull/1200) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2023-02-02&to=2023-02-15&type=c))

[@blink1073](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ablink1073+updated%3A2023-02-02..2023-02-15&type=Issues) | [@cmd-ntrf](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Acmd-ntrf+updated%3A2023-02-02..2023-02-15&type=Issues) | [@codecov](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Acodecov+updated%3A2023-02-02..2023-02-15&type=Issues) | [@dcsaba89](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Adcsaba89+updated%3A2023-02-02..2023-02-15&type=Issues) | [@meeseeksdev](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ameeseeksdev+updated%3A2023-02-02..2023-02-15&type=Issues) | [@minrk](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aminrk+updated%3A2023-02-02..2023-02-15&type=Issues) | [@pre-commit-ci](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Apre-commit-ci+updated%3A2023-02-02..2023-02-15&type=Issues) | [@schnell18](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aschnell18+updated%3A2023-02-02..2023-02-15&type=Issues) | [@welcome](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Awelcome+updated%3A2023-02-02..2023-02-15&type=Issues)

## 2.2.1

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/v2.2.0...0f9556b48d7699bd2d246222067b1cb215d44c28))

### Maintenance and upkeep improvements

- Delete the extra "or" in front of the second url [#1194](https://github.com/jupyter-server/jupyter_server/pull/1194) ([@jonnygrout](https://github.com/jonnygrout))
- remove upper bound on anyio [#1192](https://github.com/jupyter-server/jupyter_server/pull/1192) ([@minrk](https://github.com/minrk))
- Adopt more lint rules [#1189](https://github.com/jupyter-server/jupyter_server/pull/1189) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2023-01-31&to=2023-02-02&type=c))

[@blink1073](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ablink1073+updated%3A2023-01-31..2023-02-02&type=Issues) | [@codecov](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Acodecov+updated%3A2023-01-31..2023-02-02&type=Issues) | [@jonnygrout](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ajonnygrout+updated%3A2023-01-31..2023-02-02&type=Issues) | [@minrk](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aminrk+updated%3A2023-01-31..2023-02-02&type=Issues) | [@welcome](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Awelcome+updated%3A2023-01-31..2023-02-02&type=Issues)

## 2.2.0

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/v2.1.0...b6c1edb0b205f8d53f1a2e81abb997bfc693f144))

### Enhancements made

- Only load enabled extension packages [#1180](https://github.com/jupyter-server/jupyter_server/pull/1180) ([@minrk](https://github.com/minrk))
- Pass in a logger to get_metadata [#1176](https://github.com/jupyter-server/jupyter_server/pull/1176) ([@yuvipanda](https://github.com/yuvipanda))

### Bugs fixed

- Don't assume that resources entries are relative [#1182](https://github.com/jupyter-server/jupyter_server/pull/1182) ([@ojarjur](https://github.com/ojarjur))

### Maintenance and upkeep improvements

- Updates for client 8 [#1188](https://github.com/jupyter-server/jupyter_server/pull/1188) ([@blink1073](https://github.com/blink1073))
- Use repr in logging for exception. [#1185](https://github.com/jupyter-server/jupyter_server/pull/1185) ([@Carreau](https://github.com/Carreau))
- Update example npm deps [#1184](https://github.com/jupyter-server/jupyter_server/pull/1184) ([@blink1073](https://github.com/blink1073))
- Fix docs and examples [#1183](https://github.com/jupyter-server/jupyter_server/pull/1183) ([@blink1073](https://github.com/blink1073))
- Update jupyter client api docs links [#1179](https://github.com/jupyter-server/jupyter_server/pull/1179) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2023-01-13&to=2023-01-31&type=c))

[@blink1073](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ablink1073+updated%3A2023-01-13..2023-01-31&type=Issues) | [@Carreau](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3ACarreau+updated%3A2023-01-13..2023-01-31&type=Issues) | [@codecov](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Acodecov+updated%3A2023-01-13..2023-01-31&type=Issues) | [@kevin-bates](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Akevin-bates+updated%3A2023-01-13..2023-01-31&type=Issues) | [@minrk](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aminrk+updated%3A2023-01-13..2023-01-31&type=Issues) | [@ojarjur](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aojarjur+updated%3A2023-01-13..2023-01-31&type=Issues) | [@welcome](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Awelcome+updated%3A2023-01-13..2023-01-31&type=Issues) | [@yuvipanda](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ayuvipanda+updated%3A2023-01-13..2023-01-31&type=Issues)

## 2.1.0

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/v2.0.7...34f509d8da1710039634bc16f5336570c4861bcd))

### Bugs fixed

- Fix preferred_dir for sync contents manager [#1173](https://github.com/jupyter-server/jupyter_server/pull/1173) ([@vidartf](https://github.com/vidartf))

### Maintenance and upkeep improvements

- Update typing and warning handling [#1174](https://github.com/jupyter-server/jupyter_server/pull/1174) ([@blink1073](https://github.com/blink1073))

### Documentation improvements

- Add api docs [#1159](https://github.com/jupyter-server/jupyter_server/pull/1159) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2023-01-12&to=2023-01-12&type=c))

[@blink1073](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ablink1073+updated%3A2023-01-12..2023-01-12&type=Issues) | [@codecov](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Acodecov+updated%3A2023-01-12..2023-01-12&type=Issues) | [@vidartf](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Avidartf+updated%3A2023-01-12..2023-01-12&type=Issues)

## 2.0.7

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/v2.0.6...5cce2afcbeeb44581e9b29ab27fef75a12d651ca))

### Enhancements made

- Log how long each extension module takes to import [#1171](https://github.com/jupyter-server/jupyter_server/pull/1171) ([@yuvipanda](https://github.com/yuvipanda))
- Set JPY_SESSION_NAME to full notebook path. [#1100](https://github.com/jupyter-server/jupyter_server/pull/1100) ([@Carreau](https://github.com/Carreau))

### Bugs fixed

- Reapply preferred_dir fix, now with better backwards compatability [#1162](https://github.com/jupyter-server/jupyter_server/pull/1162) ([@vidartf](https://github.com/vidartf))

### Maintenance and upkeep improvements

- Update example to use hatch [#1169](https://github.com/jupyter-server/jupyter_server/pull/1169) ([@blink1073](https://github.com/blink1073))
- Clean up docs build and typing [#1168](https://github.com/jupyter-server/jupyter_server/pull/1168) ([@blink1073](https://github.com/blink1073))
- Fix check release by ignoring duplicate file name in wheel [#1163](https://github.com/jupyter-server/jupyter_server/pull/1163) ([@blink1073](https://github.com/blink1073))
- Fix broken link in warning message [#1158](https://github.com/jupyter-server/jupyter_server/pull/1158) ([@consideRatio](https://github.com/consideRatio))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2022-12-29&to=2023-01-12&type=c))

[@blink1073](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ablink1073+updated%3A2022-12-29..2023-01-12&type=Issues) | [@Carreau](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3ACarreau+updated%3A2022-12-29..2023-01-12&type=Issues) | [@codecov](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Acodecov+updated%3A2022-12-29..2023-01-12&type=Issues) | [@consideRatio](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3AconsideRatio+updated%3A2022-12-29..2023-01-12&type=Issues) | [@meeseeksdev](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ameeseeksdev+updated%3A2022-12-29..2023-01-12&type=Issues) | [@pre-commit-ci](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Apre-commit-ci+updated%3A2022-12-29..2023-01-12&type=Issues) | [@vidartf](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Avidartf+updated%3A2022-12-29..2023-01-12&type=Issues) | [@welcome](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Awelcome+updated%3A2022-12-29..2023-01-12&type=Issues) | [@yuvipanda](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ayuvipanda+updated%3A2022-12-29..2023-01-12&type=Issues)

## 2.0.6

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/v2.0.5...73d577610cda544e85139842c4186f7e77197440))

### Bugs fixed

- Iterate through set of apps in `extension_manager.any_activity` method [#1157](https://github.com/jupyter-server/jupyter_server/pull/1157) ([@mahendrapaipuri](https://github.com/mahendrapaipuri))

### Maintenance and upkeep improvements

- Handle flake8-errmsg [#1155](https://github.com/jupyter-server/jupyter_server/pull/1155) ([@blink1073](https://github.com/blink1073))
- Add spelling and docstring enforcement [#1147](https://github.com/jupyter-server/jupyter_server/pull/1147) ([@blink1073](https://github.com/blink1073))

### Documentation improvements

- Add spelling and docstring enforcement [#1147](https://github.com/jupyter-server/jupyter_server/pull/1147) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2022-12-23&to=2022-12-29&type=c))

[@blink1073](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ablink1073+updated%3A2022-12-23..2022-12-29&type=Issues) | [@codecov](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Acodecov+updated%3A2022-12-23..2022-12-29&type=Issues) | [@mahendrapaipuri](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Amahendrapaipuri+updated%3A2022-12-23..2022-12-29&type=Issues) | [@welcome](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Awelcome+updated%3A2022-12-23..2022-12-29&type=Issues)

## 2.0.5

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/v2.0.4...ec9029f07fe377ebb86b77e0eadd159fc9288c98))

### Bugs fixed

- Remove `end` kwarg after migration from print to info [#1151](https://github.com/jupyter-server/jupyter_server/pull/1151) ([@krassowski](https://github.com/krassowski))

### Maintenance and upkeep improvements

- Import ensure-sync directly from dependence. [#1149](https://github.com/jupyter-server/jupyter_server/pull/1149) ([@Carreau](https://github.com/Carreau))
- Update deprecation warning [#1148](https://github.com/jupyter-server/jupyter_server/pull/1148) ([@Carreau](https://github.com/Carreau))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2022-12-21&to=2022-12-23&type=c))

[@Carreau](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3ACarreau+updated%3A2022-12-21..2022-12-23&type=Issues) | [@codecov](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Acodecov+updated%3A2022-12-21..2022-12-23&type=Issues) | [@krassowski](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Akrassowski+updated%3A2022-12-21..2022-12-23&type=Issues)

## 2.0.4

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/v2.0.3...53377e25efe0faf4e2a984254ca2c301aeea096d))

### Bugs fixed

- Fix handling of extension last activity [#1145](https://github.com/jupyter-server/jupyter_server/pull/1145) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2022-12-21&to=2022-12-21&type=c))

[@blink1073](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ablink1073+updated%3A2022-12-21..2022-12-21&type=Issues)

## 2.0.3

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/v2.0.2...e35fbbc238a5b96d869c574fe8b8eb27b9605a05))

### Bugs fixed

- Restore default writing of browser open redirect file, add opt-in to skip [#1144](https://github.com/jupyter-server/jupyter_server/pull/1144) ([@bollwyvl](https://github.com/bollwyvl))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2022-12-20&to=2022-12-21&type=c))

[@bollwyvl](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Abollwyvl+updated%3A2022-12-20..2022-12-21&type=Issues)

## 2.0.2

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/v2.0.1...b5b7c5e9141698ab0206f74b8944972cbc4cf6fe))

### Bugs fixed

- Raise errors on individual problematic extensions when listing extension [#1139](https://github.com/jupyter-server/jupyter_server/pull/1139) ([@Zsailer](https://github.com/Zsailer))
- Find an available port before starting event loop [#1136](https://github.com/jupyter-server/jupyter_server/pull/1136) ([@blink1073](https://github.com/blink1073))
- only write browser files if we're launching the browser [#1133](https://github.com/jupyter-server/jupyter_server/pull/1133) ([@hhuuggoo](https://github.com/hhuuggoo))
- Logging message used to list sessions fails with template error [#1132](https://github.com/jupyter-server/jupyter_server/pull/1132) ([@vindex10](https://github.com/vindex10))
- Include base_url at start of kernelspec resources path [#1124](https://github.com/jupyter-server/jupyter_server/pull/1124) ([@bloomsa](https://github.com/bloomsa))

### Maintenance and upkeep improvements

- Fix lint rule [#1128](https://github.com/jupyter-server/jupyter_server/pull/1128) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2022-12-08&to=2022-12-20&type=c))

[@blink1073](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ablink1073+updated%3A2022-12-08..2022-12-20&type=Issues) | [@bloomsa](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Abloomsa+updated%3A2022-12-08..2022-12-20&type=Issues) | [@codecov](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Acodecov+updated%3A2022-12-08..2022-12-20&type=Issues) | [@hhuuggoo](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ahhuuggoo+updated%3A2022-12-08..2022-12-20&type=Issues) | [@kevin-bates](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Akevin-bates+updated%3A2022-12-08..2022-12-20&type=Issues) | [@vidartf](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Avidartf+updated%3A2022-12-08..2022-12-20&type=Issues) | [@vindex10](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Avindex10+updated%3A2022-12-08..2022-12-20&type=Issues) | [@welcome](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Awelcome+updated%3A2022-12-08..2022-12-20&type=Issues) | [@Zsailer](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3AZsailer+updated%3A2022-12-08..2022-12-20&type=Issues)

## 2.0.1

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/v2.0.0...a400c0e0de56b1abe821ce26875fad9e7e711596))

### Enhancements made

- \[Gateway\] Remove redundant list kernels request during session poll [#1112](https://github.com/jupyter-server/jupyter_server/pull/1112) ([@kevin-bates](https://github.com/kevin-bates))

### Maintenance and upkeep improvements

- Fix jupyter_core pinning [#1122](https://github.com/jupyter-server/jupyter_server/pull/1122) ([@ophie200](https://github.com/ophie200))
- Update docutils requirement from \<0.19 to \<0.20 [#1120](https://github.com/jupyter-server/jupyter_server/pull/1120) ([@dependabot](https://github.com/dependabot))
- Adopt ruff and use less pre-commit [#1114](https://github.com/jupyter-server/jupyter_server/pull/1114) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2022-12-06&to=2022-12-08&type=c))

[@blink1073](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ablink1073+updated%3A2022-12-06..2022-12-08&type=Issues) | [@codecov](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Acodecov+updated%3A2022-12-06..2022-12-08&type=Issues) | [@dependabot](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Adependabot+updated%3A2022-12-06..2022-12-08&type=Issues) | [@kevin-bates](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Akevin-bates+updated%3A2022-12-06..2022-12-08&type=Issues) | [@ofek](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aofek+updated%3A2022-12-06..2022-12-08&type=Issues) | [@ophie200](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aophie200+updated%3A2022-12-06..2022-12-08&type=Issues) | [@welcome](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Awelcome+updated%3A2022-12-06..2022-12-08&type=Issues)

## 2.0.0

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/6d0803b...312327fc498e3b96f7334c36b2623389d4f79b33))

### Enhancements made

- Introduce ServerKernelManager class [#1101](https://github.com/jupyter-server/jupyter_server/pull/1101) ([@kevin-bates](https://github.com/kevin-bates))
- New configurable/overridable kernel ZMQ+Websocket connection API [#1047](https://github.com/jupyter-server/jupyter_server/pull/1047) ([@Zsailer](https://github.com/Zsailer))
- Pass kernel environment to `cwd_for_path` method [#1046](https://github.com/jupyter-server/jupyter_server/pull/1046) ([@divyansshhh](https://github.com/divyansshhh))
- Better Handling of Asyncio [#1035](https://github.com/jupyter-server/jupyter_server/pull/1035) ([@blink1073](https://github.com/blink1073))
- Add authorization to AuthenticatedFileHandler [#1021](https://github.com/jupyter-server/jupyter_server/pull/1021) ([@jiajunjie](https://github.com/jiajunjie))
- \[Gateway\] Add support for gateway token renewal [#985](https://github.com/jupyter-server/jupyter_server/pull/985) ([@kevin-bates](https://github.com/kevin-bates))
- Make it easier to pass custom env variables to kernel [#981](https://github.com/jupyter-server/jupyter_server/pull/981) ([@divyansshhh](https://github.com/divyansshhh))
- Accept and manage cookies when requesting gateways [#969](https://github.com/jupyter-server/jupyter_server/pull/969) ([@wjsi](https://github.com/wjsi))
- Emit events from the Contents Service [#954](https://github.com/jupyter-server/jupyter_server/pull/954) ([@Zsailer](https://github.com/Zsailer))
- Retry certain errors between server and gateway [#944](https://github.com/jupyter-server/jupyter_server/pull/944) ([@kevin-bates](https://github.com/kevin-bates))
- Allow new file types [#895](https://github.com/jupyter-server/jupyter_server/pull/895) ([@davidbrochart](https://github.com/davidbrochart))
- Make it easier for extensions to customize the ServerApp [#879](https://github.com/jupyter-server/jupyter_server/pull/879) ([@minrk](https://github.com/minrk))
- Adds anonymous users [#863](https://github.com/jupyter-server/jupyter_server/pull/863) ([@hbcarlos](https://github.com/hbcarlos))
- switch to jupyter_events [#862](https://github.com/jupyter-server/jupyter_server/pull/862) ([@Zsailer](https://github.com/Zsailer))
- consolidate auth config on IdentityProvider [#825](https://github.com/jupyter-server/jupyter_server/pull/825) ([@minrk](https://github.com/minrk))

### Bugs fixed

- Fix kernel WebSocket protocol [#1110](https://github.com/jupyter-server/jupyter_server/pull/1110) ([@davidbrochart](https://github.com/davidbrochart))
- Defer webbrowser import [#1095](https://github.com/jupyter-server/jupyter_server/pull/1095) ([@blink1073](https://github.com/blink1073))
- Use handle_outgoing_message for ZMQ replies [#1089](https://github.com/jupyter-server/jupyter_server/pull/1089) ([@Zsailer](https://github.com/Zsailer))
- Call `ports_changed` on the multi-kernel-manager instead of the kernel manager [#1088](https://github.com/jupyter-server/jupyter_server/pull/1088) ([@Zsailer](https://github.com/Zsailer))
- Add more websocket connection tests and fix bugs [#1085](https://github.com/jupyter-server/jupyter_server/pull/1085) ([@blink1073](https://github.com/blink1073))
- Tornado WebSocketHandler fixup [#1083](https://github.com/jupyter-server/jupyter_server/pull/1083) ([@davidbrochart](https://github.com/davidbrochart))
- persist userid cookie when auth is disabled [#1076](https://github.com/jupyter-server/jupyter_server/pull/1076) ([@minrk](https://github.com/minrk))
- Fix rename_file and delete_file to handle hidden files properly [#1073](https://github.com/jupyter-server/jupyter_server/pull/1073) ([@yacchin1205](https://github.com/yacchin1205))
- Add more coverage [#1069](https://github.com/jupyter-server/jupyter_server/pull/1069) ([@blink1073](https://github.com/blink1073))
- Increase nbconvert and checkpoints coverage [#1066](https://github.com/jupyter-server/jupyter_server/pull/1066) ([@blink1073](https://github.com/blink1073))
- Fix min version check again [#1049](https://github.com/jupyter-server/jupyter_server/pull/1049) ([@blink1073](https://github.com/blink1073))
- Fallback new file type to file for contents put [#1013](https://github.com/jupyter-server/jupyter_server/pull/1013) ([@a3626a](https://github.com/a3626a))
- Fix some typos in release instructions [#1003](https://github.com/jupyter-server/jupyter_server/pull/1003) ([@kevin-bates](https://github.com/kevin-bates))
- Wrap the concurrent futures in an asyncio future [#1001](https://github.com/jupyter-server/jupyter_server/pull/1001) ([@blink1073](https://github.com/blink1073))
- \[Gateway\] Fix and deprecate env whitelist handling [#979](https://github.com/jupyter-server/jupyter_server/pull/979) ([@kevin-bates](https://github.com/kevin-bates))
- fix issues with jupyter_events 0.5.0 [#972](https://github.com/jupyter-server/jupyter_server/pull/972) ([@Zsailer](https://github.com/Zsailer))
- Correct content-type headers [#965](https://github.com/jupyter-server/jupyter_server/pull/965) ([@epignot](https://github.com/epignot))
- Don't validate certs for when stopping server [#959](https://github.com/jupyter-server/jupyter_server/pull/959) ([@Zsailer](https://github.com/Zsailer))
- Parse list value for `terminado_settings` [#949](https://github.com/jupyter-server/jupyter_server/pull/949) ([@krassowski](https://github.com/krassowski))
- Fix bug in `api/contents` requests for an allowed copy [#939](https://github.com/jupyter-server/jupyter_server/pull/939) ([@kiersten-stokes](https://github.com/kiersten-stokes))
- Fix error that prevents posting to `api/contents` endpoint with no body [#937](https://github.com/jupyter-server/jupyter_server/pull/937) ([@kiersten-stokes](https://github.com/kiersten-stokes))
- avoid creating asyncio.Lock at import time [#935](https://github.com/jupyter-server/jupyter_server/pull/935) ([@minrk](https://github.com/minrk))
- Fix `get_kernel_path` for `AsyncFileManager`s. [#929](https://github.com/jupyter-server/jupyter_server/pull/929) ([@thetorpedodog](https://github.com/thetorpedodog))
- Fix c.GatewayClient.url snippet syntax [#917](https://github.com/jupyter-server/jupyter_server/pull/917) ([@rickwierenga](https://github.com/rickwierenga))
- Add back support for kernel launch timeout pad [#910](https://github.com/jupyter-server/jupyter_server/pull/910) ([@CiprianAnton](https://github.com/CiprianAnton))
- Notify ChannelQueue that the response router thread is finishing [#896](https://github.com/jupyter-server/jupyter_server/pull/896) ([@CiprianAnton](https://github.com/CiprianAnton))
- Make ChannelQueue.get_msg true async [#892](https://github.com/jupyter-server/jupyter_server/pull/892) ([@CiprianAnton](https://github.com/CiprianAnton))
- Check for serverapp for reraise flag [#887](https://github.com/jupyter-server/jupyter_server/pull/887) ([@vidartf](https://github.com/vidartf))

### Maintenance and upkeep improvements

- Make tests less sensitive to default kernel name [#1118](https://github.com/jupyter-server/jupyter_server/pull/1118) ([@blink1073](https://github.com/blink1073))
- Tweak codecov settings [#1113](https://github.com/jupyter-server/jupyter_server/pull/1113) ([@blink1073](https://github.com/blink1073))
- Bump minimatch from 3.0.4 to 3.1.2 [#1109](https://github.com/jupyter-server/jupyter_server/pull/1109) ([@dependabot](https://github.com/dependabot))
- Add skip-if-exists config [#1108](https://github.com/jupyter-server/jupyter_server/pull/1108) ([@blink1073](https://github.com/blink1073))
- Use pytest-jupyter [#1099](https://github.com/jupyter-server/jupyter_server/pull/1099) ([@blink1073](https://github.com/blink1073))
- Clean up release instructions and coverage handling [#1098](https://github.com/jupyter-server/jupyter_server/pull/1098) ([@blink1073](https://github.com/blink1073))
- Import ensure_async from jupyter_core [#1093](https://github.com/jupyter-server/jupyter_server/pull/1093) ([@davidbrochart](https://github.com/davidbrochart))
- Add more tests [#1092](https://github.com/jupyter-server/jupyter_server/pull/1092) ([@blink1073](https://github.com/blink1073))
- Fix coverage upload [#1091](https://github.com/jupyter-server/jupyter_server/pull/1091) ([@blink1073](https://github.com/blink1073))
- Add base handler tests [#1090](https://github.com/jupyter-server/jupyter_server/pull/1090) ([@blink1073](https://github.com/blink1073))
- Add more websocket connection tests and fix bugs [#1085](https://github.com/jupyter-server/jupyter_server/pull/1085) ([@blink1073](https://github.com/blink1073))
- Use base setup dependency type [#1084](https://github.com/jupyter-server/jupyter_server/pull/1084) ([@blink1073](https://github.com/blink1073))
- Add more serverapp tests [#1079](https://github.com/jupyter-server/jupyter_server/pull/1079) ([@blink1073](https://github.com/blink1073))
- Add more gateway tests [#1078](https://github.com/jupyter-server/jupyter_server/pull/1078) ([@blink1073](https://github.com/blink1073))
- More cleanup [#1077](https://github.com/jupyter-server/jupyter_server/pull/1077) ([@blink1073](https://github.com/blink1073))
- Fix hatch scripts and windows workflow run [#1074](https://github.com/jupyter-server/jupyter_server/pull/1074) ([@blink1073](https://github.com/blink1073))
- use recommended github-workflows checker [#1071](https://github.com/jupyter-server/jupyter_server/pull/1071) ([@blink1073](https://github.com/blink1073))
- Add more coverage [#1069](https://github.com/jupyter-server/jupyter_server/pull/1069) ([@blink1073](https://github.com/blink1073))
- More coverage [#1067](https://github.com/jupyter-server/jupyter_server/pull/1067) ([@blink1073](https://github.com/blink1073))
- Increase nbconvert and checkpoints coverage [#1066](https://github.com/jupyter-server/jupyter_server/pull/1066) ([@blink1073](https://github.com/blink1073))
- Test downstream jupyter_server_terminals [#1065](https://github.com/jupyter-server/jupyter_server/pull/1065) ([@blink1073](https://github.com/blink1073))
- Test notebook prerelease [#1064](https://github.com/jupyter-server/jupyter_server/pull/1064) ([@blink1073](https://github.com/blink1073))
- MAINT: remove python 3.4 branch [#1061](https://github.com/jupyter-server/jupyter_server/pull/1061) ([@Carreau](https://github.com/Carreau))
- Bump actions/checkout from 2 to 3 [#1056](https://github.com/jupyter-server/jupyter_server/pull/1056) ([@dependabot](https://github.com/dependabot))
- Bump actions/setup-python from 2 to 4 [#1055](https://github.com/jupyter-server/jupyter_server/pull/1055) ([@dependabot](https://github.com/dependabot))
- Bump pre-commit/action from 2.0.0 to 3.0.0 [#1054](https://github.com/jupyter-server/jupyter_server/pull/1054) ([@dependabot](https://github.com/dependabot))
- Add dependabot file [#1053](https://github.com/jupyter-server/jupyter_server/pull/1053) ([@blink1073](https://github.com/blink1073))
- Use global env for min version check [#1048](https://github.com/jupyter-server/jupyter_server/pull/1048) ([@blink1073](https://github.com/blink1073))
- Clean up handling of synchronous managers [#1044](https://github.com/jupyter-server/jupyter_server/pull/1044) ([@blink1073](https://github.com/blink1073))
- Clean up config files [#1031](https://github.com/jupyter-server/jupyter_server/pull/1031) ([@blink1073](https://github.com/blink1073))
- Make node optional [#1030](https://github.com/jupyter-server/jupyter_server/pull/1030) ([@blink1073](https://github.com/blink1073))
- Use admin github token for releaser [#1025](https://github.com/jupyter-server/jupyter_server/pull/1025) ([@blink1073](https://github.com/blink1073))
- CI Cleanup [#1023](https://github.com/jupyter-server/jupyter_server/pull/1023) ([@blink1073](https://github.com/blink1073))
- Use mdformat instead of prettier [#1022](https://github.com/jupyter-server/jupyter_server/pull/1022) ([@blink1073](https://github.com/blink1073))
- Add pyproject validation [#1020](https://github.com/jupyter-server/jupyter_server/pull/1020) ([@blink1073](https://github.com/blink1073))
- Remove hardcoded client install in CI [#1019](https://github.com/jupyter-server/jupyter_server/pull/1019) ([@blink1073](https://github.com/blink1073))
- Handle client 8 pending kernels [#1014](https://github.com/jupyter-server/jupyter_server/pull/1014) ([@blink1073](https://github.com/blink1073))
- Use releaser v2 tag [#1010](https://github.com/jupyter-server/jupyter_server/pull/1010) ([@blink1073](https://github.com/blink1073))
- Use hatch environments to simplify test, coverage, and docs build [#1007](https://github.com/jupyter-server/jupyter_server/pull/1007) ([@blink1073](https://github.com/blink1073))
- Update to version2 releaser [#1006](https://github.com/jupyter-server/jupyter_server/pull/1006) ([@blink1073](https://github.com/blink1073))
- Do not use dev version yet [#999](https://github.com/jupyter-server/jupyter_server/pull/999) ([@blink1073](https://github.com/blink1073))
- Add workflows for simplified publish [#993](https://github.com/jupyter-server/jupyter_server/pull/993) ([@blink1073](https://github.com/blink1073))
- Remove hardcoded client install [#991](https://github.com/jupyter-server/jupyter_server/pull/991) ([@blink1073](https://github.com/blink1073))
- Test with client 8 updates [#988](https://github.com/jupyter-server/jupyter_server/pull/988) ([@blink1073](https://github.com/blink1073))
- Switch to using hatchling version command [#984](https://github.com/jupyter-server/jupyter_server/pull/984) ([@blink1073](https://github.com/blink1073))
- Run downstream tests in parallel [#973](https://github.com/jupyter-server/jupyter_server/pull/973) ([@blink1073](https://github.com/blink1073))
- Update pytest_plugin with fixtures to test auth in core and extensions [#956](https://github.com/jupyter-server/jupyter_server/pull/956) ([@akshaychitneni](https://github.com/akshaychitneni))
- Fix docs build [#952](https://github.com/jupyter-server/jupyter_server/pull/952) ([@blink1073](https://github.com/blink1073))
- Fix flake8 v5 compat [#941](https://github.com/jupyter-server/jupyter_server/pull/941) ([@blink1073](https://github.com/blink1073))
- Improve logging of bare exceptions and other cleanups. [#922](https://github.com/jupyter-server/jupyter_server/pull/922) ([@thetorpedodog](https://github.com/thetorpedodog))
- Use more explicit version template for pyproject [#919](https://github.com/jupyter-server/jupyter_server/pull/919) ([@blink1073](https://github.com/blink1073))
- Fix handling of dev version [#913](https://github.com/jupyter-server/jupyter_server/pull/913) ([@blink1073](https://github.com/blink1073))
- Fix owasp link [#908](https://github.com/jupyter-server/jupyter_server/pull/908) ([@blink1073](https://github.com/blink1073))
- default to system node version in precommit [#906](https://github.com/jupyter-server/jupyter_server/pull/906) ([@dlqqq](https://github.com/dlqqq))
- Test python 3.11 on ubuntu [#839](https://github.com/jupyter-server/jupyter_server/pull/839) ([@blink1073](https://github.com/blink1073))

### Documentation improvements

- Remove left over from notebook [#1117](https://github.com/jupyter-server/jupyter_server/pull/1117) ([@fcollonval](https://github.com/fcollonval))
- Fix wording [#1037](https://github.com/jupyter-server/jupyter_server/pull/1037) ([@fcollonval](https://github.com/fcollonval))
- Fix GitHub actions badge link [#1011](https://github.com/jupyter-server/jupyter_server/pull/1011) ([@blink1073](https://github.com/blink1073))
- Pin docutils to fix docs build [#1004](https://github.com/jupyter-server/jupyter_server/pull/1004) ([@blink1073](https://github.com/blink1073))
- Update server extension disable instructions [#998](https://github.com/jupyter-server/jupyter_server/pull/998) ([@3coins](https://github.com/3coins))
- Update index.rst [#970](https://github.com/jupyter-server/jupyter_server/pull/970) ([@razrotenberg](https://github.com/razrotenberg))
- Fix typo in IdentityProvider documentation [#915](https://github.com/jupyter-server/jupyter_server/pull/915) ([@danielyahn](https://github.com/danielyahn))
- docs: document the logging_config trait [#844](https://github.com/jupyter-server/jupyter_server/pull/844) ([@oliver-sanders](https://github.com/oliver-sanders))

### Deprecated features

- \[Gateway\] Fix and deprecate env whitelist handling [#979](https://github.com/jupyter-server/jupyter_server/pull/979) ([@kevin-bates](https://github.com/kevin-bates))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2022-06-23&to=2022-12-06&type=c))

[@3coins](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3A3coins+updated%3A2022-06-23..2022-12-06&type=Issues) | [@a3626a](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aa3626a+updated%3A2022-06-23..2022-12-06&type=Issues) | [@akshaychitneni](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aakshaychitneni+updated%3A2022-06-23..2022-12-06&type=Issues) | [@blink1073](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ablink1073+updated%3A2022-06-23..2022-12-06&type=Issues) | [@bloomsa](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Abloomsa+updated%3A2022-06-23..2022-12-06&type=Issues) | [@Carreau](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3ACarreau+updated%3A2022-06-23..2022-12-06&type=Issues) | [@CiprianAnton](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3ACiprianAnton+updated%3A2022-06-23..2022-12-06&type=Issues) | [@codecov](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Acodecov+updated%3A2022-06-23..2022-12-06&type=Issues) | [@codecov-commenter](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Acodecov-commenter+updated%3A2022-06-23..2022-12-06&type=Issues) | [@danielyahn](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Adanielyahn+updated%3A2022-06-23..2022-12-06&type=Issues) | [@davidbrochart](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Adavidbrochart+updated%3A2022-06-23..2022-12-06&type=Issues) | [@dependabot](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Adependabot+updated%3A2022-06-23..2022-12-06&type=Issues) | [@divyansshhh](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Adivyansshhh+updated%3A2022-06-23..2022-12-06&type=Issues) | [@dlqqq](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Adlqqq+updated%3A2022-06-23..2022-12-06&type=Issues) | [@echarles](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aecharles+updated%3A2022-06-23..2022-12-06&type=Issues) | [@ellisonbg](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aellisonbg+updated%3A2022-06-23..2022-12-06&type=Issues) | [@epignot](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aepignot+updated%3A2022-06-23..2022-12-06&type=Issues) | [@fcollonval](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Afcollonval+updated%3A2022-06-23..2022-12-06&type=Issues) | [@hbcarlos](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ahbcarlos+updated%3A2022-06-23..2022-12-06&type=Issues) | [@jiajunjie](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ajiajunjie+updated%3A2022-06-23..2022-12-06&type=Issues) | [@kevin-bates](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Akevin-bates+updated%3A2022-06-23..2022-12-06&type=Issues) | [@kiersten-stokes](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Akiersten-stokes+updated%3A2022-06-23..2022-12-06&type=Issues) | [@krassowski](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Akrassowski+updated%3A2022-06-23..2022-12-06&type=Issues) | [@meeseeksdev](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ameeseeksdev+updated%3A2022-06-23..2022-12-06&type=Issues) | [@minrk](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aminrk+updated%3A2022-06-23..2022-12-06&type=Issues) | [@ofek](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aofek+updated%3A2022-06-23..2022-12-06&type=Issues) | [@oliver-sanders](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aoliver-sanders+updated%3A2022-06-23..2022-12-06&type=Issues) | [@pre-commit-ci](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Apre-commit-ci+updated%3A2022-06-23..2022-12-06&type=Issues) | [@razrotenberg](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Arazrotenberg+updated%3A2022-06-23..2022-12-06&type=Issues) | [@rickwierenga](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Arickwierenga+updated%3A2022-06-23..2022-12-06&type=Issues) | [@thetorpedodog](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Athetorpedodog+updated%3A2022-06-23..2022-12-06&type=Issues) | [@vidartf](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Avidartf+updated%3A2022-06-23..2022-12-06&type=Issues) | [@welcome](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Awelcome+updated%3A2022-06-23..2022-12-06&type=Issues) | [@wjsi](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Awjsi+updated%3A2022-06-23..2022-12-06&type=Issues) | [@yacchin1205](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ayacchin1205+updated%3A2022-06-23..2022-12-06&type=Issues) | [@Zsailer](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3AZsailer+updated%3A2022-06-23..2022-12-06&type=Issues)

## 2.0.0rc8

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/v2.0.0rc7...d2c974a4580e9269580a632a3c8258e99792e279))

### Enhancements made

- Introduce ServerKernelManager class [#1101](https://github.com/jupyter-server/jupyter_server/pull/1101) ([@kevin-bates](https://github.com/kevin-bates))

### Bugs fixed

- Defer webbrowser import [#1095](https://github.com/jupyter-server/jupyter_server/pull/1095) ([@blink1073](https://github.com/blink1073))

### Maintenance and upkeep improvements

- Use pytest-jupyter [#1099](https://github.com/jupyter-server/jupyter_server/pull/1099) ([@blink1073](https://github.com/blink1073))
- Clean up release instructions and coverage handling [#1098](https://github.com/jupyter-server/jupyter_server/pull/1098) ([@blink1073](https://github.com/blink1073))
- Add more tests [#1092](https://github.com/jupyter-server/jupyter_server/pull/1092) ([@blink1073](https://github.com/blink1073))
- Fix coverage upload [#1091](https://github.com/jupyter-server/jupyter_server/pull/1091) ([@blink1073](https://github.com/blink1073))
- Add base handler tests [#1090](https://github.com/jupyter-server/jupyter_server/pull/1090) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2022-11-23&to=2022-11-29&type=c))

[@blink1073](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ablink1073+updated%3A2022-11-23..2022-11-29&type=Issues) | [@codecov](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Acodecov+updated%3A2022-11-23..2022-11-29&type=Issues) | [@kevin-bates](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Akevin-bates+updated%3A2022-11-23..2022-11-29&type=Issues) | [@Zsailer](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3AZsailer+updated%3A2022-11-23..2022-11-29&type=Issues)

## 2.0.0rc7

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/v2.0.0rc6...339038b532ec928b59861f9426a8ba1214454741))

### Bugs fixed

- Use handle_outgoing_message for ZMQ replies [#1089](https://github.com/jupyter-server/jupyter_server/pull/1089) ([@Zsailer](https://github.com/Zsailer))
- Call `ports_changed` on the multi-kernel-manager instead of the kernel manager [#1088](https://github.com/jupyter-server/jupyter_server/pull/1088) ([@Zsailer](https://github.com/Zsailer))
- Add more websocket connection tests and fix bugs [#1085](https://github.com/jupyter-server/jupyter_server/pull/1085) ([@blink1073](https://github.com/blink1073))

### Maintenance and upkeep improvements

- Add more websocket connection tests and fix bugs [#1085](https://github.com/jupyter-server/jupyter_server/pull/1085) ([@blink1073](https://github.com/blink1073))
- Use base setup dependency type [#1084](https://github.com/jupyter-server/jupyter_server/pull/1084) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2022-11-21&to=2022-11-23&type=c))

[@blink1073](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ablink1073+updated%3A2022-11-21..2022-11-23&type=Issues) | [@codecov](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Acodecov+updated%3A2022-11-21..2022-11-23&type=Issues) | [@Zsailer](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3AZsailer+updated%3A2022-11-21..2022-11-23&type=Issues)

## 2.0.0rc6

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/v2.0.0rc5...cd060da67aa6e3e5d8ff791f0a559a91282be2b3))

### Bugs fixed

- Tornado WebSocketHandler fixup [#1083](https://github.com/jupyter-server/jupyter_server/pull/1083) ([@davidbrochart](https://github.com/davidbrochart))

### Maintenance and upkeep improvements

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2022-11-21&to=2022-11-21&type=c))

[@codecov](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Acodecov+updated%3A2022-11-21..2022-11-21&type=Issues) | [@davidbrochart](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Adavidbrochart+updated%3A2022-11-21..2022-11-21&type=Issues) | [@pre-commit-ci](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Apre-commit-ci+updated%3A2022-11-21..2022-11-21&type=Issues)

## 2.0.0rc5

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/v2.0.0rc4...12f7c1d47e0ca76f8c39dfd1499142e8b6df09ee))

### Enhancements made

- New configurable/overridable kernel ZMQ+Websocket connection API [#1047](https://github.com/jupyter-server/jupyter_server/pull/1047) ([@Zsailer](https://github.com/Zsailer))
- Add authorization to AuthenticatedFileHandler [#1021](https://github.com/jupyter-server/jupyter_server/pull/1021) ([@jiajunjie](https://github.com/jiajunjie))

### Bugs fixed

- persist userid cookie when auth is disabled [#1076](https://github.com/jupyter-server/jupyter_server/pull/1076) ([@minrk](https://github.com/minrk))
- Fix rename_file and delete_file to handle hidden files properly [#1073](https://github.com/jupyter-server/jupyter_server/pull/1073) ([@yacchin1205](https://github.com/yacchin1205))
- Add more coverage [#1069](https://github.com/jupyter-server/jupyter_server/pull/1069) ([@blink1073](https://github.com/blink1073))
- Increase nbconvert and checkpoints coverage [#1066](https://github.com/jupyter-server/jupyter_server/pull/1066) ([@blink1073](https://github.com/blink1073))

### Maintenance and upkeep improvements

- Add more serverapp tests [#1079](https://github.com/jupyter-server/jupyter_server/pull/1079) ([@blink1073](https://github.com/blink1073))
- Add more gateway tests [#1078](https://github.com/jupyter-server/jupyter_server/pull/1078) ([@blink1073](https://github.com/blink1073))
- More cleanup [#1077](https://github.com/jupyter-server/jupyter_server/pull/1077) ([@blink1073](https://github.com/blink1073))
- Fix hatch scripts and windows workflow run [#1074](https://github.com/jupyter-server/jupyter_server/pull/1074) ([@blink1073](https://github.com/blink1073))
- use recommended github-workflows checker [#1071](https://github.com/jupyter-server/jupyter_server/pull/1071) ([@blink1073](https://github.com/blink1073))
- Add more coverage [#1069](https://github.com/jupyter-server/jupyter_server/pull/1069) ([@blink1073](https://github.com/blink1073))
- More coverage [#1067](https://github.com/jupyter-server/jupyter_server/pull/1067) ([@blink1073](https://github.com/blink1073))
- Increase nbconvert and checkpoints coverage [#1066](https://github.com/jupyter-server/jupyter_server/pull/1066) ([@blink1073](https://github.com/blink1073))
- Test downstream jupyter_server_terminals [#1065](https://github.com/jupyter-server/jupyter_server/pull/1065) ([@blink1073](https://github.com/blink1073))
- Test notebook prerelease [#1064](https://github.com/jupyter-server/jupyter_server/pull/1064) ([@blink1073](https://github.com/blink1073))

### Documentation improvements

- docs: document the logging_config trait [#844](https://github.com/jupyter-server/jupyter_server/pull/844) ([@oliver-sanders](https://github.com/oliver-sanders))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2022-11-10&to=2022-11-21&type=c))

[@blink1073](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ablink1073+updated%3A2022-11-10..2022-11-21&type=Issues) | [@codecov](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Acodecov+updated%3A2022-11-10..2022-11-21&type=Issues) | [@codecov-commenter](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Acodecov-commenter+updated%3A2022-11-10..2022-11-21&type=Issues) | [@jiajunjie](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ajiajunjie+updated%3A2022-11-10..2022-11-21&type=Issues) | [@minrk](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aminrk+updated%3A2022-11-10..2022-11-21&type=Issues) | [@oliver-sanders](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aoliver-sanders+updated%3A2022-11-10..2022-11-21&type=Issues) | [@pre-commit-ci](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Apre-commit-ci+updated%3A2022-11-10..2022-11-21&type=Issues) | [@welcome](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Awelcome+updated%3A2022-11-10..2022-11-21&type=Issues) | [@yacchin1205](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ayacchin1205+updated%3A2022-11-10..2022-11-21&type=Issues) | [@Zsailer](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3AZsailer+updated%3A2022-11-10..2022-11-21&type=Issues)

## 2.0.0rc4

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/v2.0.0rc3...f6b732c652e0b5a600ff0d3f60c6a34173d8d6a5))

### Enhancements made

- Pass kernel environment to `cwd_for_path` method [#1046](https://github.com/jupyter-server/jupyter_server/pull/1046) ([@divyansshhh](https://github.com/divyansshhh))
- Better Handling of Asyncio [#1035](https://github.com/jupyter-server/jupyter_server/pull/1035) ([@blink1073](https://github.com/blink1073))

### Bugs fixed

- Fix min version check again [#1049](https://github.com/jupyter-server/jupyter_server/pull/1049) ([@blink1073](https://github.com/blink1073))

### Maintenance and upkeep improvements

- MAINT: remove python 3.4 branch [#1061](https://github.com/jupyter-server/jupyter_server/pull/1061) ([@Carreau](https://github.com/Carreau))
- Bump actions/checkout from 2 to 3 [#1056](https://github.com/jupyter-server/jupyter_server/pull/1056) ([@dependabot](https://github.com/dependabot))
- Bump actions/setup-python from 2 to 4 [#1055](https://github.com/jupyter-server/jupyter_server/pull/1055) ([@dependabot](https://github.com/dependabot))
- Bump pre-commit/action from 2.0.0 to 3.0.0 [#1054](https://github.com/jupyter-server/jupyter_server/pull/1054) ([@dependabot](https://github.com/dependabot))
- Add dependabot file [#1053](https://github.com/jupyter-server/jupyter_server/pull/1053) ([@blink1073](https://github.com/blink1073))
- Use global env for min version check [#1048](https://github.com/jupyter-server/jupyter_server/pull/1048) ([@blink1073](https://github.com/blink1073))
- Clean up handling of synchronous managers [#1044](https://github.com/jupyter-server/jupyter_server/pull/1044) ([@blink1073](https://github.com/blink1073))

### Documentation improvements

- Fix wording [#1037](https://github.com/jupyter-server/jupyter_server/pull/1037) ([@fcollonval](https://github.com/fcollonval))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2022-10-17&to=2022-11-10&type=c))

[@blink1073](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ablink1073+updated%3A2022-10-17..2022-11-10&type=Issues) | [@Carreau](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3ACarreau+updated%3A2022-10-17..2022-11-10&type=Issues) | [@codecov-commenter](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Acodecov-commenter+updated%3A2022-10-17..2022-11-10&type=Issues) | [@dependabot](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Adependabot+updated%3A2022-10-17..2022-11-10&type=Issues) | [@divyansshhh](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Adivyansshhh+updated%3A2022-10-17..2022-11-10&type=Issues) | [@fcollonval](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Afcollonval+updated%3A2022-10-17..2022-11-10&type=Issues) | [@pre-commit-ci](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Apre-commit-ci+updated%3A2022-10-17..2022-11-10&type=Issues)

## 2.0.0rc3

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/v2.0.0rc2...fc0ac3236fdd92778ea765db6e8982212c8389ee))

### Maintenance and upkeep improvements

- Clean up config files [#1031](https://github.com/jupyter-server/jupyter_server/pull/1031) ([@blink1073](https://github.com/blink1073))
- Make node optional [#1030](https://github.com/jupyter-server/jupyter_server/pull/1030) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2022-10-11&to=2022-10-17&type=c))

[@blink1073](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ablink1073+updated%3A2022-10-11..2022-10-17&type=Issues) | [@codecov-commenter](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Acodecov-commenter+updated%3A2022-10-11..2022-10-17&type=Issues)

## 2.0.0rc2

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/v2.0.0rc1...32de53beae1e9396dd3111b17222ec802b122f0b))

### Bugs fixed

- Fallback new file type to file for contents put [#1013](https://github.com/jupyter-server/jupyter_server/pull/1013) ([@a3626a](https://github.com/a3626a))
- Fix some typos in release instructions [#1003](https://github.com/jupyter-server/jupyter_server/pull/1003) ([@kevin-bates](https://github.com/kevin-bates))

### Maintenance and upkeep improvements

- Use admin github token for releaser [#1025](https://github.com/jupyter-server/jupyter_server/pull/1025) ([@blink1073](https://github.com/blink1073))
- CI Cleanup [#1023](https://github.com/jupyter-server/jupyter_server/pull/1023) ([@blink1073](https://github.com/blink1073))
- Use mdformat instead of prettier [#1022](https://github.com/jupyter-server/jupyter_server/pull/1022) ([@blink1073](https://github.com/blink1073))
- Add pyproject validation [#1020](https://github.com/jupyter-server/jupyter_server/pull/1020) ([@blink1073](https://github.com/blink1073))
- Remove hardcoded client install in CI [#1019](https://github.com/jupyter-server/jupyter_server/pull/1019) ([@blink1073](https://github.com/blink1073))
- Handle client 8 pending kernels [#1014](https://github.com/jupyter-server/jupyter_server/pull/1014) ([@blink1073](https://github.com/blink1073))
- Use releaser v2 tag [#1010](https://github.com/jupyter-server/jupyter_server/pull/1010) ([@blink1073](https://github.com/blink1073))
- Use hatch environments to simplify test, coverage, and docs build [#1007](https://github.com/jupyter-server/jupyter_server/pull/1007) ([@blink1073](https://github.com/blink1073))
- Update to version2 releaser [#1006](https://github.com/jupyter-server/jupyter_server/pull/1006) ([@blink1073](https://github.com/blink1073))

### Documentation improvements

- Fix GitHub actions badge link [#1011](https://github.com/jupyter-server/jupyter_server/pull/1011) ([@blink1073](https://github.com/blink1073))
- Pin docutils to fix docs build [#1004](https://github.com/jupyter-server/jupyter_server/pull/1004) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2022-09-27&to=2022-10-11&type=c))

[@a3626a](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aa3626a+updated%3A2022-09-27..2022-10-11&type=Issues) | [@blink1073](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ablink1073+updated%3A2022-09-27..2022-10-11&type=Issues) | [@codecov-commenter](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Acodecov-commenter+updated%3A2022-09-27..2022-10-11&type=Issues) | [@kevin-bates](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Akevin-bates+updated%3A2022-09-27..2022-10-11&type=Issues) | [@pre-commit-ci](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Apre-commit-ci+updated%3A2022-09-27..2022-10-11&type=Issues) | [@welcome](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Awelcome+updated%3A2022-09-27..2022-10-11&type=Issues)

## 2.0.0rc1

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/v2.0.0rc0...dd8a6937651170e2cea38a2fecbecc2a1a4f655f))

### Enhancements made

- \[Gateway\] Add support for gateway token renewal [#985](https://github.com/jupyter-server/jupyter_server/pull/985) ([@kevin-bates](https://github.com/kevin-bates))
- Make it easier to pass custom env variables to kernel [#981](https://github.com/jupyter-server/jupyter_server/pull/981) ([@divyansshhh](https://github.com/divyansshhh))

### Bugs fixed

- Wrap the concurrent futures in an asyncio future [#1001](https://github.com/jupyter-server/jupyter_server/pull/1001) ([@blink1073](https://github.com/blink1073))
- \[Gateway\] Fix and deprecate env whitelist handling [#979](https://github.com/jupyter-server/jupyter_server/pull/979) ([@kevin-bates](https://github.com/kevin-bates))

### Maintenance and upkeep improvements

- Do not use dev version yet [#999](https://github.com/jupyter-server/jupyter_server/pull/999) ([@blink1073](https://github.com/blink1073))
- Add workflows for simplified publish [#993](https://github.com/jupyter-server/jupyter_server/pull/993) ([@blink1073](https://github.com/blink1073))
- Remove hardcoded client install [#991](https://github.com/jupyter-server/jupyter_server/pull/991) ([@blink1073](https://github.com/blink1073))
- Test with client 8 updates [#988](https://github.com/jupyter-server/jupyter_server/pull/988) ([@blink1073](https://github.com/blink1073))
- Switch to using hatchling version command [#984](https://github.com/jupyter-server/jupyter_server/pull/984) ([@blink1073](https://github.com/blink1073))
- Test python 3.11 on ubuntu [#839](https://github.com/jupyter-server/jupyter_server/pull/839) ([@blink1073](https://github.com/blink1073))

### Documentation improvements

- Update server extension disable instructions [#998](https://github.com/jupyter-server/jupyter_server/pull/998) ([@3coins](https://github.com/3coins))

### Deprecated features

- \[Gateway\] Fix and deprecate env whitelist handling [#979](https://github.com/jupyter-server/jupyter_server/pull/979) ([@kevin-bates](https://github.com/kevin-bates))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2022-09-13&to=2022-09-27&type=c))

[@3coins](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3A3coins+updated%3A2022-09-13..2022-09-27&type=Issues) | [@blink1073](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ablink1073+updated%3A2022-09-13..2022-09-27&type=Issues) | [@codecov-commenter](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Acodecov-commenter+updated%3A2022-09-13..2022-09-27&type=Issues) | [@divyansshhh](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Adivyansshhh+updated%3A2022-09-13..2022-09-27&type=Issues) | [@kevin-bates](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Akevin-bates+updated%3A2022-09-13..2022-09-27&type=Issues) | [@meeseeksdev](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ameeseeksdev+updated%3A2022-09-13..2022-09-27&type=Issues) | [@pre-commit-ci](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Apre-commit-ci+updated%3A2022-09-13..2022-09-27&type=Issues)

## 2.0.0rc0

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/v2.0.0b1...90905e116a2ae49b35b49c360614b0831498477b))

### New features added

- Identity API at /api/me [#671](https://github.com/jupyter-server/jupyter_server/pull/671) ([@minrk](https://github.com/minrk))

### Enhancements made

- Accept and manage cookies when requesting gateways [#969](https://github.com/jupyter-server/jupyter_server/pull/969) ([@wjsi](https://github.com/wjsi))
- Emit events from the Contents Service [#954](https://github.com/jupyter-server/jupyter_server/pull/954) ([@Zsailer](https://github.com/Zsailer))
- Retry certain errors between server and gateway [#944](https://github.com/jupyter-server/jupyter_server/pull/944) ([@kevin-bates](https://github.com/kevin-bates))
- Allow new file types [#895](https://github.com/jupyter-server/jupyter_server/pull/895) ([@davidbrochart](https://github.com/davidbrochart))
- Adds anonymous users [#863](https://github.com/jupyter-server/jupyter_server/pull/863) ([@hbcarlos](https://github.com/hbcarlos))
- switch to jupyter_events [#862](https://github.com/jupyter-server/jupyter_server/pull/862) ([@Zsailer](https://github.com/Zsailer))
- Make it easier for extensions to customize the ServerApp [#879](https://github.com/jupyter-server/jupyter_server/pull/879) ([@minrk](https://github.com/minrk))
- consolidate auth config on IdentityProvider [#825](https://github.com/jupyter-server/jupyter_server/pull/825) ([@minrk](https://github.com/minrk))
- Show import error when faiing to load an extension [#878](https://github.com/jupyter-server/jupyter_server/pull/878) ([@minrk](https://github.com/minrk))
- Add the root_dir value to the logging message in case of non compliant preferred_dir [#804](https://github.com/jupyter-server/jupyter_server/pull/804) ([@echarles](https://github.com/echarles))
- Hydrate a Kernel Manager when calling GatewayKernelManager.start_kernel with a kernel_id [#788](https://github.com/jupyter-server/jupyter_server/pull/788) ([@Zsailer](https://github.com/Zsailer))
- Remove terminals in favor of jupyter_server_terminals extension [#651](https://github.com/jupyter-server/jupyter_server/pull/651) ([@Zsailer](https://github.com/Zsailer))

### Bugs fixed

- fix issues with jupyter_events 0.5.0 [#972](https://github.com/jupyter-server/jupyter_server/pull/972) ([@Zsailer](https://github.com/Zsailer))
- Correct content-type headers [#965](https://github.com/jupyter-server/jupyter_server/pull/965) ([@epignot](https://github.com/epignot))
- Don't validate certs for when stopping server [#959](https://github.com/jupyter-server/jupyter_server/pull/959) ([@Zsailer](https://github.com/Zsailer))
- Parse list value for `terminado_settings` [#949](https://github.com/jupyter-server/jupyter_server/pull/949) ([@krassowski](https://github.com/krassowski))
- Fix bug in `api/contents` requests for an allowed copy [#939](https://github.com/jupyter-server/jupyter_server/pull/939) ([@kiersten-stokes](https://github.com/kiersten-stokes))
- Fix error that prevents posting to `api/contents` endpoint with no body [#937](https://github.com/jupyter-server/jupyter_server/pull/937) ([@kiersten-stokes](https://github.com/kiersten-stokes))
- avoid creating asyncio.Lock at import time [#935](https://github.com/jupyter-server/jupyter_server/pull/935) ([@minrk](https://github.com/minrk))
- Fix `get_kernel_path` for `AsyncFileManager`s. [#929](https://github.com/jupyter-server/jupyter_server/pull/929) ([@thetorpedodog](https://github.com/thetorpedodog))
- Check for serverapp for reraise flag [#887](https://github.com/jupyter-server/jupyter_server/pull/887) ([@vidartf](https://github.com/vidartf))
- Notify ChannelQueue that the response router thread is finishing [#896](https://github.com/jupyter-server/jupyter_server/pull/896) ([@CiprianAnton](https://github.com/CiprianAnton))
- Make ChannelQueue.get_msg true async [#892](https://github.com/jupyter-server/jupyter_server/pull/892) ([@CiprianAnton](https://github.com/CiprianAnton))
- Fix gateway kernel shutdown [#874](https://github.com/jupyter-server/jupyter_server/pull/874) ([@kevin-bates](https://github.com/kevin-bates))
- Defer preferred_dir validation until root_dir is set [#826](https://github.com/jupyter-server/jupyter_server/pull/826) ([@kevin-bates](https://github.com/kevin-bates))
- missing required arguments in utils.fetch [#798](https://github.com/jupyter-server/jupyter_server/pull/798) ([@minrk](https://github.com/minrk))

### Maintenance and upkeep improvements

- Run downstream tests in parallel [#973](https://github.com/jupyter-server/jupyter_server/pull/973) ([@blink1073](https://github.com/blink1073))
- \[pre-commit.ci\] pre-commit autoupdate [#971](https://github.com/jupyter-server/jupyter_server/pull/971) ([@pre-commit-ci](https://github.com/pre-commit-ci))
- \[pre-commit.ci\] pre-commit autoupdate [#963](https://github.com/jupyter-server/jupyter_server/pull/963) ([@pre-commit-ci](https://github.com/pre-commit-ci))
- Update pytest_plugin with fixtures to test auth in core and extensions [#956](https://github.com/jupyter-server/jupyter_server/pull/956) ([@akshaychitneni](https://github.com/akshaychitneni))
- \[pre-commit.ci\] pre-commit autoupdate [#955](https://github.com/jupyter-server/jupyter_server/pull/955) ([@pre-commit-ci](https://github.com/pre-commit-ci))
- Fix docs build [#952](https://github.com/jupyter-server/jupyter_server/pull/952) ([@blink1073](https://github.com/blink1073))
- \[pre-commit.ci\] pre-commit autoupdate [#945](https://github.com/jupyter-server/jupyter_server/pull/945) ([@pre-commit-ci](https://github.com/pre-commit-ci))
- \[pre-commit.ci\] pre-commit autoupdate [#942](https://github.com/jupyter-server/jupyter_server/pull/942) ([@pre-commit-ci](https://github.com/pre-commit-ci))
- Fix flake8 v5 compat [#941](https://github.com/jupyter-server/jupyter_server/pull/941) ([@blink1073](https://github.com/blink1073))
- \[pre-commit.ci\] pre-commit autoupdate [#938](https://github.com/jupyter-server/jupyter_server/pull/938) ([@pre-commit-ci](https://github.com/pre-commit-ci))
- \[pre-commit.ci\] pre-commit autoupdate [#928](https://github.com/jupyter-server/jupyter_server/pull/928) ([@pre-commit-ci](https://github.com/pre-commit-ci))
- \[pre-commit.ci\] pre-commit autoupdate [#902](https://github.com/jupyter-server/jupyter_server/pull/902) ([@pre-commit-ci](https://github.com/pre-commit-ci))
- \[pre-commit.ci\] pre-commit autoupdate [#894](https://github.com/jupyter-server/jupyter_server/pull/894) ([@pre-commit-ci](https://github.com/pre-commit-ci))
- Normalize os_path [#886](https://github.com/jupyter-server/jupyter_server/pull/886) ([@martinRenou](https://github.com/martinRenou))
- \[pre-commit.ci\] pre-commit autoupdate [#885](https://github.com/jupyter-server/jupyter_server/pull/885) ([@pre-commit-ci](https://github.com/pre-commit-ci))
- suppress tornado deprecation warnings [#882](https://github.com/jupyter-server/jupyter_server/pull/882) ([@minrk](https://github.com/minrk))
- Fix lint [#867](https://github.com/jupyter-server/jupyter_server/pull/867) ([@blink1073](https://github.com/blink1073))
- \[pre-commit.ci\] pre-commit autoupdate [#866](https://github.com/jupyter-server/jupyter_server/pull/866) ([@pre-commit-ci](https://github.com/pre-commit-ci))
- Fix sphinx 5.0 support [#865](https://github.com/jupyter-server/jupyter_server/pull/865) ([@blink1073](https://github.com/blink1073))
- Add license metadata and file [#827](https://github.com/jupyter-server/jupyter_server/pull/827) ([@blink1073](https://github.com/blink1073))
- CI cleanup [#824](https://github.com/jupyter-server/jupyter_server/pull/824) ([@blink1073](https://github.com/blink1073))
- Switch to flit [#823](https://github.com/jupyter-server/jupyter_server/pull/823) ([@blink1073](https://github.com/blink1073))
- Remove unused pytest-mock dependency [#814](https://github.com/jupyter-server/jupyter_server/pull/814) ([@mgorny](https://github.com/mgorny))
- Remove duplicate requests requirement from setup.cfg [#813](https://github.com/jupyter-server/jupyter_server/pull/813) ([@mgorny](https://github.com/mgorny))
- \[pre-commit.ci\] pre-commit autoupdate [#802](https://github.com/jupyter-server/jupyter_server/pull/802) ([@pre-commit-ci](https://github.com/pre-commit-ci))
- Add helper jobs for branch protection [#797](https://github.com/jupyter-server/jupyter_server/pull/797) ([@blink1073](https://github.com/blink1073))
- \[pre-commit.ci\] pre-commit autoupdate [#793](https://github.com/jupyter-server/jupyter_server/pull/793) ([@pre-commit-ci](https://github.com/pre-commit-ci))
- Centralize app cleanup [#792](https://github.com/jupyter-server/jupyter_server/pull/792) ([@blink1073](https://github.com/blink1073))
- \[pre-commit.ci\] pre-commit autoupdate [#785](https://github.com/jupyter-server/jupyter_server/pull/785) ([@pre-commit-ci](https://github.com/pre-commit-ci))
- Clean up pre-commit [#782](https://github.com/jupyter-server/jupyter_server/pull/782) ([@blink1073](https://github.com/blink1073))
- Add mypy check [#779](https://github.com/jupyter-server/jupyter_server/pull/779) ([@blink1073](https://github.com/blink1073))
- Use new post-version-spec from jupyter_releaser [#777](https://github.com/jupyter-server/jupyter_server/pull/777) ([@blink1073](https://github.com/blink1073))
- Give write permissions to enforce label workflow [#776](https://github.com/jupyter-server/jupyter_server/pull/776) ([@blink1073](https://github.com/blink1073))
- \[pre-commit.ci\] pre-commit autoupdate [#775](https://github.com/jupyter-server/jupyter_server/pull/775) ([@pre-commit-ci](https://github.com/pre-commit-ci))
- Add explicit handling of warnings [#771](https://github.com/jupyter-server/jupyter_server/pull/771) ([@blink1073](https://github.com/blink1073))
- Use test-sdist from maintainer-tools [#769](https://github.com/jupyter-server/jupyter_server/pull/769) ([@blink1073](https://github.com/blink1073))
- Add pyupgrade and doc8 hooks [#768](https://github.com/jupyter-server/jupyter_server/pull/768) ([@blink1073](https://github.com/blink1073))
- update some metadata fields, sort deps [#675](https://github.com/jupyter-server/jupyter_server/pull/675) ([@bollwyvl](https://github.com/bollwyvl))

### Documentation improvements

- Fix typo in IdentityProvider documentation [#915](https://github.com/jupyter-server/jupyter_server/pull/915) ([@danielyahn](https://github.com/danielyahn))
- Add Session workflows documentation [#808](https://github.com/jupyter-server/jupyter_server/pull/808) ([@andreyvelich](https://github.com/andreyvelich))
- Add Jupyter Server Architecture diagram [#801](https://github.com/jupyter-server/jupyter_server/pull/801) ([@andreyvelich](https://github.com/andreyvelich))
- Fix path for full config doc [#800](https://github.com/jupyter-server/jupyter_server/pull/800) ([@andreyvelich](https://github.com/andreyvelich))
- Fix contributing guide for building the docs [#794](https://github.com/jupyter-server/jupyter_server/pull/794) ([@andreyvelich](https://github.com/andreyvelich))
- Update team meetings doc [#772](https://github.com/jupyter-server/jupyter_server/pull/772) ([@willingc](https://github.com/willingc))
- Update documentation about registering file save hooks [#770](https://github.com/jupyter-server/jupyter_server/pull/770) ([@davidbrochart](https://github.com/davidbrochart))

### Other merged PRs

- Update index.rst [#970](https://github.com/jupyter-server/jupyter_server/pull/970) ([@razrotenberg](https://github.com/razrotenberg))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2022-09-01&to=2022-09-13&type=c))

[@blink1073](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ablink1073+updated%3A2022-09-01..2022-09-13&type=Issues) | [@codecov-commenter](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Acodecov-commenter+updated%3A2022-09-01..2022-09-13&type=Issues) | [@echarles](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aecharles+updated%3A2022-09-01..2022-09-13&type=Issues) | [@epignot](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aepignot+updated%3A2022-09-01..2022-09-13&type=Issues) | [@krassowski](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Akrassowski+updated%3A2022-09-01..2022-09-13&type=Issues) | [@pre-commit-ci](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Apre-commit-ci+updated%3A2022-09-01..2022-09-13&type=Issues) | [@razrotenberg](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Arazrotenberg+updated%3A2022-09-01..2022-09-13&type=Issues) | [@welcome](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Awelcome+updated%3A2022-09-01..2022-09-13&type=Issues) | [@wjsi](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Awjsi+updated%3A2022-09-01..2022-09-13&type=Issues) | [@Zsailer](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3AZsailer+updated%3A2022-09-01..2022-09-13&type=Issues)

## 2.0.0b1

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/v2.0.0b0...644540b4128e8295e5cedf75e7d7d1c04ba9b3ea))

### Enhancements made

- Emit events from the Contents Service [#954](https://github.com/jupyter-server/jupyter_server/pull/954) ([@Zsailer](https://github.com/Zsailer))
- Retry certain errors between server and gateway [#944](https://github.com/jupyter-server/jupyter_server/pull/944) ([@kevin-bates](https://github.com/kevin-bates))
- Allow new file types [#895](https://github.com/jupyter-server/jupyter_server/pull/895) ([@davidbrochart](https://github.com/davidbrochart))
- Adds anonymous users [#863](https://github.com/jupyter-server/jupyter_server/pull/863) ([@hbcarlos](https://github.com/hbcarlos))
- switch to jupyter_events [#862](https://github.com/jupyter-server/jupyter_server/pull/862) ([@Zsailer](https://github.com/Zsailer))

### Bugs fixed

- Fix bug in `api/contents` requests for an allowed copy [#939](https://github.com/jupyter-server/jupyter_server/pull/939) ([@kiersten-stokes](https://github.com/kiersten-stokes))
- Fix error that prevents posting to `api/contents` endpoint with no body [#937](https://github.com/jupyter-server/jupyter_server/pull/937) ([@kiersten-stokes](https://github.com/kiersten-stokes))
- avoid creating asyncio.Lock at import time [#935](https://github.com/jupyter-server/jupyter_server/pull/935) ([@minrk](https://github.com/minrk))
- Fix `get_kernel_path` for `AsyncFileManager`s. [#929](https://github.com/jupyter-server/jupyter_server/pull/929) ([@thetorpedodog](https://github.com/thetorpedodog))
- Check for serverapp for reraise flag [#887](https://github.com/jupyter-server/jupyter_server/pull/887) ([@vidartf](https://github.com/vidartf))

### Maintenance and upkeep improvements

- Update pytest_plugin with fixtures to test auth in core and extensions [#956](https://github.com/jupyter-server/jupyter_server/pull/956) ([@akshaychitneni](https://github.com/akshaychitneni))
- \[pre-commit.ci\] pre-commit autoupdate [#955](https://github.com/jupyter-server/jupyter_server/pull/955) ([@pre-commit-ci](https://github.com/pre-commit-ci))
- Fix docs build [#952](https://github.com/jupyter-server/jupyter_server/pull/952) ([@blink1073](https://github.com/blink1073))
- \[pre-commit.ci\] pre-commit autoupdate [#945](https://github.com/jupyter-server/jupyter_server/pull/945) ([@pre-commit-ci](https://github.com/pre-commit-ci))
- \[pre-commit.ci\] pre-commit autoupdate [#942](https://github.com/jupyter-server/jupyter_server/pull/942) ([@pre-commit-ci](https://github.com/pre-commit-ci))
- Fix flake8 v5 compat [#941](https://github.com/jupyter-server/jupyter_server/pull/941) ([@blink1073](https://github.com/blink1073))
- \[pre-commit.ci\] pre-commit autoupdate [#938](https://github.com/jupyter-server/jupyter_server/pull/938) ([@pre-commit-ci](https://github.com/pre-commit-ci))
- \[pre-commit.ci\] pre-commit autoupdate [#928](https://github.com/jupyter-server/jupyter_server/pull/928) ([@pre-commit-ci](https://github.com/pre-commit-ci))

### Documentation improvements

- Fix typo in IdentityProvider documentation [#915](https://github.com/jupyter-server/jupyter_server/pull/915) ([@danielyahn](https://github.com/danielyahn))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2022-07-14&to=2022-09-01&type=c))

[@akshaychitneni](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aakshaychitneni+updated%3A2022-07-14..2022-09-01&type=Issues) | [@blink1073](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ablink1073+updated%3A2022-07-14..2022-09-01&type=Issues) | [@codecov-commenter](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Acodecov-commenter+updated%3A2022-07-14..2022-09-01&type=Issues) | [@danielyahn](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Adanielyahn+updated%3A2022-07-14..2022-09-01&type=Issues) | [@davidbrochart](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Adavidbrochart+updated%3A2022-07-14..2022-09-01&type=Issues) | [@dlqqq](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Adlqqq+updated%3A2022-07-14..2022-09-01&type=Issues) | [@hbcarlos](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ahbcarlos+updated%3A2022-07-14..2022-09-01&type=Issues) | [@kevin-bates](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Akevin-bates+updated%3A2022-07-14..2022-09-01&type=Issues) | [@kiersten-stokes](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Akiersten-stokes+updated%3A2022-07-14..2022-09-01&type=Issues) | [@meeseeksdev](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ameeseeksdev+updated%3A2022-07-14..2022-09-01&type=Issues) | [@minrk](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aminrk+updated%3A2022-07-14..2022-09-01&type=Issues) | [@pre-commit-ci](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Apre-commit-ci+updated%3A2022-07-14..2022-09-01&type=Issues) | [@thetorpedodog](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Athetorpedodog+updated%3A2022-07-14..2022-09-01&type=Issues) | [@vidartf](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Avidartf+updated%3A2022-07-14..2022-09-01&type=Issues) | [@welcome](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Awelcome+updated%3A2022-07-14..2022-09-01&type=Issues) | [@Zsailer](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3AZsailer+updated%3A2022-07-14..2022-09-01&type=Issues)

## 2.0.0b0

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/v2.0.0a2...cb9c5edff77c2146d0e66425a82c7b6125b5039e))

### Enhancements made

- Make it easier for extensions to customize the ServerApp [#879](https://github.com/jupyter-server/jupyter_server/pull/879) ([@minrk](https://github.com/minrk))
- consolidate auth config on IdentityProvider [#825](https://github.com/jupyter-server/jupyter_server/pull/825) ([@minrk](https://github.com/minrk))

### Bugs fixed

- Fix c.GatewayClient.url snippet syntax [#917](https://github.com/jupyter-server/jupyter_server/pull/917) ([@rickwierenga](https://github.com/rickwierenga))
- Add back support for kernel launch timeout pad [#910](https://github.com/jupyter-server/jupyter_server/pull/910) ([@CiprianAnton](https://github.com/CiprianAnton))

### Maintenance and upkeep improvements

- Improve logging of bare exceptions and other cleanups. [#922](https://github.com/jupyter-server/jupyter_server/pull/922) ([@thetorpedodog](https://github.com/thetorpedodog))
- Use more explicit version template for pyproject [#919](https://github.com/jupyter-server/jupyter_server/pull/919) ([@blink1073](https://github.com/blink1073))
- \[pre-commit.ci\] pre-commit autoupdate [#916](https://github.com/jupyter-server/jupyter_server/pull/916) ([@pre-commit-ci](https://github.com/pre-commit-ci))
- Fix handling of dev version [#913](https://github.com/jupyter-server/jupyter_server/pull/913) ([@blink1073](https://github.com/blink1073))
- Fix owasp link [#908](https://github.com/jupyter-server/jupyter_server/pull/908) ([@blink1073](https://github.com/blink1073))
- default to system node version in precommit [#906](https://github.com/jupyter-server/jupyter_server/pull/906) ([@dlqqq](https://github.com/dlqqq))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2022-07-05&to=2022-07-14&type=c))

[@blink1073](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ablink1073+updated%3A2022-07-05..2022-07-14&type=Issues) | [@CiprianAnton](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3ACiprianAnton+updated%3A2022-07-05..2022-07-14&type=Issues) | [@codecov-commenter](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Acodecov-commenter+updated%3A2022-07-05..2022-07-14&type=Issues) | [@dlqqq](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Adlqqq+updated%3A2022-07-05..2022-07-14&type=Issues) | [@minrk](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aminrk+updated%3A2022-07-05..2022-07-14&type=Issues) | [@pre-commit-ci](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Apre-commit-ci+updated%3A2022-07-05..2022-07-14&type=Issues) | [@rickwierenga](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Arickwierenga+updated%3A2022-07-05..2022-07-14&type=Issues) | [@thetorpedodog](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Athetorpedodog+updated%3A2022-07-05..2022-07-14&type=Issues) | [@welcome](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Awelcome+updated%3A2022-07-05..2022-07-14&type=Issues) | [@Zsailer](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3AZsailer+updated%3A2022-07-05..2022-07-14&type=Issues)

## 2.0.0a2

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/v2.0.0a1...bd1e7d70b64716097c6b064b2fd5dc67e23d2320))

### Enhancements made

- Show import error when faiing to load an extension [#878](https://github.com/jupyter-server/jupyter_server/pull/878) ([@minrk](https://github.com/minrk))

### Bugs fixed

- Notify ChannelQueue that the response router thread is finishing [#896](https://github.com/jupyter-server/jupyter_server/pull/896) ([@CiprianAnton](https://github.com/CiprianAnton))
- Make ChannelQueue.get_msg true async [#892](https://github.com/jupyter-server/jupyter_server/pull/892) ([@CiprianAnton](https://github.com/CiprianAnton))
- Fix gateway kernel shutdown [#874](https://github.com/jupyter-server/jupyter_server/pull/874) ([@kevin-bates](https://github.com/kevin-bates))

### Maintenance and upkeep improvements

- \[pre-commit.ci\] pre-commit autoupdate [#902](https://github.com/jupyter-server/jupyter_server/pull/902) ([@pre-commit-ci](https://github.com/pre-commit-ci))
- \[pre-commit.ci\] pre-commit autoupdate [#894](https://github.com/jupyter-server/jupyter_server/pull/894) ([@pre-commit-ci](https://github.com/pre-commit-ci))
- Normalize os_path [#886](https://github.com/jupyter-server/jupyter_server/pull/886) ([@martinRenou](https://github.com/martinRenou))
- \[pre-commit.ci\] pre-commit autoupdate [#885](https://github.com/jupyter-server/jupyter_server/pull/885) ([@pre-commit-ci](https://github.com/pre-commit-ci))
- suppress tornado deprecation warnings [#882](https://github.com/jupyter-server/jupyter_server/pull/882) ([@minrk](https://github.com/minrk))
- Fix lint [#867](https://github.com/jupyter-server/jupyter_server/pull/867) ([@blink1073](https://github.com/blink1073))
- \[pre-commit.ci\] pre-commit autoupdate [#866](https://github.com/jupyter-server/jupyter_server/pull/866) ([@pre-commit-ci](https://github.com/pre-commit-ci))
- Fix sphinx 5.0 support [#865](https://github.com/jupyter-server/jupyter_server/pull/865) ([@blink1073](https://github.com/blink1073))

### Documentation improvements

- Add changelog for 2.0.0a1 [#870](https://github.com/jupyter-server/jupyter_server/pull/870) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2022-06-07&to=2022-07-05&type=c))

[@blink1073](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ablink1073+updated%3A2022-06-07..2022-07-05&type=Issues) | [@Carreau](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3ACarreau+updated%3A2022-06-07..2022-07-05&type=Issues) | [@CiprianAnton](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3ACiprianAnton+updated%3A2022-06-07..2022-07-05&type=Issues) | [@codecov-commenter](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Acodecov-commenter+updated%3A2022-06-07..2022-07-05&type=Issues) | [@davidbrochart](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Adavidbrochart+updated%3A2022-06-07..2022-07-05&type=Issues) | [@echarles](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aecharles+updated%3A2022-06-07..2022-07-05&type=Issues) | [@kevin-bates](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Akevin-bates+updated%3A2022-06-07..2022-07-05&type=Issues) | [@martinRenou](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3AmartinRenou+updated%3A2022-06-07..2022-07-05&type=Issues) | [@minrk](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aminrk+updated%3A2022-06-07..2022-07-05&type=Issues) | [@pre-commit-ci](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Apre-commit-ci+updated%3A2022-06-07..2022-07-05&type=Issues)

## 2.0.0a1

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/v2.0.0a0...v2.0.0a1)

- Address security advisory [GHSA-q874-g24w-4q9g](https://github.com/jupyter-server/jupyter_server/security/advisories/GHSA-q874-g24w-4q9g).

## 2.0.0a0

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/v1.16.0...3e64fa5eef7fba9f8e17c30cec688254adf913bd))

### New features added

- Identity API at /api/me [#671](https://github.com/jupyter-server/jupyter_server/pull/671) ([@minrk](https://github.com/minrk))

### Enhancements made

- Add the root_dir value to the logging message in case of non compliant preferred_dir [#804](https://github.com/jupyter-server/jupyter_server/pull/804) ([@echarles](https://github.com/echarles))
- Hydrate a Kernel Manager when calling GatewayKernelManager.start_kernel with a kernel_id [#788](https://github.com/jupyter-server/jupyter_server/pull/788) ([@Zsailer](https://github.com/Zsailer))
- Remove terminals in favor of jupyter_server_terminals extension [#651](https://github.com/jupyter-server/jupyter_server/pull/651) ([@Zsailer](https://github.com/Zsailer))

### Bugs fixed

- Defer preferred_dir validation until root_dir is set [#826](https://github.com/jupyter-server/jupyter_server/pull/826) ([@kevin-bates](https://github.com/kevin-bates))
- missing required arguments in utils.fetch [#798](https://github.com/jupyter-server/jupyter_server/pull/798) ([@minrk](https://github.com/minrk))

### Maintenance and upkeep improvements

- Add license metadata and file [#827](https://github.com/jupyter-server/jupyter_server/pull/827) ([@blink1073](https://github.com/blink1073))
- CI cleanup [#824](https://github.com/jupyter-server/jupyter_server/pull/824) ([@blink1073](https://github.com/blink1073))
- Switch to flit [#823](https://github.com/jupyter-server/jupyter_server/pull/823) ([@blink1073](https://github.com/blink1073))
- Remove unused pytest-mock dependency [#814](https://github.com/jupyter-server/jupyter_server/pull/814) ([@mgorny](https://github.com/mgorny))
- Remove duplicate requests requirement from setup.cfg [#813](https://github.com/jupyter-server/jupyter_server/pull/813) ([@mgorny](https://github.com/mgorny))
- \[pre-commit.ci\] pre-commit autoupdate [#802](https://github.com/jupyter-server/jupyter_server/pull/802) ([@pre-commit-ci](https://github.com/pre-commit-ci))
- Add helper jobs for branch protection [#797](https://github.com/jupyter-server/jupyter_server/pull/797) ([@blink1073](https://github.com/blink1073))
- \[pre-commit.ci\] pre-commit autoupdate [#793](https://github.com/jupyter-server/jupyter_server/pull/793) ([@pre-commit-ci](https://github.com/pre-commit-ci))
- Centralize app cleanup [#792](https://github.com/jupyter-server/jupyter_server/pull/792) ([@blink1073](https://github.com/blink1073))
- \[pre-commit.ci\] pre-commit autoupdate [#785](https://github.com/jupyter-server/jupyter_server/pull/785) ([@pre-commit-ci](https://github.com/pre-commit-ci))
- Clean up pre-commit [#782](https://github.com/jupyter-server/jupyter_server/pull/782) ([@blink1073](https://github.com/blink1073))
- Add mypy check [#779](https://github.com/jupyter-server/jupyter_server/pull/779) ([@blink1073](https://github.com/blink1073))
- Use new post-version-spec from jupyter_releaser [#777](https://github.com/jupyter-server/jupyter_server/pull/777) ([@blink1073](https://github.com/blink1073))
- Give write permissions to enforce label workflow [#776](https://github.com/jupyter-server/jupyter_server/pull/776) ([@blink1073](https://github.com/blink1073))
- \[pre-commit.ci\] pre-commit autoupdate [#775](https://github.com/jupyter-server/jupyter_server/pull/775) ([@pre-commit-ci](https://github.com/pre-commit-ci))
- Add explicit handling of warnings [#771](https://github.com/jupyter-server/jupyter_server/pull/771) ([@blink1073](https://github.com/blink1073))
- Use test-sdist from maintainer-tools [#769](https://github.com/jupyter-server/jupyter_server/pull/769) ([@blink1073](https://github.com/blink1073))
- Add pyupgrade and doc8 hooks [#768](https://github.com/jupyter-server/jupyter_server/pull/768) ([@blink1073](https://github.com/blink1073))
- update some metadata fields, sort deps [#675](https://github.com/jupyter-server/jupyter_server/pull/675) ([@bollwyvl](https://github.com/bollwyvl))

### Documentation improvements

- Add Session workflows documentation [#808](https://github.com/jupyter-server/jupyter_server/pull/808) ([@andreyvelich](https://github.com/andreyvelich))
- Add Jupyter Server Architecture diagram [#801](https://github.com/jupyter-server/jupyter_server/pull/801) ([@andreyvelich](https://github.com/andreyvelich))
- Fix path for full config doc [#800](https://github.com/jupyter-server/jupyter_server/pull/800) ([@andreyvelich](https://github.com/andreyvelich))
- Fix contributing guide for building the docs [#794](https://github.com/jupyter-server/jupyter_server/pull/794) ([@andreyvelich](https://github.com/andreyvelich))
- Update team meetings doc [#772](https://github.com/jupyter-server/jupyter_server/pull/772) ([@willingc](https://github.com/willingc))
- Update documentation about registering file save hooks [#770](https://github.com/jupyter-server/jupyter_server/pull/770) ([@davidbrochart](https://github.com/davidbrochart))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2022-03-29&to=2022-05-03&type=c))

[@andreyvelich](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aandreyvelich+updated%3A2022-03-29..2022-05-03&type=Issues) | [@blink1073](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ablink1073+updated%3A2022-03-29..2022-05-03&type=Issues) | [@bollwyvl](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Abollwyvl+updated%3A2022-03-29..2022-05-03&type=Issues) | [@codecov-commenter](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Acodecov-commenter+updated%3A2022-03-29..2022-05-03&type=Issues) | [@davidbrochart](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Adavidbrochart+updated%3A2022-03-29..2022-05-03&type=Issues) | [@echarles](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aecharles+updated%3A2022-03-29..2022-05-03&type=Issues) | [@hbcarlos](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ahbcarlos+updated%3A2022-03-29..2022-05-03&type=Issues) | [@kevin-bates](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Akevin-bates+updated%3A2022-03-29..2022-05-03&type=Issues) | [@meeseeksdev](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ameeseeksdev+updated%3A2022-03-29..2022-05-03&type=Issues) | [@mgorny](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Amgorny+updated%3A2022-03-29..2022-05-03&type=Issues) | [@minrk](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aminrk+updated%3A2022-03-29..2022-05-03&type=Issues) | [@pre-commit-ci](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Apre-commit-ci+updated%3A2022-03-29..2022-05-03&type=Issues) | [@SylvainCorlay](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3ASylvainCorlay+updated%3A2022-03-29..2022-05-03&type=Issues) | [@welcome](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Awelcome+updated%3A2022-03-29..2022-05-03&type=Issues) | [@Wh1isper](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3AWh1isper+updated%3A2022-03-29..2022-05-03&type=Issues) | [@willingc](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Awillingc+updated%3A2022-03-29..2022-05-03&type=Issues) | [@Zsailer](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3AZsailer+updated%3A2022-03-29..2022-05-03&type=Issues)

## 1.17.0

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/v1.16.0...2b296099777d50aa86f67faf94d5cbfde906b169))

### Enhancements made

- Add the root_dir value to the logging message in case of non compliant preferred_dir [#804](https://github.com/jupyter-server/jupyter_server/pull/804) ([@echarles](https://github.com/echarles))

### Bugs fixed

- missing required arguments in utils.fetch [#798](https://github.com/jupyter-server/jupyter_server/pull/798) ([@minrk](https://github.com/minrk))

### Maintenance and upkeep improvements

- Add helper jobs for branch protection [#797](https://github.com/jupyter-server/jupyter_server/pull/797) ([@blink1073](https://github.com/blink1073))
- \[pre-commit.ci\] pre-commit autoupdate [#793](https://github.com/jupyter-server/jupyter_server/pull/793) ([@pre-commit-ci\[bot\]](https://github.com/apps/pre-commit-ci))
- Update branch references and links [#791](https://github.com/jupyter-server/jupyter_server/pull/791) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2022-03-29&to=2022-04-27&type=c))

[@blink1073](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ablink1073+updated%3A2022-03-29..2022-04-27&type=Issues) | [@codecov-commenter](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Acodecov-commenter+updated%3A2022-03-29..2022-04-27&type=Issues) | [@davidbrochart](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Adavidbrochart+updated%3A2022-03-29..2022-04-27&type=Issues) | [@echarles](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aecharles+updated%3A2022-03-29..2022-04-27&type=Issues) | [@kevin-bates](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Akevin-bates+updated%3A2022-03-29..2022-04-27&type=Issues) | [@meeseeksdev](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ameeseeksdev+updated%3A2022-03-29..2022-04-27&type=Issues) | [@meeseeksmachine](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ameeseeksmachine+updated%3A2022-03-29..2022-04-27&type=Issues) | [@Wh1isper](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3AWh1isper+updated%3A2022-03-29..2022-04-27&type=Issues) | [@Zsailer](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3AZsailer+updated%3A2022-03-29..2022-04-27&type=Issues)

## 1.16.0

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/v1.15.6...d32b887ae2c3b77fe3ae67ba79c3d3c6713c0d8a))

### New features added

- add hook to observe pending sessions [#751](https://github.com/jupyter-server/jupyter_server/pull/751) ([@Zsailer](https://github.com/Zsailer))

### Enhancements made

- Add `max-age` Cache-Control header to kernel logos [#760](https://github.com/jupyter-server/jupyter_server/pull/760) ([@divyansshhh](https://github.com/divyansshhh))

### Bugs fixed

- Regression in connection URL calcuation in ServerApp [#761](https://github.com/jupyter-server/jupyter_server/pull/761) ([@jhamet93](https://github.com/jhamet93))
- Include explicit package data [#757](https://github.com/jupyter-server/jupyter_server/pull/757) ([@blink1073](https://github.com/blink1073))
- Ensure terminal cwd exists [#755](https://github.com/jupyter-server/jupyter_server/pull/755) ([@fcollonval](https://github.com/fcollonval))
- make 'cwd' param for TerminalManager absolute [#749](https://github.com/jupyter-server/jupyter_server/pull/749) ([@rccern](https://github.com/rccern))
- wait to cleanup kernels after kernel is finished pending [#748](https://github.com/jupyter-server/jupyter_server/pull/748) ([@Zsailer](https://github.com/Zsailer))

### Maintenance and upkeep improvements

- Skip jsonschema in CI [#766](https://github.com/jupyter-server/jupyter_server/pull/766) ([@blink1073](https://github.com/blink1073))
- Remove redundant job and problematic check [#765](https://github.com/jupyter-server/jupyter_server/pull/765) ([@blink1073](https://github.com/blink1073))
- Update pre-commit [#764](https://github.com/jupyter-server/jupyter_server/pull/764) ([@blink1073](https://github.com/blink1073))
- Install pre-commit automatically [#763](https://github.com/jupyter-server/jupyter_server/pull/763) ([@blink1073](https://github.com/blink1073))
- Add pytest opts and use isort [#762](https://github.com/jupyter-server/jupyter_server/pull/762) ([@blink1073](https://github.com/blink1073))
- Ensure minimal nbconvert support jinja2 v2 & v3 [#756](https://github.com/jupyter-server/jupyter_server/pull/756) ([@fcollonval](https://github.com/fcollonval))
- Fix error handler in simple extension examples [#750](https://github.com/jupyter-server/jupyter_server/pull/750) ([@andreyvelich](https://github.com/andreyvelich))
- Clean up workflows [#747](https://github.com/jupyter-server/jupyter_server/pull/747) ([@blink1073](https://github.com/blink1073))
- Remove Redundant Dir_Exists Invocation When Creating New Files with ContentsManager [#720](https://github.com/jupyter-server/jupyter_server/pull/720) ([@jhamet93](https://github.com/jhamet93))

### Other merged PRs

- Handle importstring pre/post save hooks [#754](https://github.com/jupyter-server/jupyter_server/pull/754) ([@dleen](https://github.com/dleen))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2022-03-16&to=2022-03-29&type=c))

[@andreyvelich](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aandreyvelich+updated%3A2022-03-16..2022-03-29&type=Issues) | [@blink1073](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ablink1073+updated%3A2022-03-16..2022-03-29&type=Issues) | [@codecov-commenter](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Acodecov-commenter+updated%3A2022-03-16..2022-03-29&type=Issues) | [@divyansshhh](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Adivyansshhh+updated%3A2022-03-16..2022-03-29&type=Issues) | [@dleen](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Adleen+updated%3A2022-03-16..2022-03-29&type=Issues) | [@fcollonval](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Afcollonval+updated%3A2022-03-16..2022-03-29&type=Issues) | [@jhamet93](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ajhamet93+updated%3A2022-03-16..2022-03-29&type=Issues) | [@meeseeksdev](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ameeseeksdev+updated%3A2022-03-16..2022-03-29&type=Issues) | [@minrk](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aminrk+updated%3A2022-03-16..2022-03-29&type=Issues) | [@rccern](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Arccern+updated%3A2022-03-16..2022-03-29&type=Issues) | [@welcome](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Awelcome+updated%3A2022-03-16..2022-03-29&type=Issues) | [@Zsailer](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3AZsailer+updated%3A2022-03-16..2022-03-29&type=Issues)

## 1.15.6

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/v1.15.5...7fbaa767c71302cc756bdf1fb11fcbf1b3768dcc))

### Bugs fixed

- Missing warning when no authorizer in found ZMQ handlers [#744](https://github.com/jupyter-server/jupyter_server/pull/744) ([@Zsailer](https://github.com/Zsailer))

### Maintenance and upkeep improvements

- More CI Cleanup [#742](https://github.com/jupyter-server/jupyter_server/pull/742) ([@blink1073](https://github.com/blink1073))
- Clean up downstream tests [#741](https://github.com/jupyter-server/jupyter_server/pull/741) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2022-03-16&to=2022-03-16&type=c))

[@blink1073](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ablink1073+updated%3A2022-03-16..2022-03-16&type=Issues) | [@codecov-commenter](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Acodecov-commenter+updated%3A2022-03-16..2022-03-16&type=Issues) | [@Zsailer](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3AZsailer+updated%3A2022-03-16..2022-03-16&type=Issues)

## 1.15.5

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/v1.15.4...67f6140ebca60bfde0fb068f10b428320c6c67cd))

### Bugs fixed

- Relax type checking on ExtensionApp.serverapp [#739](https://github.com/jupyter-server/jupyter_server/pull/739) ([@minrk](https://github.com/minrk))
- raise no-authorization warning once and allow disabled authorization [#738](https://github.com/jupyter-server/jupyter_server/pull/738) ([@Zsailer](https://github.com/Zsailer))

### Maintenance and upkeep improvements

- Fix sdist test [#736](https://github.com/jupyter-server/jupyter_server/pull/736) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2022-03-15&to=2022-03-16&type=c))

[@blink1073](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ablink1073+updated%3A2022-03-15..2022-03-16&type=Issues) | [@codecov-commenter](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Acodecov-commenter+updated%3A2022-03-15..2022-03-16&type=Issues) | [@minrk](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aminrk+updated%3A2022-03-15..2022-03-16&type=Issues) | [@Zsailer](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3AZsailer+updated%3A2022-03-15..2022-03-16&type=Issues)

## 1.15.3

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/v1.15.2...461b55146888b58a84c6cfc70c9bbfdb3e8d6aba))

### Bugs fixed

- Fix server-extension paths (3rd time's the charm) [#734](https://github.com/jupyter-server/jupyter_server/pull/734) ([@minrk](https://github.com/minrk))
- Revert "Server extension paths (#730)" [#732](https://github.com/jupyter-server/jupyter_server/pull/732) ([@blink1073](https://github.com/blink1073))

### Maintenance and upkeep improvements

- Avoid usage of ipython_genutils [#718](https://github.com/jupyter-server/jupyter_server/pull/718) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2022-03-14&to=2022-03-14&type=c))

[@blink1073](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ablink1073+updated%3A2022-03-14..2022-03-14&type=Issues) | [@codecov-commenter](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Acodecov-commenter+updated%3A2022-03-14..2022-03-14&type=Issues) | [@minrk](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aminrk+updated%3A2022-03-14..2022-03-14&type=Issues)

## 1.15.2

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/v1.15.1...9711822e157bd2ff2d4f8abe4c12a013223230e0))

### Bugs fixed

- Server extension paths [#730](https://github.com/jupyter-server/jupyter_server/pull/730) ([@minrk](https://github.com/minrk))
- allow handlers to work without an authorizer in the Tornado settings [#717](https://github.com/jupyter-server/jupyter_server/pull/717) ([@Zsailer](https://github.com/Zsailer))

### Maintenance and upkeep improvements

- Skip nbclassic downstream tests for now [#725](https://github.com/jupyter-server/jupyter_server/pull/725) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2022-03-14&to=2022-03-14&type=c))

[@blink1073](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ablink1073+updated%3A2022-03-14..2022-03-14&type=Issues) | [@minrk](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aminrk+updated%3A2022-03-14..2022-03-14&type=Issues) | [@Zsailer](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3AZsailer+updated%3A2022-03-14..2022-03-14&type=Issues)

## 1.15.1

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/v1.15.0...262cb46b95de2443c8552d80d6adade6bde5734b))

### Bugs fixed

- Revert "Re-use ServerApp.config_file_paths for consistency (#715)" [#728](https://github.com/jupyter-server/jupyter_server/pull/728) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2022-03-14&to=2022-03-14&type=c))

[@blink1073](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ablink1073+updated%3A2022-03-14..2022-03-14&type=Issues)

## 1.15.0

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/v1.13.5...6e0e49e720ee6626b5233df716b0fdb891b79793))

### New features added

- Add authorization layer to server request handlers [#165](https://github.com/jupyter-server/jupyter_server/pull/165) ([@Zsailer](https://github.com/Zsailer))

### Enhancements made

- Validate notebooks once per fetch or save [#724](https://github.com/jupyter-server/jupyter_server/pull/724) ([@kevin-bates](https://github.com/kevin-bates))
- Register pre/post save hooks, call them sequentially [#696](https://github.com/jupyter-server/jupyter_server/pull/696) ([@davidbrochart](https://github.com/davidbrochart))

### Bugs fixed

- Implement Required Methods in Async Manner [#721](https://github.com/jupyter-server/jupyter_server/pull/721) ([@jhamet93](https://github.com/jhamet93))
- Call pre_save_hook only on first chunk of large files [#716](https://github.com/jupyter-server/jupyter_server/pull/716) ([@davidbrochart](https://github.com/davidbrochart))
- Re-use ServerApp.config_file_paths for consistency [#715](https://github.com/jupyter-server/jupyter_server/pull/715) ([@minrk](https://github.com/minrk))
- serverapp: Use .absolute() instead of .resolve() for symlinks [#712](https://github.com/jupyter-server/jupyter_server/pull/712) ([@EricCousineau-TRI](https://github.com/EricCousineau-TRI))
- Fall back to legacy protocol if selected_subprotocol raises exception [#706](https://github.com/jupyter-server/jupyter_server/pull/706) ([@davidbrochart](https://github.com/davidbrochart))
- Fix FilesHandler not meet RFC 6713 [#701](https://github.com/jupyter-server/jupyter_server/pull/701) ([@Wh1isper](https://github.com/Wh1isper))

### Maintenance and upkeep improvements

- Clean up CI [#723](https://github.com/jupyter-server/jupyter_server/pull/723) ([@blink1073](https://github.com/blink1073))
- Clean up activity recording [#722](https://github.com/jupyter-server/jupyter_server/pull/722) ([@blink1073](https://github.com/blink1073))
- Clean up Dependency Handling [#707](https://github.com/jupyter-server/jupyter_server/pull/707) ([@blink1073](https://github.com/blink1073))
- Add Minimum Requirements Test [#704](https://github.com/jupyter-server/jupyter_server/pull/704) ([@blink1073](https://github.com/blink1073))
- Clean up handling of tests [#700](https://github.com/jupyter-server/jupyter_server/pull/700) ([@blink1073](https://github.com/blink1073))
- Refresh precommit [#698](https://github.com/jupyter-server/jupyter_server/pull/698) ([@blink1073](https://github.com/blink1073))
- Use pytest-github-actions-annotate-failures [#694](https://github.com/jupyter-server/jupyter_server/pull/694) ([@blink1073](https://github.com/blink1073))

### Documentation improvements

- Add WebSocket wire protocol documentation [#693](https://github.com/jupyter-server/jupyter_server/pull/693) ([@davidbrochart](https://github.com/davidbrochart))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2022-02-05&to=2022-03-14&type=c))

[@blink1073](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ablink1073+updated%3A2022-02-05..2022-03-14&type=Issues) | [@codecov-commenter](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Acodecov-commenter+updated%3A2022-02-05..2022-03-14&type=Issues) | [@davidbrochart](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Adavidbrochart+updated%3A2022-02-05..2022-03-14&type=Issues) | [@echarles](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aecharles+updated%3A2022-02-05..2022-03-14&type=Issues) | [@EricCousineau-TRI](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3AEricCousineau-TRI+updated%3A2022-02-05..2022-03-14&type=Issues) | [@jhamet93](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ajhamet93+updated%3A2022-02-05..2022-03-14&type=Issues) | [@kevin-bates](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Akevin-bates+updated%3A2022-02-05..2022-03-14&type=Issues) | [@minrk](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aminrk+updated%3A2022-02-05..2022-03-14&type=Issues) | [@vidartf](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Avidartf+updated%3A2022-02-05..2022-03-14&type=Issues) | [@welcome](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Awelcome+updated%3A2022-02-05..2022-03-14&type=Issues) | [@Wh1isper](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3AWh1isper+updated%3A2022-02-05..2022-03-14&type=Issues) | [@Zsailer](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3AZsailer+updated%3A2022-02-05..2022-03-14&type=Issues)

## 1.13.5

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/v1.13.4...cbc54fa3a99abdf1d2a8b5e35d33a74dd524d905))

### Enhancements made

- Protocol alignment [#657](https://github.com/jupyter-server/jupyter_server/pull/657) ([@davidbrochart](https://github.com/davidbrochart))

### Bugs fixed

- Fix to remove potential memory leak on Jupyter Server ZMQChannelHandler code [#682](https://github.com/jupyter-server/jupyter_server/pull/682) ([@Vishwajeet0510](https://github.com/Vishwajeet0510))
- Pin pywintpy for now [#681](https://github.com/jupyter-server/jupyter_server/pull/681) ([@blink1073](https://github.com/blink1073))
- Fix the non-writable path deletion error [#670](https://github.com/jupyter-server/jupyter_server/pull/670) ([@vkaidalov](https://github.com/vkaidalov))
- make unit tests backwards compatible without pending kernels [#669](https://github.com/jupyter-server/jupyter_server/pull/669) ([@Zsailer](https://github.com/Zsailer))

### Maintenance and upkeep improvements

- Clean up full install test [#689](https://github.com/jupyter-server/jupyter_server/pull/689) ([@blink1073](https://github.com/blink1073))
- Update trigger_precommit.yml [#687](https://github.com/jupyter-server/jupyter_server/pull/687) ([@blink1073](https://github.com/blink1073))
- Add Auto Pre-Commit [#685](https://github.com/jupyter-server/jupyter_server/pull/685) ([@blink1073](https://github.com/blink1073))
- Fix a typo [#683](https://github.com/jupyter-server/jupyter_server/pull/683) ([@krassowski](https://github.com/krassowski))
- (temporarily) skip pending kernels unit tests on Windows CI [#673](https://github.com/jupyter-server/jupyter_server/pull/673) ([@Zsailer](https://github.com/Zsailer))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2022-01-21&to=2022-02-05&type=c))

[@blink1073](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ablink1073+updated%3A2022-01-21..2022-02-05&type=Issues) | [@codecov-commenter](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Acodecov-commenter+updated%3A2022-01-21..2022-02-05&type=Issues) | [@davidbrochart](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Adavidbrochart+updated%3A2022-01-21..2022-02-05&type=Issues) | [@echarles](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aecharles+updated%3A2022-01-21..2022-02-05&type=Issues) | [@github-actions](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Agithub-actions+updated%3A2022-01-21..2022-02-05&type=Issues) | [@jasongrout](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ajasongrout+updated%3A2022-01-21..2022-02-05&type=Issues) | [@krassowski](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Akrassowski+updated%3A2022-01-21..2022-02-05&type=Issues) | [@maartenbreddels](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Amaartenbreddels+updated%3A2022-01-21..2022-02-05&type=Issues) | [@SylvainCorlay](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3ASylvainCorlay+updated%3A2022-01-21..2022-02-05&type=Issues) | [@Vishwajeet0510](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3AVishwajeet0510+updated%3A2022-01-21..2022-02-05&type=Issues) | [@vkaidalov](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Avkaidalov+updated%3A2022-01-21..2022-02-05&type=Issues) | [@welcome](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Awelcome+updated%3A2022-01-21..2022-02-05&type=Issues) | [@Wh1isper](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3AWh1isper+updated%3A2022-01-21..2022-02-05&type=Issues) | [@Zsailer](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3AZsailer+updated%3A2022-01-21..2022-02-05&type=Issues)

## 1.13.4

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/v1.13.3...d2015290b80bfdaa6ebb990cdccc0155921696f5))

### Bugs fixed

- Fix nbconvert handler run_sync() [#667](https://github.com/jupyter-server/jupyter_server/pull/667) ([@davidbrochart](https://github.com/davidbrochart))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2022-01-14&to=2022-01-21&type=c))

[@codecov-commenter](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Acodecov-commenter+updated%3A2022-01-14..2022-01-21&type=Issues) | [@davidbrochart](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Adavidbrochart+updated%3A2022-01-14..2022-01-21&type=Issues) | [@Zsailer](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3AZsailer+updated%3A2022-01-14..2022-01-21&type=Issues)

## 1.13.3

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/v1.13.2...ee01e1955c8881b46075c78f1fbc932fa234bc72))

### Enhancements made

- More updates to unit tests for pending kernels work [#662](https://github.com/jupyter-server/jupyter_server/pull/662) ([@Zsailer](https://github.com/Zsailer))

### Bugs fixed

- bump traitlets dependency [#663](https://github.com/jupyter-server/jupyter_server/pull/663) ([@Zsailer](https://github.com/Zsailer))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2022-01-12&to=2022-01-14&type=c))

[@Zsailer](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3AZsailer+updated%3A2022-01-12..2022-01-14&type=Issues)

## 1.13.2

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/v1.13.1...362d100ff24c1da7ef4cbd171c213e9570e8c289))

### Enhancements made

- Don't block the event loop when exporting with nbconvert [#655](https://github.com/jupyter-server/jupyter_server/pull/655) ([@davidbrochart](https://github.com/davidbrochart))
- Add more awaits for pending kernel in unit tests [#654](https://github.com/jupyter-server/jupyter_server/pull/654) ([@Zsailer](https://github.com/Zsailer))
- Print IPv6 url as hostname or enclosed in brackets [#652](https://github.com/jupyter-server/jupyter_server/pull/652) ([@op3](https://github.com/op3))

### Bugs fixed

- Run pre_save_hook before model check [#643](https://github.com/jupyter-server/jupyter_server/pull/643) ([@davidbrochart](https://github.com/davidbrochart))
- handle KeyError when get session [#641](https://github.com/jupyter-server/jupyter_server/pull/641) ([@ccw630](https://github.com/ccw630))

### Maintenance and upkeep improvements

- Clean up deprecations [#650](https://github.com/jupyter-server/jupyter_server/pull/650) ([@blink1073](https://github.com/blink1073))
- Update branch references [#646](https://github.com/jupyter-server/jupyter_server/pull/646) ([@blink1073](https://github.com/blink1073))
- pyproject.toml: clarify build system version [#634](https://github.com/jupyter-server/jupyter_server/pull/634) ([@adamjstewart](https://github.com/adamjstewart))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2021-12-09&to=2022-01-12&type=c))

[@adamjstewart](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aadamjstewart+updated%3A2021-12-09..2022-01-12&type=Issues) | [@blink1073](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ablink1073+updated%3A2021-12-09..2022-01-12&type=Issues) | [@ccw630](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Accw630+updated%3A2021-12-09..2022-01-12&type=Issues) | [@codecov-commenter](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Acodecov-commenter+updated%3A2021-12-09..2022-01-12&type=Issues) | [@davidbrochart](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Adavidbrochart+updated%3A2021-12-09..2022-01-12&type=Issues) | [@echarles](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aecharles+updated%3A2021-12-09..2022-01-12&type=Issues) | [@fcollonval](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Afcollonval+updated%3A2021-12-09..2022-01-12&type=Issues) | [@kevin-bates](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Akevin-bates+updated%3A2021-12-09..2022-01-12&type=Issues) | [@op3](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aop3+updated%3A2021-12-09..2022-01-12&type=Issues) | [@welcome](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Awelcome+updated%3A2021-12-09..2022-01-12&type=Issues) | [@Wh1isper](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3AWh1isper+updated%3A2021-12-09..2022-01-12&type=Issues) | [@Zsailer](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3AZsailer+updated%3A2021-12-09..2022-01-12&type=Issues)

## 1.13.1

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/v1.13.0...affd5d9a2e6d718baa2185518256f51921fd4484))

### Bugs fixed

- nudge both the shell and control channels [#636](https://github.com/jupyter-server/jupyter_server/pull/636) ([@Zsailer](https://github.com/Zsailer))

### Maintenance and upkeep improvements

- Fix macos pypy check [#632](https://github.com/jupyter-server/jupyter_server/pull/632) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2021-12-06&to=2021-12-09&type=c))

[@blink1073](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ablink1073+updated%3A2021-12-06..2021-12-09&type=Issues) | [@codecov-commenter](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Acodecov-commenter+updated%3A2021-12-06..2021-12-09&type=Issues) | [@Zsailer](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3AZsailer+updated%3A2021-12-06..2021-12-09&type=Issues)

## 1.13.0

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/v1.12.1...b51969f16f04375d52cb029d72f90174141c760d))

### Enhancements made

- Persistent session storage [#614](https://github.com/jupyter-server/jupyter_server/pull/614) ([@Zsailer](https://github.com/Zsailer))

### Bugs fixed

- Nudge on the control channel instead of the shell [#628](https://github.com/jupyter-server/jupyter_server/pull/628) ([@JohanMabille](https://github.com/JohanMabille))

### Maintenance and upkeep improvements

- Clean up downstream tests [#629](https://github.com/jupyter-server/jupyter_server/pull/629) ([@blink1073](https://github.com/blink1073))
- Clean up version info handling [#620](https://github.com/jupyter-server/jupyter_server/pull/620) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2021-11-26&to=2021-12-06&type=c))

[@blink1073](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ablink1073+updated%3A2021-11-26..2021-12-06&type=Issues) | [@codecov-commenter](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Acodecov-commenter+updated%3A2021-11-26..2021-12-06&type=Issues) | [@echarles](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aecharles+updated%3A2021-11-26..2021-12-06&type=Issues) | [@JohanMabille](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3AJohanMabille+updated%3A2021-11-26..2021-12-06&type=Issues) | [@jtpio](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ajtpio+updated%3A2021-11-26..2021-12-06&type=Issues) | [@Zsailer](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3AZsailer+updated%3A2021-11-26..2021-12-06&type=Issues)

## 1.12.1

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/v1.12.0...ead83374b3b874bdf4ea47fca5aee1ecb5940a85))

### Bugs fixed

- Await `_finish_kernel_start` [#617](https://github.com/jupyter-server/jupyter_server/pull/617) ([@jtpio](https://github.com/jtpio))

### Maintenance and upkeep improvements

- Update to Python 3.10 in the CI workflows [#618](https://github.com/jupyter-server/jupyter_server/pull/618) ([@jtpio](https://github.com/jtpio))
- Use `maintainer-tools` base setup action [#616](https://github.com/jupyter-server/jupyter_server/pull/616) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2021-11-23&to=2021-11-26&type=c))

[@blink1073](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ablink1073+updated%3A2021-11-23..2021-11-26&type=Issues) | [@codecov-commenter](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Acodecov-commenter+updated%3A2021-11-23..2021-11-26&type=Issues) | [@jtpio](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ajtpio+updated%3A2021-11-23..2021-11-26&type=Issues)

## 1.12.0

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/v1.11.2...758dba6f8873f60c1ca41057b4be108da5a6ff1a))

### Enhancements made

- Consistent logging method [#607](https://github.com/jupyter-server/jupyter_server/pull/607) ([@mwakaba2](https://github.com/mwakaba2))
- Use pending kernels [#593](https://github.com/jupyter-server/jupyter_server/pull/593) ([@blink1073](https://github.com/blink1073))

### Bugs fixed

- Set `xsrf` cookie on base url [#612](https://github.com/jupyter-server/jupyter_server/pull/612) ([@minrk](https://github.com/minrk))
- Update `jpserver_extensions` trait to work with `traitlets` 5.x [#610](https://github.com/jupyter-server/jupyter_server/pull/610) ([@Zsailer](https://github.com/Zsailer))
- Fix `allow_origin_pat` property to properly parse regex [#603](https://github.com/jupyter-server/jupyter_server/pull/603) ([@havok2063](https://github.com/havok2063))

### Maintenance and upkeep improvements

- Enforce labels on PRs [#613](https://github.com/jupyter-server/jupyter_server/pull/613) ([@blink1073](https://github.com/blink1073))
- Normalize file name and path in `test_api` [#608](https://github.com/jupyter-server/jupyter_server/pull/608) ([@toonn](https://github.com/toonn))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2021-11-01&to=2021-11-23&type=c))

[@blink1073](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ablink1073+updated%3A2021-11-01..2021-11-23&type=Issues) | [@codecov-commenter](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Acodecov-commenter+updated%3A2021-11-01..2021-11-23&type=Issues) | [@havok2063](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ahavok2063+updated%3A2021-11-01..2021-11-23&type=Issues) | [@minrk](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aminrk+updated%3A2021-11-01..2021-11-23&type=Issues) | [@mwakaba2](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Amwakaba2+updated%3A2021-11-01..2021-11-23&type=Issues) | [@toonn](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Atoonn+updated%3A2021-11-01..2021-11-23&type=Issues) | [@welcome](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Awelcome+updated%3A2021-11-01..2021-11-23&type=Issues) | [@Zsailer](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3AZsailer+updated%3A2021-11-01..2021-11-23&type=Issues)

## 1.11.2

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/v1.11.1...fda4cc5a96703bb4e871a5a622ef6031c7f6385b))

### Bugs fixed

- Fix \\s deprecation warning [#600](https://github.com/jupyter-server/jupyter_server/pull/600) ([@Zsailer](https://github.com/Zsailer))
- Remove requests-unixsocket dependency [#599](https://github.com/jupyter-server/jupyter_server/pull/599) ([@kevin-bates](https://github.com/kevin-bates))
- bugfix: dir_exists is never awaited [#597](https://github.com/jupyter-server/jupyter_server/pull/597) ([@stdll00](https://github.com/stdll00))
- Fix missing await when call 'async_replace_file' [#595](https://github.com/jupyter-server/jupyter_server/pull/595) ([@Wh1isper](https://github.com/Wh1isper))
- add a pytest fixture for capturing logging stream [#588](https://github.com/jupyter-server/jupyter_server/pull/588) ([@Zsailer](https://github.com/Zsailer))

### Maintenance and upkeep improvements

- Avoid dependency on NBConvert versions for REST API test [#601](https://github.com/jupyter-server/jupyter_server/pull/601) ([@Zsailer](https://github.com/Zsailer))
- Bump ansi-regex from 5.0.0 to 5.0.1 [#590](https://github.com/jupyter-server/jupyter_server/pull/590) ([@dependabot](https://github.com/dependabot))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2021-10-04&to=2021-11-01&type=c))

[@codecov-commenter](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Acodecov-commenter+updated%3A2021-10-04..2021-11-01&type=Issues) | [@dependabot](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Adependabot+updated%3A2021-10-04..2021-11-01&type=Issues) | [@kevin-bates](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Akevin-bates+updated%3A2021-10-04..2021-11-01&type=Issues) | [@stdll00](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Astdll00+updated%3A2021-10-04..2021-11-01&type=Issues) | [@welcome](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Awelcome+updated%3A2021-10-04..2021-11-01&type=Issues) | [@Wh1isper](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3AWh1isper+updated%3A2021-10-04..2021-11-01&type=Issues) | [@Zsailer](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3AZsailer+updated%3A2021-10-04..2021-11-01&type=Issues)

## 1.11.1

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/v1.11.0...f4c3889658c1daad1d8966438d1f1b98b3f60641))

### Bugs fixed

- Do not log connection error if the kernel is already shutdown [#584](https://github.com/jupyter-server/jupyter_server/pull/584) ([@martinRenou](https://github.com/martinRenou))
- \[BUG\]: allow None for min_open_files_limit trait [#587](https://github.com/jupyter-server/jupyter_server/pull/587) ([@Zsailer](https://github.com/Zsailer))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2021-09-09&to=2021-10-04&type=c))

[@codecov-commenter](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Acodecov-commenter+updated%3A2021-09-09..2021-10-04&type=Issues) | [@martinRenou](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3AmartinRenou+updated%3A2021-09-09..2021-10-04&type=Issues) | [@Zsailer](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3AZsailer+updated%3A2021-09-09..2021-10-04&type=Issues)

## 1.11.0

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/v1.10.2...1863fde11af7971d040ad50ad015caa83b6c7d54))

### Enhancements made

- Allow non-empty directory deletion through settings [#574](https://github.com/jupyter-server/jupyter_server/pull/574) ([@fcollonval](https://github.com/fcollonval))

### Bugs fixed

- pytest_plugin: allow user specified headers in jp_ws_fetch [#580](https://github.com/jupyter-server/jupyter_server/pull/580) ([@oliver-sanders](https://github.com/oliver-sanders))
- Shutdown kernels/terminals on api/shutdown [#579](https://github.com/jupyter-server/jupyter_server/pull/579) ([@martinRenou](https://github.com/martinRenou))
- pytest: package conftest [#576](https://github.com/jupyter-server/jupyter_server/pull/576) ([@oliver-sanders](https://github.com/oliver-sanders))
- Set stacklevel on warning to point to the right place. [#572](https://github.com/jupyter-server/jupyter_server/pull/572) ([@Carreau](https://github.com/Carreau))
- Respect reraise setting [#571](https://github.com/jupyter-server/jupyter_server/pull/571) ([@vidartf](https://github.com/vidartf))

### Maintenance and upkeep improvements

- Fix jupyter_client warning [#581](https://github.com/jupyter-server/jupyter_server/pull/581) ([@martinRenou](https://github.com/martinRenou))
- Add Pre-Commit Config [#575](https://github.com/jupyter-server/jupyter_server/pull/575) ([@fcollonval](https://github.com/fcollonval))
- Clean up link checking [#569](https://github.com/jupyter-server/jupyter_server/pull/569) ([@blink1073](https://github.com/blink1073))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2021-08-02&to=2021-09-09&type=c))

[@blink1073](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ablink1073+updated%3A2021-08-02..2021-09-09&type=Issues) | [@Carreau](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3ACarreau+updated%3A2021-08-02..2021-09-09&type=Issues) | [@codecov-commenter](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Acodecov-commenter+updated%3A2021-08-02..2021-09-09&type=Issues) | [@fcollonval](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Afcollonval+updated%3A2021-08-02..2021-09-09&type=Issues) | [@martinRenou](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3AmartinRenou+updated%3A2021-08-02..2021-09-09&type=Issues) | [@oliver-sanders](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aoliver-sanders+updated%3A2021-08-02..2021-09-09&type=Issues) | [@vidartf](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Avidartf+updated%3A2021-08-02..2021-09-09&type=Issues)

## 1.10.2

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/v1.10.1...7956dc51d8239b7b9e8de3b22ceb4473bbf1d4e5))

### Bugs fixed

- fix: make command line aliases work again [#564](https://github.com/jupyter-server/jupyter_server/pull/564) ([@mariobuikhuizen](https://github.com/mariobuikhuizen))
- decode bytes from secure cookie [#562](https://github.com/jupyter-server/jupyter_server/pull/562) ([@oliver-sanders](https://github.com/oliver-sanders))

### Maintenance and upkeep improvements

- Add the needed space in the welcome message [#561](https://github.com/jupyter-server/jupyter_server/pull/561) ([@echarles](https://github.com/echarles))
- Update check-release workflow [#558](https://github.com/jupyter-server/jupyter_server/pull/558) ([@afshin](https://github.com/afshin))

### Documentation improvements

- Fix typo in allow_password_change help [#559](https://github.com/jupyter-server/jupyter_server/pull/559) ([@manics](https://github.com/manics))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2021-07-23&to=2021-08-02&type=c))

[@afshin](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aafshin+updated%3A2021-07-23..2021-08-02&type=Issues) | [@codecov-commenter](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Acodecov-commenter+updated%3A2021-07-23..2021-08-02&type=Issues) | [@echarles](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aecharles+updated%3A2021-07-23..2021-08-02&type=Issues) | [@manics](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Amanics+updated%3A2021-07-23..2021-08-02&type=Issues) | [@mariobuikhuizen](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Amariobuikhuizen+updated%3A2021-07-23..2021-08-02&type=Issues) | [@oliver-sanders](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aoliver-sanders+updated%3A2021-07-23..2021-08-02&type=Issues) | [@welcome](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Awelcome+updated%3A2021-07-23..2021-08-02&type=Issues) | [@Zsailer](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3AZsailer+updated%3A2021-07-23..2021-08-02&type=Issues)

## 1.10.1

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/v1.10.0...42a195665aa8ae218fce4ec8165f19e734a9edaf))

### Bugs fixed

- Protect against unset spec [#556](https://github.com/jupyter-server/jupyter_server/pull/556) ([@fcollonval](https://github.com/fcollonval))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2021-07-22&to=2021-07-23&type=c))

[@fcollonval](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Afcollonval+updated%3A2021-07-22..2021-07-23&type=Issues)

## 1.10.0

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/v1.9.0...c9ee2a45e9a8f04215c2f3901f90cdc7b8fdc9c6))

### Enhancements made

- PR: Add a new preferred-dir traitlet [#549](https://github.com/jupyter-server/jupyter_server/pull/549) ([@goanpeca](https://github.com/goanpeca))
- stop hook for extensions [#526](https://github.com/jupyter-server/jupyter_server/pull/526) ([@oliver-sanders](https://github.com/oliver-sanders))
- extensions: allow extensions in namespace packages [#523](https://github.com/jupyter-server/jupyter_server/pull/523) ([@oliver-sanders](https://github.com/oliver-sanders))

### Bugs fixed

- Fix examples/simple test execution [#552](https://github.com/jupyter-server/jupyter_server/pull/552) ([@davidbrochart](https://github.com/davidbrochart))
- Rebuild package-lock, fixing local setup [#548](https://github.com/jupyter-server/jupyter_server/pull/548) ([@martinRenou](https://github.com/martinRenou))

### Maintenance and upkeep improvements

- small test changes [#541](https://github.com/jupyter-server/jupyter_server/pull/541) ([@oliver-sanders](https://github.com/oliver-sanders))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2021-06-24&to=2021-07-21&type=c))

[@blink1073](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ablink1073+updated%3A2021-06-24..2021-07-21&type=Issues) | [@codecov-commenter](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Acodecov-commenter+updated%3A2021-06-24..2021-07-21&type=Issues) | [@davidbrochart](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Adavidbrochart+updated%3A2021-06-24..2021-07-21&type=Issues) | [@goanpeca](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Agoanpeca+updated%3A2021-06-24..2021-07-21&type=Issues) | [@kevin-bates](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Akevin-bates+updated%3A2021-06-24..2021-07-21&type=Issues) | [@martinRenou](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3AmartinRenou+updated%3A2021-06-24..2021-07-21&type=Issues) | [@oliver-sanders](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aoliver-sanders+updated%3A2021-06-24..2021-07-21&type=Issues) | [@welcome](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Awelcome+updated%3A2021-06-24..2021-07-21&type=Issues) | [@Zsailer](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3AZsailer+updated%3A2021-06-24..2021-07-21&type=Issues)

## 1.9.0

([Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/v1.8.0...f712734c4f7005f6a844abec9f57b993e7b004b0))

### Enhancements made

- enable a way to run a task when an io_loop is created [#531](https://github.com/jupyter-server/jupyter_server/pull/531) ([@eastonsuo](https://github.com/eastonsuo))
- adds `GatewayClient.auth_scheme` configurable [#529](https://github.com/jupyter-server/jupyter_server/pull/529) ([@telamonian](https://github.com/telamonian))
- \[Notebook port 4835\] Add UNIX socket support to notebook server [#525](https://github.com/jupyter-server/jupyter_server/pull/525) ([@jtpio](https://github.com/jtpio))

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
[@blink1073](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ablink1073+updated%3A2021-05-01..2021-05-05&type=Issues) | [@candlerb](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Acandlerb+updated%3A2021-05-01..2021-05-05&type=Issues) | [@kevin-bates](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Akevin-bates+updated%3A2021-05-01..2021-05-05&type=Issues) | [@minrk](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Aminrk+updated%3A2021-05-01..2021-05-05&type=Issues) | [@mwakaba2](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Amwakaba2+updated%3A2021-05-01..2021-05-05&type=Issues) | [@Zsailer](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3AZsailer+updated%3A2021-05-01..2021-05-05&type=Issues) | [@kiendang](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Akiendang+updated%3A2021-04-21..2021-05-01&type=Issues) | \[@Carreau\]
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

- Ensure jupyter config dir exists [#454](https://github.com/jupyter-server/jupyter_server/pull/454) ([@afshin](https://github.com/afshin))
- Allow `pre_save_hook` to cancel save with `HTTPError` [#456](https://github.com/jupyter-server/jupyter_server/pull/456) ([@minrk](https://github.com/minrk))

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

- Update README.md [#425](https://github.com/jupyter-server/jupyter_server/pull/425) ([@BobinMathew](https://github.com/BobinMathew))
- Solve UnboundLocalError in launch_browser() [#421](https://github.com/jupyter-server/jupyter_server/pull/421) ([@jamesmishra](https://github.com/jamesmishra))
- Add file_to_run to server extension docs [#420](https://github.com/jupyter-server/jupyter_server/pull/420) ([@Zsailer](https://github.com/Zsailer))
- Remove outdated reference to \_jupyter_server_extension_paths in docs [#419](https://github.com/jupyter-server/jupyter_server/pull/419) ([@Zsailer](https://github.com/Zsailer))

**Contributors to this release:**

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server/graphs/contributors?from=2021-02-18&to=2021-02-22&type=c))

[@jamesmishra](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3Ajamesmishra+updated%3A2021-02-18..2021-02-22&type=Issues) | [@Zsailer](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server+involves%3AZsailer+updated%3A2021-02-18..2021-02-22&type=Issues)

## [1.4.0](https://github.com/jupyter-server/jupyter_server/tree/1.4.0) (2021-02-18)

[Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/1.3.0...HEAD)

**Merged pull requests:**

- Add Tests to Distribution [#416](https://github.com/jupyter-server/jupyter_server/pull/416) ([afshin](https://github.com/afshin))
- Enable extensions to control the file_to_run [#415](https://github.com/jupyter-server/jupyter_server/pull/415) ([afshin](https://github.com/afshin))
- add missing template for view.html [#414](https://github.com/jupyter-server/jupyter_server/pull/414) ([minrk](https://github.com/minrk))
- Remove obsoleted asyncio-patch fixture [#412](https://github.com/jupyter-server/jupyter_server/pull/412) ([kevin-bates](https://github.com/kevin-bates))
- Emit deprecation warning on old name [#411](https://github.com/jupyter-server/jupyter_server/pull/411) ([fcollonval](https://github.com/fcollonval))
- Correct logging message position [#410](https://github.com/jupyter-server/jupyter_server/pull/410) ([fcollonval](https://github.com/fcollonval))
- Update 1.3.0 Changelog to include broken 1.2.3 PRs [#408](https://github.com/jupyter-server/jupyter_server/pull/408) ([kevin-bates](https://github.com/kevin-bates))
- \[Gateway\] Track only this server's kernels [#407](https://github.com/jupyter-server/jupyter_server/pull/407) ([kevin-bates](https://github.com/kevin-bates))
- Update manager.py: more descriptive warnings when extensions fail to load [#396](https://github.com/jupyter-server/jupyter_server/pull/396) ([alberti42](https://github.com/alberti42))

## [1.3.0](https://github.com/jupyter-server/jupyter_server/tree/1.3.0) (2021-02-04)

[Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/1.2.2...HEAD)

**Merged pull requests (includes those from broken 1.2.3 release):**

- Special case ExtensionApp that starts the ServerApp [#401](https://github.com/jupyter-server/jupyter_server/pull/401) ([afshin](https://github.com/afshin))
- only use deprecated notebook_dir config if root_dir is not set [#400](https://github.com/jupyter-server/jupyter_server/pull/400) ([minrk](https://github.com/minrk))
- Use async kernel manager by default [#399](https://github.com/jupyter-server/jupyter_server/pull/399) ([kevin-bates](https://github.com/kevin-bates))
- Revert Session.username default value change [#398](https://github.com/jupyter-server/jupyter_server/pull/398) ([mwakaba2](https://github.com/mwakaba2))
- Re-enable default_url in ExtensionApp [#393](https://github.com/jupyter-server/jupyter_server/pull/393) ([afshin](https://github.com/afshin))
- Enable notebook ContentsManager in jupyter_server [#392](https://github.com/jupyter-server/jupyter_server/pull/392) ([afshin](https://github.com/afshin))
- Use jupyter_server_config.json as config file in the update password api [#390](https://github.com/jupyter-server/jupyter_server/pull/390) ([echarles](https://github.com/echarles))
- Increase culling test idle timeout [#388](https://github.com/jupyter-server/jupyter_server/pull/388) ([kevin-bates](https://github.com/kevin-bates))
- update changelog for 1.2.2 [#387](https://github.com/jupyter-server/jupyter_server/pull/387) ([Zsailer](https://github.com/Zsailer))

## [1.2.3](https://github.com/jupyter-server/jupyter_server/tree/1.2.3) (2021-01-29)

This was a broken release and was yanked from PyPI.

[Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/1.2.2...HEAD)

**Merged pull requests:**

- Re-enable default_url in ExtensionApp [#393](https://github.com/jupyter-server/jupyter_server/pull/393) ([afshin](https://github.com/afshin))
- Enable notebook ContentsManager in jupyter_server [#392](https://github.com/jupyter-server/jupyter_server/pull/392) ([afshin](https://github.com/afshin))
- Use jupyter_server_config.json as config file in the update password api [#390](https://github.com/jupyter-server/jupyter_server/pull/390) ([echarles](https://github.com/echarles))
- Increase culling test idle timeout [#388](https://github.com/jupyter-server/jupyter_server/pull/388) ([kevin-bates](https://github.com/kevin-bates))
- update changelog for 1.2.2 [#387](https://github.com/jupyter-server/jupyter_server/pull/387) ([Zsailer](https://github.com/Zsailer))

## [1.2.2](https://github.com/jupyter-server/jupyter_server/tree/1.2.2) (2021-01-14)

**Merged pull requests:**

- Apply missing ensure_async to root session handler methods [#386](https://github.com/jupyter-server/jupyter_server/pull/386) ([kevin-bates](https://github.com/kevin-bates))
- Update changelog to 1.2.1 [#385](https://github.com/jupyter-server/jupyter_server/pull/385) ([Zsailer](https://github.com/Zsailer))
- Fix application exit [#384](https://github.com/jupyter-server/jupyter_server/pull/384) ([afshin](https://github.com/afshin))
- Replace secure_write, is_hidden, exists with jupyter_core's [#382](https://github.com/jupyter-server/jupyter_server/pull/382) ([kevin-bates](https://github.com/kevin-bates))
- Add --autoreload flag [#380](https://github.com/jupyter-server/jupyter_server/pull/380) ([afshin](https://github.com/afshin))

## [1.2.1](https://github.com/jupyter-server/jupyter_server/tree/1.2.1) (2021-01-08)

[Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/1.2.0...1.2.1)

**Merged pull requests:**

- Enable extensions to set debug and open-browser flags [#379](https://github.com/jupyter-server/jupyter_server/pull/379) ([afshin](https://github.com/afshin))
- Add reconnection to Gateway [#378](https://github.com/jupyter-server/jupyter_server/pull/378) ([oyvsyo](https://github.com/oyvsyo))

## [1.2.0](https://github.com/jupyter-server/jupyter_server/tree/1.2.0) (2021-01-07)

[Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/1.1.4...1.2.0)

**Merged pull requests:**

- Flip default value for open_browser in extensions [#377](https://github.com/jupyter-server/jupyter_server/pull/377) ([ajbozarth](https://github.com/ajbozarth))
- Improve Handling of the soft limit on open file handles [#376](https://github.com/jupyter-server/jupyter_server/pull/376) ([afshin](https://github.com/afshin))
- Handle open_browser trait in ServerApp and ExtensionApp differently [#375](https://github.com/jupyter-server/jupyter_server/pull/375) ([afshin](https://github.com/afshin))
- Add setting to disable redirect file browser launch [#374](https://github.com/jupyter-server/jupyter_server/pull/374) ([afshin](https://github.com/afshin))
- Make trust handle use ensure_async [#373](https://github.com/jupyter-server/jupyter_server/pull/373) ([vidartf](https://github.com/vidartf))

## [1.1.4](https://github.com/jupyter-server/jupyter_server/tree/1.1.4) (2021-01-04)

[Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/1.1.3...1.1.4)

**Merged pull requests:**

- Update the link to paths documentation [#371](https://github.com/jupyter-server/jupyter_server/pull/371) ([krassowski](https://github.com/krassowski))
- IPythonHandler -> JupyterHandler [#370](https://github.com/jupyter-server/jupyter_server/pull/370) ([krassowski](https://github.com/krassowski))
- use setuptools find_packages, exclude tests, docs and examples from dist [#368](https://github.com/jupyter-server/jupyter_server/pull/368) ([bollwyvl](https://github.com/bollwyvl))
- Update serverapp.py [#367](https://github.com/jupyter-server/jupyter_server/pull/367) ([michaelaye](https://github.com/michaelaye))

## [1.1.3](https://github.com/jupyter-server/jupyter_server/tree/1.1.3) (2020-12-23)

[Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/1.1.2...1.1.3)

**Merged pull requests:**

- Culling: ensure last_activity attr exists before use [#365](https://github.com/jupyter-server/jupyter_server/pull/365) ([afshin](https://github.com/afshin))

## [1.1.2](https://github.com/jupyter-server/jupyter_server/tree/1.1.2) (2020-12-21)

[Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/1.0.11...1.1.2)

**Merged pull requests:**

- Nudge kernel with info request until we receive IOPub messages [#361](https://github.com/jupyter-server/jupyter_server/pull/361) ([SylvainCorlay](https://github.com/SylvainCorlay))

## [1.1.1](https://github.com/jupyter-server/jupyter_server/tree/1.1.1) (2020-12-16)

[Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/1.1.0...1.1.1)

**Merged pull requests:**

- Fix: await possible async dir_exists method [#363](https://github.com/jupyter-server/jupyter_server/pull/363) ([mwakaba2](https://github.com/mwakaba2))

## 1.1.0 (2020-12-11)

[Full Changelog](https://github.com/jupyter-server/jupyter_server/compare/1.0.10...1.1.0)

**Merged pull requests:**

- Restore pytest plugin from pytest-jupyter [#360](https://github.com/jupyter-server/jupyter_server/pull/360) ([kevin-bates](https://github.com/kevin-bates))
- Fix upgrade packaging dependencies build step [#354](https://github.com/jupyter-server/jupyter_server/pull/354) ([mwakaba2](https://github.com/mwakaba2))
- Await \_connect and inline read_messages callback to \_connect [#350](https://github.com/jupyter-server/jupyter_server/pull/350) ([ricklamers](https://github.com/ricklamers))
- Update release instructions and dev version [#348](https://github.com/jupyter-server/jupyter_server/pull/348) ([kevin-bates](https://github.com/kevin-bates))
- Fix test_trailing_slash [#346](https://github.com/jupyter-server/jupyter_server/pull/346) ([kevin-bates](https://github.com/kevin-bates))
- Apply security advisory fix to master [#345](https://github.com/jupyter-server/jupyter_server/pull/345) ([kevin-bates](https://github.com/kevin-bates))
- Allow toggling auth for prometheus metrics [#344](https://github.com/jupyter-server/jupyter_server/pull/344) ([yuvipanda](https://github.com/yuvipanda))
- Port Notebook PRs 5565 and 5588 - terminal shell heuristics [#343](https://github.com/jupyter-server/jupyter_server/pull/343) ([kevin-bates](https://github.com/kevin-bates))
- Port gateway updates from notebook (PRs 5317 and 5484) [#341](https://github.com/jupyter-server/jupyter_server/pull/341) ([kevin-bates](https://github.com/kevin-bates))
- add check_origin handler to gateway WebSocketChannelsHandler [#340](https://github.com/jupyter-server/jupyter_server/pull/340) ([ricklamers](https://github.com/ricklamers))
- Remove pytest11 entrypoint and plugin, require tornado 6.1, remove asyncio patch, CI work [#339](https://github.com/jupyter-server/jupyter_server/pull/339) ([bollwyvl](https://github.com/bollwyvl))
- Switch fixtures to use those in pytest-jupyter to avoid collisions [#335](https://github.com/jupyter-server/jupyter_server/pull/335) ([kevin-bates](https://github.com/kevin-bates))
- Enable CodeQL runs on all pushed branches [#333](https://github.com/jupyter-server/jupyter_server/pull/333) ([kevin-bates](https://github.com/kevin-bates))
- Asynchronous Contents API [#324](https://github.com/jupyter-server/jupyter_server/pull/324) ([mwakaba2](https://github.com/mwakaba2))

## 1.0.6 (2020-11-18)

1.0.6 is a security release, fixing one vulnerability:

### Changed

- Fix open redirect vulnerability GHSA-grfj-wjv9-4f9v (CVE-2020-26232)

## 1.0 (2020-9-18)

### Added.

- Added a basic, styled `login.html` template. ([220](https://github.com/jupyter/jupyter_server/pull/220), [295](https://github.com/jupyter/jupyter_server/pull/295))
- Added new extension manager API for handling server extensions. ([248](https://github.com/jupyter/jupyter_server/pull/248), [265](https://github.com/jupyter/jupyter_server/pull/265), [275](https://github.com/jupyter/jupyter_server/pull/275), [303](https://github.com/jupyter/jupyter_server/pull/303))
- The favicon and Jupyter logo are now available under jupyter_server's static namespace. ([284](https://github.com/jupyter/jupyter_server/pull/284))

### Changed.

- `load_jupyter_server_extension` should be renamed to `_load_jupyter_server_extension` in server extensions. Server now throws a warning when the old name is used. ([213](https://github.com/jupyter/jupyter_server/pull/213))
- Docs for server extensions now recommend using `authenticated` decorator for handlers. ([219](https://github.com/jupyter/jupyter_server/pull/219))
- `_load_jupyter_server_paths` should be renamed to `_load_jupyter_server_points` in server extensions. ([277](https://github.com/jupyter/jupyter_server/pull/277))
- `static_url_prefix` in ExtensionApps is now a configurable trait. ([289](https://github.com/jupyter/jupyter_server/pull/289))
- `extension_name` trait was removed in favor of `name`. ([232](https://github.com/jupyter/jupyter_server/pull/232))
- Dropped support for Python 3.5. ([296](https://github.com/jupyter/jupyter_server/pull/296))
- Made the `config_dir_name` trait configurable in `ConfigManager`. ([297](https://github.com/jupyter/jupyter_server/pull/297))

### Removed for now removed features.

- Removed ipykernel as a dependency of jupyter_server. ([255](https://github.com/jupyter/jupyter_server/pull/255))

### Fixed for any bug fixes.

- Prevent a re-definition of prometheus metrics if `notebook` package already imports them. ([#210](https://github.com/jupyter/jupyter_server/pull/210))
- Fixed `terminals` REST API unit tests that weren't shutting down properly. ([221](https://github.com/jupyter/jupyter_server/pull/221))
- Fixed jupyter_server on Windows for Python \< 3.7. Added patch to handle subprocess cleanup. ([240](https://github.com/jupyter/jupyter_server/pull/240))
- `base_url` was being duplicated when getting a url path from the `ServerApp`. ([280](https://github.com/jupyter/jupyter_server/pull/280))
- Extension URLs are now properly prefixed with `base_url`. Previously, all `static` paths were not. ([285](https://github.com/jupyter/jupyter_server/pull/285))
- Changed ExtensionApp mixin to inherit from `HasTraits`. This broke in traitlets 5.0 ([294](https://github.com/jupyter/jupyter_server/pull/294))
- Replaces `urlparse` with `url_path_join` to prevent URL squashing issues. ([304](https://github.com/jupyter/jupyter_server/pull/304))

## \[0.3\] - 2020-4-22

### Added

- ([#191](https://github.com/jupyter/jupyter_server/pull/191)) Async kernel managment is now possible using the `AsyncKernelManager` from `jupyter_client`
- ([#201](https://github.com/jupyter/jupyter_server/pull/201)) Parameters can now be passed to new terminals created by the `terminals` REST API.

### Changed

- ([#196](https://github.com/jupyter/jupyter_server/pull/196)) Documentation was rewritten + refactored to use pydata_sphinx_theme.
- ([#174](https://github.com/jupyter/jupyter_server/pull/174)) `ExtensionHandler` was changed to an Mixin class, i.e. `ExtensionHandlerMixin`

### Removed

- ([#194](https://github.com/jupyter/jupyter_server/pull/194)) The bundlerextension entry point was removed.

## \[0.2.1\] - 2020-1-10

### Added

- **pytest-plugin** for Jupyter Server.
  - Allows one to write async/await syntax in tests functions.
  - Some particularly useful fixtures include:
    - `serverapp`: a default ServerApp instance that handles setup+teardown.
    - `configurable_serverapp`: a function that returns a ServerApp instance.
    - `fetch`: an awaitable function that tests makes requests to the server API
    - `create_notebook`: a function that writes a notebook to a given temporary file path.

## \[0.2.0\] - 2019-12-19

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
