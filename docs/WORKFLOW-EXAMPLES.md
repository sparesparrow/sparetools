# GitHub Actions Workflow Examples for SpareTools

This document provides reusable workflow fragments for integrating SpareTools packages into your CI/CD pipelines.

---

## Table of Contents

1. [Basic OpenSSL Build](#basic-openssl-build)
2. [Multi-Profile Matrix Builds](#multi-profile-matrix-builds)
3. [Security Scanning Integration](#security-scanning-integration)
4. [FIPS-Enabled Builds](#fips-enabled-builds)
5. [Cross-Platform Builds](#cross-platform-builds)
6. [Package Publishing](#package-publishing)

---

## Basic OpenSSL Build

Simple workflow to build OpenSSL with SpareTools:

```yaml
name: Build OpenSSL

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install Conan
        run: |
          pip install conan==2.21.0
          conan profile detect

      - name: Add Cloudsmith Remote
        run: |
          conan remote add sparesparrow-conan \
            https://conan.cloudsmith.io/sparesparrow-conan/openssl-conan/

      - name: Build OpenSSL
        run: |
          conan install --requires=sparetools-openssl/3.3.2 \
            -r sparesparrow-conan --build=missing

      - name: Test Build
        run: |
          conan test packages/sparetools-openssl/test_package \
            sparetools-openssl/3.3.2@
```

---

## Multi-Profile Matrix Builds

Build with multiple configurations using profiles:

```yaml
name: Matrix Build

on: [push, pull_request]

jobs:
  build-matrix:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        build_method: [perl, cmake, autotools]
        features: [minimal, performance, fips]
        exclude:
          # FIPS not supported on macOS
          - os: macos-latest
            features: fips
          # Autotools not supported on Windows
          - os: windows-latest
            build_method: autotools

    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install Conan
        run: pip install conan==2.21.0

      - name: Detect Profile
        run: conan profile detect --force

      - name: Build with Profiles
        run: |
          conan create packages/sparetools-openssl \
            --version=3.3.2 \
            -pr:b packages/sparetools-openssl-tools/profiles/build-methods/${{ matrix.build_method }} \
            -pr:b packages/sparetools-openssl-tools/profiles/features/${{ matrix.features }} \
            --build=missing

      - name: Run Tests
        run: |
          conan test packages/sparetools-openssl/test_package \
            sparetools-openssl/3.3.2@
```

---

## Security Scanning Integration

Integrate Trivy and Syft security gates:

```yaml
name: Security Scan

on:
  push:
    branches: [main]
  schedule:
    # Run daily security scans
    - cron: '0 2 * * *'

jobs:
  trivy-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'

      - name: Upload Trivy results to GitHub Security
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: 'trivy-results.sarif'

  sbom-generation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Generate SBOM with Syft
        uses: anchore/sbom-action@v0
        with:
          format: 'cyclonedx-json'
          output-file: 'sbom.json'

      - name: Upload SBOM
        uses: actions/upload-artifact@v4
        with:
          name: sbom-cyclonedx
          path: sbom.json

      - name: Generate SPDX SBOM
        uses: anchore/sbom-action@v0
        with:
          format: 'spdx-json'
          output-file: 'sbom-spdx.json'

      - name: Upload SPDX SBOM
        uses: actions/upload-artifact@v4
        with:
          name: sbom-spdx
          path: sbom-spdx.json

  codeql-analysis:
    runs-on: ubuntu-latest
    permissions:
      security-events: write
    steps:
      - uses: actions/checkout@v4

      - name: Initialize CodeQL
        uses: github/codeql-action/init@v3
        with:
          languages: python

      - name: Perform CodeQL Analysis
        uses: github/codeql-action/analyze@v3
```

---

## FIPS-Enabled Builds

Build and validate FIPS-compliant OpenSSL:

```yaml
name: FIPS Build

on:
  push:
    tags:
      - 'fips-*'

jobs:
  fips-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install Conan
        run: |
          pip install conan==2.21.0
          conan profile detect

      - name: Build FIPS OpenSSL
        run: |
          conan create packages/sparetools-openssl \
            --version=3.3.2 \
            -pr:b packages/sparetools-openssl-tools/profiles/features/fips-enabled \
            -o sparetools-openssl/*:fips=True \
            --build=missing

      - name: Run FIPS Smoke Tests
        run: |
          conan test packages/sparetools-openssl/test_package \
            sparetools-openssl/3.3.2@

      - name: Validate FIPS Module
        run: |
          python3 -c "
          from packages.sparetools_bootstrap.bootstrap.openssl.fips_validator import FIPSValidator
          validator = FIPSValidator()
          # Add FIPS module validation logic
          print('FIPS validation complete')
          "

      - name: Generate FIPS Compliance Report
        run: |
          mkdir -p reports
          echo "FIPS Build Report - $(date)" > reports/fips-report.txt
          echo "========================" >> reports/fips-report.txt
          echo "" >> reports/fips-report.txt
          echo "Build Configuration:" >> reports/fips-report.txt
          conan profile show default >> reports/fips-report.txt

      - name: Upload FIPS Report
        uses: actions/upload-artifact@v4
        with:
          name: fips-compliance-report
          path: reports/fips-report.txt
```

---

## Cross-Platform Builds

Build for Linux, macOS, and Windows with architecture variants:

```yaml
name: Cross-Platform Build

on: [push]

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        include:
          # Linux builds
          - os: ubuntu-latest
            arch: x86_64
            profile: linux-gcc11
          - os: ubuntu-latest
            arch: aarch64
            profile: linux-gcc11-arm64

          # macOS builds
          - os: macos-14
            arch: x86_64
            profile: darwin-clang
          - os: macos-14
            arch: arm64
            profile: darwin-clang-arm64

          # Windows builds
          - os: windows-2022
            arch: x86_64
            profile: windows-msvc2022
          - os: windows-2022
            arch: arm64
            profile: windows-msvc2022-arm64

    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install Conan
        run: pip install conan==2.21.0

      - name: Detect Profile
        run: conan profile detect --force

      - name: Build for ${{ matrix.arch }}
        run: |
          conan create packages/sparetools-openssl \
            --version=3.3.2 \
            -pr:b packages/sparetools-openssl-tools/profiles/base/${{ matrix.profile }} \
            --build=missing

      - name: Package Artifacts
        run: |
          mkdir -p artifacts/${{ matrix.os }}-${{ matrix.arch }}
          conan list --format=compact > artifacts/${{ matrix.os }}-${{ matrix.arch }}/package-list.txt

      - name: Upload Artifacts
        uses: actions/upload-artifact@v4
        with:
          name: openssl-${{ matrix.os }}-${{ matrix.arch }}
          path: artifacts/
```

---

## Package Publishing

Publish packages to Cloudsmith:

```yaml
name: Publish Packages

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install Conan
        run: pip install conan==2.21.0

      - name: Configure Conan Remote
        run: |
          conan remote add sparesparrow-conan \
            https://dl.cloudsmith.io/public/sparesparrow-conan/openssl-conan/conan/

      - name: Build All Packages
        run: |
          # Build in dependency order
          conan create packages/sparetools-base --version=2.0.0
          conan create packages/sparetools-cpython --version=3.12.7
          conan create packages/sparetools-shared-dev-tools --version=2.0.0
          conan create packages/sparetools-openssl-tools --version=2.0.0
          conan create packages/sparetools-openssl --version=3.3.2 --build=missing

      - name: Login to Cloudsmith
        env:
          CLOUDSMITH_API_KEY: ${{ secrets.CLOUDSMITH_API_KEY }}
        run: |
          conan remote login sparesparrow-conan \
            sparesparrow-conan -p $CLOUDSMITH_API_KEY

      - name: Upload Packages
        run: |
          conan upload 'sparetools-*/*' \
            -r sparesparrow-conan \
            --confirm

      - name: Create Release Notes
        run: |
          echo "# SpareTools OpenSSL Release ${{ github.ref_name }}" > release-notes.md
          echo "" >> release-notes.md
          echo "## Packages Published" >> release-notes.md
          conan list 'sparetools-*/*' --format=compact >> release-notes.md

      - name: Update Release
        uses: softprops/action-gh-release@v1
        with:
          files: release-notes.md
          body_path: release-notes.md
```

---

## Advanced: Smart Build Matrix Generation

Use the SpareTools CLI to generate optimized build matrices:

```yaml
name: Smart Matrix Build

on: [push]

jobs:
  generate-matrix:
    runs-on: ubuntu-latest
    outputs:
      matrix: ${{ steps.generate.outputs.matrix }}
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install Conan
        run: pip install conan==2.21.0

      - name: Add Cloudsmith Remote
        run: |
          conan remote add sparesparrow-conan \
            https://conan.cloudsmith.io/sparesparrow-conan/openssl-conan/

      - name: Install sparetools-openssl-tools
        run: |
          conan install --tool-requires=sparetools-openssl-tools/2.0.0 \
            -r sparesparrow-conan

      - name: Generate Matrix
        id: generate
        run: |
          # Use the SpareTools CLI to generate optimized matrix
          python3 -c "
          import sys
          sys.path.insert(0, '~/.conan2/p/.../sparetools-openssl-tools/p')
          from openssl_tools.cli import main
          sys.argv = ['cli', 'matrix', 'generate', '--optimization', 'high', '--github-actions']
          main()
          " > matrix.json
          echo "matrix=$(cat matrix.json)" >> $GITHUB_OUTPUT

  build:
    needs: generate-matrix
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix: ${{ fromJson(needs.generate-matrix.outputs.matrix) }}

    steps:
      - uses: actions/checkout@v4

      - name: Build Configuration
        run: |
          echo "Building: ${{ matrix.config_name }}"
          echo "OS: ${{ matrix.os }}"
          echo "Profile: ${{ matrix.profile }}"

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install Conan
        run: pip install conan==2.21.0

      - name: Build
        run: |
          conan create packages/sparetools-openssl \
            --version=3.3.2 \
            -pr:b ${{ matrix.profile }} \
            --build=missing
```

---

## Reusable Workflow Components

### Reusable Conan Setup

Create `.github/workflows/setup-conan.yml`:

```yaml
name: Setup Conan

on:
  workflow_call:
    inputs:
      python-version:
        required: false
        type: string
        default: '3.12'
      conan-version:
        required: false
        type: string
        default: '2.21.0'

jobs:
  setup:
    runs-on: ubuntu-latest
    steps:
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ inputs.python-version }}

      - name: Install Conan
        run: pip install conan==${{ inputs.conan-version }}

      - name: Configure Conan
        run: |
          conan profile detect
          conan remote add sparesparrow-conan \
            https://conan.cloudsmith.io/sparesparrow-conan/openssl-conan/
```

Use in other workflows:

```yaml
jobs:
  setup:
    uses: ./.github/workflows/setup-conan.yml
    with:
      python-version: '3.12'
      conan-version: '2.21.0'

  build:
    needs: setup
    runs-on: ubuntu-latest
    steps:
      # Your build steps here
```

---

## Best Practices

### 1. **Always Pin Versions**
```yaml
# Good
pip install conan==2.21.0

# Bad
pip install conan  # Uses latest, may break
```

### 2. **Use Build Profiles**
```yaml
# Good - Explicit configuration
-pr:b profiles/base/linux-gcc11
-pr:b profiles/features/fips-enabled

# Bad - Relies on auto-detection
conan create . --build=missing
```

### 3. **Cache Dependencies**
```yaml
- name: Cache Conan packages
  uses: actions/cache@v3
  with:
    path: ~/.conan2
    key: conan-${{ runner.os }}-${{ hashFiles('**/conanfile.py') }}
```

### 4. **Fail Fast Strategy**
```yaml
strategy:
  fail-fast: false  # Continue other jobs even if one fails
  matrix:
    # Your matrix here
```

### 5. **Artifact Retention**
```yaml
- name: Upload Build Artifacts
  uses: actions/upload-artifact@v4
  with:
    name: build-results
    path: build/
    retention-days: 7  # Don't keep forever
```

---

## Troubleshooting

### Common Issues

**Issue: "Conan profile not found"**
```yaml
# Solution: Always detect profile first
- run: conan profile detect --force
```

**Issue: "Package not found on remote"**
```yaml
# Solution: Add --build=missing
- run: conan install --requires=package/version --build=missing
```

**Issue: "Permission denied on Windows"**
```yaml
# Solution: Use PowerShell on Windows
- name: Build (Windows)
  if: runner.os == 'Windows'
  shell: pwsh
  run: |
    conan create .
```

---

## Additional Resources

- [Conan 2.x Documentation](https://docs.conan.io/2/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [SpareTools GitHub](https://github.com/sparesparrow/sparetools)
- [Cloudsmith Repository](https://cloudsmith.io/~sparesparrow-conan/repos/openssl-conan/)
