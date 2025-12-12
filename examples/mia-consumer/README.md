# MIA Consumer Example

This example demonstrates how to use sparetools Conan packages from MIA's `conanfile.py`.

## Prerequisites

1. Conan 2.x installed: `pip install conan==2.21.0`
2. Cloudsmith remote configured (see [MIA Integration Guide](../../docs/MIA-INTEGRATION.md))

## Usage

### 1. Configure Conan Remote

```bash
conan remote add sparesparrow-conan \
  https://dl.cloudsmith.io/public/sparesparrow-conan/openssl-conan/conan/ \
  --force
```

### 2. Install Dependencies

```bash
conan install . --build=missing
```

### 3. Build

```bash
conan build .
```

## Package Dependencies

This example demonstrates:

- **sparetools-openssl/3.3.2**: Main OpenSSL library
- **sparetools-base/2.0.0**: Foundation utilities (via python_requires)

## Integration with MIA

To use sparetools packages in MIA:

1. Add sparetools packages to your `conanfile.py` `requires` or `tool_requires`
2. Configure the Cloudsmith remote
3. Install and build as shown above

See [MIA Integration Guide](../../docs/MIA-INTEGRATION.md) for complete details.
