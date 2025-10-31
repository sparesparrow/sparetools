# Windows Build Guide for SpareTools OpenSSL

This guide covers building OpenSSL with SpareTools on Windows using MSVC (Visual Studio).

## Prerequisites

### Required Software

1. **Visual Studio 2022** (Community, Professional, or Enterprise)
   - Download: https://visualstudio.microsoft.com/downloads/
   - Required workloads:
     - Desktop development with C++
     - C++ CMake tools for Windows

2. **Perl** (Active Perl or Strawberry Perl)
   - Required for OpenSSL's Perl Configure script
   - Download: https://www.activestate.com/products/perl/ or https://strawberryperl.com/
   - Add to PATH during installation

3. **Conan 2.x**
   ```bash
   pip install conan
   ```

4. **Python 3.10+** (for optional Python build method)
   ```bash
   # Download from python.org or use Windows Store
   ```

### Environment Setup

1. **Visual Studio Command Line**

   Open "Developer Command Prompt for VS 2022":

   ```cmd
   # This sets up MSVC compiler and build tools
   "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
   ```

2. **Verify Perl Installation**

   ```cmd
   perl --version
   ```

3. **Verify Conan Installation**

   ```cmd
   conan --version
   ```

---

## Quick Start

### 1. Clone Repository

```cmd
git clone https://github.com/sparesparrow/sparetools.git
cd sparetools
```

### 2. Build OpenSSL (x86_64)

```cmd
cd packages\sparetools-openssl

conan create . --version=3.3.2 ^
  -pr:b ..\sparetools-openssl-tools\profiles\base\windows-msvc2022 ^
  --build=missing
```

### 3. Build OpenSSL (ARM64)

```cmd
cd packages\sparetools-openssl

conan create . --version=3.3.2 ^
  -pr:b ..\sparetools-openssl-tools\profiles\base\windows-msvc2022-arm64 ^
  --build=missing
```

---

## Build Options

### Windows MSVC Build Profiles

Available profiles for Windows:

| Profile | Architecture | Use Case |
|---------|---|---|
| `windows-msvc2022` | x86_64 | Standard 64-bit Windows |
| `windows-msvc2022-arm64` | ARM64 | Windows on ARM (Surface X, etc.) |

### Command Line Options

Control build behavior with options:

```cmd
conan create . --version=3.3.2 ^
  -pr:b ..\sparetools-openssl-tools\profiles\base\windows-msvc2022 ^
  -o sparetools-openssl/*:shared=False ^
  -o sparetools-openssl/*:enable_asm=True ^
  -o sparetools-openssl/*:enable_zlib=True ^
  --build=missing
```

### Available Options

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `shared` | True/False | False | Build shared libraries (.dll) |
| `build_method` | perl, cmake | perl | Build method (Perl Configure) |
| `enable_asm` | True/False | True | Enable assembly optimizations |
| `enable_avx` | True/False | True | Enable AVX instructions |
| `enable_avx2` | True/False | True | Enable AVX2 instructions |
| `enable_zlib` | True/False | True | Enable zlib compression support |
| `enable_threads` | True/False | True | Enable threading support |

---

## Feature Profiles

### Assembly Optimizations

```cmd
# Maximum performance (AVX2)
conan create . --version=3.3.2 ^
  -pr:b ..\sparetools-openssl-tools\profiles\base\windows-msvc2022 ^
  -pr:b ..\sparetools-openssl-tools\profiles\features\assembly-optimized ^
  --build=missing

# AVX only (older CPUs)
conan create . --version=3.3.2 ^
  -pr:b ..\sparetools-openssl-tools\profiles\base\windows-msvc2022 ^
  -pr:b ..\sparetools-openssl-tools\profiles\features\assembly-avx-only ^
  --build=missing

# No assembly (pure C)
conan create . --version=3.3.2 ^
  -pr:b ..\sparetools-openssl-tools\profiles\base\windows-msvc2022 ^
  -pr:b ..\sparetools-openssl-tools\profiles\features\assembly-minimal ^
  --build=missing
```

### FIPS Support

```cmd
# Build with FIPS enabled
conan create . --version=3.3.2 ^
  -pr:b ..\sparetools-openssl-tools\profiles\base\windows-msvc2022 ^
  -pr:b ..\sparetools-openssl-tools\profiles\features\fips-enabled ^
  --build=missing
```

---

## Testing

### Run Integration Tests

```cmd
cd packages\sparetools-openssl

conan test test_package sparetools-openssl/3.3.2@ ^
  -pr:b ..\sparetools-openssl-tools\profiles\base\windows-msvc2022

# With provider tests
conan test test_package sparetools-openssl/3.3.2@ ^
  -pr:b ..\sparetools-openssl-tools\profiles\base\windows-msvc2022 ^
  -o "*:test_provider=default"

# With FIPS tests
conan test test_package sparetools-openssl/3.3.2@ ^
  -pr:b ..\sparetools-openssl-tools\profiles\base\windows-msvc2022 ^
  -o "*:test_fips=True"
```

### Test Package Contents

The test suite includes:
1. **Basic OpenSSL tests** - SHA-256 hashing
2. **Provider ordering tests** - Algorithm availability
3. **FIPS smoke tests** - FIPS compliance (if enabled)

---

## Using Built Package

### Consume in Your Project

Create a `conanfile.py`:

```python
from conan import ConanFile
from conan.tools.cmake import cmake_layout, CMake

class MyAppConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    requires = "sparetools-openssl/3.3.2"
    generators = "CMakeDeps", "CMakeToolchain"

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
```

Install and build:

```cmd
conan install . -pr:b ..\sparetools-openssl-tools\profiles\base\windows-msvc2022
conan build .
```

### CMake Integration

In your `CMakeLists.txt`:

```cmake
cmake_minimum_required(VERSION 3.15)
project(MyApp CXX)

find_package(OpenSSL REQUIRED)

add_executable(myapp main.cpp)
target_link_libraries(myapp PRIVATE OpenSSL::SSL OpenSSL::Crypto)
```

---

## Troubleshooting

### Build Failure: "perl not found"

**Problem:** Configure script can't find Perl

**Solution:**
1. Install Perl (ActiveState or Strawberry)
2. Verify Perl is in PATH: `perl --version`
3. Restart command prompt after Perl installation

### Build Failure: "nmake not found"

**Problem:** Build tool can't find nmake

**Solution:**
1. Open "Developer Command Prompt for VS 2022"
2. nmake should be available in that environment
3. Or add to PATH: `C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.xx.xxxxx\bin\Hostx64\x64\`

### Build Failure: "MSVC compiler not found"

**Problem:** Conan can't find MSVC compiler

**Solution:**
1. Install Visual Studio C++ development tools
2. Run Developer Command Prompt
3. Set Conan profile: `conan profile detect --force`

### Long Paths Error

**Problem:** "The filename or extension is too long"

**Solution:**
1. Enable long paths in Windows:
   ```cmd
   reg add HKLM\SYSTEM\CurrentControlSet\Control\FileSystem /v LongPathsEnabled /t REG_DWORD /d 1
   ```
2. Or build in a shorter path directory

### ARM64 Build Issues

**Problem:** Build fails on ARM64 platform

**Solution:**
1. Use `windows-msvc2022-arm64` profile
2. Cross-compilation is not supported by default
3. Build on native ARM64 Windows machine

---

## Advanced Usage

### Custom Profile

Create a custom profile file `my-windows-profile`:

```
include(../sparetools-openssl-tools/profiles/base/windows-msvc2022)

[settings]
build_type=Debug

[options]
sparetools-openssl/*:shared=True
sparetools-openssl/*:enable_asm=False
```

Use it:

```cmd
conan create . --version=3.3.2 -pr:b my-windows-profile --build=missing
```

### Local Development Build

For development without uploading:

```cmd
# Create local
conan create . --version=3.3.2 ^
  -pr:b ..\sparetools-openssl-tools\profiles\base\windows-msvc2022

# Install locally
conan install --requires=sparetools-openssl/3.3.2
```

### Multi-Configuration CI/CD

```cmd
REM Build x86_64
conan create . --version=3.3.2 ^
  -pr:b ..\sparetools-openssl-tools\profiles\base\windows-msvc2022

REM Build ARM64
conan create . --version=3.3.2 ^
  -pr:b ..\sparetools-openssl-tools\profiles\base\windows-msvc2022-arm64

REM Run tests for both
conan test test_package sparetools-openssl/3.3.2@ ^
  -pr:b ..\sparetools-openssl-tools\profiles\base\windows-msvc2022

conan test test_package sparetools-openssl/3.3.2@ ^
  -pr:b ..\sparetools-openssl-tools\profiles\base\windows-msvc2022-arm64
```

---

## Windows Batch Script Template

Create `build-openssl.bat`:

```batch
@echo off
REM SpareTools OpenSSL Windows Build Script

setlocal enabledelayedexpansion

REM Check for Visual Studio
if not defined VCVARS_VER (
    echo Opening Developer Command Prompt...
    call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
)

REM Check prerequisites
perl --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Perl not found. Please install Perl and add to PATH.
    exit /b 1
)

echo Building OpenSSL with SpareTools...
cd packages\sparetools-openssl

REM Build for x86_64
echo.
echo Building for x86_64...
conan create . --version=3.3.2 ^
    -pr:b ..\sparetools-openssl-tools\profiles\base\windows-msvc2022 ^
    --build=missing
if errorlevel 1 (
    echo ERROR: x86_64 build failed
    exit /b 1
)

REM Optional: Build for ARM64
if "%1"=="--arm64" (
    echo.
    echo Building for ARM64...
    conan create . --version=3.3.2 ^
        -pr:b ..\sparetools-openssl-tools\profiles\base\windows-msvc2022-arm64 ^
        --build=missing
    if errorlevel 1 (
        echo ERROR: ARM64 build failed
        exit /b 1
    )
)

echo.
echo Build completed successfully!
```

Run:
```cmd
build-openssl.bat
build-openssl.bat --arm64  # Include ARM64
```

---

## PowerShell Script Template

Create `build-openssl.ps1`:

```powershell
# SpareTools OpenSSL Windows Build Script

param(
    [switch]$Arm64,
    [switch]$Assembly,
    [switch]$FIPS
)

# Check prerequisites
Write-Host "Checking prerequisites..."

# Check Perl
$perl = Get-Command perl -ErrorAction SilentlyContinue
if (-not $perl) {
    Write-Error "Perl not found. Please install and add to PATH."
    exit 1
}

# Check Conan
$conan = Get-Command conan -ErrorAction SilentlyContinue
if (-not $conan) {
    Write-Error "Conan not found. Please install: pip install conan"
    exit 1
}

Write-Host "Found Perl: $($perl.Source)"
Write-Host "Found Conan: $($conan.Source)"

# Build arguments
$buildArgs = @(
    "create", ".", "--version=3.3.2",
    "-pr:b", "..\sparetools-openssl-tools\profiles\base\windows-msvc2022"
)

if ($Assembly) {
    $buildArgs += "-pr:b", "..\sparetools-openssl-tools\profiles\features\assembly-optimized"
}

if ($FIPS) {
    $buildArgs += "-pr:b", "..\sparetools-openssl-tools\profiles\features\fips-enabled"
}

$buildArgs += "--build=missing"

# Build
Set-Location packages\sparetools-openssl
Write-Host "Building OpenSSL x86_64..."
& conan @buildArgs

if ($LASTEXITCODE -ne 0) {
    Write-Error "Build failed"
    exit 1
}

if ($Arm64) {
    Write-Host "Building OpenSSL ARM64..."
    $buildArgs[3] = "..\sparetools-openssl-tools\profiles\base\windows-msvc2022-arm64"
    & conan @buildArgs

    if ($LASTEXITCODE -ne 0) {
        Write-Error "ARM64 build failed"
        exit 1
    }
}

Write-Host "Build completed successfully!"
```

Run:
```powershell
.\build-openssl.ps1
.\build-openssl.ps1 -Arm64 -Assembly -FIPS
```

---

## CI/CD with GitHub Actions

```yaml
name: Build OpenSSL Windows

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  windows-build:
    runs-on: windows-latest
    strategy:
      matrix:
        include:
          - arch: x86_64
            profile: windows-msvc2022
          - arch: arm64
            profile: windows-msvc2022-arm64

    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install Conan
        run: pip install conan

      - name: Install Perl
        uses: crazy-max/ghaction-chocolatey@v3
        with:
          args: install strawberryperl

      - name: Build OpenSSL
        run: |
          cd packages\sparetools-openssl
          conan create . --version=3.3.2 `
            -pr:b ..\sparetools-openssl-tools\profiles\base\${{ matrix.profile }} `
            --build=missing

      - name: Run Tests
        run: |
          conan test test_package sparetools-openssl/3.3.2@ `
            -pr:b packages\sparetools-openssl-tools\profiles\base\${{ matrix.profile }}
```

---

## References

- [OpenSSL Installation](https://github.com/openssl/openssl/blob/master/INSTALL.md)
- [Visual Studio Download](https://visualstudio.microsoft.com/downloads/)
- [Strawberry Perl](https://strawberryperl.com/)
- [Active State Perl](https://www.activestate.com/products/perl/)
- [Conan Documentation](https://docs.conan.io/)

---

## Support

For Windows-specific issues:
1. Check this guide
2. Review OpenSSL documentation
3. Create a GitHub issue with:
   - Windows version
   - Visual Studio version
   - Build command and full error log
   - Perl version
