# SpareTools GitHub Actions Workflow Examples

This document provides reusable GitHub Actions workflow fragments for building and testing OpenSSL with SpareTools.

## Quick Start

Use these workflow fragments in your `.github/workflows/` directory:

- **Build OpenSSL** - Basic build with Conan
- **FIPS Validation** - Validate FIPS compliance
- **Provider Testing** - Test OpenSSL providers
- **Matrix Generation** - Generate optimized CI matrices
- **Security Scanning** - Vulnerability and SBOM scanning

---

## Fragment 1: Basic OpenSSL Build

**File:** `.github/workflows/openssl-build.yml`

```yaml
name: Build OpenSSL

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-22.04, windows-2022, macos-13]
        profile: [linux-gcc11, windows-msvc, macos-clang]
        include:
          - os: ubuntu-22.04
            profile: linux-gcc11
          - os: windows-2022
            profile: windows-msvc
          - os: macos-13
            profile: macos-clang

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install Conan
        run: pip install conan

      - name: Configure Conan
        run: |
          conan remote add sparesparrow-conan \
            https://conan.cloudsmith.io/sparesparrow-conan/openssl-conan/

      - name: Build OpenSSL
        run: |
          cd packages/sparetools-openssl
          conan create . --version=3.3.2 \
            -pr:b ../sparetools-openssl-tools/profiles/base/${{ matrix.profile }} \
            --build=missing

      - name: Test Package
        run: |
          conan test test_package sparetools-openssl/3.3.2@ \
            -pr:b ../sparetools-openssl-tools/profiles/base/${{ matrix.profile }}
```

---

## Fragment 2: FIPS Validation Workflow

**File:** `.github/workflows/fips-validation.yml`

```yaml
name: FIPS Validation

on:
  push:
    branches: [main]
    paths:
      - 'packages/sparetools-openssl/**'
      - 'packages/sparetools-openssl-tools/**'

jobs:
  fips-validation:
    runs-on: ubuntu-22.04

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install conan
          pip install -e packages/sparetools-openssl-tools

      - name: Build FIPS-enabled OpenSSL
        run: |
          cd packages/sparetools-openssl
          conan create . --version=3.3.2 \
            -pr:b ../sparetools-openssl-tools/profiles/base/linux-gcc11 \
            -pr:b ../sparetools-openssl-tools/profiles/features/fips-enabled \
            --build=missing

      - name: Validate FIPS Module
        run: |
          python3 -c "
          from sparetools.openssl_tools.openssl.fips_validator import FIPSValidator
          validator = FIPSValidator()
          result = validator.validate_module('/path/to/fips/module')
          if not result:
              raise RuntimeError('FIPS validation failed')
          "

      - name: Generate FIPS Report
        if: always()
        run: |
          python3 -c "
          from sparetools.openssl_tools.openssl.fips_validator import FIPSValidator
          validator = FIPSValidator()
          report = validator.generate_report()
          print(report)
          " > fips-report.txt

      - name: Upload FIPS Report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: fips-report
          path: fips-report.txt
```

---

## Fragment 3: Provider Testing Workflow

**File:** `.github/workflows/provider-tests.yml`

```yaml
name: Provider Tests

on:
  push:
    branches: [main, develop]
    paths:
      - 'packages/sparetools-openssl/test_package/**'

jobs:
  provider-tests:
    runs-on: ubuntu-22.04
    strategy:
      matrix:
        profile: ['linux-gcc11', 'linux-clang14']
        provider: ['default', 'legacy']

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install Conan
        run: pip install conan

      - name: Build OpenSSL
        run: |
          cd packages/sparetools-openssl
          conan create . --version=3.3.2 \
            -pr:b ../sparetools-openssl-tools/profiles/base/${{ matrix.profile }} \
            --build=missing

      - name: Run Provider Tests
        run: |
          conan test test_package sparetools-openssl/3.3.2@ \
            -pr:b ../sparetools-openssl-tools/profiles/base/${{ matrix.profile }} \
            -o test_provider=${{ matrix.provider }}

      - name: Upload Test Results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: provider-test-results-${{ matrix.profile }}-${{ matrix.provider }}
          path: test_results/
```

---

## Fragment 4: Matrix Generation Workflow

**File:** `.github/workflows/generate-matrix.yml`

```yaml
name: Generate Build Matrix

on:
  workflow_dispatch:
  push:
    branches: [main]
    paths:
      - '.github/workflows/**'

jobs:
  generate-matrix:
    runs-on: ubuntu-22.04
    outputs:
      matrix: ${{ steps.generate.outputs.matrix }}

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: pip install -e packages/sparetools-openssl-tools

      - name: Generate Build Matrix
        id: generate
        run: |
          python3 -m openssl_tools.cli matrix generate \
            --optimization high \
            --github-actions \
            --output matrix.json

          # Export matrix for use in other jobs
          MATRIX=$(cat matrix.json)
          echo "matrix=$MATRIX" >> $GITHUB_OUTPUT

      - name: Upload Generated Matrix
        uses: actions/upload-artifact@v3
        with:
          name: build-matrix
          path: matrix.json

  build-from-matrix:
    needs: generate-matrix
    runs-on: ${{ matrix.os }}
    strategy:
      matrix: ${{ fromJson(needs.generate-matrix.outputs.matrix) }}

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install Conan
        run: pip install conan

      - name: Build with Matrix Configuration
        run: |
          cd packages/sparetools-openssl
          conan create . --version=3.3.2 \
            -o build_method=${{ matrix.build_method }} \
            --build=missing
```

---

## Fragment 5: Security Scanning Workflow

**File:** `.github/workflows/security-scan.yml`

```yaml
name: Security Scanning

on:
  push:
    branches: [main]
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC

jobs:
  trivy-scan:
    runs-on: ubuntu-22.04

    steps:
      - uses: actions/checkout@v4

      - name: Run Trivy vulnerability scan
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'

      - name: Upload Trivy results to GitHub Security tab
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'

  sbom-generation:
    runs-on: ubuntu-22.04

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install Syft
        run: |
          curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin

      - name: Generate SBOM (CycloneDX)
        run: |
          syft packages . -o cyclonedx-json > sbom-cyclonedx.json

      - name: Generate SBOM (SPDX)
        run: |
          syft packages . -o spdx-json > sbom-spdx.json

      - name: Upload SBOMs
        uses: actions/upload-artifact@v3
        with:
          name: sbom-artifacts
          path: |
            sbom-cyclonedx.json
            sbom-spdx.json

      - name: Create Release with SBOM
        if: startsWith(github.ref, 'refs/tags/')
        uses: softprops/action-gh-release@v1
        with:
          files: |
            sbom-cyclonedx.json
            sbom-spdx.json
```

---

## Reusable Workflow (GitHub Advanced)

For more advanced setups, you can create reusable workflows. Here's an example structure:

**File:** `.github/workflows/reusable-openssl-build.yml`

```yaml
name: Reusable OpenSSL Build

on:
  workflow_call:
    inputs:
      openssl-version:
        required: true
        type: string
        default: '3.3.2'
      profile:
        required: true
        type: string
        default: 'linux-gcc11'
      build-method:
        required: false
        type: string
        default: 'perl'
      build-missing:
        required: false
        type: boolean
        default: true

jobs:
  build:
    runs-on: ubuntu-22.04

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install Conan
        run: pip install conan

      - name: Build OpenSSL
        run: |
          cd packages/sparetools-openssl
          conan create . \
            --version=${{ inputs.openssl-version }} \
            -pr:b ../sparetools-openssl-tools/profiles/base/${{ inputs.profile }} \
            -o build_method=${{ inputs.build-method }} \
            ${{ inputs.build-missing && '--build=missing' || '' }}
```

**Usage in another workflow:**

```yaml
jobs:
  build-openssl:
    uses: ./.github/workflows/reusable-openssl-build.yml
    with:
      openssl-version: '3.3.2'
      profile: 'linux-gcc11'
      build-method: 'perl'
```

---

## Integration Examples

### Build on PR, Deploy on Main

```yaml
name: Build and Deploy

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  build:
    uses: ./.github/workflows/reusable-openssl-build.yml
    with:
      openssl-version: '3.3.2'
      profile: 'linux-gcc11'

  deploy:
    needs: build
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-22.04
    steps:
      - name: Deploy to Cloudsmith
        run: |
          conan remote add sparesparrow-conan \
            https://conan.cloudsmith.io/sparesparrow-conan/openssl-conan/

          conan upload 'sparetools-openssl/*' \
            -r sparesparrow-conan --confirm
```

---

## Best Practices

1. **Use matrix builds** to test multiple configurations in parallel
2. **Cache dependencies** to speed up builds
3. **Generate SBOMs** for supply chain security
4. **Run FIPS validation** on every release
5. **Use reusable workflows** to reduce duplication
6. **Upload artifacts** for investigation on failures
7. **Schedule security scans** to run regularly

---

## Environment Setup

All workflows assume:
- Python 3.12+ available
- Conan 2.x installed
- SpareTools packages available in Cloudsmith

Configure Cloudsmith access with:

```bash
conan remote add sparesparrow-conan \
  https://conan.cloudsmith.io/sparesparrow-conan/openssl-conan/

conan remote login sparesparrow-conan spare-sparrow \
  --password "$CLOUDSMITH_API_KEY"
```

---

## Troubleshooting

### Matrix not generating
Check that `openssl_tools/cli.py` is properly installed and accessible.

### FIPS validation failing
Ensure the FIPS module is built with `-pr:b profiles/features/fips-enabled`.

### Provider tests timing out
Increase the timeout in GitHub Actions or reduce the number of test combinations.

### SBOMs not generated
Verify Syft is installed: `curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin`

---

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Conan Documentation](https://docs.conan.io/)
- [OpenSSL Build Documentation](https://github.com/openssl/openssl/blob/master/INSTALL.md)
- [Syft SBOM Generator](https://github.com/anchore/syft)
- [Trivy Security Scanner](https://github.com/aquasecurity/trivy)
