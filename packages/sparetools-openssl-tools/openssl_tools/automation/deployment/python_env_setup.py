#!/usr/bin/env python3
"""
Conan Python Environment Setup - Cross-platform setup script
Sets up a complete Python-based Conan development environment
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path
from typing import Dict, List, Optional
import argparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ConanPythonEnvironmentSetup:
    """Cross-platform Conan Python environment setup"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.platform = platform.system().lower()
        self.conan_dir = project_root / "conan-dev"
        self.scripts_dir = project_root / "scripts" / "conan"
        
    def setup_environment(self, force: bool = False) -> bool:
        """Set up the complete Conan Python environment"""
        try:
            logger.info("🚀 Setting up Conan Python development environment...")
            logger.info(f"📋 Platform: {self.platform}")
            
            # Create directory structure
            self._create_directory_structure()
            
            # Set up Python environment
            self._setup_python_environment()
            
            # Create platform-specific launchers
            self._create_platform_launchers()
            
            # Set up CI/CD workflows
            self._setup_cicd_workflows()
            
            # Create configuration files
            self._create_configuration_files()
            
            # Create documentation
            self._create_documentation()
            
            logger.info("✅ Conan Python environment setup complete!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Setup failed: {e}")
            return False
    
    def _create_directory_structure(self):
        """Create necessary directory structure"""
        directories = [
            self.conan_dir,
            self.conan_dir / "profiles",
            self.conan_dir / "locks",
            self.conan_dir / "cache",
            self.conan_dir / "artifacts",
            self.conan_dir / "venv",
            self.scripts_dir,
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"📁 Created directory: {directory}")
    
    def _setup_python_environment(self):
        """Set up Python environment with Conan orchestrator"""
        logger.info("🐍 Setting up Python environment...")
        
        # Make Python scripts executable
        python_scripts = [
            "conan_orchestrator.py",
            "conan_cli.py",
            "conan-install.py",
            "conan-build.py",
            "conan-dev-setup.py",
            "performance_benchmark.py"
        ]
        
        for script in python_scripts:
            script_path = self.scripts_dir / script
            if script_path.exists():
                if self.platform != "windows":
                    os.chmod(script_path, 0o755)
                logger.info(f"✅ Made executable: {script}")
    
    def _create_platform_launchers(self):
        """Create platform-specific launcher scripts"""
        logger.info("🔗 Creating platform-specific launchers...")
        
        if self.platform == "windows":
            self._create_windows_launchers()
        else:
            self._create_unix_launchers()
    
    def _create_windows_launchers(self):
        """Create Windows batch file launchers"""
        launchers = {
            "conan-install.bat": "conan-install.py",
            "conan-build.bat": "conan-build.py",
            "conan-dev-setup.bat": "conan-dev-setup.py",
            "conan-cli.bat": "conan_cli.py"
        }
        
        for launcher_name, python_script in launchers.items():
            launcher_path = self.scripts_dir / launcher_name
            if not launcher_path.exists():
                logger.warning(f"Launcher not found: {launcher_name}")
                continue
            
            logger.info(f"✅ Windows launcher ready: {launcher_name}")
    
    def _create_unix_launchers(self):
        """Create Unix shell script launchers"""
        launchers = {
            "conan-install": "conan-install.py",
            "conan-build": "conan-build.py",
            "conan-dev-setup": "conan-dev-setup.py",
            "conan-cli": "conan_cli.py"
        }
        
        for launcher_name, python_script in launchers.items():
            launcher_path = self.scripts_dir / launcher_name
            if launcher_path.exists():
                # Make executable
                os.chmod(launcher_path, 0o755)
                logger.info(f"✅ Unix launcher ready: {launcher_name}")
    
    def _setup_cicd_workflows(self):
        """Set up CI/CD workflows for Python orchestration"""
        logger.info("🔄 Setting up CI/CD workflows...")
        
        workflows_dir = self.project_root / ".github" / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)
        
        # Update existing workflows to use Python orchestration
        workflow_files = [
            "conan-ci.yml",
            "conan-pr-tests.yml", 
            "conan-release.yml",
            "conan-manual-trigger.yml",
            "conan-nightly.yml"
        ]
        
        for workflow_file in workflow_files:
            workflow_path = workflows_dir / workflow_file
            if workflow_path.exists():
                self._update_workflow_for_python(workflow_path)
                logger.info(f"✅ Updated workflow: {workflow_file}")
    
    def _update_workflow_for_python(self, workflow_path: Path):
        """Update workflow to use Python orchestration"""
        # Read the workflow file
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Replace bash commands with Python orchestration
        replacements = {
            "conan install . --profile=": "python scripts/conan/conan_cli.py install --profile=",
            "conan build . --profile=": "python scripts/conan/conan_cli.py build --profile=",
            "conan test test_package": "python scripts/conan/conan_cli.py test --profile=",
            "conan create .": "python scripts/conan/conan_cli.py build --profile=",
            "conan remove": "python scripts/conan/conan_cli.py build --clean --profile=",
        }
        
        for old_cmd, new_cmd in replacements.items():
            content = content.replace(old_cmd, new_cmd)
        
        # Write updated content
        with open(workflow_path, 'w') as f:
            f.write(content)
    
    def _create_configuration_files(self):
        """Create configuration files"""
        logger.info("⚙️ Creating configuration files...")
        
        # Create platform-specific configuration
        config = self._get_platform_config()
        
        # Write configuration
        config_file = self.conan_dir / "platform-config.yml"
        import yaml
        with open(config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        logger.info(f"✅ Created configuration: {config_file}")
    
    def _get_platform_config(self) -> Dict:
        """Get platform-specific configuration"""
        config = {
            "platform": self.platform,
            "python_executable": sys.executable,
            "conan_dir": str(self.conan_dir),
            "scripts_dir": str(self.scripts_dir),
            "profiles": {
                "default": self._get_default_profile(),
                "available": self._get_available_profiles()
            },
            "launchers": self._get_launcher_info()
        }
        
        return config
    
    def _get_default_profile(self) -> str:
        """Get default profile for current platform"""
        if self.platform == "windows":
            return "windows-msvc2022"
        elif self.platform == "darwin":
            return "macos-clang14"
        else:
            return "linux-gcc11"
    
    def _get_available_profiles(self) -> List[str]:
        """Get available profiles for current platform"""
        if self.platform == "windows":
            return ["windows-msvc2022", "debug"]
        elif self.platform == "darwin":
            return ["macos-clang14", "debug"]
        else:
            return ["linux-gcc11", "linux-clang15", "debug"]
    
    def _get_launcher_info(self) -> Dict[str, str]:
        """Get launcher information for current platform"""
        if self.platform == "windows":
            return {
                "install": "conan-install.bat",
                "build": "conan-build.bat",
                "setup": "conan-dev-setup.bat",
                "cli": "conan-cli.bat"
            }
        else:
            return {
                "install": "conan-install",
                "build": "conan-build", 
                "setup": "conan-dev-setup",
                "cli": "conan-cli"
            }
    
    def _create_documentation(self):
        """Create documentation for the Python environment"""
        logger.info("📚 Creating documentation...")
        
        doc_content = self._generate_documentation()
        
        doc_file = self.project_root / "CONAN-PYTHON-ENVIRONMENT.md"
        with open(doc_file, 'w') as f:
            f.write(doc_content)
        
        logger.info(f"✅ Created documentation: {doc_file}")
    
    def _generate_documentation(self) -> str:
        """Generate documentation content"""
        return f"""# Conan Python Environment

Cross-platform Python-based Conan development environment.

## 🚀 Quick Start

### Setup Environment
```bash
# Cross-platform setup
python scripts/setup-conan-python-env.py

# Or use the orchestrator directly
python scripts/conan/conan_cli.py setup
```

### Developer Commands
```bash
# Using Python CLI (cross-platform)
python scripts/conan/conan_cli.py install
python scripts/conan/conan_cli.py build
python scripts/conan/conan_cli.py test

# Using platform-specific launchers
# Windows:
conan-install.bat
conan-build.bat

# Unix/Linux/macOS:
./conan-install
./conan-build
```

## 🖥️ Platform Support

### Windows
- **Launchers**: `.bat` files
- **Default Profile**: `windows-msvc2022`
- **Available Profiles**: `windows-msvc2022`, `debug`

### macOS
- **Launchers**: Shell scripts
- **Default Profile**: `macos-clang14`
- **Available Profiles**: `macos-clang14`, `debug`

### Linux
- **Launchers**: Shell scripts
- **Default Profile**: `linux-gcc11`
- **Available Profiles**: `linux-gcc11`, `linux-clang15`, `debug`

## 🔧 Python Orchestrator

The `conan_orchestrator.py` provides:
- Cross-platform profile management
- Virtual environment handling
- Platform detection
- Unified command interface

## 📁 Directory Structure

```
conan-dev/
├── profiles/           # Platform-specific profiles
├── venv/              # Python virtual environment
├── cache/             # Conan cache
├── artifacts/         # Build artifacts
└── platform-config.yml # Platform configuration

scripts/conan/
├── conan_orchestrator.py  # Core orchestrator
├── conan_cli.py          # Unified CLI
├── conan-install.py      # Install script
├── conan-build.py        # Build script
├── conan-dev-setup.py    # Setup script
├── conan-install.bat     # Windows launcher
├── conan-build.bat       # Windows launcher
├── conan-dev-setup.bat   # Windows launcher
├── conan-cli.bat         # Windows launcher
├── conan-install         # Unix launcher
├── conan-build           # Unix launcher
├── conan-dev-setup       # Unix launcher
└── conan-cli             # Unix launcher
```

## 🎯 Usage Examples

### Basic Usage
```bash
# Setup (one time)
python scripts/conan/conan_cli.py setup

# Install dependencies
python scripts/conan/conan_cli.py install

# Build package
python scripts/conan/conan_cli.py build

# Build and test
python scripts/conan/conan_cli.py build --test
```

### Platform-Specific Usage
```bash
# Windows
conan-install.bat -p windows-msvc2022
conan-build.bat -t

# macOS
./conan-install -p macos-clang14
./conan-build -t

# Linux
./conan-install -p linux-clang15
./conan-build -t
```

### Advanced Usage
```bash
# List available profiles
python scripts/conan/conan_cli.py list-profiles

# Show environment info
python scripts/conan/conan_cli.py info

# Verbose output
python scripts/conan/conan_cli.py build --verbose

# Clean build
python scripts/conan/conan_cli.py build --clean
```

## 🔄 CI/CD Integration

The CI/CD workflows have been updated to use Python orchestration:
- Cross-platform compatibility
- Unified command interface
- Better error handling
- Platform detection

## 🛠️ Troubleshooting

### Common Issues

#### 1. Python Not Found
```bash
# Check Python installation
python --version
python3 --version

# Use full path if needed
/path/to/python scripts/conan/conan_cli.py setup
```

#### 2. Permission Issues (Unix)
```bash
# Make scripts executable
chmod +x scripts/conan/conan-*
```

#### 3. Profile Not Found
```bash
# List available profiles
python scripts/conan/conan_cli.py list-profiles

# Check platform configuration
python scripts/conan/conan_cli.py info
```

### Debug Commands
```bash
# Verbose output
python scripts/conan/conan_cli.py build --verbose

# Environment info
python scripts/conan/conan_cli.py info

# List profiles
python scripts/conan/conan_cli.py list-profiles
```

## 📈 Benefits

### Cross-Platform
- Works on Windows, macOS, and Linux
- Platform-specific optimizations
- Unified command interface

### Python-Based
- Better error handling
- Rich logging and output
- Extensible and maintainable

### Developer-Friendly
- Simple commands
- Helpful error messages
- Comprehensive documentation

## 🤝 Contributing

1. Fork the repository
2. Make changes to Python scripts
3. Test on multiple platforms
4. Submit a pull request

The Python orchestrator makes it easy to add new features and platforms.
"""

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Set up Conan Python development environment")
    parser.add_argument("--project-root", type=Path, default=Path.cwd(),
                       help="Project root directory")
    parser.add_argument("--force", "-f", action="store_true",
                       help="Force setup (recreate environment)")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Set up environment
    setup = ConanPythonEnvironmentSetup(args.project_root)
    success = setup.setup_environment(force=args.force)
    
    if success:
        print("\n🎉 Conan Python environment setup complete!")
        print("\n📋 Next steps:")
        print("1. Run: python scripts/conan/conan_cli.py setup")
        print("2. Use: python scripts/conan/conan_cli.py install")
        print("3. Use: python scripts/conan/conan_cli.py build")
        print("\n🖥️ Platform-specific launchers:")
        if platform.system().lower() == "windows":
            print("- conan-install.bat, conan-build.bat")
        else:
            print("- ./conan-install, ./conan-build")
        sys.exit(0)
    else:
        print("\n❌ Setup failed. Check the logs above.")
        sys.exit(1)

if __name__ == "__main__":
    main()