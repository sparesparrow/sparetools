from conan import ConanFile
from conan.tools.files import copy, save
import os


class SpareToolsMCPTransportTelegramConan(ConanFile):
    name = "sparetools-mcp-transport-telegram"
    version = "1.0.0"
    license = "MIT"
    author = "sparesparrow"
    url = "https://github.com/sparesparrow/sparetools"
    description = "MCP Transport for Telegram messaging integration with MIA"
    topics = ("mcp", "telegram", "transport", "messaging", "ai", "mia")

    # Use SpareTools foundation utilities
    python_requires = "sparetools-base/2.0.3"
    python_requires_extend = "sparetools-base.SpareToolsSecurityMixin"

    # Pure Python application; no C/C++ settings required
    settings = None
    package_type = "application"

    exports_sources = (
        "src/**/*",
        "tests/**/*",
        "config/**/*",
        "Dockerfile*",
        "docker-compose.yml",
        "k8s-deployment.yaml",
        "pyproject.toml",
        "requirements.txt",
        "README.md",
        "LICENSE",
        "*.md"
    )

    def build_requirements(self):
        # Use SpareTools CPython for bundled Python runtime
        versions = self.python_requires["sparetools-base"].module.SpareToolsVersions.versions
        self.tool_requires(f"sparetools-cpython/{versions['cpython']}")

    def package(self):
        """Package the MCP Transport Telegram application."""
        # Copy all source files
        copy(self, "src/**/*", dst=os.path.join(self.package_folder, "src"), src=self.source_folder)
        copy(self, "tests/**/*", dst=os.path.join(self.package_folder, "tests"), src=self.source_folder)
        copy(self, "config/**/*", dst=os.path.join(self.package_folder, "config"), src=self.source_folder)

        # Copy configuration and documentation
        copy(self, "*.yml", dst=self.package_folder, src=self.source_folder)
        copy(self, "*.yaml", dst=self.package_folder, src=self.source_folder)
        copy(self, "*.toml", dst=self.package_folder, src=self.source_folder)
        copy(self, "*.txt", dst=self.package_folder, src=self.source_folder)
        copy(self, "*.md", dst=self.package_folder, src=self.source_folder)
        copy(self, "LICENSE", dst=self.package_folder, src=self.source_folder)
        copy(self, "Dockerfile*", dst=self.package_folder, src=self.source_folder)

        # Create launcher script
        self._create_launcher_script()

        # Apply security gates and generate SBOM
        self.apply_security_gates()
        self.generate_sbom()

    def _create_launcher_script(self):
        """Create launcher script for MCP Transport Telegram."""
        bin_dir = os.path.join(self.package_folder, "bin")
        os.makedirs(bin_dir, exist_ok=True)

        launcher_script = f"""#!/usr/bin/env bash
set -euo pipefail

# Define package directory
PACKAGE_DIR="{self.package_folder}"

echo "🚀 SpareTools MCP Transport Telegram"
echo "Telegram integration for MIA (Lean IoT Assistant)"
echo ""

# Set up environment
export PYTHONPATH="$PACKAGE_DIR/src:$PYTHONPATH"

# Check if required environment variables are set
if [ -z "${{TELEGRAM_API_ID:-}}" ]; then
    echo "⚠️  TELEGRAM_API_ID not set. Please configure Telegram API credentials."
    echo "   Get credentials from: https://my.telegram.org/"
    echo ""
fi

if [ -z "${{TELEGRAM_API_HASH:-}}" ]; then
    echo "⚠️  TELEGRAM_API_HASH not set. Please configure Telegram API credentials."
    echo ""
fi

if [ -z "${{TELEGRAM_BOT_TOKEN:-}}" ]; then
    echo "⚠️  TELEGRAM_BOT_TOKEN not set. Please create a bot via @BotFather."
    echo "   See: https://t.me/botfather"
    echo ""
fi

echo "Starting MCP Transport Telegram server..."
echo "Press Ctrl+C to stop"
echo ""

# Launch the MCP server
exec python -m mcp_transport_telegram "$@"
"""
        launcher_path = os.path.join(bin_dir, "sparetools-mcp-transport-telegram")
        save(self, launcher_path, launcher_script)
        os.chmod(launcher_path, 0o755)

    def package_info(self):
        """Configure package environment for consumers."""
        # Set up paths
        bin_dir = os.path.join(self.package_folder, "bin")
        src_dir = os.path.join(self.package_folder, "src")

        # Make binary available
        self.runenv_info.append_path("PATH", bin_dir)

        # Set PYTHONPATH for proper imports
        self.runenv_info.append_path("PYTHONPATH", src_dir)

        # Set package directories
        self.runenv_info.define("SPARETOOLS_MCP_TRANSPORT_TELEGRAM_DIR", self.package_folder)
        self.runenv_info.define("MCP_TRANSPORT_TELEGRAM_CONFIG_DIR", os.path.join(self.package_folder, "config"))

        # Configure bundled Python environment
        try:
            if hasattr(self, 'deps_cpp_info') and "sparetools-cpython" in self.deps_cpp_info:
                cpython_info = self.deps_cpp_info["sparetools-cpython"]
                self.runenv_info.prepend_path("PATH", cpython_info.bin_paths[0])
        except Exception:
            pass