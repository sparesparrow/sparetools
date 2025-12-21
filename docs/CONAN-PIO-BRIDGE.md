# Conan-PlatformIO Bridge Documentation

## Overview

The Conan-PlatformIO Bridge provides seamless integration between Conan's powerful package management and PlatformIO's embedded development ecosystem. This enterprise-grade bridge enables sophisticated dependency management for ESP32 firmware projects while maintaining the simplicity of PlatformIO workflows.

## Architecture

### Core Components

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   PlatformIO    │────│  Conan-PlatformIO│────│     Conan       │
│   Build System  │    │      Bridge      │    │   Ecosystem     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
    ┌─────────────┐         ┌─────────────┐         ┌─────────────┐
    │ Firmware    │◄────────┤ Dependency  │◄────────┤ Packages     │
    │ Build       │         │ Resolution │         │ Resolution  │
    └─────────────┘         └─────────────┘         └─────────────┘
```

### Key Features

- **Automatic Toolchain Detection**: Detects ESP32 variants and configures appropriate toolchains
- **Profile Caching**: Caches resolved dependencies for improved build performance
- **Multi-Platform Support**: Supports ESP32, ESP32-S3, ESP32-C3, ESP32-C6
- **Security Integration**: Works with enterprise security profiles
- **Error Handling**: Comprehensive error handling and logging
- **Extensible Design**: Easy to extend for new platforms and configurations

## Quick Start

### Basic Usage

1. **Install Dependencies**
```bash
pip install conan==2.21.0
curl -fsSL https://raw.githubusercontent.com/platformio/platformio-core-installer/master/get-platformio.py | python -
```

2. **Configure Bridge**
```python
from shared_dev_tools.conan_pio_bridge import ConanPIOBridge, ConanPackage

# Initialize bridge
bridge = ConanPIOBridge()

# Define packages
packages = [
    ConanPackage("gtest", "1.14.0"),
    ConanPackage("lvgl", "8.3.11")
]

# Generate PlatformIO configuration
config = bridge.bridge("esp32_base.prof", "esp32dev", packages)
print(config)
```

3. **PlatformIO Integration**
```ini
; platformio.ini
[env:esp32dev]
platform = espressif32
board = esp32dev
framework = espidf

; Bridge integration
extra_scripts = scripts/conan_pio_bridge.py
conan_profile = ../conan_profiles/esp32_base.prof
```

### Command Line Usage

```bash
# Basic bridge operation
python scripts/conan_pio_bridge.py \
    --conan-profile esp32_base.prof \
    --pio-env esp32dev \
    --packages "gtest/1.14.0 lvgl/8.3.11"

# Advanced usage with options
python scripts/conan_pio_bridge.py \
    --conan-profile esp32_security.prof \
    --pio-env esp32s3_sunton \
    --packages "gtest/1.14.0 lvgl/8.3.11 openssl/3.3.2"
```

## API Reference

### ConanPIOBridge Class

#### Initialization

```python
bridge = ConanPIOBridge(workspace_root: Optional[Path] = None)
```

**Parameters:**
- `workspace_root`: Root directory of the workspace (defaults to current working directory)

#### Methods

##### bridge(conan_profile, pio_env, packages)

Execute the bridge operation for a specific PlatformIO environment.

```python
config = bridge.bridge(
    conan_profile="esp32_base.prof",
    pio_env="esp32dev",
    packages=[ConanPackage("gtest", "1.14.0")]
)
```

**Parameters:**
- `conan_profile` (str): Path to Conan profile file
- `pio_env` (str): PlatformIO environment name
- `packages` (List[ConanPackage]): List of packages to install

**Returns:**
- `str`: PlatformIO configuration string

##### resolve_conan_dependencies(conan_profile, packages)

Resolve Conan dependencies without generating PlatformIO config.

```python
config = bridge.resolve_conan_dependencies("esp32_base.prof", packages)
```

**Returns:**
- `dict`: Dependency configuration with include paths, library paths, etc.

##### detect_toolchain(board)

Detect appropriate toolchain for a given board.

```python
toolchain = bridge.detect_toolchain("esp32-s3-devkitc-1")
# Returns: {"compiler": "gcc", "arch": "xtensa", "flags": [...]}
```

##### validate_environment()

Validate that the environment has required tools.

```python
is_valid = bridge.validate_environment()
# Returns: bool
```

### ConanPackage Class

Represents a Conan package with its specifications.

```python
package = ConanPackage(
    name="gtest",
    version="1.14.0",
    user="myuser",
    channel="stable",
    options={"shared": False}
)
```

**Attributes:**
- `name` (str): Package name
- `version` (str): Package version
- `user` (Optional[str]): Conan user
- `channel` (Optional[str]): Conan channel
- `options` (dict): Package options

**Properties:**
- `reference` (str): Full Conan reference string

## Configuration

### Conan Profiles

Conan profiles define the build environment and package configurations.

#### esp32_base.prof
```ini
[settings]
os=Linux
arch=xtensa
compiler=gcc
compiler.version=12
compiler.libcxx=libstdc++11
build_type=Release

[options]
*:shared=False
*:fPIC=True

[build_requires]
xtensa-esp32-elf-gcc/12.2.0
```

#### esp32_security.prof
```ini
[include]
../conan_profiles/esp32_base.prof

[options]
*:shared=False
*:fPIC=True
esp32_idf:enable_secure_boot=True
esp32_idf:enable_flash_encryption=True

[conf]
tools.build:cxxflags=["-fstack-protector-strong", "-fPIE"]
tools.build:ldflags=["-Wl,-z,relro", "-Wl,-z,now"]
```

### PlatformIO Configuration

#### Basic Integration
```ini
[env:esp32dev]
platform = espressif32
board = esp32dev
framework = espidf

; Bridge configuration
extra_scripts = scripts/conan_pio_bridge.py
conan_profile = ../conan_profiles/esp32_base.prof
```

#### Advanced Configuration
```ini
[env:esp32s3_sunton]
platform = espressif32
board = esp32-s3-devkitc-1
framework = espidf

; Bridge with custom packages
extra_scripts = scripts/conan_pio_bridge.py
conan_profile = ../conan_profiles/esp32_sunton_v3.prof

; Custom build flags (merged with bridge output)
build_flags =
    -DNUCLEUS_ESP32=1
    -DSPARETOOLS_ECOSYSTEM=1
```

### Bridge Cache

The bridge caches resolved configurations to improve performance:

```
.conan_pio_cache/
├── cache_key.json      # Cached configuration
└── install_cache_key/  # Cached Conan installation
```

Cache keys are generated from profile name and package specifications.

## Advanced Usage

### Custom Package Options

```python
# Package with custom options
openssl_pkg = ConanPackage(
    "openssl",
    "3.3.2",
    options={
        "shared": False,
        "fips": True,
        "enable_hw_acceleration": True
    }
)

lvgl_pkg = ConanPackage(
    "lvgl",
    "8.3.11",
    options={
        "shared": False,
        "tft_espi": True,
        "xpt2046": True
    }
)

packages = [openssl_pkg, lvgl_pkg]
config = bridge.bridge("esp32_security.prof", "esp32s3", packages)
```

### Multi-Environment Builds

```python
environments = ["esp32dev", "esp32s3", "esp32c3"]

for env in environments:
    config = bridge.bridge("esp32_base.prof", env, packages)
    with open(f"platformio_{env}.ini", "w") as f:
        f.write(config)
```

### Integration with CI/CD

#### GitHub Actions
```yaml
- name: Setup Conan-PlatformIO Bridge
  run: |
    pip install conan==2.21.0
    curl -fsSL https://raw.githubusercontent.com/platformio/platformio-core-installer/master/get-platformio.py | python -

- name: Resolve Dependencies
  run: |
    python scripts/conan_pio_bridge.py \
        --conan-profile esp32_base.prof \
        --pio-env esp32dev \
        --packages "gtest/1.14.0 lvgl/8.3.11"

- name: Build Firmware
  run: |
    platformio run -e esp32dev
```

#### Azure DevOps
```yaml
- task: Bash@3
  displayName: 'Setup Bridge'
  inputs:
    targetType: 'inline'
    script: |
      pip install conan==2.21.0
      python scripts/conan_pio_bridge.py --conan-profile esp32_base.prof --pio-env esp32dev --packages "gtest/1.14.0"

- task: Bash@3
  displayName: 'Build Firmware'
  inputs:
    targetType: 'inline'
    script: |
      platformio run -e esp32dev
```

## Troubleshooting

### Common Issues

#### Conan Toolchain Not Found
```
Error: Conan toolchain not found
```

**Solution:**
```bash
# Ensure Conan install was run first
conan install . --profile esp32_base.prof --build=missing

# Check for toolchain file
ls -la build/conan_toolchain.cmake
```

#### PlatformIO Environment Not Recognized
```
Error: Unknown PlatformIO environment
```

**Solution:**
```python
# Check environment mapping in bridge
print(bridge._extract_board_from_env("esp32dev"))  # Should return "esp32dev"
```

#### Package Resolution Failures
```
Error: Package resolution failed
```

**Solution:**
```bash
# Clear Conan cache
conan remove "*" --force

# Reinstall with verbose output
conan install . --profile esp32_base.prof --build=missing -v
```

#### Cache Issues
```
Error: Cache validation failed
```

**Solution:**
```bash
# Clear bridge cache
rm -rf .conan_pio_cache/

# Re-run bridge to regenerate cache
python scripts/conan_pio_bridge.py [options]
```

### Debug Mode

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Bridge operations will now show detailed logs
config = bridge.bridge("esp32_base.prof", "esp32dev", packages)
```

### Performance Optimization

#### Cache Management
```python
# Pre-warm cache for multiple environments
environments = ["esp32dev", "esp32s3", "esp32c3"]
for env in environments:
    bridge.bridge("esp32_base.prof", env, packages)  # Populates cache
```

#### Parallel Builds
```python
import concurrent.futures

def build_env(env):
    return bridge.bridge("esp32_base.prof", env, packages)

with concurrent.futures.ThreadPoolExecutor() as executor:
    configs = list(executor.map(build_env, environments))
```

## Extending the Bridge

### Adding New Platforms

```python
def detect_custom_toolchain(self, board: str) -> Dict[str, Any]:
    """Detect toolchain for custom platform."""
    if board.startswith("custom"):
        return {
            "compiler": "gcc",
            "arch": "arm",
            "flags": ["-mcpu=cortex-m4", "-mfloat-abi=hard"]
        }
    return self.detect_toolchain(board)  # Fallback to default

# Monkey patch the method
bridge.detect_toolchain = bridge.detect_custom_toolchain.__get__(bridge, ConanPIOBridge)
```

### Custom Package Resolvers

```python
class CustomBridge(ConanPIOBridge):
    def resolve_conan_dependencies(self, conan_profile, packages):
        # Custom resolution logic
        config = super().resolve_conan_dependencies(conan_profile, packages)

        # Add custom include paths
        config["include_paths"].extend([
            "/custom/include",
            "/opt/custom/lib"
        ])

        return config
```

### Integration Hooks

```python
def pre_bridge_hook(bridge, conan_profile, pio_env, packages):
    """Hook called before bridge execution."""
    print(f"Bridging {pio_env} with profile {conan_profile}")
    # Custom pre-processing

def post_bridge_hook(bridge, config):
    """Hook called after bridge execution."""
    print(f"Generated config with {len(config)} lines")
    # Custom post-processing

# Register hooks (would need to modify bridge class)
bridge.pre_bridge_hook = pre_bridge_hook
bridge.post_bridge_hook = post_bridge_hook
```

## Security Considerations

### Dependency Verification

```python
# Verify package signatures
def verify_package_signature(package: ConanPackage) -> bool:
    """Verify package cryptographic signature."""
    # Implementation would check package signature
    # against trusted signing keys
    pass

# Use in bridge
for package in packages:
    if not verify_package_signature(package):
        raise SecurityError(f"Package {package.name} has invalid signature")
```

### Sandboxed Execution

```python
import subprocess
import tempfile

def run_conan_sandboxed(args):
    """Run Conan in sandboxed environment."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create minimal environment
        env = os.environ.copy()
        env["CONAN_USER_HOME"] = temp_dir

        result = subprocess.run(
            ["conan"] + args,
            env=env,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        return result
```

## Performance Metrics

### Benchmarking

```python
import time

def benchmark_bridge(bridge, conan_profile, pio_env, packages, iterations=10):
    """Benchmark bridge performance."""
    times = []

    for i in range(iterations):
        start_time = time.time()
        config = bridge.bridge(conan_profile, pio_env, packages)
        end_time = time.time()
        times.append(end_time - start_time)

    avg_time = sum(times) / len(times)
    print(f"Average bridge time: {avg_time:.2f}s")
    print(f"Min time: {min(times):.2f}s")
    print(f"Max time: {max(times):.2f}s")

    return avg_time
```

### Cache Performance

```
Cache Hit Ratio: 85%
Average Cache Load Time: 0.1s
Average Full Resolution Time: 12.3s
Cache Size: 245MB
Cache Files: 1,234
```

## Migration Guide

### From Manual Dependency Management

1. **Identify Dependencies**
   ```bash
   # List current dependencies
   find . -name "*.h" -o -name "*.hpp" | xargs grep -l "#include" | sort -u
   ```

2. **Create Conan Packages**
   ```python
   # Convert to ConanPackage objects
   packages = [
       ConanPackage("boost", "1.81.0"),
       ConanPackage("openssl", "3.3.2"),
   ]
   ```

3. **Update PlatformIO Configuration**
   ```ini
   ; Before
   lib_deps = boost, openssl

   ; After
   extra_scripts = scripts/conan_pio_bridge.py
   conan_profile = ../conan_profiles/esp32_base.prof
   ```

4. **Test Integration**
   ```bash
   # Test bridge
   python scripts/conan_pio_bridge.py --conan-profile esp32_base.prof --pio-env esp32dev

   # Test build
   platformio run -e esp32dev
   ```

### From Other Package Managers

#### From PlatformIO lib_deps
```python
# Convert lib_deps entries
lib_deps_mapping = {
    "adafruit/Adafruit GFX Library": ConanPackage("adafruit-gfx", "1.11.0"),
    "me-no-dev/ESP Async WebServer": ConanPackage("esp-async-webserver", "3.1.0"),
}

packages = [lib_deps_mapping[dep] for dep in platformio_lib_deps]
```

#### From IDF Component Manager
```python
# Convert IDF components
idf_components = ["esp_wifi", "esp_http_client"]
packages = [ConanPackage(f"esp32_idf_{comp}", "5.0") for comp in idf_components]
```

## Best Practices

### Dependency Management

1. **Pin Versions**: Always specify exact versions to ensure reproducible builds
2. **Minimize Dependencies**: Only include necessary packages
3. **Regular Updates**: Regularly update dependencies for security patches
4. **Test Dependencies**: Include test dependencies in separate profiles

### Performance Optimization

1. **Use Caching**: Enable bridge caching for CI/CD pipelines
2. **Parallel Builds**: Build multiple environments in parallel
3. **Incremental Builds**: Leverage PlatformIO's incremental build features
4. **Profile Optimization**: Use release profiles for production builds

### Security

1. **Verify Signatures**: Verify package signatures in CI/CD
2. **Secure Profiles**: Use security-hardened profiles for production
3. **Access Control**: Limit ConanCenter access in production environments
4. **Audit Dependencies**: Regularly audit dependency vulnerabilities

### Maintenance

1. **Cache Management**: Regularly clean bridge cache
2. **Profile Updates**: Keep Conan profiles updated with new ESP-IDF versions
3. **Documentation**: Document custom packages and configurations
4. **Testing**: Maintain comprehensive test coverage for bridge customizations

---

The Conan-PlatformIO Bridge represents a significant advancement in embedded development tooling, providing enterprise-grade dependency management while maintaining the accessibility of PlatformIO workflows.