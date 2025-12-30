# SpareTools FlatBuffers

FlatBuffers compiler and runtime package for the SpareTools ecosystem.

## Overview

This package provides the FlatBuffers compiler (`flatc`) and runtime libraries as a Conan tool requirement for the SpareTools ecosystem. It ensures consistent FlatBuffers versions across all SpareTools packages and provides a standardized way to generate code from `.fbs` schema files.

## Features

- **FlatBuffers Compiler**: Provides `flatc` binary for code generation
- **Cross-Platform**: Works on Linux, macOS, and Windows
- **Version Pinned**: Uses FlatBuffers 24.3.25 for ecosystem consistency
- **Security Hardened**: Includes SpareTools security gates and SBOM generation
- **Tool Integration**: Seamlessly integrates with Conan build system

## Usage

### As a Tool Requirement

Add to your `conanfile.py`:

```python
def build_requirements(self):
    # Provides flatc compiler in PATH
    self.tool_requires("sparetools-flatbuffers/24.3.25")
```

### Code Generation

After installation, `flatc` will be available in your PATH:

```bash
# Generate C++ headers
flatc --cpp --scoped-enums schema.fbs

# Generate Python bindings
flatc --python schema.fbs

# Generate multiple languages
flatc --cpp --python --java schema.fbs
```

### Configuration Access

Access the flatc executable path programmatically:

```python
def generate(self):
    flatc_path = self.conf_info["user.flatbuffers:flatc"]
    # Use flatc_path to generate code
```

## Integration with SpareTools Schemas

This package works seamlessly with SpareTools schema packages:

- `sparetools-bpm-schemas`: BPM detection protocol schemas
- `sparetools-protocols`: Common protocol schemas (MCP, MIA, VEHICLE)
- Future schema packages...

## Building

```bash
# Build for local development
conan create . --build=missing

# Cross-compile for different platforms
conan create . --profile=android-armv8
conan create . --profile=esp32-xtensa
```

## Dependencies

- `flatbuffers/24.3.25`: Core FlatBuffers library
- `sparetools-base/2.0.3`: SpareTools foundation utilities
- `sparetools-cpython/3.12.7`: Bundled Python runtime

## Schema Development Workflow

1. **Define schemas** in `.fbs` files
2. **Generate code** using `flatc` during build
3. **Integrate generated code** into your projects
4. **Version schemas** with semantic versioning
5. **Test compatibility** across platforms

## Common Issues

### flatc not found
- Ensure `sparetools-flatbuffers` is in `tool_requires`
- Check that the package was built correctly
- Verify PATH includes the package bin directory

### Version conflicts
- All SpareTools packages should use the same FlatBuffers version
- Update versions.yaml if upgrading FlatBuffers

### Cross-compilation issues
- Use appropriate Conan profiles for target platforms
- Ensure FlatBuffers supports the target architecture

## Contributing

Follow SpareTools development guidelines:
- Use `python_requires = "sparetools-base/2.0.3"`
- Include security gates and SBOM generation
- Test across all supported platforms
- Update versions.yaml for version changes