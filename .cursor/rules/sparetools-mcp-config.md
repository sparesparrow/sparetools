# SpareTools MCP Configuration Guide

## Overview

This repository uses MCP-Prompts to provide specialized assistance for Conan package ecosystem development, zero-copy deployment patterns, and security scanning workflows.

## MCP Server Configuration

The repository uses the global MCP-Prompts server configured in `~/.cursor/mcp.json`. No repository-specific overrides are needed.

**Current Server**: `mcp-prompts` (file storage)
- Location: `/home/sparrow/mcp/data/prompts`
- Mode: MCP (stdio transport)

## Available Prompts

### Existing Prompts (Reused from mcp-prompts)
- `conan-toolchain-package-creation` - Creating Conan toolchain packages
- `conan-toolchain-package-id` - Package ID management
- `conan-toolchain-testing` - Conan package testing workflows
- `code-review-assistant` - Code review assistance (language: python/cpp)
- `architecture-design-assistant` - Architecture design thinking

### SpareTools-Specific Prompts
- `sparetools-package-bootstrap` - Bootstrap new SpareTools packages
- `sparetools-zero-copy-deployment` - Zero-copy deployment pattern implementation
- `sparetools-security-scan` - Security scanning workflow (Trivy, Syft, CodeQL)
- `sparetools-ci-cd-workflow` - GitHub Actions workflow creation
- `sparetools-profile-composition` - Conan profile creation and composition

## Usage Examples

### Creating a New Package
```bash
# In Cursor, use the slash command:
/sparetools-package-bootstrap
# Variables:
# - package_name: "sparetools-new-package"
# - package_type: "tool-require"
# - dependencies: "sparetools-base/2.0.0"
```

### Setting Up Zero-Copy Deployment
```bash
# Use the prompt:
/sparetools-zero-copy-deployment
# Variables:
# - workspace_path: "packages/sparetools-openssl"
# - conan_cache_path: "~/.conan2/p"
```

### Security Scanning
```bash
# Before publishing:
/sparetools-security-scan
# Variables:
# - package_name: "sparetools-openssl/3.3.2"
# - scan_type: "full" (includes Trivy, Syft, FIPS)
```

## Repository-Specific Context

The MCP-Prompts server automatically understands this is a SpareTools repository and will provide context-aware assistance for:

- Conan package development patterns
- Zero-copy deployment architecture
- Security scanning integration
- Multi-platform build configurations
- Profile composition for different platforms/compilers

## Integration Points

### With GitHub Actions
The repository's CI/CD workflows integrate with MCP-Prompts for:
- Automated package validation
- Security scan orchestration
- Build matrix generation
- Deployment verification

### With Conan Ecosystem
MCP-Prompts provides specialized assistance for:
- Package recipe development
- Profile management
- Build system integration
- Dependency resolution
- Cross-platform testing

## Best Practices

1. **Use Repository-Specific Prompts**: Leverage `sparetools-*` prompts for consistent package development
2. **Context-Aware Variables**: Provide repository-specific paths and package names as variables
3. **Iterative Refinement**: Update prompt variables based on usage patterns
4. **Security First**: Always run security scans before publishing packages
5. **Zero-Copy Pattern**: Use symlink-based deployment for efficient development workflows

## Troubleshooting

### Prompt Not Found
- Verify MCP-Prompts server is running: `ps aux | grep mcp-prompts`
- Check Cursor MCP server status in settings
- Ensure prompts are loaded: Check `/home/sparrow/mcp/data/prompts/` directory

### Context Not Recognized
- Ensure you're in the correct workspace directory
- Check that repository-specific prompts are installed
- Verify MCP server configuration in Cursor settings

### Variables Not Working
- Use exact variable names as specified in prompt descriptions
- Provide all required variables (marked as `required: true`)
- Check variable format (string values, no special characters)

## Contributing New Prompts

When adding new SpareTools-specific prompts:

1. Create JSON file in `/home/sparrow/mcp/data/prompts/`
2. Use `sparetools-` prefix for prompt ID
3. Include repository-specific variables and context
4. Add to this documentation
5. Test in Cursor MCP interface

## Related Documentation

- [MCP-Prompts Documentation](../../mcp-prompts/README.md)
- [SpareTools Architecture](ARCHITECTURE.md)
- [Package Development Guide](docs/PACKAGES.md)
- [Security Integration](docs/SECURITY-GUIDE.md)

