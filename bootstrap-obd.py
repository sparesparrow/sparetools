#!/usr/bin/env python3
"""
SpareTools Bootstrap Script

Multi-purpose bootstrap script for SpareTools ecosystem:

1. OBD-II Simulation: Bootstraps hermetic CPython and launches ELM327-emulator
2. Project Templates: Creates new projects from pre-configured templates

Usage:
  python bootstrap-obd.py                    # OBD-II simulation (default)
  python bootstrap-obd.py --template=mia     # Create MIA project
  python bootstrap-obd.py --list-templates   # List available templates
"""

import sys
import os
import subprocess
import platform
import shutil
import argparse
import json
from pathlib import Path

# CONFIGURATION
CPY_VER = "3.12.7"
CPYTHON_PACKAGE = f"sparetools-cpython/{CPY_VER}"
CONAN_REMOTE = "sparesparrow-conan"
INSTALL_DIR = os.path.abspath(".mia/python")
BIN_DIR = os.path.join(INSTALL_DIR, "Scripts" if platform.system() == "Windows" else "bin")
PIP_EXE = os.path.join(BIN_DIR, "pip.exe" if platform.system() == "Windows" else "pip3")
PYTHON_EXE = os.path.join(BIN_DIR, "python.exe" if platform.system() == "Windows" else "python3")
SYS_PLATFORM = platform.system()

# Template configuration
TEMPLATES_DIR = Path(__file__).parent / "templates"
AVAILABLE_TEMPLATES = ["generic", "mia", "mcp", "android"]


def print_status(msg):
    """Print status message."""
    print(f"[BOOTSTRAP] {msg}", flush=True)


def print_error(msg):
    """Print error message."""
    print(f"[ERROR] {msg}", file=sys.stderr, flush=True)


def list_available_templates():
    """List all available project templates."""
    # Static descriptions for templates
    template_descriptions = {
        "generic": "C++ library with CMake, Conan, and testing framework",
        "mia": "Python application with hermetic environment and OpenSSL integration",
        "mcp": "MCP server for AI assistants with protocol validation",
        "android": "Android app with JNI native integration and Gradle build"
    }

    print_status("Available templates:")
    for template in AVAILABLE_TEMPLATES:
        template_path = TEMPLATES_DIR / template
        if template_path.exists():
            description = template_descriptions.get(template, f"{template.capitalize()} project template")
            print(f"  - {template}: {description}")
        else:
            print(f"  - {template}: (not found)")


def validate_template_name(template_name):
    """Validate that a template name is available."""
    if template_name not in AVAILABLE_TEMPLATES:
        print_error(f"Unknown template: {template_name}")
        print_error(f"Available templates: {', '.join(AVAILABLE_TEMPLATES)}")
        return False

    template_path = TEMPLATES_DIR / template_name
    if not template_path.exists():
        print_error(f"Template directory not found: {template_path}")
        return False

    return True


def get_default_template_variables(template_name, project_name):
    """Get default template variables for a given template."""
    # Convert project name to different formats
    module_name = project_name.replace("-", "_").replace(" ", "_").lower()
    class_name = "".join(word.capitalize() for word in project_name.replace("-", " ").replace("_", " ").split())

    # Get current year for copyright
    from datetime import datetime
    current_year = datetime.now().year

    defaults = {
        "project_name": project_name,
        "module_name": module_name,
        "class_name": class_name,
        "version": "1.0.0",
        "author": "Your Name",
        "author_email": "your.email@example.com",
        "description": f"{project_name} - A SpareTools project",
        "license": "MIT",
        "repository_url": f"https://github.com/yourusername/{project_name}",
        "homepage_url": f"https://github.com/yourusername/{project_name}",
        "documentation_url": f"https://github.com/yourusername/{project_name}/README.md",
        "issues_url": f"https://github.com/yourusername/{project_name}/issues",
        "year": str(current_year),
        "topic1": "software",
        "topic2": "development",
    }

    # Template-specific defaults
    if template_name == "mia":
        defaults.update({
            "cpython_version": "3.12.7",
            "openssl_version": "3.3.2",
            "base_version": "2.0.0",
            "topic1": "python",
            "topic2": "cryptography",
        })
    elif template_name == "mcp":
        defaults.update({
            "cpython_version": "3.12.7",
            "openssl_version": "3.3.2",
            "base_version": "2.0.0",
            "topic1": "ai",
            "topic2": "assistant",
        })
    elif template_name == "android":
        defaults.update({
            "package_name": f"com.example.{module_name}",
            "cpython_version": "3.12.7",
            "openssl_version": "3.3.2",
            "base_version": "2.0.0",
            "topic1": "mobile",
            "topic2": "android",
        })
    elif template_name == "generic":
        defaults.update({
            "namespace": f"{class_name}Namespace",
            "cpython_version": "3.12.7",
            "openssl_version": "3.3.2",
            "base_version": "2.0.0",
            "topic1": "library",
            "topic2": "cpp",
        })

    return defaults


def instantiate_template(template_name, project_name, target_dir, variables=None):
    """Instantiate a template with the given variables."""
    if not validate_template_name(template_name):
        return False

    template_path = TEMPLATES_DIR / template_name
    target_path = Path(target_dir) / project_name

    if target_path.exists():
        print_error(f"Target directory already exists: {target_path}")
        return False

    # Get default variables
    template_vars = get_default_template_variables(template_name, project_name)

    # Override with user-provided variables
    if variables:
        if isinstance(variables, str):
            try:
                user_vars = json.loads(variables)
            except json.JSONDecodeError as e:
                print_error(f"Invalid JSON in variables: {e}")
                return False
        else:
            user_vars = variables
        template_vars.update(user_vars)

    print_status(f"Creating project '{project_name}' from template '{template_name}'")
    print_status(f"Target directory: {target_path}")

    try:
        # Copy template directory
        shutil.copytree(template_path, target_path)

        # Replace template variables in all files
        for root, dirs, files in os.walk(target_path):
            # Skip .git directories if any
            dirs[:] = [d for d in dirs if not d.startswith('.')]

            for file in files:
                file_path = Path(root) / file

                # Skip binary files and specific file types
                if file_path.suffix in ['.png', '.jpg', '.jpeg', '.gif', '.ico', '.pdf']:
                    continue

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Replace template variables
                    original_content = content
                    for key, value in template_vars.items():
                        placeholder = "{{" + key + "}}"
                        content = content.replace(placeholder, str(value))

                    # Only write if content changed
                    if content != original_content:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)

                except UnicodeDecodeError:
                    # Skip files that can't be decoded as UTF-8
                    continue
                except Exception as e:
                    print_error(f"Error processing {file_path}: {e}")
                    continue

        print_status("Template instantiation complete!")
        print_status(f"Project created at: {target_path}")
        print_status("Next steps:")
        print_status(f"  cd {project_name}")
        print_status("  # Follow the README.md for setup instructions")

        return True

    except Exception as e:
        print_error(f"Template instantiation failed: {e}")
        # Clean up on failure
        if target_path.exists():
            shutil.rmtree(target_path)
        return False


def find_conan_executable():
    """Find Conan executable in PATH."""
    conan_exe = shutil.which("conan")
    if conan_exe:
        return conan_exe
    
    # Try common locations
    common_paths = [
        os.path.expanduser("~/.local/bin/conan"),
        "/usr/local/bin/conan",
        "/usr/bin/conan",
    ]
    
    for path in common_paths:
        if os.path.exists(path) and os.access(path, os.X_OK):
            return path
    
    return None


def install_cpython_via_conan():
    """Install CPython via Conan."""
    conan_exe = find_conan_executable()
    if not conan_exe:
        print_error("Conan not found in PATH")
        print_error("Please install Conan: pip install conan==2.21.0")
        return False
    
    print_status(f"Using Conan: {conan_exe}")
    
    # Check if package is already built
    list_cmd = [conan_exe, "list", f"{CPYTHON_PACKAGE}:*"]
    result = subprocess.run(list_cmd, capture_output=True, text=True, timeout=30)
    
    has_package = False
    if result.returncode == 0:
        # Check if there's a built package (has package_id)
        output = result.stdout
        if "packages" in output and "da39a3ee5e6b4b0d3255bfef95601890afd80709" not in output:
            # Has actual package, not just recipe
            has_package = True
        elif "packages" in output:
            # Check if package folder exists
            package_path = get_conan_package_path()
            if package_path and os.path.exists(os.path.join(package_path, "bin", "python3")):
                has_package = True
    
    if has_package:
        print_status(f"{CPYTHON_PACKAGE} found in cache")
        return True
    
    # Install from remote or build
    print_status(f"Installing/Building {CPYTHON_PACKAGE} via Conan...")
    
    # Try to install from remote first, then build if needed
    install_cmd = [
        conan_exe, "install", "--tool-requires", CPYTHON_PACKAGE,
        "--build=missing"
    ]
    
    # Add remote if specified
    if CONAN_REMOTE:
        install_cmd.extend(["-r", CONAN_REMOTE])
    
    print_status("This may take several minutes if building from source...")
    result = subprocess.run(install_cmd, timeout=1800)  # 30 minute timeout
    
    if result.returncode != 0:
        # Try building locally
        print_status("Remote install failed, trying local build...")
        local_build_cmd = [
            conan_exe, "create", "packages/sparetools-cpython",
            f"--version={CPY_VER}", "--build=missing"
        ]
        result = subprocess.run(local_build_cmd, timeout=1800)
        
        if result.returncode != 0:
            print_error("Conan install/build failed")
            print_error("You may need to build the package manually:")
            print_error(f"  cd packages/sparetools-cpython")
            print_error(f"  conan create . --version={CPY_VER} --build=missing")
            return False
    
    print_status("CPython installed successfully via Conan")
    return True


def get_conan_package_path():
    """Get the Conan cache path for CPython package."""
    conan_exe = find_conan_executable()
    if not conan_exe:
        return None
    
    # First, try to get package ID from list command
    list_cmd = [conan_exe, "list", f"{CPYTHON_PACKAGE}:*", "--format", "json"]
    result = subprocess.run(list_cmd, capture_output=True, text=True, timeout=30)
    
    package_id = None
    if result.returncode == 0:
        import json
        try:
            data = json.loads(result.stdout)
            # Navigate the JSON structure to find package_id
            for pkg_ref in data.get("Local Cache", {}).get("sparetools-cpython", {}).get("sparetools-cpython/3.12.7", {}).get("revisions", {}).values():
                for pkg_id in pkg_ref.get("packages", {}).keys():
                    if pkg_id != "da39a3ee5e6b4b0d3255bfef95601890afd80709":  # Skip empty package ID
                        package_id = pkg_id
                        break
        except (json.JSONDecodeError, KeyError, TypeError):
            pass
    
    # If we have a package ID, use it to get the path
    if package_id:
        cache_cmd = [conan_exe, "cache", "path", f"{CPYTHON_PACKAGE}:{package_id}"]
        result = subprocess.run(cache_cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            package_path = result.stdout.strip().split('\n')[0]
            if package_path and os.path.exists(package_path):
                # Verify it has bin/python3
                bin_path = os.path.join(package_path, "bin", "python3")
                if os.path.exists(bin_path):
                    return package_path
    
    # Fallback: search entire Conan cache for bin directory with python3
    conan_home = os.path.expanduser("~/.conan2")
    if os.path.exists(conan_home):
        for root, dirs, files in os.walk(conan_home):
            # Look for bin/python3 or Scripts/python.exe
            if os.path.basename(root) == "bin":
                python_exe = os.path.join(root, "python3")
                if os.path.exists(python_exe):
                    # Check if this is sparetools-cpython by checking parent path
                    parent = os.path.dirname(root)
                    if "sparetools-cpython" in str(parent) or "spare" in str(parent):
                        return parent
            elif os.path.basename(root) == "Scripts":
                python_exe = os.path.join(root, "python.exe")
                if os.path.exists(python_exe):
                    parent = os.path.dirname(root)
                    if "sparetools-cpython" in str(parent) or "spare" in str(parent):
                        return parent
    
    return None


def copy_from_conan_cache(source_dir, dest_dir):
    """Copy CPython from Conan cache to installation directory."""
    print_status(f"Copying CPython from Conan cache to {dest_dir}...")
    
    if not os.path.exists(source_dir):
        print_error(f"Source directory not found: {source_dir}")
        return False
    
    # Remove existing installation if it exists
    if os.path.exists(dest_dir):
        print_status("Removing existing installation...")
        shutil.rmtree(dest_dir)
    
    # Create parent directory
    os.makedirs(os.path.dirname(dest_dir), exist_ok=True)
    
    # Copy entire directory
    try:
        shutil.copytree(source_dir, dest_dir)
        print_status("Copy complete")
        return True
    except OSError as e:
        print_error(f"Copy failed: {e}")
        print_error("Check disk space and permissions")
        return False
    except Exception as e:
        print_error(f"Copy failed: {e}")
        return False


def verify_installation():
    """Verify that CPython installation is valid."""
    print_status("Verifying installation...")
    
    if not os.path.exists(PYTHON_EXE):
        print_error(f"Python executable not found: {PYTHON_EXE}")
        return False
    
    if not os.path.exists(PIP_EXE):
        print_error(f"pip executable not found: {PIP_EXE}")
        return False
    
    # Test Python version
    try:
        result = subprocess.run(
            [PYTHON_EXE, "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode != 0:
            print_error("Python version check failed")
            return False
        print_status(f"Python version: {result.stdout.strip()}")
    except Exception as e:
        print_error(f"Python verification failed: {e}")
        return False
    
    return True


def install_packages():
    """Install ELM327-emulator and obd packages."""
    print_status("Installing ELM327-emulator and obd packages...")
    
    packages = ["ELM327-emulator", "obd"]
    
    for package in packages:
        print_status(f"Installing {package}...")
        try:
            result = subprocess.run(
                [PIP_EXE, "install", package],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            if result.returncode != 0:
                print_error(f"Failed to install {package}")
                print_error(result.stderr)
                return False
            print_status(f"{package} installed successfully")
        except subprocess.TimeoutExpired:
            print_error(f"Installation of {package} timed out")
            return False
        except Exception as e:
            print_error(f"Failed to install {package}: {e}")
            return False
    
    return True


def launch_emulator():
    """Launch ELM327-emulator in car scenario mode."""
    print_status("Launching ELM327-emulator in car scenario mode...")
    
    # Set up environment
    env = os.environ.copy()
    env["PYTHONHOME"] = INSTALL_DIR
    env["PATH"] = BIN_DIR + os.pathsep + env.get("PATH", "")
    
    # Launch emulator with car scenario
    try:
        # ELM327-emulator typically runs with: python -m elm327_emulator --scenario car
        cmd = [PYTHON_EXE, "-m", "elm327_emulator", "--scenario", "car"]
        
        print_status("Starting emulator (this will run in foreground)...")
        print_status("Press Ctrl+C to stop the emulator")
        print_status("=" * 60)
        
        # Run in foreground so user can see output
        subprocess.run(cmd, env=env, check=False)
        
    except KeyboardInterrupt:
        print_status("\nEmulator stopped by user")
    except FileNotFoundError:
        print_error("ELM327-emulator module not found")
        print_error("Verify installation completed successfully")
        return False
    except Exception as e:
        print_error(f"Failed to launch emulator: {e}")
        return False
    
    return True


def bootstrap(skip_emulator=False):
    """Main bootstrap function for OBD-II simulation.

    Args:
        skip_emulator: If True, skip launching the ELM327 emulator
    """
    print_status("=" * 60)
    print_status("SpareTools OBD-II Bootstrap")
    print_status("=" * 60)
    print_status(f"Platform: {SYS_PLATFORM}")
    print_status(f"CPython Version: {CPY_VER}")
    print_status(f"Install Directory: {INSTALL_DIR}")
    print_status("=" * 60)
    
    # Check if already installed
    if os.path.exists(INSTALL_DIR) and os.path.exists(PYTHON_EXE):
        print_status("CPython installation found, skipping download")
        if not verify_installation():
            print_error("Installation verification failed, re-downloading...")
            shutil.rmtree(INSTALL_DIR)
        else:
            print_status("Installation verified")
    else:
        # Install CPython via Conan
        if not install_cpython_via_conan():
            print_error("\n" + "="*60)
            print_error("CPython installation failed. Options:")
            print_error("1. Install Conan: pip install conan==2.21.0")
            print_error(f"2. Build locally: cd packages/sparetools-cpython && conan create . --version={CPY_VER} --build=missing")
            print_error("3. Check Conan remote configuration")
            print_error("="*60)
            return 1
        
        # Get package path from Conan cache
        conan_package_path = get_conan_package_path()
        if not conan_package_path:
            print_error("Could not locate CPython package in Conan cache")
            print_error(f"Try: conan cache path {CPYTHON_PACKAGE}")
            return 1
        
        print_status(f"Found CPython in Conan cache: {conan_package_path}")
        
        # Copy from Conan cache to installation directory
        if not copy_from_conan_cache(conan_package_path, INSTALL_DIR):
            return 1
        
        if not verify_installation():
            return 1
    
    # Install packages
    if not install_packages():
        return 1

    # Launch emulator (unless skipped)
    if not skip_emulator:
        if not launch_emulator():
            return 1
    else:
        print_status("Skipping ELM327 emulator launch (--skip-emulator)")
        print_status("To run the emulator manually:")
        print_status(f"  cd {os.getcwd()}")
        print_status(f"  {PYTHON_EXE} -m elm327_emulator --scenario car")

    return 0


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="SpareTools Bootstrap Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # OBD-II simulation (default)
  python bootstrap-obd.py

  # List available templates
  python bootstrap-obd.py --list-templates

  # Create project from template
  python bootstrap-obd.py --template=mia --name=my-mia-app

  # Create project with custom variables
  python bootstrap-obd.py --template=generic --name=my-lib \\
    --variables='{"author": "John Doe", "license": "Apache-2.0"}'
        """
    )

    # Template-related arguments
    parser.add_argument(
        "--template", "-t",
        choices=AVAILABLE_TEMPLATES,
        help="Create project from template"
    )

    parser.add_argument(
        "--name", "-n",
        help="Project name (required with --template)"
    )

    parser.add_argument(
        "--variables", "-v",
        help="JSON string of template variables to override"
    )

    parser.add_argument(
        "--list-templates",
        action="store_true",
        help="List available project templates"
    )

    # OBD-II related arguments
    parser.add_argument(
        "--obd", "--obd-ii",
        action="store_true",
        help="Run OBD-II bootstrap and simulation (default if no template specified)"
    )

    parser.add_argument(
        "--skip-emulator",
        action="store_true",
        help="Skip launching ELM327 emulator after bootstrap"
    )

    args = parser.parse_args()

    # Handle template operations
    if args.list_templates:
        list_available_templates()
        return 0

    if args.template:
        if not args.name:
            print_error("--name is required when using --template")
            return 1

        target_dir = os.getcwd()
        success = instantiate_template(args.template, args.name, target_dir, args.variables)
        return 0 if success else 1

    # Default: OBD-II bootstrap
    if not args.obd and not any([args.template, args.list_templates]):
        # If no arguments provided, default to OBD-II
        args.obd = True

    if args.obd:
        return bootstrap(skip_emulator=args.skip_emulator)

    # If we get here, no valid operation was specified
    parser.print_help()
    return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print_status("\nOperation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
