# SpareTools Template Usage Guide

Complete guide to using SpareTools project templates for rapid development with hermetic builds.

## Overview

SpareTools provides pre-configured project templates that include:
- Complete project structure
- CI/CD workflows
- Testing frameworks
- Documentation templates
- Bootstrap scripts for hermetic builds

## Available Templates

| Template | Description | Use Case |
|----------|-------------|----------|
| `generic` | C++ library with CMake | Cross-platform C++ libraries |
| `mia` | Python application | Hermetic Python apps with OpenSSL |
| `mcp` | MCP server | AI assistant servers with MCP protocol |
| `android` | Android app | Mobile apps with native JNI integration |

## Quick Start

### Using Bootstrap Script

```bash
# Create new MIA project
python bootstrap-obd.py --template=mia --name=my-mia-app

# Create Android project
python bootstrap-obd.py --template=android --name=MyAndroidApp

# Create generic C++ library
python bootstrap-obd.py --template=generic --name=my-cpp-lib

# Create MCP server
python bootstrap-obd.py --template=mcp --name=my-mcp-server
```

### Manual Template Usage

```bash
# Copy template manually
cp -r templates/mia my-project
cd my-project

# Replace template variables
find . -type f -name "*.template" -o -name "*.md" -o -name "*.py" -o -name "*.txt" | xargs sed -i 's/{{project_name}}/my-project/g'
```

## Template Details

### Generic Template

**Structure:**
```
my-cpp-lib/
├── CMakeLists.txt          # Root CMake configuration
├── conanfile.py           # Conan recipe
├── README.md              # Project documentation
├── .gitignore             # Git ignore rules
├── include/               # Public headers
│   └── my-cpp-lib.h
├── src/                   # Source files
│   └── my-cpp-lib.cpp
├── test/                  # Unit tests
│   ├── CMakeLists.txt
│   └── test_my-cpp-lib.cpp
└── test_package/          # Conan test package
    ├── conanfile.py
    └── example.cpp
```

**Features:**
- CMake-based build system
- GTest for unit testing
- Conan package management
- Cross-platform support (Linux, macOS, Windows)

**Next Steps:**
```bash
cd my-cpp-lib
conan create . --version=1.0.0 --build=missing
```

### MIA Template

**Structure:**
```
my-mia-app/
├── pyproject.toml         # Python package configuration
├── conanfile.py          # Conan integration
├── README.md             # Project documentation
├── .gitignore            # Python-specific ignore rules
├── src/my_mia_app/       # Python source
│   ├── __init__.py
│   └── my_mia_app.py
├── test/                 # Unit tests
│   ├── conftest.py
│   └── test_my_mia_app.py
├── test_package/         # Conan test package
│   └── conanfile.py
├── requirements-dev.txt  # Development dependencies
└── .github/workflows/    # CI/CD workflows
    └── ci.yml
```

**Features:**
- Hermetic Python environment via SpareTools CPython
- OpenSSL integration
- pytest testing framework
- Black code formatting
- Ruff linting
- Multi-platform CI/CD

**Next Steps:**
```bash
cd my-mia-app
conan install . --build=missing
conan build .
pytest
```

### MCP Template

**Structure:**
```
my-mcp-server/
├── pyproject.toml         # Python package configuration
├── conanfile.py          # Conan integration
├── README.md             # Project documentation
├── .gitignore            # Python-specific ignore rules
├── src/my_mcp_server/   # Python source
│   ├── __init__.py
│   ├── server.py         # MCP server implementation
│   ├── tools/            # MCP tools
│   │   ├── __init__.py
│   │   └── example_tool.py
│   └── resources/        # MCP resources
│       ├── __init__.py
│       └── example_resource.py
├── test/                 # Unit tests
│   └── test_server.py
├── test_package/         # Conan test package
│   └── conanfile.py
├── docker/               # Docker configuration
│   ├── Dockerfile
│   └── docker-compose.yml
└── .github/workflows/    # CI/CD workflows
    └── ci.yml
```

**Features:**
- MCP protocol implementation
- stdio and HTTP transports
- Tool and resource providers
- Docker containerization
- Security scanning
- Protocol compliance testing

**Next Steps:**
```bash
cd my-mcp-server
conan install . --build=missing
conan build .
python -m my_mcp_server.server
```

### Android Template

**Structure:**
```
MyAndroidApp/
├── build.gradle.kts       # Root Gradle configuration
├── settings.gradle.kts    # Project settings
├── .gitignore             # Android-specific ignore rules
├── app/                   # Main application module
│   ├── build.gradle.kts   # App configuration
│   ├── src/main/
│   │   ├── AndroidManifest.xml
│   │   ├── java/com/example/myandroidapp/
│   │   │   ├── MainActivity.kt
│   │   │   └── native/NativeInterface.java
│   │   ├── cpp/           # Native C++ code
│   │   │   ├── CMakeLists.txt
│   │   │   ├── conanfile.py
│   │   │   └── native-lib.cpp
│   │   └── res/           # Android resources
│   └── src/androidTest/   # Instrumented tests
└── .github/workflows/     # CI/CD workflows
    └── ci.yml
```

**Features:**
- Android Studio project structure
- JNI native integration
- Gradle build system with Conan
- Cross-ABI support (armeabi-v7a, arm64-v8a, x86, x86_64)
- Jetpack Compose UI
- Material Design 3

**Next Steps:**
```bash
cd MyAndroidApp
# Open in Android Studio or use command line
./gradlew assembleDebug
```

## Template Variables

Templates use mustache-style variables that are replaced during instantiation:

| Variable | Description | Example |
|----------|-------------|---------|
| `{{project_name}}` | Project name (snake_case) | `my_mia_app` |
| `{{class_name}}` | Class name (PascalCase) | `MyMiaApp` |
| `{{module_name}}` | Python module name | `my_mia_app` |
| `{{package_name}}` | Java package name | `com.example.myandroidapp` |
| `{{version}}` | Version string | `1.0.0` |
| `{{author}}` | Author name | `Your Name` |
| `{{author_email}}` | Author email | `your.email@example.com` |
| `{{description}}` | Project description | `My awesome project` |
| `{{license}}` | License type | `MIT` |
| `{{repository_url}}` | Git repository URL | `https://github.com/user/repo` |
| `{{topic1}}` | Primary topic | `cryptography` |
| `{{topic2}}` | Secondary topic | `security` |

## Customization

### Adding Custom Variables

1. Add variables to template files using `{{variable_name}}` syntax
2. Update bootstrap script to handle new variables
3. Test template instantiation

### Modifying Templates

1. Edit template files in `templates/` directory
2. Test changes with bootstrap script
3. Update documentation

### Creating New Templates

1. Create new directory under `templates/`
2. Follow existing template structure
3. Add template to bootstrap script
4. Update documentation

## Bootstrap Script Integration

The bootstrap script (`bootstrap-obd.py`) now supports template instantiation:

```bash
# Interactive mode
python bootstrap-obd.py

# Direct template selection
python bootstrap-obd.py --template=mia --name=my-app --author="John Doe"

# List available templates
python bootstrap-obd.py --list-templates

# Template with custom variables
python bootstrap-obd.py --template=generic \
    --name=my-lib \
    --variables='{"version": "2.0.0", "license": "Apache-2.0"}'
```

## CI/CD Integration

Templates include pre-configured CI/CD workflows:

- **Generic/MIA/MCP**: Multi-platform testing (Linux, macOS, Windows)
- **Android**: Android-specific builds and instrumented tests
- **All**: Code quality checks, security scanning, automated releases

Workflows automatically:
- Install Conan and configure remotes
- Build dependencies with SpareTools
- Run comprehensive tests
- Upload coverage reports
- Create releases on tags

## Troubleshooting

### Template Instantiation Issues

```bash
# Check bootstrap script version
python bootstrap-obd.py --version

# Validate template exists
python bootstrap-obd.py --list-templates

# Manual template copy for debugging
cp -r templates/mia /tmp/test-template
cd /tmp/test-template
# Manually replace variables
```

### Build Issues

```bash
# Clear Conan cache
conan remove "*" -c

# Rebuild from scratch
conan install . --build=missing

# Check Conan configuration
conan profile show
conan remote list
```

### CI/CD Issues

```bash
# Test workflow locally (if using act)
act -j build

# Check GitHub Actions logs
gh run list
gh run view <run-id> --log
```

## Best Practices

### Project Structure
- Keep template structure consistent
- Use clear naming conventions
- Include comprehensive documentation

### CI/CD Integration
- Test workflows locally before pushing
- Use matrix builds for multi-platform testing
- Include security scanning in all templates

### Template Maintenance
- Regularly update template dependencies
- Test all templates after changes
- Keep documentation synchronized

## Contributing

To contribute new templates or improve existing ones:

1. Follow the established template structure
2. Include comprehensive documentation
3. Add appropriate CI/CD workflows
4. Test across all supported platforms
5. Update this documentation

See the main SpareTools documentation for detailed contribution guidelines.