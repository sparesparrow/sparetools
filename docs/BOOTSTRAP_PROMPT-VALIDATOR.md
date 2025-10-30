You are the agent validator. Validate the first - executor - agent’s output without redoing the work. This agent reads logs, environment files, and runs non-destructive checks.
- Read ~/.openssl-bootstrap/logs/<latest>/summary.json and env.json if present.
- Verify:

1) Activation script exists and is executable/readable:
        - POSIX: test -f ~/.openssl-bootstrap/activate-openssl-env.sh
        - Windows: Test-Path ~/.openssl-bootstrap/activate-openssl-env.ps1
2) Environment snapshot includes:
        - PYTHONHOME path pointing to ~/.openssl-bootstrap/cpython
        - PATH includes python bin directory for POSIX; proper path entries on Windows
3) Executables:
        - python --version (should match CPython version provisioned)
        - python -c "import ssl, sys; print(sys.version, ssl.OPENSSL_VERSION)" to ensure SSL binding
        - python -m pip --version
        - conan --version equals 2.21.0
4) Conan configured:
        - conan remote list contains conancenter and Cloudsmith remote
        - conan profile show (default) exists and prints settings; capture to logs
5) Integration results:
        - junit.xml exists under ~/.openssl-bootstrap/logs/<latest>/ or repo test output directory
        - Parse junit.xml: zero failures for minimal workflow
6) Cloudsmith reachability (no secret use required):
        - conan search '*' -r conancenter works
        - If public listing is configured, a harmless Cloudsmith query is permitted; otherwise skip
7) Filesystem layout:
        - ~/.openssl-bootstrap/cpython structure intact; bin/Scripts present
8) Security gate status (if CI artifacts exist):
        - If SBOMs and Trivy reports were generated, verify status markers (no CRITICAL)
- Emit validation report:
    - Write ~/.openssl-bootstrap/logs/<latest>/validation-report.json with fields:
        - status: pass/fail
        - checks: list with name, result, details
        - versions: python, pip, conan
        - remotes: list
        - profileSummary: first 10 lines of profile show
        - timestamps

Final Validation Checklist (operator-readable)

- Environment
    - [ ] Activation script exists (sh/ps1)
    - [ ] PYTHONHOME points to ~/.openssl-bootstrap/cpython
    - [ ] PATH includes CPython bin/Scripts
- Tooling
    - [ ] python --version prints expected version
    - [ ] python -m pip --version succeeds
    - [ ] conan --version is exactly 2.21.0
- Conan
    - [ ] conan remote list shows conancenter and Cloudsmith
    - [ ] conan profile detect ran; profile show prints expected settings
    - [ ] conan search '*' -r conancenter succeeds
- Tests
    - [ ] junit.xml exists and has zero failures for minimal run
    - [ ] Orchestration logs present in ~/.openssl-bootstrap/logs/<latest>/
- Security (if applicable in this run)
    - [ ] SBOM file exists
    - [ ] Trivy summary indicates no CRITICAL vulns
    - [ ] CodeQL gate not bypassed in CI
- Artifacts
    - [ ] summary.json and validation-report.json exist and are consistent
    - [ ] Absolute paths in logs resolve correctly

Usual mistakes the validator must flag

- Using system python instead of bootstrap python (version mismatch).
- Conan installed but PATH not updated, so conan command not found.
- Remotes configured only partially (missing Cloudsmith).
- No profile detection applied prior to integration tests.
- junit.xml missing or contains failures that weren’t surfaced.

Recommended approach for the second agent if failures are found

- If python or conan missing:
    - Re-source activation script and re-run minimal checks.
- If remotes missing:
    - Add remotes idempotently; re-run minimal queries.
- If tests failed:
    - Inspect the last 200 lines of integration log; attach to validation report for triage by a remediation agent.

Go/No-Go checklist for the first agent (to be evaluated by second agent)

- Go if:
    - All environment/tooling checks pass.
    - Remotes and profile verified.
    - junit.xml success and logs exist.
- No-Go if:
    - Any tool missing or wrong version.
    - Conan remotes misconfigured.
    - Tests failed or absent.
