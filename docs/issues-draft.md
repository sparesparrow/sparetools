# Draft GitHub Issues

## sparesparrow/openssl
- Track: update Python `configure.py` for OpenSSL 3.6+ provider ordering and
  assembly tunes.
- Track: add Windows/MSVC CI job mirroring SpareTools matrix profiles.

## sparesparrow/openssl-tools
- Generate `build_matrix` CLI wrapper that emits GitHub Actions-compatible JSON.
- Deprecate legacy `openssl-tools-mini` references and ensure documentation
  points to consolidated scripts.

## sparesparrow/openssl-profiles
- Regenerate profile catalogue using new axes (`openssl_release`,
  `optimization_tier`).
- Document profile usage examples for downstream consumers.

## sparesparrow/openssl-test
- Expand integration suite with FIPS smoke tests for each matrix profile.
- Pipe SBOM and Trivy scans into CI artifacts for auditing.

## sparesparrow/cpy
- Build and publish CPython 3.12.7 artefacts for Windows and macOS runners.

## sparesparrow/mcp-prompts
- Update bootstrap prompts to reference the new VS Code workspaces and tasks.

## sparesparrow/mcp-project-orchestrator
- Integrate `scripts/aggregate-build-logs.py` output into MCP dashboard views.

