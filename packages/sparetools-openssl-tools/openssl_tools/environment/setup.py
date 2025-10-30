#!/usr/bin/env python3
"""
Unified Environment Setup Module

Consolidates all environment setup logic into a single module with CLI support.
Supports --minimal, --full, and --dev flags for different setup modes.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

# Import existing setup modules
from ..automation.deployment.python_env_setup import ConanPythonEnvironmentSetup
from ..util.conan_python_env import ConanPythonEnvironment


def setup_environment(mode: str = "full", force: bool = False) -> bool:
    """
    Set up the OpenSSL development environment.
    
    Args:
        mode: Setup mode - 'minimal', 'full', or 'dev'
        force: Force reinstall even if environment exists
        
    Returns:
        True if setup successful, False otherwise
    """
    project_root = Path(__file__).parent.parent.parent
    
    if mode == "minimal":
        # Minimal setup - just basic Python environment
        env = ConanPythonEnvironment(project_root)
        return env.setup_minimal_environment(force=force)
    
    elif mode == "full":
        # Full setup - complete Conan Python environment
        setup = ConanPythonEnvironmentSetup(project_root)
        return setup.setup_environment(force=force)
    
    elif mode == "dev":
        # Development setup - includes testing and development tools
        setup = ConanPythonEnvironmentSetup(project_root)
        success = setup.setup_environment(force=force)
        if success:
            # Add development-specific setup
            env = ConanPythonEnvironment(project_root)
            return env.setup_development_tools(force=force)
        return success
    
    else:
        print(f"❌ Unknown setup mode: {mode}")
        return False


def main() -> int:
    """CLI entry point for environment setup."""
    parser = argparse.ArgumentParser(
        description="OpenSSL Tools Environment Setup",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  openssl-env --minimal    # Basic Python environment
  openssl-env --full       # Complete Conan environment (default)
  openssl-env --dev        # Development environment with testing tools
  openssl-env --force      # Force reinstall
        """
    )
    
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--minimal", 
        action="store_const", 
        dest="mode", 
        const="minimal",
        help="Set up minimal Python environment"
    )
    mode_group.add_argument(
        "--full", 
        action="store_const", 
        dest="mode", 
        const="full",
        help="Set up full Conan environment (default)"
    )
    mode_group.add_argument(
        "--dev", 
        action="store_const", 
        dest="mode", 
        const="dev",
        help="Set up development environment with testing tools"
    )
    
    parser.add_argument(
        "--force", 
        action="store_true",
        help="Force reinstall even if environment exists"
    )
    
    parser.set_defaults(mode="full")
    
    args = parser.parse_args()
    
    print(f"🚀 Setting up OpenSSL development environment ({args.mode} mode)...")
    
    success = setup_environment(mode=args.mode, force=args.force)
    
    if success:
        print("✅ Environment setup completed successfully!")
        return 0
    else:
        print("❌ Environment setup failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
