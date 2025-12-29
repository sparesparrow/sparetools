# Conan & Cloudsmith MCP Server

A comprehensive MCP server for Conan package management and Cloudsmith integration, providing tools for package creation, validation, upload, and remote management.

## Features

- **Package Validation**: Conanfile syntax checking and dependency validation
- **Package Creation**: Automated Conan package building from conanfiles
- **Package Upload**: Upload packages to Conan remotes and Cloudsmith
- **Package Search**: Search available packages in Conan remotes
- **Dependency Installation**: Install dependencies from conanfiles
- **Package Information**: Get detailed package metadata
- **Cloudsmith Integration**: Direct integration with Cloudsmith repositories
- **Remote Management**: Configure and manage Conan remotes
- **Session Tracking**: Persistent session management across operations

## Prerequisites

- Python 3.8+
- Conan package manager installed (`pip install conan`)
- Cloudsmith account (for Cloudsmith operations)
- Proper Conan configuration

## Installation

```bash
cd /home/sparrow/mcp/servers/conan_cloudsmith
pip install -r requirements.txt
```

## Configuration

Add to your `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "conan-cloudsmith": {
      "command": "uv",
      "args": ["run", "--with", "mcp", "python3", "/home/sparrow/mcp/servers/conan_cloudsmith/conan_cloudsmith_mcp_server.py"],
      "env": {
        "CONAN_LOG_LEVEL": "INFO",
        "CONAN_LOG_DIR": "/home/sparrow/conan_logs",
        "CONAN_SESSION_STORAGE": "/home/sparrow/.mcp/conan_sessions.json",
        "CLOUDSMITH_API_KEY": "your-api-key",
        "CLOUDSMITH_ORG": "your-org-name"
      },
      "cwd": "${workspaceFolder}"
    }
  }
}
```

### Environment Variables

- `CONAN_LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `CONAN_LOG_DIR`: Directory for log files
- `CONAN_SESSION_STORAGE`: Path for session persistence
- `CLOUDSMITH_API_KEY`: Cloudsmith API key
- `CLOUDSMITH_ORG`: Cloudsmith organization name

## Available Tools

### 1. validate_conanfile
Validate conanfile.py syntax and dependencies
- **Parameters**: conanfile_path
- **Returns**: Validation results with syntax checks and missing attributes

### 2. create_conan_package
Create Conan package from conanfile
- **Parameters**: conanfile_path, terminal (boolean)
- **Returns**: Package creation session details

### 3. upload_conan_package
Upload package to Conan remote
- **Parameters**: package_reference, remote_name, terminal (boolean)
- **Returns**: Upload session details

### 4. search_conan_packages
Search available Conan packages
- **Parameters**: query, remote_name
- **Returns**: Search results with matching packages

### 5. install_conan_dependencies
Install dependencies from conanfile
- **Parameters**: conanfile_path, install_folder, terminal (boolean)
- **Returns**: Installation session details

### 6. conan_info
Get package information
- **Parameters**: package_reference, remote_name
- **Returns**: Detailed package metadata

### 7. setup_cloudsmith_remote
Configure Cloudsmith remote
- **Parameters**: remote_name, repository
- **Returns**: Remote setup result

### 8. upload_to_cloudsmith
Upload package to Cloudsmith
- **Parameters**: package_reference, remote_name
- **Returns**: Upload result

### 9. list_cloudsmith_packages
List packages in Cloudsmith repository
- **Parameters**: repository
- **Returns**: Package list from Cloudsmith

## Usage Examples

### Validating a Conanfile
```javascript
// Validate conanfile syntax
mcp_conan-cloudsmith_validate_conanfile({
  conanfile_path: "/path/to/conanfile.py"
})
```

### Creating a Package
```javascript
// Create package in terminal
mcp_conan-cloudsmith_create_conan_package({
  conanfile_path: "/path/to/conanfile.py",
  terminal: true
})
```

### Uploading a Package
```javascript
// Upload to conancenter
mcp_conan-cloudsmith_upload_conan_package({
  package_reference: "mylib/1.0@user/stable",
  remote_name: "conancenter"
})
```

### Searching Packages
```javascript
// Search for boost packages
mcp_conan-cloudsmith_search_conan_packages({
  query: "boost*",
  remote_name: "conancenter"
})
```

### Installing Dependencies
```javascript
// Install dependencies to build folder
mcp_conan-cloudsmith_install_conan_dependencies({
  conanfile_path: "/path/to/conanfile.py",
  install_folder: "build"
})
```

### Setting up Cloudsmith Remote
```javascript
// Configure Cloudsmith remote
mcp_conan-cloudsmith_setup_cloudsmith_remote({
  remote_name: "mycloudsmith",
  repository: "my-repo"
})
```

### Listing Cloudsmith Packages
```javascript
// List packages in repository
mcp_conan-cloudsmith_list_cloudsmith_packages({
  repository: "my-repo"
})
```

## Conan Configuration

### Initial Setup
```bash
# Initialize Conan (first time)
conan profile new default --detect

# Add remotes
conan remote add conancenter https://center.conan.io
```

### Profile Configuration
```bash
# List profiles
conan profile list

# Show current profile
conan profile show default
```

## Cloudsmith Integration

### Authentication
Set environment variables for Cloudsmith access:
```bash
export CLOUDSMITH_API_KEY="your-api-key-here"
export CLOUDSMITH_ORG="your-organization"
```

### Repository Setup
```javascript
// Setup remote for your repository
mcp_conan-cloudsmith_setup_cloudsmith_remote({
  remote_name: "myremote",
  repository: "my-private-repo"
})
```

## Session Management

All operations create sessions that are tracked persistently:
- Session IDs for tracking long-running operations
- Progress updates and status monitoring
- Log file generation for all operations
- Automatic cleanup of stale sessions

## Logging

All operations generate logs stored in `~/conan_logs/`:
- Validation logs with syntax check results
- Build logs with Conan create output
- Upload logs with transfer status
- Installation logs with dependency resolution

## Error Handling

- Comprehensive error reporting with detailed messages
- Conan command validation and error parsing
- Cloudsmith API error handling
- Timeout management for long-running operations
- Recovery mechanisms for failed operations

## Package Reference Format

Conan packages are referenced using the format:
```
name/version@user/channel
```

Examples:
- `boost/1.78.0@_/_` - Official Boost package
- `mylib/1.0@user/stable` - Custom package
- `openssl/1.1.1@_/_` - OpenSSL library

## Troubleshooting

### Conan Not Found
- Ensure Conan is installed: `pip install conan`
- Check PATH: `which conan`
- Verify installation: `conan --version`

### Cloudsmith Authentication Issues
- Verify API key is set: `echo $CLOUDSMITH_API_KEY`
- Check organization name: `echo $CLOUDSMITH_ORG`
- Validate credentials with Cloudsmith API

### Package Upload Failures
- Check remote exists: `conan remote list`
- Verify package reference format
- Ensure you have upload permissions

### Build Failures
- Check conanfile.py syntax
- Verify dependencies are available
- Review build logs for specific errors

### Network Issues
- Check internet connectivity
- Verify remote URLs are accessible
- Check proxy settings if applicable

## Best Practices

### Package Development
1. Validate conanfile before building
2. Use descriptive package names and versions
3. Include proper metadata (description, license, etc.)
4. Test packages locally before uploading

### Repository Management
1. Use consistent remote naming
2. Organize packages by user/channel
3. Regularly clean up old package versions
4. Backup important packages

### Cloudsmith Usage
1. Use separate repositories for different projects
2. Implement proper access controls
3. Monitor package download statistics
4. Keep API keys secure

## Integration with Build Systems

### CMake Integration
```cmake
# CMakeLists.txt
find_package(CMake Conan REQUIRED)
conan_cmake_run(CONANFILE conanfile.py BASIC_SETUP)
```

### Visual Studio Integration
Use Conan Visual Studio extension or integrate via build scripts.

### CI/CD Integration
```yaml
# GitHub Actions example
- name: Install dependencies
  run: |
    pip install conan
    conan install . --build=missing
```