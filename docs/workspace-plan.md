# VS Code Workspace Plan

Summary of observations from the legacy `_OLD_openssl-devenv.code-workspace`
and the newer `_openssl-devenv.code-workspace` files. This will inform the new
workspaces that will be added to the SpareTools repository.

## Observed Requirements

- Multi-folder workspace bringing together recipes, tooling, profiles, cache
  views, and consumer examples.
- Python tooling requires custom interpreter path and extended `PYTHONPATH`
  covering shared utilities and recipes.
- C/C++ tooling uses Ninja/CMake with explicit include paths into the OpenSSL
  source tree and cached Conan packages.
- Tasks cover common flows: build/test/install OpenSSL, create Conan packages,
  run security scanners (Syft/Trivy), execute integration tests, and refresh
  symlinks.
- Launch configurations span both native binaries (`apps/openssl`) and Python
  modules (pytest, orchestrator entry points).
- Terminal environments set `CONAN_USER_HOME`, `OPENSSL_CONF`, `PYTHONPATH`, and
  extend `PATH` with packaged toolchains.
- Legacy workspace referenced now-deleted `openssl-tools-mini`; any new setup
  must avoid those paths and point to `sparetools-openssl-tools` instead.

## Action Items for New Workspace Definitions

1. Create `workspaces/openssl-integration.code-workspace` inside SpareTools
   featuring the consolidated folders: packages, docs, `.github/workflows`, and
   cached Conan directories via `${env:HOME}` references.
2. Mirror key settings from the newer workspace (Python formatting, CMake
   preferences, exclusion globs) while simplifying the folder list to match the
   SpareTools tree structure.
3. Recreate task groups for bootstrap, build, security scan, and release flows
   using the new package names and profile paths.
4. Provide launch configurations for debugging OpenSSL CLI binaries (built via
   the unified recipe) and Python automation scripts within
   `sparetools-openssl-tools`.
5. Introduce a second workspace targeting automatic builds of OpenSSL 3.6.0 in
   `/home/sparrow/projects/openssl-devenv/openssl-3.6.0`, wiring the matrix
  profiles and parallel build tasks.
6. Ensure terminal profiles source the activation scripts generated during the
   bootstrap flow (`~/.openssl-bootstrap/activate-openssl-env.sh`).

These notes will drive the implementation of the new workspace JSON files and
associated `tasks.json`/`launch.json` composed under the `workspaces/` and
`.vscode/` directories in the SpareTools repository.

