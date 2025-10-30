#!/usr/bin/env python3
"""
Conan Python Environment Management
Provides utilities for managing Python environment through Conan cache/remote
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class ConanPythonEnvironment:
    """Manages Python environment through Conan cache/remote"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.conan_dev_dir = project_root / "conan-dev"
        self.conan_cache_dir = self.conan_dev_dir / "cache"
        self.conan_python_cache = self.conan_cache_dir / "python"
        
    def setup_environment(self) -> Dict[str, str]:
        """Setup Conan-managed Python environment variables"""
        env = os.environ.copy()
        
        # Set core Conan Python environment variables
        env['CONAN_PYTHON_ENV'] = 'managed'
        env['CONAN_PYTHON_SOURCE'] = 'cache_remote'
        env['CONAN_USER_HOME'] = str(self.conan_dev_dir)
        env['OPENSSL_TOOLS_ROOT'] = str(self.project_root)
        
        # Set Python cache path
        if self.conan_python_cache.exists():
            env['CONAN_PYTHON_CACHE'] = str(self.conan_python_cache)
            logger.info(f"Using Conan Python cache: {self.conan_python_cache}")
        else:
            logger.warning(f"Conan Python cache not found: {self.conan_python_cache}")
        
        # Setup Python paths
        python_paths = self._get_python_paths()
        if python_paths:
            current_pythonpath = env.get('PYTHONPATH', '')
            new_pythonpath = os.pathsep.join(python_paths + [current_pythonpath])
            env['PYTHONPATH'] = new_pythonpath
            logger.info(f"Updated PYTHONPATH with {len(python_paths)} Conan paths")
        
        # Setup PATH
        python_bin_paths = self._get_python_bin_paths()
        if python_bin_paths:
            current_path = env.get('PATH', '')
            new_path = os.pathsep.join(python_bin_paths + [current_path])
            env['PATH'] = new_path
            logger.info(f"Updated PATH with {len(python_bin_paths)} Conan Python bin paths")
        
        return env
    
    def get_python_interpreter(self) -> str:
        """Get the appropriate Python interpreter from Conan environment"""
        # Priority order:
        # 1. Conan package Python wrapper
        # 2. Conan cache Python
        # 3. Virtual environment Python
        # 4. System Python
        
        # Check for Conan package Python wrapper
        conan_package_python = self._find_conan_package_python()
        if conan_package_python:
            logger.info(f"Using Conan package Python wrapper: {conan_package_python}")
            return str(conan_package_python)
        
        # Check for Conan cache Python
        conan_cache_python = self.conan_python_cache / "bin" / "python"
        if conan_cache_python.exists():
            logger.info(f"Using Conan cache Python: {conan_cache_python}")
            return str(conan_cache_python)
        
        # Check for virtual environment
        venv_python = self.project_root / "venv" / "bin" / "python"
        if venv_python.exists():
            logger.info(f"Using virtual environment Python: {venv_python}")
            return str(venv_python)
        
        # Fallback to system Python
        logger.info(f"Using system Python: {sys.executable}")
        return sys.executable
    
    def _find_conan_package_python(self) -> Optional[Path]:
        """Find Conan package Python wrapper"""
        packages_dir = self.conan_dev_dir / "packages"
        if not packages_dir.exists():
            return None
        
        # Look for openssl-tools package
        for package_dir in packages_dir.iterdir():
            if package_dir.is_dir():
                python_wrapper = package_dir / "python" / "bin" / "python"
                if python_wrapper.exists():
                    return python_wrapper
        
        return None
    
    def _get_python_paths(self) -> List[str]:
        """Get Python paths from Conan environment"""
        python_paths = []
        
        # Add Conan Python cache
        if self.conan_python_cache.exists():
            python_paths.append(str(self.conan_python_cache))
        
        # Add project openssl_tools
        openssl_tools_path = self.project_root / "openssl_tools"
        if openssl_tools_path.exists():
            python_paths.append(str(openssl_tools_path))
        
        # Add Conan package paths
        packages_dir = self.conan_dev_dir / "packages"
        if packages_dir.exists():
            for package_dir in packages_dir.iterdir():
                if package_dir.is_dir():
                    # Add package openssl_tools
                    package_openssl_tools = package_dir / "openssl_tools"
                    if package_openssl_tools.exists():
                        python_paths.append(str(package_openssl_tools))
                    
                    # Add package Python lib
                    package_python_lib = package_dir / "python" / "lib"
                    if package_python_lib.exists():
                        python_paths.append(str(package_python_lib))
        
        return python_paths
    
    def _get_python_bin_paths(self) -> List[str]:
        """Get Python binary paths from Conan environment"""
        bin_paths = []
        
        # Add Conan Python cache bin
        conan_python_bin = self.conan_python_cache / "bin"
        if conan_python_bin.exists():
            bin_paths.append(str(conan_python_bin))
        
        # Add Conan package Python bin paths
        packages_dir = self.conan_dev_dir / "packages"
        if packages_dir.exists():
            for package_dir in packages_dir.iterdir():
                if package_dir.is_dir():
                    package_python_bin = package_dir / "python" / "bin"
                    if package_python_bin.exists():
                        bin_paths.append(str(package_python_bin))
        
        return bin_paths
    
    def create_environment_info(self) -> Dict:
        """Create environment information for debugging"""
        return {
            "conan_python_env": "managed",
            "conan_python_source": "cache_remote",
            "project_root": str(self.project_root),
            "conan_dev_dir": str(self.conan_dev_dir),
            "conan_cache_dir": str(self.conan_cache_dir),
            "conan_python_cache": str(self.conan_python_cache),
            "python_interpreter": self.get_python_interpreter(),
            "python_paths": self._get_python_paths(),
            "python_bin_paths": self._get_python_bin_paths(),
            "environment_variables": {
                "CONAN_PYTHON_ENV": os.environ.get('CONAN_PYTHON_ENV', 'not_set'),
                "CONAN_PYTHON_SOURCE": os.environ.get('CONAN_PYTHON_SOURCE', 'not_set'),
                "CONAN_PYTHON_CACHE": os.environ.get('CONAN_PYTHON_CACHE', 'not_set'),
                "OPENSSL_TOOLS_ROOT": os.environ.get('OPENSSL_TOOLS_ROOT', 'not_set'),
                "PYTHONPATH": os.environ.get('PYTHONPATH', 'not_set'),
            }
        }
    
    def save_environment_info(self, output_path: Optional[Path] = None) -> Path:
        """Save environment information to file"""
        if output_path is None:
            output_path = self.conan_dev_dir / "python_env_info.json"
        
        env_info = self.create_environment_info()
        
        with open(output_path, 'w') as f:
            json.dump(env_info, f, indent=2)
        
        logger.info(f"Environment info saved to: {output_path}")
        return output_path
    
    def validate_environment(self) -> Tuple[bool, List[str]]:
        """Validate Conan Python environment setup"""
        issues = []
        
        # Check if Conan dev directory exists
        if not self.conan_dev_dir.exists():
            issues.append(f"Conan dev directory not found: {self.conan_dev_dir}")
        
        # Check if Python interpreter is accessible
        python_interpreter = self.get_python_interpreter()
        if not Path(python_interpreter).exists():
            issues.append(f"Python interpreter not found: {python_interpreter}")
        
        # Check if Python paths are valid
        python_paths = self._get_python_paths()
        for path in python_paths:
            if not Path(path).exists():
                issues.append(f"Python path not found: {path}")
        
        # Check environment variables
        required_env_vars = [
            'CONAN_PYTHON_ENV',
            'CONAN_PYTHON_SOURCE',
            'OPENSSL_TOOLS_ROOT'
        ]
        
        for var in required_env_vars:
            if not os.environ.get(var):
                issues.append(f"Required environment variable not set: {var}")
        
        is_valid = len(issues) == 0
        return is_valid, issues


def setup_conan_python_environment(project_root: Path) -> ConanPythonEnvironment:
    """Setup and return Conan Python environment manager"""
    env_manager = ConanPythonEnvironment(project_root)
    env_manager.setup_environment()
    return env_manager


def get_conan_python_interpreter(project_root: Path) -> str:
    """Get Conan-managed Python interpreter"""
    env_manager = ConanPythonEnvironment(project_root)
    return env_manager.get_python_interpreter()


def validate_conan_python_environment(project_root: Path) -> Tuple[bool, List[str]]:
    """Validate Conan Python environment"""
    env_manager = ConanPythonEnvironment(project_root)
    return env_manager.validate_environment()


if __name__ == "__main__":
    # Command line interface for environment management
    import argparse
    
    parser = argparse.ArgumentParser(description="Conan Python Environment Management")
    parser.add_argument("--project-root", type=Path, default=Path.cwd(),
                       help="Project root directory")
    parser.add_argument("--validate", action="store_true",
                       help="Validate environment setup")
    parser.add_argument("--info", action="store_true",
                       help="Show environment information")
    parser.add_argument("--save-info", action="store_true",
                       help="Save environment information to file")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    # Create environment manager
    env_manager = ConanPythonEnvironment(args.project_root)
    
    if args.validate:
        is_valid, issues = env_manager.validate_environment()
        if is_valid:
            print("✅ Conan Python environment is valid")
        else:
            print("❌ Conan Python environment has issues:")
            for issue in issues:
                print(f"  - {issue}")
    
    if args.info:
        env_info = env_manager.create_environment_info()
        print(json.dumps(env_info, indent=2))
    
    if args.save_info:
        output_path = env_manager.save_environment_info()
        print(f"Environment info saved to: {output_path}")
    
    if not any([args.validate, args.info, args.save_info]):
        # Default: setup environment
        env_manager.setup_environment()
        print("Conan Python environment setup complete")
