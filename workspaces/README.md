# Workspace Overview

This directory contains curated VS Code workspace definitions for the SpareTools
ecosystem.

- `openssl-integration.code-workspace` – day-to-day workspace for working on the
  SpareTools repository. Includes tasks for bootstrapping the developer
  environment, building/testing the unified `sparetools-openssl` package, and
  running security gates.
- `openssl-3.6.0-matrix.code-workspace` – dedicated workspace for running
  matrix builds of the upstream OpenSSL 3.6.0 source tree located at
  `/home/sparrow/projects/openssl-devenv/openssl-3.6.0`. Tasks invoke the new
  `build-openssl-source.py` helper to execute parallel hybrid builds and log
  results under `~/.openssl-matrix/logs`.

Each workspace expects the bootstrap script to have populated
`~/.openssl-bootstrap/activate-openssl-env.sh` and the prebuilt CPython runtime.
Launch VS Code via:

```bash
code workspaces/openssl-integration.code-workspace
```

Refer to the tasks panel (`Terminal → Run Task…`) to execute the predefined
flows. The matrix workspace supports parallel execution through the
`Matrix :: Build All` task, and the companion `Matrix :: Tail Logs` task shows
live progress as JSON summaries are generated.

