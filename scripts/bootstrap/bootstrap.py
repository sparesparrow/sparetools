#!/usr/bin/env python3
"""
Universal SpareTools Bootstrap Script

One-command setup for any repository to get:
- Bundled CPython 3.12.7 (hermetic, no system dependencies)
- Unified test harness (ngapy-style verification framework)
- Consistent CI/CD workflows
- Cross-platform compatibility

Usage:
    python bootstrap.py [--project-type TYPE] [--sparetools-repo PATH]

Project Types:
    generic  - Basic Python project (default)
    mia      - MIA (Mission Information Architecture) project
    mcp      - MCP (Mission Control Platform) project
    android  - Android consumer project

Options:
    --project-type TYPE    Project type (generic, mia, mcp, android)
    --sparetools-repo PATH Local path to SpareTools repository for development
    --help                 Show this help message
"""

import argparse
import subprocess
import sys
import os
import platform
from pathlib import Path
from typing import Optional, Dict, Any
import json


class BootstrapError(Exception):
    """Bootstrap-specific error."""
    pass


class SpareToolsBootstrap:
    """Universal bootstrap for SpareTools ecosystem."""

    def __init__(self, project_type: str = "generic", sparetools_repo: Optional[str] = None):
        """Initialize bootstrap.

        Args:
            project_type: Type of project (generic, mia, mcp, android)
            sparetools_repo: Path to local SpareTools repo for development
        """
        self.project_type = project_type
        self.sparetools_repo = Path(sparetools_repo) if sparetools_repo else None
        self.system = platform.system().lower()
        self.arch = platform.machine().lower()

        # Project-specific configurations
        self.configs = {
            "generic": {
                "python_deps": ["pytest", "pytest-cov", "black", "flake8"],
                "conan_deps": [],
                "env_vars": {}
            },
            "mia": {
                "python_deps": ["pytest", "pytest-cov", "black", "flake8", "flatbuffers"],
                "conan_deps": ["sparetools-obd-sim/2.0.0"],
                "env_vars": {"PROJECT_TYPE": "mia"}
            },
            "mcp": {
                "python_deps": ["pytest", "pytest-cov", "black", "flake8", "websockets"],
                "conan_deps": [],
                "env_vars": {"PROJECT_TYPE": "mcp"}
            },
            "android": {
                "python_deps": ["pytest", "pytest-cov", "black", "flake8"],
                "conan_deps": ["sparetools-cliphist-android/2.0.0"],
                "env_vars": {"PROJECT_TYPE": "android", "ANDROID_HOME": "/opt/android-sdk"}
            }
        }

        if project_type not in self.configs:
            raise BootstrapError(f"Unknown project type: {project_type}")

    def log(self, message: str, level: str = "INFO") -> None:
        """Log message with level."""
        print(f"[{level}] {message}")

    def run_command(self, cmd: list, check: bool = True, capture_output: bool = False) -> subprocess.CompletedProcess:
        """Run shell command with error handling."""
        try:
            result = subprocess.run(
                cmd,
                check=check,
                capture_output=capture_output,
                text=True,
                cwd=os.getcwd()
            )
            return result
        except subprocess.CalledProcessError as e:
            raise BootstrapError(f"Command failed: {' '.join(cmd)}\n{e.stderr}")

    def ensure_conan(self) -> None:
        """Ensure Conan is available."""
        self.log("🔧 Checking Conan installation...")

        try:
            result = self.run_command(["conan", "--version"], capture_output=True)
            version = result.stdout.strip().split()[-1]
            self.log(f"✅ Conan {version} found")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.log("📦 Installing Conan...")
            self.run_command([sys.executable, "-m", "pip", "install", "conan>=2.0"])
            self.log("✅ Conan installed")

    def install_bundled_python(self) -> None:
        """Install sparetools-cpython package."""
        self.log("🐍 Installing bundled CPython 3.12.7...")

        if self.sparetools_repo:
            # Build from local repo
            cpython_path = self.sparetools_repo / "packages" / "foundation" / "sparetools-cpython"
            if not cpython_path.exists():
                raise BootstrapError(f"SpareTools CPython package not found at {cpython_path}")

            cmd = [
                "conan", "create",
                str(cpython_path),
                "--version=3.12.7",
                "--build=missing"
            ]
        else:
            # Install from remote
            cmd = [
                "conan", "install",
                "--tool-requires=sparetools-cpython/3.12.7",
                "--build=missing",
                "-of", ".conan"
            ]

        self.run_command(cmd)
        self.log("✅ Bundled CPython installed")

    def get_bundled_python(self) -> str:
        """Get path to bundled Python executable."""
        # Use Conan's conf system to get Python path
        try:
            result = self.run_command(
                ["conan", "conf", "get", "user.cpython:executable"],
                capture_output=True
            )
            python_path = result.stdout.strip()
            if python_path:
                return python_path
        except subprocess.CalledProcessError:
            pass

        # Fallback: look in .conan directory
        conan_dir = Path(".conan")
        if conan_dir.exists():
            # Try common locations
            candidates = [
                conan_dir / "sparetools-cpython" / "3.12.7" / "bin" / "python3",
                conan_dir / "sparetools-cpython" / "3.12.7" / "bin" / "python",
            ]
            for candidate in candidates:
                if candidate.exists():
                    return str(candidate)

        raise BootstrapError("Could not locate bundled Python executable")

    def setup_venv(self, python_exe: str) -> None:
        """Set up virtual environment using bundled Python."""
        self.log("🔧 Setting up virtual environment...")

        venv_path = Path(".venv")

        # Remove existing venv if it exists
        if venv_path.exists():
            import shutil
            shutil.rmtree(venv_path)

        # Create new venv
        self.run_command([python_exe, "-m", "venv", str(venv_path)])

        # Upgrade pip
        pip_exe = venv_path / "bin" / "pip"
        self.run_command([str(pip_exe), "install", "--upgrade", "pip"])

        self.log("✅ Virtual environment created")

    def install_test_harness(self) -> None:
        """Install sparetools-test-harness package."""
        self.log("🧪 Installing test harness...")

        if self.sparetools_repo:
            # Build from local repo
            harness_path = self.sparetools_repo / "packages" / "foundation" / "sparetools-test-harness"
            if not harness_path.exists():
                raise BootstrapError(f"Test harness package not found at {harness_path}")

            cmd = [
                "conan", "create",
                str(harness_path),
                "--version=2.0.0",
                "--build=missing"
            ]
        else:
            # Install from remote
            cmd = [
                "conan", "install",
                "--tool-requires=sparetools-test-harness/2.0.0",
                "--build=missing",
                "-of", ".conan"
            ]

        self.run_command(cmd)
        self.log("✅ Test harness installed")

    def install_python_deps(self) -> None:
        """Install Python dependencies."""
        self.log("📦 Installing Python dependencies...")

        config = self.configs[self.project_type]
        deps = config["python_deps"]

        if deps:
            pip_exe = Path(".venv") / "bin" / "pip"
            self.run_command([str(pip_exe), "install"] + deps)

        self.log("✅ Python dependencies installed")

    def setup_hooks(self) -> None:
        """Set up pre-commit hooks and development tools."""
        self.log("🔗 Setting up development hooks...")

        pip_exe = Path(".venv") / "bin" / "pip"

        # Install pre-commit if not already installed
        try:
            self.run_command([str(pip_exe), "install", "pre-commit"])
        except BootstrapError:
            self.log("⚠️  Could not install pre-commit (optional)")

        # Create basic pre-commit config if it doesn't exist
        precommit_config = Path(".pre-commit-config.yaml")
        if not precommit_config.exists():
            config_content = """
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 23.9.1
    hooks:
      - id: black

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
"""
            precommit_config.write_text(config_content)
            self.log("✅ Created .pre-commit-config.yaml")
        else:
            self.log("ℹ️  .pre-commit-config.yaml already exists")

    def create_config(self) -> None:
        """Create project-specific configuration."""
        self.log("⚙️  Creating project configuration...")

        config = self.configs[self.project_type]

        # Create .env file with environment variables
        env_file = Path(".env")
        if not env_file.exists():
            env_content = "# Environment variables for SpareTools project\n"
            for key, value in config["env_vars"].items():
                env_content += f"{key}={value}\n"
            env_file.write_text(env_content)
            self.log("✅ Created .env file")

        # Create pytest.ini if it doesn't exist
        pytest_config = Path("pytest.ini")
        if not pytest_config.exists():
            pytest_content = """[tool:pytest]
testpaths = test
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --cov-report=term-missing
"""
            pytest_config.write_text(pytest_content)
            self.log("✅ Created pytest.ini")

        # Create .gitignore additions
        gitignore = Path(".gitignore")
        additions = [
            ".conan/",
            ".venv/",
            "test-results/",
            "*.pyc",
            "__pycache__/",
            ".pytest_cache/",
            ".coverage",
        ]

        if gitignore.exists():
            existing_content = gitignore.read_text()
            for addition in additions:
                if addition not in existing_content:
                    with open(gitignore, 'a') as f:
                        f.write(f"{addition}\n")
        else:
            gitignore.write_text("\n".join(additions) + "\n")
            self.log("✅ Created .gitignore")

    def create_activation_script(self) -> None:
        """Create activation script for easy environment setup."""
        self.log("📜 Creating activation script...")

        script_content = """#!/bin/bash
# SpareTools Environment Activation Script
# Run: source activate.sh

export PYTHONPATH="$PWD/.conan:$PYTHONPATH"
export PATH="$PWD/.venv/bin:$PATH"

# Load environment variables
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

echo "🔧 SpareTools environment activated!"
echo "   Python: $(which python)"
echo "   Pip: $(which pip)"
echo "   Run tests: python scripts/test_runner.py"
"""

        script_path = Path("activate.sh")
        script_path.write_text(script_content)
        script_path.chmod(0o755)
        self.log("✅ Created activate.sh script")

    def run(self) -> None:
        """Run the complete bootstrap process."""
        self.log("🚀 SpareTools Bootstrap Starting...")
        self.log(f"   Project Type: {self.project_type}")
        self.log(f"   Platform: {self.system}/{self.arch}")

        try:
            # Step 1: Ensure Conan is available
            self.ensure_conan()

            # Step 2: Install bundled Python
            self.install_bundled_python()

            # Step 3: Get bundled Python executable
            bundled_python = self.get_bundled_python()
            self.log(f"📍 Bundled Python: {bundled_python}")

            # Step 4: Set up virtual environment
            self.setup_venv(bundled_python)

            # Step 5: Install test harness
            self.install_test_harness()

            # Step 6: Install Python dependencies
            self.install_python_deps()

            # Step 7: Set up development hooks
            self.setup_hooks()

            # Step 8: Create project configuration
            self.create_config()

            # Step 9: Create activation script
            self.create_activation_script()

            self.log("✅ SpareTools Bootstrap Complete!")
            self.log("")
            self.log("Next steps:")
            self.log(f"   1. Activate environment: source activate.sh")
            self.log(f"   2. Run tests: python scripts/test_runner.py")
            self.log(f"   3. Develop with bundled Python: python --version")

        except BootstrapError as e:
            self.log(f"❌ Bootstrap failed: {e}", "ERROR")
            sys.exit(1)
        except Exception as e:
            self.log(f"❌ Unexpected error: {e}", "ERROR")
            sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Universal SpareTools Bootstrap",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        "--project-type",
        choices=["generic", "mia", "mcp", "android"],
        default="generic",
        help="Project type (default: generic)"
    )

    parser.add_argument(
        "--sparetools-repo",
        help="Local path to SpareTools repository for development"
    )

    args = parser.parse_args()

    bootstrap = SpareToolsBootstrap(
        project_type=args.project_type,
        sparetools_repo=args.sparetools_repo
    )

    bootstrap.run()


if __name__ == "__main__":
    main()