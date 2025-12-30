from conan import ConanFile
from conan.tools.files import copy, save
import os


class SpareToolsMCPPromptsConan(ConanFile):
    name = "sparetools-mcp-prompts"
    version = "3.13.0"
    license = "MIT"
    author = "sparesparrow"
    url = "https://github.com/sparesparrow/sparetools"
    description = "MCP Prompts server for AI-assisted development workflows in SpareTools ecosystem"
    topics = ("mcp", "prompts", "ai", "typescript", "server", "development", "automation")

    # Use SpareTools foundation utilities
    python_requires = "sparetools-base/2.0.3"

    # Node.js application - no C/C++ compilation needed
    settings = None
    package_type = "application"

    exports_sources = (
        "package.json",
        "package-lock.json",
        "tsconfig.json",
        "tsconfig.package.json",
        "eslint.config.js",
        "vitest.config.ts",
        "src/**/*",
        "dist/**/*",
        "data/**/*",
        "layers/**/*",
        "apps/**/*",
        "packages/**/*",
        "scripts/**/*",
        "public/**/*",
        "web/**/*",
        "docs/**/*",
        "examples/**/*",
        "README.md",
        "CHANGELOG.md",
        "CLAUDE.md",
        "PR_COMMENTS.md",
        "ALT-COMPOSER-CHAT.md",
        "RELEASE_SUMMARY_v3.12.3.md",
        "VERIFICATION_REPORT.md",
        "PRODUCTION_SECURITY_GUIDE.md",
        "DEPLOYMENT_GUIDE.md",
        "DOCKER_AWS_TEST_REPORT.md",
        "IMPLEMENTATION_GUIDE.md",
        "IMPLEMENTATION_SUMMARY.md",
        "QUICK_REFERENCE.md",
        "SECURITY.md",
        "CONTRIBUTING.md",
        "CODE_OF_CONDUCT.md",
        "LICENSE",
        ".gitignore",
        ".swcrc",
        ".prettierignore",
        ".prettierrc",
        ".windsurfrules",
        ".dockerignore",
        ".env.example",
        ".eslintignore",
        ".npmrc",
        "docker-compose.yml",
        "docker-compose.*.yml",
        "Dockerfile*",
        "mcp-inspector-config.json",
        "mcp.code-workspace",
        "glama.json",
        "create-alarms.sh",
        "create-dashboard.sh",
        "pnpm-lock.yaml",
        "vitest.config.ts",
        "tsconfig.base.json",
        "eslint.config.js",
    )

    def build_requirements(self):
        # Use SpareTools CPython for any Python tooling/scripts
        versions = self.python_requires["sparetools-base"].module.SpareToolsVersions.versions
        self.tool_requires(f"sparetools-cpython/{versions['cpython']}")

    def package(self):
        """Package the MCP Prompts application and all supporting files."""
        # Core application files
        copy(self, "package.json", dst=os.path.join(self.package_folder, "app"), src=self.source_folder)
        copy(self, "package-lock.json", dst=os.path.join(self.package_folder, "app"), src=self.source_folder)
        copy(self, "pnpm-lock.yaml", dst=os.path.join(self.package_folder, "app"), src=self.source_folder)

        # TypeScript source and compiled output
        copy(self, "src/**/*", dst=os.path.join(self.package_folder, "app"), src=self.source_folder)
        copy(self, "dist/**/*", dst=os.path.join(self.package_folder, "app"), src=self.source_folder)

        # Configuration files
        copy(self, "*.config.*", dst=os.path.join(self.package_folder, "config"), src=self.source_folder)
        copy(self, "tsconfig*.json", dst=os.path.join(self.package_folder, "config"), src=self.source_folder)
        copy(self, ".env.example", dst=os.path.join(self.package_folder, "config"), src=self.source_folder)

        # Data and prompts
        copy(self, "data/**/*", dst=os.path.join(self.package_folder, "data"), src=self.source_folder)
        copy(self, "layers/**/*", dst=os.path.join(self.package_folder, "data"), src=self.source_folder)

        # Scripts and tools
        copy(self, "scripts/**/*", dst=os.path.join(self.package_folder, "scripts"), src=self.source_folder)

        # Documentation
        copy(self, "README.md", dst=os.path.join(self.package_folder, "docs"), src=self.source_folder)
        copy(self, "docs/**/*", dst=os.path.join(self.package_folder, "docs"), src=self.source_folder)
        copy(self, "*.md", dst=os.path.join(self.package_folder, "docs"), src=self.source_folder)

        # Docker and deployment files
        copy(self, "Dockerfile*", dst=os.path.join(self.package_folder, "docker"), src=self.source_folder)
        copy(self, "docker-compose*.yml", dst=os.path.join(self.package_folder, "docker"), src=self.source_folder)

        # Licenses and legal
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)

        # Create launcher scripts
        bin_dir = os.path.join(self.package_folder, "bin")
        os.makedirs(bin_dir, exist_ok=True)

        # MCP server launcher
        mcp_launcher = """#!/usr/bin/env bash
set -euo pipefail

# Set up environment
export NODE_ENV="${NODE_ENV:-production}"
export MODE="${MODE:-mcp}"

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is required but not found in PATH"
    echo "Please install Node.js or ensure it's available"
    exit 1
fi

# Check if dependencies are installed
if [ ! -d "$PACKAGE_DIR/app/node_modules" ]; then
    echo "Installing dependencies..."
    cd "$PACKAGE_DIR/app"
    if command -v pnpm &> /dev/null; then
        pnpm install --frozen-lockfile
    else
        npm ci
    fi
fi

# Launch the MCP server
cd "$PACKAGE_DIR/app"
exec node dist/mcp-server-standalone.js "$@"
"""
        save(self, os.path.join(bin_dir, "sparetools-mcp-prompts"), mcp_launcher)
        os.chmod(os.path.join(bin_dir, "sparetools-mcp-prompts"), 0o755)

        # HTTP server launcher
        http_launcher = """#!/usr/bin/env bash
set -euo pipefail

# Set up environment
export NODE_ENV="${NODE_ENV:-production}"
export MODE="${MODE:-http}"
export PORT="${PORT:-3000}"

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is required but not found in PATH"
    echo "Please install Node.js or ensure it's available"
    exit 1
fi

# Check if dependencies are installed
if [ ! -d "$PACKAGE_DIR/app/node_modules" ]; then
    echo "Installing dependencies..."
    cd "$PACKAGE_DIR/app"
    if command -v pnpm &> /dev/null; then
        pnpm install --frozen-lockfile
    else
        npm ci
    fi
fi

# Launch the HTTP server
cd "$PACKAGE_DIR/app"
exec node dist/index.js "$@"
"""
        save(self, os.path.join(bin_dir, "sparetools-mcp-prompts-http"), http_launcher)
        os.chmod(os.path.join(bin_dir, "sparetools-mcp-prompts-http"), 0o755)

        # CLI launcher
        cli_launcher = """#!/usr/bin/env bash
set -euo pipefail

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is required but not found in PATH"
    echo "Please install Node.js or ensure it's available"
    exit 1
fi

# Check if dependencies are installed
if [ ! -d "$PACKAGE_DIR/app/node_modules" ]; then
    echo "Installing dependencies..."
    cd "$PACKAGE_DIR/app"
    if command -v pnpm &> /dev/null; then
        pnpm install --frozen-lockfile
    else
        npm ci
    fi
fi

# Launch the CLI
cd "$PACKAGE_DIR/app"
exec node dist/cli.js "$@"
"""
        save(self, os.path.join(bin_dir, "sparetools-mcp-prompts-cli"), cli_launcher)
        os.chmod(os.path.join(bin_dir, "sparetools-mcp-prompts-cli"), 0o755)

    def package_info(self):
        """Configure package environment for consumers."""
        # Set up paths
        app_dir = os.path.join(self.package_folder, "app")
        bin_dir = os.path.join(self.package_folder, "bin")
        data_dir = os.path.join(self.package_folder, "data")

        # Make binaries available
        self.runenv_info.append_path("PATH", bin_dir)

        # Set package directory for scripts
        self.runenv_info.define("SPARETOOLS_MCP_PROMPTS_DIR", self.package_folder)
        self.runenv_info.define("SPARETOOLS_MCP_PROMPTS_APP_DIR", app_dir)
        self.runenv_info.define("SPARETOOLS_MCP_PROMPTS_DATA_DIR", data_dir)

        # Configure bundled Python environment
        try:
            if hasattr(self, 'deps_cpp_info') and "sparetools-cpython" in self.deps_cpp_info:
                cpython_info = self.deps_cpp_info["sparetools-cpython"]
                self.runenv_info.prepend_path("PATH", cpython_info.bin_paths[0])
        except Exception:
            pass

