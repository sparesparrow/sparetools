# Cross-Repository Testing Guide

Comprehensive guide to testing SpareTools packages across repositories and ensuring ecosystem compatibility.

## Overview

Cross-repository testing ensures that SpareTools packages work correctly across different projects and environments. This guide covers:

- Testing SpareTools packages in consumer projects
- Multi-repository validation workflows
- Integration testing strategies
- Compatibility matrices
- Automated cross-repo testing

## Testing Strategies

### 1. Consumer Integration Testing

Test SpareTools packages in real consumer applications:

```python
# test_sparetools_consumer.py
"""Test SpareTools packages in consumer context."""

import subprocess
import tempfile
import os
from pathlib import Path

def test_sparetools_in_consumer():
    """Test SpareTools integration in a consumer project."""

    # Create temporary consumer project
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir) / "consumer"
        project_dir.mkdir()

        # Create consumer conanfile.py
        conanfile = project_dir / "conanfile.py"
        conanfile.write_text("""
from conan import ConanFile

class Consumer(ConanFile):
    name = "consumer"
    version = "1.0.0"

    requires = "sparetools-openssl/3.3.2"
    tool_requires = "sparetools-cpython/3.12.7"

    def generate(self):
        # Test that generators work
        pass

    def build(self):
        # Test build integration
        self.run("echo 'Consumer build successful'")
""")

        # Test Conan integration
        os.chdir(project_dir)
        result = subprocess.run([
            "conan", "install", ".", "--build=missing"
        ], capture_output=True, text=True)

        assert result.returncode == 0, f"Conan install failed: {result.stderr}"

        # Test build
        result = subprocess.run([
            "conan", "build", "."
        ], capture_output=True, text=True)

        assert result.returncode == 0, f"Build failed: {result.stderr}"

        print("✅ Consumer integration test passed")
```

### 2. Multi-Repository Validation

Test package compatibility across repository boundaries:

```bash
#!/bin/bash
# cross_repo_test.sh

# Test repositories
REPOS=(
    "https://github.com/sparesparrow/sparetools"
    "https://github.com/example/mia-consumer"
    "https://github.com/example/android-consumer"
)

# Test scenarios
SCENARIOS=(
    "basic-integration"
    "version-compatibility"
    "platform-matrix"
)

for repo in "${REPOS[@]}"; do
    echo "Testing repository: $repo"

    # Clone and test
    repo_name=$(basename "$repo")
    git clone "$repo" "test-$repo_name"
    cd "test-$repo_name"

    for scenario in "${SCENARIOS[@]}"; do
        echo "Running scenario: $scenario"
        ./test/scripts/run_cross_repo_test.sh "$scenario"
    done

    cd ..
    rm -rf "test-$repo_name"
done
```

### 3. Version Compatibility Matrix

Test package combinations systematically:

```python
# test_version_matrix.py
"""Test version compatibility across SpareTools packages."""

import itertools
import subprocess
import json

# Package versions to test
VERSIONS = {
    "sparetools-base": ["2.0.0"],
    "sparetools-cpython": ["3.12.7"],
    "sparetools-openssl": ["3.3.2"],
    "sparetools-openssl-tools": ["2.0.0"]
}

def generate_version_combinations():
    """Generate all version combinations to test."""
    keys = list(VERSIONS.keys())
    values = list(VERSIONS.values())
    combinations = list(itertools.product(*values))

    return [dict(zip(keys, combo)) for combo in combinations]

def test_version_combination(versions):
    """Test a specific version combination."""

    # Create test conanfile
    conanfile_content = f"""
from conan import ConanFile

class VersionTest(ConanFile):
    requires = "{versions['sparetools-openssl']}"
    tool_requires = "{versions['sparetools-cpython']}"
    python_requires = "{versions['sparetools-base']}"
"""

    with open("test_conanfile.py", "w") as f:
        f.write(conanfile_content)

    try:
        # Test installation
        result = subprocess.run([
            "conan", "install", "test_conanfile.py", "--build=missing"
        ], capture_output=True, timeout=300)

        return result.returncode == 0

    except subprocess.TimeoutExpired:
        return False
    finally:
        os.remove("test_conanfile.py")

# Run compatibility matrix
combinations = generate_version_combinations()
results = []

for combo in combinations:
    compatible = test_version_combination(combo)
    results.append({
        "versions": combo,
        "compatible": compatible
    })

# Save results
with open("compatibility_matrix.json", "w") as f:
    json.dump(results, f, indent=2)
```

## Automated Cross-Repository Testing

### GitHub Actions Workflow

```yaml
# .github/workflows/cross-repo-test.yml
name: Cross-Repository Testing

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  workflow_dispatch:
    inputs:
      target_repo:
        description: 'Target repository to test against'
        required: false
        default: 'sparesparrow/mia-consumer'

env:
  CONAN_VERSION: "2.21.0"

jobs:
  cross-repo-test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        target_repo: [
          'sparesparrow/mia-consumer',
          'sparesparrow/android-consumer',
          'sparesparrow/mcp-consumer'
        ]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install Conan
        run: |
          pip install conan==${{ env.CONAN_VERSION }}
          conan profile detect --force

      - name: Configure Conan remotes
        run: |
          conan remote add sparesparrow-conan \
            https://dl.cloudsmith.io/public/sparesparrow-conan/openssl-conan/conan/

      - name: Clone target repository
        run: |
          git clone https://github.com/${{ matrix.target_repo }}.git target_repo
          cd target_repo

      - name: Install dependencies
        run: |
          cd target_repo
          conan install . --build=missing

      - name: Run consumer tests
        run: |
          cd target_repo
          conan build .
          conan test test_package

      - name: Report results
        if: always()
        run: |
          echo "## Cross-Repo Test Results" >> $GITHUB_STEP_SUMMARY
          echo "- **Target:** ${{ matrix.target_repo }}" >> $GITHUB_STEP_SUMMARY
          echo "- **Status:** $status" >> $GITHUB_STEP_SUMMARY
          echo "- **Timestamp:** $(date)" >> $GITHUB_STEP_SUMMARY
```

### Local Cross-Repository Testing

```bash
#!/bin/bash
# local_cross_repo_test.sh

set -e

# Configuration
SPARETOOLS_REPO="path/to/sparetools"
CONSUMER_REPOS=(
    "path/to/mia-consumer"
    "path/to/android-consumer"
)

# Build SpareTools packages locally
echo "Building SpareTools packages..."
cd "$SPARETOOLS_REPO"
conan create packages/sparetools-base --version=2.0.0 --build=missing
conan create packages/sparetools-cpython --version=3.12.7 --build=missing
conan create packages/sparetools-openssl --version=3.3.2 --build=missing

# Test in each consumer repository
for consumer_repo in "${CONSUMER_REPOS[@]}"; do
    echo "Testing in consumer: $consumer_repo"

    cd "$consumer_repo"

    # Clean previous builds
    rm -rf build/

    # Test with local packages
    conan install . --build=missing
    conan build .
    conan test test_package

    echo "✅ $consumer_repo tests passed"
done

echo "🎉 All cross-repository tests passed!"
```

## Integration Testing Scenarios

### 1. MIA Consumer Integration

```python
# test_mia_integration.py
"""Test SpareTools in MIA consumer context."""

import os
import sys
import subprocess
from pathlib import Path

def test_mia_consumer():
    """Test MIA consumer with SpareTools packages."""

    # Create MIA consumer project
    project_dir = Path("test_mia_consumer")
    project_dir.mkdir(exist_ok=True)

    # Create pyproject.toml
    pyproject = project_dir / "pyproject.toml"
    pyproject.write_text("""
[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"

[project]
name = "mia-consumer"
version = "1.0.0"
dependencies = ["cryptography"]

[tool.setuptools]
packages = ["mia_consumer"]
""")

    # Create conanfile.py
    conanfile = project_dir / "conanfile.py"
    conanfile.write_text("""
from conan import ConanFile

class MiaConsumer(ConanFile):
    requires = "sparetools-openssl/3.3.2"
    tool_requires = "sparetools-cpython/3.12.7"

    def generate(self):
        # Generate Python environment
        pass
""")

    # Create Python package
    pkg_dir = project_dir / "mia_consumer"
    pkg_dir.mkdir()

    init_file = pkg_dir / "__init__.py"
    init_file.write_text("""
"""MIA consumer package."""

import ssl

def test_openssl_integration():
    """Test OpenSSL integration via ssl module."""
    version = ssl.OPENSSL_VERSION
    print(f"OpenSSL version: {version}")
    return version
""")

    # Test the integration
    os.chdir(project_dir)

    # Install dependencies
    subprocess.run(["conan", "install", ".", "--build=missing"], check=True)

    # Build package
    subprocess.run(["conan", "build", "."], check=True)

    # Test Python integration
    result = subprocess.run([
        sys.executable, "-c",
        "from mia_consumer import test_openssl_integration; test_openssl_integration()"
    ], capture_output=True, text=True, check=True)

    assert "OpenSSL version:" in result.stdout
    print("✅ MIA consumer integration test passed")
```

### 2. Android Consumer Integration

```python
# test_android_integration.py
"""Test SpareTools in Android consumer context."""

import os
import subprocess
from pathlib import Path

def test_android_consumer():
    """Test Android consumer with SpareTools native libraries."""

    project_dir = Path("test_android_consumer")
    project_dir.mkdir(exist_ok=True)

    # Create Android project structure
    app_dir = project_dir / "app" / "src" / "main" / "cpp"
    app_dir.mkdir(parents=True)

    # Create native conanfile.py
    conanfile = app_dir / "conanfile.py"
    conanfile.write_text("""
from conan import ConanFile

class AndroidConsumer(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    requires = "sparetools-openssl/3.3.2"

    def configure(self):
        # Android-specific configuration
        self.options["sparetools-openssl/*"].shared = False
""")

    # Create CMakeLists.txt
    cmake = app_dir / "CMakeLists.txt"
    cmake.write_text("""
cmake_minimum_required(VERSION 3.18.1)
project(android-consumer)

find_package(sparetools-openssl REQUIRED)

add_library(consumer-lib SHARED consumer.cpp)
target_link_libraries(consumer-lib sparetools-openssl::sparetools-openssl)
""")

    # Create consumer.cpp
    cpp_file = app_dir / "consumer.cpp"
    cpp_file.write_text("""
#include <jni.h>
#include <openssl/ssl.h>

extern "C" JNIEXPORT jstring JNICALL
Java_com_example_Consumer_getOpenSSLVersion(JNIEnv* env, jobject) {
    const char* version = OpenSSL_version(OPENSSL_VERSION);
    return env->NewStringUTF(version);
}
""")

    # Test Android build
    os.chdir(app_dir)

    # Install dependencies
    subprocess.run([
        "conan", "install", ".", "--build=missing",
        "-pr", "android-arm64"
    ], check=True)

    # Build with CMake
    subprocess.run([
        "cmake", "-B", "build", "-S", ".",
        "-DCMAKE_TOOLCHAIN_FILE=build/conan_toolchain.cmake"
    ], check=True)

    subprocess.run([
        "cmake", "--build", "build", "--config", "Release"
    ], check=True)

    print("✅ Android consumer integration test passed")
```

## Compatibility Testing

### Platform Compatibility Matrix

```python
# test_platform_compatibility.py
"""Test SpareTools compatibility across platforms."""

import platform
import subprocess
import sys

PLATFORMS = [
    ("linux", "x86_64", "gcc", "11"),
    ("macos", "armv8", "apple-clang", "14"),
    ("windows", "x86_64", "msvc", "193"),
]

def test_platform_compatibility():
    """Test package compatibility on different platforms."""

    current_platform = platform.system().lower()

    for os_name, arch, compiler, version in PLATFORMS:
        if current_platform == os_name or os_name == "any":
            print(f"Testing {os_name}-{arch}-{compiler}{version}")

            # Create platform-specific profile
            profile_content = f"""
[settings]
os={os_name.capitalize() if os_name != "macos" else "Macos"}
arch={arch}
compiler={compiler}
compiler.version={version}
build_type=Release
"""

            profile_file = f"profile_{os_name}_{arch}.txt"
            with open(profile_file, "w") as f:
                f.write(profile_content)

            try:
                # Test package creation
                subprocess.run([
                    "conan", "create", "packages/sparetools-openssl",
                    "--version=3.3.2",
                    f"--profile={profile_file}",
                    "--build=missing"
                ], check=True, timeout=600)

                print(f"✅ {os_name}-{arch} compatibility test passed")

            except subprocess.CalledProcessError as e:
                print(f"❌ {os_name}-{arch} compatibility test failed: {e}")
                return False
            finally:
                os.remove(profile_file)

    return True

if __name__ == "__main__":
    success = test_platform_compatibility()
    sys.exit(0 if success else 1)
```

## Continuous Integration

### Multi-Repository CI Setup

```yaml
# .github/workflows/multi-repo-ci.yml
name: Multi-Repository CI

on:
  push:
    branches: [ main ]
  schedule:
    - cron: '0 3 * * *'  # Daily integration test

jobs:
  test-sparetools-core:
    uses: sparesparrow/sparetools/.github/workflows/ci.yml@main

  test-mia-consumer:
    needs: test-sparetools-core
    uses: sparesparrow/mia-consumer/.github/workflows/integration.yml@main
    with:
      sparetools-ref: ${{ github.sha }}

  test-android-consumer:
    needs: test-sparetools-core
    uses: sparesparrow/android-consumer/.github/workflows/integration.yml@main
    with:
      sparetools-ref: ${{ github.sha }}

  integration-report:
    needs: [test-sparetools-core, test-mia-consumer, test-android-consumer]
    runs-on: ubuntu-latest
    if: always()

    steps:
      - name: Generate integration report
        run: |
          echo "## Integration Test Results" >> $GITHUB_STEP_SUMMARY
          echo "- Core: ${{ needs.test-sparetools-core.result }}" >> $GITHUB_STEP_SUMMARY
          echo "- MIA: ${{ needs.test-mia-consumer.result }}" >> $GITHUB_STEP_SUMMARY
          echo "- Android: ${{ needs.test-android-consumer.result }}" >> $GITHUB_STEP_SUMMARY
```

## Best Practices

### 1. Test Isolation

- Use separate Conan caches for different test scenarios
- Clean build artifacts between tests
- Isolate network-dependent tests

### 2. Comprehensive Coverage

- Test all supported platforms and architectures
- Include version compatibility testing
- Test both release and debug builds

### 3. Automated Reporting

- Generate detailed test reports
- Track compatibility matrices over time
- Alert on breaking changes

### 4. Performance Monitoring

- Track build times across repositories
- Monitor package sizes and dependencies
- Identify performance regressions

## Troubleshooting

### Common Issues

1. **Conan Cache Conflicts**
   ```bash
   # Clear cache between tests
   conan remove "*" -c
   conan cache clean
   ```

2. **Platform-Specific Failures**
   ```bash
   # Test with specific profile
   conan create . --profile=problematic_profile --build=missing
   ```

3. **Network Timeouts**
   ```bash
   # Increase timeouts for large builds
   conan create . --build=missing --timeout=1800
   ```

4. **Dependency Resolution Issues**
   ```bash
   # Debug dependency resolution
   conan graph info . --profile=myprofile
   ```

### Debugging Cross-Repository Tests

```bash
# Enable verbose logging
export CONAN_LOG_LEVEL=debug
export CONAN_LOG_RUN_TO_OUTPUT=false

# Run with detailed output
conan create . --build=missing -v
```

This guide provides a comprehensive framework for testing SpareTools packages across repositories and ensuring ecosystem compatibility.