from conan import ConanFile
from conan.tools.files import copy, save
import os


class SpareToolsMCPEcosystemConan(ConanFile):
    name = "sparetools-mcp-ecosystem"
    version = "1.0.0"
    license = "MIT"
    author = "sparesparrow"
    url = "https://github.com/sparesparrow/sparetools"
    description = "Complete MCP (Model Context Protocol) ecosystem for AI-assisted development workflows"
    topics = ("mcp", "ai", "development", "automation", "esp32", "android", "conan", "prompts")

    # Use SpareTools foundation utilities
    python_requires = "sparetools-base/2.0.3"
    python_requires_extend = "sparetools-base.SpareToolsSecurityMixin"

    # Pure Python application; no C/C++ settings required
    settings = None
    package_type = "application"

    exports_sources = (
        # MCP Prompts (from mcp-prompts)
        "mcp-prompts/package.json",
        "mcp-prompts/package-lock.json",
        "mcp-prompts/pnpm-lock.yaml",
        "mcp-prompts/tsconfig*.json",
        "mcp-prompts/src/**/*",
        "mcp-prompts/dist/**/*",
        "mcp-prompts/data/**/*",
        "mcp-prompts/layers/**/*",
        "mcp-prompts/apps/**/*",
        "mcp-prompts/packages/**/*",
        "mcp-prompts/scripts/**/*",
        "mcp-prompts/public/**/*",
        "mcp-prompts/web/**/*",
        "mcp-prompts/docs/**/*",
        "mcp-prompts/examples/**/*",
        "mcp-prompts/docker-compose*.yml",
        "mcp-prompts/Dockerfile*",

        # MCP Servers (from mcp-servers)
        "mcp-servers/src/**/*",
        "mcp-servers/scripts/**/*",
        "mcp-servers/config/**/*",
        "mcp-servers/README.md",
        "mcp-servers/QUICKSTART.md",

        # Project Orchestrator features (from mcp-project-orchestrator)
        "project-orchestrator/src/**/*",
        "project-orchestrator/project_orchestration.json",
        "project-orchestrator/project_templates.json",
        "project-orchestrator/component_templates.json",
        "project-orchestrator/templates/**/*",
        "project-orchestrator/cursor-templates/**/*",
        "project-orchestrator/automotive-camera-system/**/*",
        "project-orchestrator/aws-sip-trunk/**/*",
        "project-orchestrator/printcast-agent/**/*",
        "project-orchestrator/elevenlabs-agents/**/*",

        # Integration and configuration
        "mcp.json",
        "cursor-mcp-config.json",
        "README.md",
        "QUICKSTART.md",
        "INTEGRATION_GUIDE.md",
        "SPARETOOLS_MCP_INTEGRATION.md",

        # Scripts and utilities
        "scripts/**/*",
        "config/**/*",
        "templates/**/*",
    )

    def build_requirements(self):
        # Use SpareTools CPython for bundled Python runtime
        versions = self.python_requires["sparetools-base"].module.SpareToolsVersions.versions
        self.tool_requires(f"sparetools-cpython/{versions['cpython']}")

    def package(self):
        """Package the complete MCP ecosystem."""
        # MCP Prompts application
        copy(self, "mcp-prompts/package.json", dst=os.path.join(self.package_folder, "mcp-prompts"), src=self.source_folder)
        copy(self, "mcp-prompts/package-lock.json", dst=os.path.join(self.package_folder, "mcp-prompts"), src=self.source_folder)
        copy(self, "mcp-prompts/pnpm-lock.yaml", dst=os.path.join(self.package_folder, "mcp-prompts"), src=self.source_folder)
        copy(self, "mcp-prompts/src/**/*", dst=os.path.join(self.package_folder, "mcp-prompts"), src=self.source_folder)
        copy(self, "mcp-prompts/dist/**/*", dst=os.path.join(self.package_folder, "mcp-prompts"), src=self.source_folder)
        copy(self, "mcp-prompts/data/**/*", dst=os.path.join(self.package_folder, "mcp-prompts", "data"), src=self.source_folder)
        copy(self, "mcp-prompts/scripts/**/*", dst=os.path.join(self.package_folder, "mcp-prompts", "scripts"), src=self.source_folder)

        # MCP Servers
        copy(self, "mcp-servers/src/**/*", dst=os.path.join(self.package_folder, "mcp-servers"), src=self.source_folder)
        copy(self, "mcp-servers/scripts/**/*", dst=os.path.join(self.package_folder, "mcp-servers", "scripts"), src=self.source_folder)
        copy(self, "mcp-servers/config/**/*", dst=os.path.join(self.package_folder, "mcp-servers", "config"), src=self.source_folder)

        # Project Orchestrator features
        copy(self, "project-orchestrator/src/**/*", dst=os.path.join(self.package_folder, "orchestrator"), src=self.source_folder)
        copy(self, "project-orchestrator/project_orchestration.json", dst=os.path.join(self.package_folder, "orchestrator", "config"), src=self.source_folder)
        copy(self, "project-orchestrator/project_templates.json", dst=os.path.join(self.package_folder, "orchestrator", "templates"), src=self.source_folder)
        copy(self, "project-orchestrator/component_templates.json", dst=os.path.join(self.package_folder, "orchestrator", "templates"), src=self.source_folder)
        copy(self, "project-orchestrator/templates/**/*", dst=os.path.join(self.package_folder, "orchestrator", "templates"), src=self.source_folder)
        copy(self, "project-orchestrator/cursor-templates/**/*", dst=os.path.join(self.package_folder, "orchestrator", "cursor-templates"), src=self.source_folder)

        # Specialized project templates
        copy(self, "project-orchestrator/automotive-camera-system/**/*", dst=os.path.join(self.package_folder, "orchestrator", "specialized", "automotive"), src=self.source_folder)
        copy(self, "project-orchestrator/aws-sip-trunk/**/*", dst=os.path.join(self.package_folder, "orchestrator", "specialized", "aws-sip"), src=self.source_folder)
        copy(self, "project-orchestrator/printcast-agent/**/*", dst=os.path.join(self.package_folder, "orchestrator", "specialized", "printcast"), src=self.source_folder)
        copy(self, "project-orchestrator/elevenlabs-agents/**/*", dst=os.path.join(self.package_folder, "orchestrator", "specialized", "elevenlabs"), src=self.source_folder)

        # Configuration and documentation
        copy(self, "*.json", dst=os.path.join(self.package_folder, "config"), src=self.source_folder)
        copy(self, "*.md", dst=os.path.join(self.package_folder, "docs"), src=self.source_folder)
        copy(self, "scripts/**/*", dst=os.path.join(self.package_folder, "scripts"), src=self.source_folder)
        copy(self, "config/**/*", dst=os.path.join(self.package_folder, "config"), src=self.source_folder)
        copy(self, "templates/**/*", dst=os.path.join(self.package_folder, "templates"), src=self.source_folder)

        # Create unified launcher scripts
        self._create_launcher_scripts()

        # Apply security gates and generate SBOM
        self.apply_security_gates()
        self.generate_sbom()

    def _create_launcher_scripts(self):
        """Create launcher scripts for all MCP ecosystem components."""
        bin_dir = os.path.join(self.package_folder, "bin")
        os.makedirs(bin_dir, exist_ok=True)

        # Main ecosystem launcher
        ecosystem_launcher = """#!/usr/bin/env bash
set -euo pipefail

echo "🚀 SpareTools MCP Ecosystem"
echo "Available components:"
echo "  mcp-prompts        - AI-powered prompts server"
echo "  mcp-servers        - Development workflow servers"
echo "  orchestrator       - Project orchestration tools"
echo "  setup              - Setup and configuration"
echo ""
echo "Use 'sparetools-mcp-ecosystem <component> --help' for more information"

if [ $# -eq 0 ]; then
    echo ""
    echo "Run 'sparetools-mcp-ecosystem setup' to configure your environment"
    exit 0
fi

case "$1" in
    "mcp-prompts")
        shift
        exec "$PACKAGE_DIR/bin/sparetools-mcp-prompts" "$@"
        ;;
    "mcp-servers")
        shift
        exec "$PACKAGE_DIR/bin/sparetools-mcp-servers" "$@"
        ;;
    "orchestrator")
        shift
        exec "$PACKAGE_DIR/bin/sparetools-orchestrator" "$@"
        ;;
    "setup")
        exec "$PACKAGE_DIR/scripts/setup-ecosystem.sh"
        ;;
    *)
        echo "Unknown component: $1"
        echo "Available: mcp-prompts, mcp-servers, orchestrator, setup"
        exit 1
        ;;
esac
"""
        save(self, os.path.join(bin_dir, "sparetools-mcp-ecosystem"), ecosystem_launcher)
        os.chmod(os.path.join(bin_dir, "sparetools-mcp-ecosystem"), 0o755)

        # MCP Prompts launcher
        mcp_prompts_launcher = """#!/usr/bin/env bash
set -euo pipefail

# Set up environment
export NODE_ENV="${NODE_ENV:-production}"
export MODE="${MODE:-mcp}"

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is required but not found in PATH"
    exit 1
fi

# Check if dependencies are installed
if [ ! -d "$PACKAGE_DIR/mcp-prompts/node_modules" ]; then
    echo "Installing MCP Prompts dependencies..."
    cd "$PACKAGE_DIR/mcp-prompts"
    if command -v pnpm &> /dev/null; then
        pnpm install --frozen-lockfile
    else
        npm ci
    fi
fi

# Launch MCP Prompts server
cd "$PACKAGE_DIR/mcp-prompts"
exec node dist/mcp-server-standalone.js "$@"
"""
        save(self, os.path.join(bin_dir, "sparetools-mcp-prompts"), mcp_prompts_launcher)
        os.chmod(os.path.join(bin_dir, "sparetools-mcp-prompts"), 0o755)

        # MCP Servers launcher
        mcp_servers_launcher = """#!/usr/bin/env bash
set -euo pipefail

echo "SpareTools MCP Servers"
echo "Available servers:"
echo "  esp32     - ESP32 serial monitoring"
echo "  android   - Android development tools"
echo "  conan     - Conan & Cloudsmith package management"
echo "  repo      - Repository cleanup and maintenance"
echo ""
echo "Usage: sparetools-mcp-servers <server_name> [args...]"

if [ $# -eq 0 ]; then
    exit 0
fi

SERVER_NAME="$1"
shift

case "$SERVER_NAME" in
    "esp32")
        exec python "$PACKAGE_DIR/mcp-servers/src/sparetools/mcp_servers/esp32_serial_monitor/server.py" "$@"
        ;;
    "android")
        exec python "$PACKAGE_DIR/mcp-servers/src/sparetools/mcp_servers/android_dev_tools/server.py" "$@"
        ;;
    "conan")
        exec python "$PACKAGE_DIR/mcp-servers/src/sparetools/mcp_servers/conan_cloudsmith/server.py" "$@"
        ;;
    "repo")
        exec python "$PACKAGE_DIR/mcp-servers/src/sparetools/mcp_servers/repo_cleanup/server.py" "$@"
        ;;
    *)
        echo "Unknown server: $SERVER_NAME"
        echo "Available: esp32, android, conan, repo"
        exit 1
        ;;
esac
"""
        save(self, os.path.join(bin_dir, "sparetools-mcp-servers"), mcp_servers_launcher)
        os.chmod(os.path.join(bin_dir, "sparetools-mcp-servers"), 0o755)

        # Orchestrator launcher
        orchestrator_launcher = """#!/usr/bin/env bash
set -euo pipefail

echo "SpareTools Project Orchestrator"
echo "Available commands:"
echo "  template     - Project and component templates"
echo "  prompt       - Prompt management"
echo "  mermaid      - Diagram generation"
echo "  aws          - AWS integration"
echo "  cursor       - Cursor IDE integration"
echo ""
echo "Usage: sparetools-orchestrator <command> [args...]"

if [ $# -eq 0 ]; then
    exit 0
fi

COMMAND="$1"
shift

# Set PYTHONPATH for orchestrator
export PYTHONPATH="$PACKAGE_DIR/orchestrator:$PYTHONPATH"

case "$COMMAND" in
    "template")
        exec python -m mcp_project_orchestrator.core.templates "$@"
        ;;
    "prompt")
        exec python -m mcp_project_orchestrator.prompt_manager.manager "$@"
        ;;
    "mermaid")
        exec python -m mcp_project_orchestrator.mermaid.generator "$@"
        ;;
    "aws")
        exec python -m mcp_project_orchestrator.aws_mcp "$@"
        ;;
    "cursor")
        exec python -m mcp_project_orchestrator.cursor_deployer "$@"
        ;;
    *)
        exec python -m mcp_project_orchestrator "$@"
        ;;
esac
"""
        save(self, os.path.join(bin_dir, "sparetools-orchestrator"), orchestrator_launcher)
        os.chmod(os.path.join(bin_dir, "sparetools-orchestrator"), 0o755)

        # Setup script
        setup_script = """#!/usr/bin/env bash
set -euo pipefail

echo "🔧 Setting up SpareTools MCP Ecosystem..."
echo ""

# Check for required tools
echo "Checking dependencies..."

if ! command -v node &> /dev/null; then
    echo "⚠️  Node.js not found. Please install Node.js 18+"
else
    echo "✅ Node.js found: $(node --version)"
fi

if ! command -v python3 &> /dev/null; then
    echo "⚠️  Python 3 not found. Please install Python 3.8+"
else
    echo "✅ Python found: $(python3 --version)"
fi

if ! command -v pip &> /dev/null; then
    echo "⚠️  pip not found. Please install pip"
else
    echo "✅ pip found"
fi

echo ""
echo "Installing MCP Prompts dependencies..."
if [ -d "$PACKAGE_DIR/mcp-prompts" ]; then
    cd "$PACKAGE_DIR/mcp-prompts"
    if command -v pnpm &> /dev/null; then
        echo "Using pnpm..."
        pnpm install --frozen-lockfile
    else
        echo "Using npm..."
        npm ci
    fi
fi

echo ""
echo "Installing MCP Servers dependencies..."
if [ -d "$PACKAGE_DIR/mcp-servers" ]; then
    cd "$PACKAGE_DIR/mcp-servers"
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    fi
fi

echo ""
echo "Installing Orchestrator dependencies..."
if [ -d "$PACKAGE_DIR/orchestrator" ]; then
    cd "$PACKAGE_DIR/orchestrator"
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    fi
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Configure Cursor MCP settings (see docs/MCP_CONFIGURATION.md)"
echo "2. Test individual components:"
echo "   sparetools-mcp-ecosystem mcp-prompts --help"
echo "   sparetools-mcp-ecosystem mcp-servers esp32 --help"
echo "   sparetools-mcp-ecosystem orchestrator --help"
echo ""
echo "3. Run integration tests:"
echo "   sparetools-mcp-ecosystem setup"
"""
        save(self, os.path.join(self.package_folder, "scripts", "setup-ecosystem.sh"), setup_script)
        os.chmod(os.path.join(self.package_folder, "scripts", "setup-ecosystem.sh"), 0o755)

    def package_info(self):
        """Configure package environment for consumers."""
        # Set up paths
        bin_dir = os.path.join(self.package_folder, "bin")
        scripts_dir = os.path.join(self.package_folder, "scripts")
        config_dir = os.path.join(self.package_folder, "config")

        # Make binaries available
        self.runenv_info.append_path("PATH", bin_dir)
        self.runenv_info.append_path("PATH", scripts_dir)

        # Set package directories
        self.runenv_info.define("SPARETOOLS_MCP_ECOSYSTEM_DIR", self.package_folder)
        self.runenv_info.define("SPARETOOLS_MCP_PROMPTS_DIR", os.path.join(self.package_folder, "mcp-prompts"))
        self.runenv_info.define("SPARETOOLS_MCP_SERVERS_DIR", os.path.join(self.package_folder, "mcp-servers"))
        self.runenv_info.define("SPARETOOLS_ORCHESTRATOR_DIR", os.path.join(self.package_folder, "orchestrator"))
        self.runenv_info.define("SPARETOOLS_MCP_CONFIG_DIR", config_dir)

        # Configure bundled Python environment
        try:
            if hasattr(self, 'deps_cpp_info') and "sparetools-cpython" in self.deps_cpp_info:
                cpython_info = self.deps_cpp_info["sparetools-cpython"]
                self.runenv_info.prepend_path("PATH", cpython_info.bin_paths[0])
        except Exception:
            pass
