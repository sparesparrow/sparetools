
- Role: You are a DevOps bootstrap agent for OpenSSL.
- Goal:
    - 1) Download prebuilt CPython package from Cloudsmith for this OS/arch.
    - 2) Extract into ~/.openssl-bootstrap/cpython and set PYTHONHOME/PATH only for this session.
    - 3) Using this Python, install conan==2.21.0 and validate conan --version.
    - 4) Configure Conan remotes: Cloudsmith (sparesparrow-conan/openssl-conan) and conancenter; configure default profile or detect platform-specific profile; persist in the bootstrap environment.
    - 5) Clone and run openssl-test integration orchestration to validate environment: smoke tests that confirm python, pip, conan, and remotes work; run the minimal integration test matrix.
    - 6) Emit logs and artifacts:
        - Logs into ~/.openssl-bootstrap/logs/YYYYMMDD-HHMM/
        - Create activation script: ~/.openssl-bootstrap/activate-openssl-env.(sh|ps1)
        - Write env snapshot: env.json with PYTHONHOME, PATH, versions, conan profile summary, remotes list, and timestamps.
- Constraints:
    - No compilation of CPython; must download prebuilt.
    - Use stdlib for network and archive handling.
    - Don’t mutate global system settings; keep changes within ~/.openssl-bootstrap and repo workspace.
- Deliverables:
    - Verified python3 --version and conan --version output lines captured in logs.
    - Remotes list with Cloudsmith and conancenter.
    - Conan profile summary saved as profile.dump.txt.
    - Minimal integration test suite results; junit.xml saved in logs dir.
- Validation pass criteria:
    - All commands return zero exit codes.
    - Activation script exists and works in a fresh shell.
    - Conan search '*' works against conancenter.
    - Integration minimal tests pass.

3) Cross-platform bootstrap logic the agent must follow

- Platform detection:
    - Linux x86_64: sparetools-cpython-<ver>-linux-x86_64.tar.gz
    - macOS arm64/x86_64: sparetools-cpython-<ver>-macos-<arch>.tar.gz
    - Windows x86_64: sparetools-cpython-<ver>-windows-x86_64.zip
- Environment setup:
    - Install directory: ~/.openssl-bootstrap/cpython
    - python_bin:
        - Linux/macOS: ~/.openssl-bootstrap/cpython/bin/python3
        - Windows: ~/.openssl-bootstrap/cpython/python.exe
    - Export:
        - POSIX: export PYTHONHOME=~/.openssl-bootstrap/cpython; export PATH="$PYTHONHOME/bin:$PATH"
        - Windows PowerShell: \$env:PYTHONHOME="..."; $env:Path="$env:PYTHONHOME;$env:PYTHONHOME\Scripts;$env:Path"
- Validate python works:
    - python3 --version (POSIX) / python --version (Windows)
    - python -c "import ssl, sys; print(sys.version)"
- Install Conan using bootstrap Python:
    - python -m ensurepip --upgrade
    - python -m pip install --upgrade pip
    - python -m pip install conan==2.21.0
    - conan --version -> “Conan version 2.21.0”
- Configure Conan:
    - conan remote list -> ensure conancenter present
    - conan remote add cloudsmith https://dl.cloudsmith.io/…/openssl-conan if not present
    - conan profile detect --force
    - conan profile path default -> save to logs
    - conan config home -> confirm it points to user-scoped config dir
- openssl-test orchestration:
    - Clone repo to a workspace directory (e.g., ~/workspace/openssl-test)
    - Run its init/orchestration entrypoint (refer to its documented task runner) to perform:
        - python/conan sanity checks
        - minimal integration tests
    - Capture outputs:
        - junit.xml for tests
        - environment dump (versions, remotes, profile)
        - SBOM and scan summaries if included in the orchestration

4) Do and Don’t lists for the agent

- Do:
    - Keep logs verbose and timestamped.
    - Save the exact Cloudsmith URL used and package hash if available.
    - Verify python and conan actually run from the newly set environment.
    - Print conan remotes and profile content into logs.
    - Use retry with backoff for downloads.
    - Use prebuilt CPython from Cloudsmith during bootstrap.
    - Use stdlib-only methods for bootstrap downloads and extraction.
    - Pin Conan to 2.21.0.
    - Use openssl-test orchestration scripts and readme to drive integration tests.
    - Emit logs to a known directory with timestamps and concise machine-parsable summaries.
- Don’t:
    - Don’t attempt system-wide installation or require admin privileges.
    - Don’t assume pip exists before ensurepip.
    - Don’t pin to unvetted Cloudsmith repos or alternate namespaces.
    - Don’t proceed if conan --version isn’t exactly 2.21.0.
    - Don’t run pip using system Python before bootstrap CPython is activated.
    - Don’t modify CI security gates or skip scanners.
    - Don’t write credentials or secrets to logs.
    - Don’t create global system changes; confine to workspace or user’s home.
- Common mistakes:
    - Running pip with system python instead of bootstrap python.
    - Forgetting to export PATH and PYTHONHOME before testing python -m pip.
    - Running integration tests prior to profile detection.
    - Skipping log capture; second agent can’t validate success without artifacts.
    - Building CPython from source in first bootstrap run.
    - Overwriting PATH/PYTHONHOME globally.
    - Failing to verify Python/Conan binaries actually run after install.
    - Running integration tests before remotes/profiles are configured.


- Do:
- Don’t:
- Common anti-patterns to avoid:

5) Recommended agent approach (execution order)

- Step 0: Detect OS and arch, set platform string.
- Step 1: Create ~/.openssl-bootstrap, logs dir with timestamp.
- Step 2: Resolve Cloudsmith URL for CPython package based on version and platform; download with retries; verify size and hash if manifest is available.
- Step 3: Extract into ~/.openssl-bootstrap/cpython; write env activation script and source it for the session.
- Step 4: python -m ensurepip; pip install conan==2.21.0; validate.
- Step 5: conan remote add + profile detect; dump configurations.
- Step 6: Clone openssl-test and run minimal integration orchestration; store junit.xml and logs.
- Step 7: Print final “SUCCESS” banner and write a machine-readable summary.json with all key outputs and paths.

6) When and how to rebuild CPython in cpy

- When:
    - New CPython point release or security patch.
    - New platform support, toolchain updates, or critical CVEs.
    - FIPS policy changes that affect Python’s SSL usage or OpenSSL linkage.
- How:
    - Use sparetools GitHub Actions matrix to build per-platform.
    - Enforce security gates: Syft SBOM + Trivy + CodeQL; block merges on CRITICAL.
    - Package as sparetools-cpython-<version>-<platform>.(tar.gz|zip), sign if applicable, upload to Cloudsmith.
    - Update openssl-test bootstrap to prefer latest stable tag; maintain a fallback list.

7) Cross-platform activation scripts the agent should output

- POSIX: ~/.openssl-bootstrap/activate-openssl-env.sh
    - export PYTHONHOME=~/.openssl-bootstrap/cpython
    - export PATH="$PYTHONHOME/bin:$PATH"
- Windows PowerShell: ~/.openssl-bootstrap/activate-openssl-env.ps1
    - \$env:PYTHONHOME="C:\Users\<User>\.openssl-bootstrap\cpython"
    - $env:Path="$env:PYTHONHOME;$env:PYTHONHOME\Scripts;$env:Path"

8) Antipatterns to avoid in logs and artifacts

- Storing secrets in logs (Cloudsmith tokens, GitHub tokens).
- Opaque logs without versions and paths.
- Non-deterministic paths; always resolve and print absolute paths for artifacts.

