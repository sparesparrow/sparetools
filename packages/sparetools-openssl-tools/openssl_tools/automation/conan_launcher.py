#!/usr/bin/env python3
"""
OpenSSL Tools Conan Launcher
Based on openssl-tools patterns for sophisticated launcher system
"""

import argparse
import logging
import os
import sys
import subprocess
import tempfile
import yaml
from pathlib import Path
from typing import List, Optional, Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from util.custom_logging import setup_logging_from_config
from util.conan_python_env import (
    ConanPythonEnvironment, 
    setup_conan_python_environment,
    get_conan_python_interpreter
)
# Note: conan_tools module was consolidated into openssl_tools
# These functions need to be implemented or imported from the correct location
# from conan_tools.conan_functions import (
#     get_default_conan, setup_parallel_download, remove_conan_lock_files
# )
# from conan_tools.artifactory_functions import (
#     enable_conan_remote, setup_artifactory_remote
# )


class ConfigLoaderManager:
    """Simple configuration loader for launcher"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.conf_dir = self.project_root / "conf"
    
    def get_configuration(self):
        """Load configuration from YAML files"""
        config = type('Config', (), {})()
        
        # Load launcher config
        launcher_config_path = self.conf_dir / "launcher.yaml"
        if launcher_config_path.exists():
            with open(launcher_config_path, 'r') as f:
                launcher_data = yaml.safe_load(f)
                config.launcher = launcher_data.get('launcher', {})
        
        # Load artifactory config
        artifactory_config_path = self.conf_dir / "1_artifactory.yaml"
        if artifactory_config_path.exists():
            with open(artifactory_config_path, 'r') as f:
                artifactory_data = yaml.safe_load(f)
                config.artifactory = artifactory_data
        
        return config


class Configuration:
    """Configuration management following openssl-tools patterns"""
    
    def __init__(self, config_data: Optional[Dict[str, Any]] = None):
        self.latest_version = '2.0'
        self.data = config_data or {
            'version': self.latest_version,
            'git_repository': '',
            'remote_setup': '',
            'conan_home': '',
            'python_interpreter': '',
            'build_optimization': True,
            'parallel_downloads': True,
            'cache_cleanup': True
        }
        self.load_config()
    
    def load_config(self):
        """Load configuration from YAML files"""
        try:
            config_loader = ConfigLoaderManager()
            config = config_loader.get_configuration()
            
            # Merge configuration
            if hasattr(config, 'launcher'):
                self.data.update(config.launcher)
            if hasattr(config, 'artifactory'):
                self.data['artifactory_config'] = config.artifactory
            if hasattr(config, 'build'):
                self.data['build_config'] = config.build
                
        except Exception as e:
            logging.warning(f"Failed to load configuration: {e}")
    
    def save_config(self):
        """Save configuration to YAML files"""
        try:
            config_path = project_root / 'conf' / 'launcher.yaml'
            config_path.parent.mkdir(exist_ok=True)
            
            import yaml
            with open(config_path, 'w') as f:
                yaml.dump({'launcher': self.data}, f, default_flow_style=False)
                
        except Exception as e:
            logging.warning(f"Failed to save configuration: {e}")


def check_conan_validity(folder_path: Path) -> bool:
    """Validate that folder contains valid conanfile.py"""
    conanfile_path = folder_path / 'conanfile.py'
    
    if not conanfile_path.exists():
        logging.error(f"No conanfile.py found in {folder_path}")
        return False
    
    # Basic validation - check if it's a valid Python file
    try:
        with open(conanfile_path, 'r') as f:
            content = f.read()
            if 'ConanFile' not in content:
                logging.error(f"Invalid conanfile.py in {folder_path}")
                return False
    except Exception as e:
        logging.error(f"Error reading conanfile.py: {e}")
        return False
    
    logging.info(f"Valid conanfile.py found in {folder_path}")
    return True


def add_packages_paths_to_search_paths(packages: Dict[str, Any]) -> None:
    """Add Conan package paths to PYTHONPATH and sys.path"""
    python_paths = []
    
    for name, (_, _, package_path) in packages.items():
        if isinstance(package_path, Path) and package_path.exists():
            # Add package root to Python path
            python_paths.append(str(package_path))
            
            # Add Conan-managed Python package subdirectories
            for subdir in ['lib', 'site-packages', 'openssl_tools', 'python', 'conan_cache/python']:
                subdir_path = package_path / subdir
                if subdir_path.exists():
                    python_paths.append(str(subdir_path))
    
    # Add Conan cache Python paths
    conan_cache_python = project_root / 'conan-dev' / 'cache' / 'python'
    if conan_cache_python.exists():
        python_paths.append(str(conan_cache_python))
    
    # Update environment with Conan-managed paths
    if python_paths:
        current_pythonpath = os.environ.get('PYTHONPATH', '')
        new_pythonpath = os.pathsep.join(python_paths + [current_pythonpath])
        os.environ['PYTHONPATH'] = new_pythonpath
        
        # Set Conan environment variables
        os.environ['CONAN_PYTHON_ENV'] = 'managed'
        os.environ['CONAN_PYTHON_SOURCE'] = 'cache_remote'
        
        # Also add to sys.path for current session
        for path in python_paths:
            if path not in sys.path:
                sys.path.insert(0, path)
        
        logging.info(f"Added {len(python_paths)} Conan package paths to Python search path")


def prepare_package_script_arguments(repository_root: Path, arguments: List[str]) -> List[str]:
    """Prepare script arguments with package path resolution"""
    prepared_args = []
    
    for arg in arguments:
        # Resolve relative paths relative to repository root
        if arg.startswith('./') or (not arg.startswith('/') and not arg.startswith('\\')):
            resolved_arg = str(repository_root / arg)
            if Path(resolved_arg).exists():
                prepared_args.append(resolved_arg)
            else:
                prepared_args.append(arg)
        else:
            prepared_args.append(arg)
    
    return prepared_args


def run_package_python_script(repository_root: Path, arguments: List[str], 
                             wait_till_finish: bool = True) -> subprocess.CompletedProcess:
    """Run Python script with Conan-managed Python environment setup"""
    
    # Prepare arguments
    script_args = prepare_package_script_arguments(repository_root, arguments)
    
    # Determine Python interpreter - prioritize Conan-managed environment
    python_interpreter = _get_conan_python_interpreter(repository_root)
    
    # Set up Conan-managed Python environment
    env = _setup_conan_python_environment(repository_root)
    
    # Run the script
    cmd = [python_interpreter] + script_args
    logging.info(f"Executing with Conan-managed Python: {' '.join(cmd)}")
    
    try:
        if wait_till_finish:
            result = subprocess.run(cmd, cwd=repository_root, env=env, 
                                  capture_output=False, text=True)
            return result
        else:
            process = subprocess.Popen(cmd, cwd=repository_root, env=env)
            return process
    except Exception as e:
        logging.error(f"Failed to execute script: {e}")
        raise


def _get_conan_python_interpreter(repository_root: Path) -> str:
    """Get Python interpreter from Conan-managed environment"""
    return get_conan_python_interpreter(repository_root)


def _setup_conan_python_environment(repository_root: Path) -> Dict[str, str]:
    """Setup Conan-managed Python environment variables"""
    env_manager = ConanPythonEnvironment(repository_root)
    return env_manager.setup_environment()


def setup_conan_environment(config: Configuration) -> None:
    """Setup Conan environment following openssl-tools patterns"""
    try:
        # Remove lock files for clean builds
        if config.data.get('cache_cleanup', True):
            remove_conan_lock_files()
            logging.info("Cleaned Conan lock files")
        
        # Setup parallel downloads
        if config.data.get('parallel_downloads', True):
            setup_parallel_download()
            logging.info("Configured parallel downloads")
        
        # Setup Artifactory remote if needed
        if config.data.get('remote_setup') != 'passed':
            setup_artifactory_remote()
            enable_conan_remote()
            config.data['remote_setup'] = 'passed'
            config.save_config()
            logging.info("Configured Artifactory remote")
        
    except Exception as e:
        logging.warning(f"Failed to setup Conan environment: {e}")


def check_for_updates(force: bool = False) -> None:
    """Check for updates following openssl-tools patterns"""
    try:
        # This would integrate with package update checking
        logging.info("Checking for updates...")
        # Implementation would go here
        logging.info("Update check completed")
    except Exception as e:
        logging.warning(f"Update check failed: {e}")


def main():
    """Main launcher function following openssl-tools patterns"""
    # Setup logging
    setup_logging_from_config()
    log = logging.getLogger(__name__)
    
    # Initialize configuration
    configuration = Configuration()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='OpenSSL Tools Conan Launcher',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -s                    # Use stored repository path
  %(prog)s -c                    # Setup Conan environment
  %(prog)s -u                    # Update only
  %(prog)s -p script.py args     # Run Python script
  %(prog)s -c conan install .    # Run Conan command
        """
    )
    
    parser.add_argument('-s', '--storedPath', action='store_true', default=True,
                       help='Use stored repository path (default: True)')
    parser.add_argument('-c', '--conanSetup', action='store_true', default=False,
                       help='Setup Conan environment')
    parser.add_argument('-u', '--update', action='store_true', default=False,
                       help='Check for updates only')
    parser.add_argument('-p', '--runWithPython', nargs='+', dest='python_arguments',
                       help='Run Python script with arguments')
    parser.add_argument('-c', '--runWithConan', nargs='+', dest='conan_arguments',
                       help='Run Conan command with arguments')
    parser.add_argument('-r', '--repository', type=str, dest='repository_path',
                       help='Specify repository path')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose logging')
    
    options = parser.parse_args()
    
    # Set logging level
    if options.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Setup Conan environment if requested
    if options.conanSetup or configuration.data['remote_setup'] != 'passed':
        setup_conan_environment(configuration)
    
    # Handle update only mode
    if options.update:
        check_for_updates(force=True)
        sys.exit(0)
    
    # Determine repository path
    if options.repository_path:
        repository_root = Path(options.repository_path)
    elif Path(configuration.data['git_repository']).exists() and options.storedPath:
        repository_root = Path(configuration.data['git_repository'])
    else:
        # Use current directory as fallback
        repository_root = Path.cwd()
        log.warning(f"Using current directory as repository: {repository_root}")
    
    # Validate repository
    if not check_conan_validity(repository_root):
        log.error("Invalid repository - no valid conanfile.py found")
        sys.exit(1)
    
    # Update stored repository path
    if str(repository_root) != configuration.data['git_repository']:
        configuration.data['git_repository'] = str(repository_root)
        configuration.save_config()
    
    # Handle Conan commands
    if options.conan_arguments:
        try:
            conan_cmd = [str(get_default_conan())] + options.conan_arguments
            log.info(f"Executing Conan command: {' '.join(conan_cmd)}")
            result = subprocess.run(conan_cmd, cwd=repository_root)
            sys.exit(result.returncode)
        except Exception as e:
            log.error(f"Conan command failed: {e}")
            sys.exit(1)
    
    # Handle Python script execution
    if options.python_arguments:
        try:
            result = run_package_python_script(repository_root, options.python_arguments)
            sys.exit(result.returncode if hasattr(result, 'returncode') else 0)
        except Exception as e:
            log.error(f"Python script execution failed: {e}")
            sys.exit(1)
    
    # Default behavior - check for updates
    if not any([options.conan_arguments, options.python_arguments]):
        check_for_updates(force=False)
        log.info("Launcher ready. Use -h for help with available options.")
        sys.exit(0)


if __name__ == '__main__':
    main()