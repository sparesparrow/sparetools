# SpareTools Integration Examples

Practical examples of integrating SpareTools packages into different project types and workflows.

## Table of Contents

- [Generic C++ Library](#generic-c-library)
- [MIA Python Application](#mia-python-application)
- [MCP Server Implementation](#mcp-server-implementation)
- [Android Native Integration](#android-native-integration)
- [Cross-Platform Development](#cross-platform-development)
- [CI/CD Integration](#cicd-integration)

## Generic C++ Library

### Basic Conan Integration

```cpp
// CMakeLists.txt
cmake_minimum_required(VERSION 3.15)
project(my-library)

find_package(sparetools-openssl REQUIRED)

add_library(my-library src/crypto.cpp)
target_link_libraries(my-library sparetools-openssl::sparetools-openssl)
```

```python
# conanfile.py
from conan import ConanFile

class MyLibrary(ConanFile):
    name = "my-library"
    version = "1.0.0"

    requires = "sparetools-openssl/3.3.2"
    tool_requires = "sparetools-cpython/3.12.7"

    def generate(self):
        # Generate build files
        pass
```

### Usage in Application

```python
# consumer/conanfile.py
from conan import ConanFile

class Consumer(ConanFile):
    requires = "my-library/1.0.0"
    tool_requires = "sparetools-cpython/3.12.7"
```

## MIA Python Application

### Hermetic Python Environment

```python
# conanfile.py
from conan import ConanFile
from conan.tools.python import PythonDeps

class MiaApp(ConanFile):
    name = "mia-app"
    version = "1.0.0"

    # Hermetic Python environment
    tool_requires = "sparetools-cpython/3.12.7"

    # OpenSSL for crypto operations
    requires = "sparetools-openssl/3.3.2"

    def generate(self):
        py_deps = PythonDeps(self)
        py_deps.generate()
```

```python
# main.py
import ssl
import OpenSSL

# Uses SpareTools OpenSSL
context = ssl.create_default_context()
print(f"OpenSSL version: {ssl.OPENSSL_VERSION}")

# Your application code here
def encrypt_data(data: bytes, key: bytes) -> bytes:
    # Use OpenSSL through Python ssl module
    # This automatically uses SpareTools OpenSSL
    pass
```

### PyPI Package with Native Dependencies

```toml
# pyproject.toml
[build-system]
requires = ["setuptools", "conan"]
build-backend = "setuptools.build_meta"

[project]
name = "mia-app"
dependencies = [
    "cryptography>=3.4.0",
    "requests>=2.25.0",
]

[tool.conan]
requirements = ["sparetools-openssl/3.3.2"]
tool_requires = ["sparetools-cpython/3.12.7"]
```

## MCP Server Implementation

### Basic MCP Server Structure

```python
# server.py
import asyncio
from mcp import Server, Tool
from conan.tools.python import PythonDeps

class MyMcpServer:
    def __init__(self):
        self.server = Server("my-mcp-server")

        # Register tools
        @self.server.list_tools()
        async def list_tools():
            return [
                Tool(
                    name="crypto_encrypt",
                    description="Encrypt data using OpenSSL",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "data": {"type": "string"},
                            "algorithm": {"type": "string", "enum": ["aes", "rsa"]}
                        }
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(request):
            if request.params.name == "crypto_encrypt":
                # Use SpareTools OpenSSL for encryption
                result = encrypt_with_sparetools(
                    request.params.arguments["data"],
                    request.params.arguments["algorithm"]
                )
                return [TextContent(type="text", text=result)]

    async def run(self):
        async with self.server.stdio_server() as streams:
            await self.server.serve(*streams)
```

```python
# conanfile.py
from conan import ConanFile

class McpServer(ConanFile):
    name = "mcp-server"
    version = "1.0.0"

    requires = "sparetools-openssl/3.3.2"
    tool_requires = "sparetools-cpython/3.12.7"

    # Python requirements
    def requirements(self):
        self.requires("mcp/0.1.0")  # Hypothetical MCP package
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.12-slim

# Copy Conan configuration
COPY conanfile.py ./

# Install dependencies via Conan
RUN pip install conan && \
    conan install . --build=missing && \
    conan build .

# Copy application
COPY src/ ./

# Run MCP server
CMD ["python", "-m", "mcp_server"]
```

## Android Native Integration

### JNI with SpareTools

```cpp
// native-lib.cpp
#include <jni.h>
#include <openssl/ssl.h>
#include <openssl/err.h>

// Use SpareTools OpenSSL
extern "C" JNIEXPORT jstring JNICALL
Java_com_example_app_NativeLib_getOpenSSLVersion(
    JNIEnv* env, jobject /* this */) {

    const char* version = OpenSSL_version(OPENSSL_VERSION);
    return env->NewStringUTF(version);
}

JNIEXPORT jbyteArray JNICALL
Java_com_example_app_NativeLib_encryptData(
    JNIEnv* env, jobject /* this */,
    jbyteArray data, jbyteArray key) {

    // JNI array handling
    jsize data_len = env->GetArrayLength(data);
    jbyte* data_ptr = env->GetByteArrayElements(data, nullptr);
    jbyte* key_ptr = env->GetByteArrayElements(key, nullptr);

    // Use OpenSSL for encryption
    // (Implementation details...)

    // Release arrays
    env->ReleaseByteArrayElements(data, data_ptr, JNI_ABORT);
    env->ReleaseByteArrayElements(key, key_ptr, JNI_ABORT);

    // Return encrypted data
    jbyteArray result = env->NewByteArray(data_len);
    env->SetByteArrayRegion(result, 0, data_len, encrypted_data);
    return result;
}
```

```kotlin
// MainActivity.kt
class MainActivity : ComponentActivity() {
    external fun getOpenSSLVersion(): String
    external fun encryptData(data: ByteArray, key: ByteArray): ByteArray

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val opensslVersion = getOpenSSLVersion()
        println("Using SpareTools OpenSSL: $opensslVersion")

        // Use encrypted data in your app
        val data = "Hello World".toByteArray()
        val key = "secretkey123".toByteArray()
        val encrypted = encryptData(data, key)
    }

    companion object {
        init {
            System.loadLibrary("native-lib")
        }
    }
}
```

```python
# app/src/main/cpp/conanfile.py
from conan import ConanFile

class AndroidNative(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    requires = "sparetools-openssl/3.3.2"

    def configure(self):
        # Android-specific configuration
        self.options["sparetools-openssl/*"].shared = False
        self.options["sparetools-openssl/*"].no_threads = False
```

### Gradle Integration

```kotlin
// app/build.gradle.kts
android {
    externalNativeBuild {
        cmake {
            path = file("src/main/cpp/CMakeLists.txt")
        }
    }
}

dependencies {
    // Conan-generated dependencies
    implementation(fileTree(mapOf("dir" to "conan", "include" to "*.jar")))
}
```

## Cross-Platform Development

### Multi-Platform Conan Profiles

```python
# profiles/linux-gcc
[settings]
os=Linux
arch=x86_64
compiler=gcc
compiler.version=11
compiler.libcxx=libstdc++11
build_type=Release

[conf]
tools.cmake.cmaketoolchain:generator=Ninja
```

```python
# profiles/macos-clang
[settings]
os=Macos
arch=armv8
compiler=apple-clang
compiler.version=14
compiler.libcxx=libc++
build_type=Release
```

```python
# profiles/windows-msvc
[settings]
os=Windows
arch=x86_64
compiler=msvc
compiler.version=193
compiler.runtime=dynamic
build_type=Release
```

### Unified Build Script

```bash
#!/bin/bash
# build.sh

PROFILES=("linux-gcc" "macos-clang" "windows-msvc")

for profile in "${PROFILES[@]}"; do
    echo "Building for $profile..."

    conan create . \
        --version=1.0.0 \
        --profile=profiles/$profile \
        --build=missing

    # Archive build artifacts
    mkdir -p artifacts/$profile
    cp -r build/* artifacts/$profile/
done
```

### Platform-Specific Code

```cpp
// platform.h
#pragma once

#ifdef _WIN32
    #include <windows.h>
    #define PLATFORM_WINDOWS
#elif __APPLE__
    #include <TargetConditionals.h>
    #if TARGET_OS_MAC
        #define PLATFORM_MACOS
    #endif
#elif __linux__
    #define PLATFORM_LINUX
#endif

// Platform-specific OpenSSL usage
#include <openssl/ssl.h>

// Consistent API across platforms
SSL_CTX* create_ssl_context();
```

## CI/CD Integration

### GitHub Actions with Templates

```yaml
# .github/workflows/ci.yml (generated from template)
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  build:
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]

    runs-on: ${{ matrix.os }}

    steps:
      - uses: actions/checkout@v4

      - name: Setup Conan
        run: |
          pip install conan==2.21.0
          conan profile detect --force

      - name: Configure SpareTools remote
        run: conan remote add sparesparrow-conan https://dl.cloudsmith.io/public/sparesparrow-conan/openssl-conan/conan/

      - name: Build with SpareTools
        run: |
          conan install . --build=missing
          conan build .

      - name: Test
        run: conan test test_package
```

### Automated Dependency Updates

```yaml
# .github/workflows/update-dependencies.yml
name: Update Dependencies

on:
  schedule:
    - cron: '0 2 * * 1'  # Weekly on Monday
  workflow_dispatch:

jobs:
  update-deps:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Update Conan dependencies
        run: |
          conan graph update . > dependencies.json

      - name: Create update PR
        uses: peter-evans/create-pull-request@v5
        with:
          title: "chore: update dependencies"
          body: "Automated dependency updates"
          branch: update-dependencies
```

## Troubleshooting Common Issues

### Python Path Issues

```python
# Ensure proper Python path in conanfile.py
def package_info(self):
    self.conf_info["user.cpython:site_packages"] = os.path.join(self.package_folder, "src")
    self.env_info.PYTHONPATH.append(os.path.join(self.package_folder, "src"))
```

### Android NDK Compatibility

```python
# Ensure NDK compatibility
def configure(self):
    if self.settings.os == "Android":
        # Use compatible OpenSSL options for Android
        self.options["sparetools-openssl/*"].no_threads = False
        self.options["sparetools-openssl/*"].no_stdlib_check = True
```

### Cross-Compilation Issues

```bash
# Set up cross-compilation environment
export CC=arm-linux-gnueabihf-gcc
export CXX=arm-linux-gnueabihf-g++
export AR=arm-linux-gnueabihf-ar

conan create . --profile=rpi --build=missing
```

These examples demonstrate how to effectively integrate SpareTools packages into various project types while maintaining hermetic, reproducible builds across platforms.