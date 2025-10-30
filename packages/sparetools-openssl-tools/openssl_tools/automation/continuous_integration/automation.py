#!/usr/bin/env python3
"""
OpenSSL Conan Automation Script
Based on ngapy-dev patterns for robust Conan package management
"""

import argparse
import json
import logging
import os
import re
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timedelta
from functools import cache
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml
from conan import ConanFile
from conan.tools.files import load, save

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)


class ConanAutomation:
    """Conan automation class based on ngapy-dev patterns"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path("scripts/ci/ci_config.yaml")
        self.config = self._load_config()
        self.conan_home = self._get_conan_home()
        self._setup_environment()
        
    def _load_config(self) -> Dict:
        """Load CI configuration from YAML file"""
        if not self.config_path.exists():
            log.warning(f"Config file {self.config_path} not found, using defaults")
            return self._get_default_config()
            
        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)
            
        # Resolve environment variables
        config = self._resolve_env_vars(config)
        return config
        
    def _get_default_config(self) -> Dict:
        """Get default configuration"""
        return {
            "conan": {
                "cache": {"home": "~/.conan2", "max_size": "5GB"},
                "profiles": []
            },
            "build": {"build_threads": -1, "parallel_download": -1},
            "testing": {"reporting": {"junit_xml": True}},
            "security": {"sbom": {"enabled": True}},
            "monitoring": {"build_metrics": {"enabled": True}}
        }
        
    def _resolve_env_vars(self, config: Dict) -> Dict:
        """Resolve environment variables in configuration"""
        def resolve_value(value):
            if isinstance(value, str):
                # Replace ${VAR} with environment variable
                return re.sub(r'\$\{([^}]+)\}', 
                             lambda m: os.environ.get(m.group(1), m.group(0)), 
                             value)
            elif isinstance(value, dict):
                return {k: resolve_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [resolve_value(item) for item in value]
            return value
            
        return resolve_value(config)
        
    def _get_conan_home(self) -> Path:
        """Get Conan home directory"""
        conan_home = os.environ.get('CONAN_USER_HOME', '~/.conan2')
        return Path(conan_home).expanduser()
        
    def _setup_environment(self):
        """Set up environment variables for Conan"""
        os.environ['CONAN_COLOR_DISPLAY'] = '1'
        os.environ['CLICOLOR_FORCE'] = '1'
        os.environ['CLICOLOR'] = '1'
        
        # Set parallel download
        parallel_download = self.config.get('build', {}).get('parallel_download', -1)
        if parallel_download == -1:
            import multiprocessing
            parallel_download = multiprocessing.cpu_count()
            
        os.environ['CONAN_CPU_COUNT'] = str(parallel_download)
        
    @cache
    def get_conan_executable(self) -> Path:
        """Find Conan executable"""
        conan_exe = Path("conan")
        
        # Check if conan is in PATH
        try:
            result = subprocess.run([str(conan_exe), "--version"], 
                                  capture_output=True, text=True, check=True)
            log.debug(f"Found Conan: {result.stdout.strip()}")
            return conan_exe
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
            
        # Check common installation paths
        common_paths = [
            Path.home() / ".local" / "bin" / "conan",
            Path("/usr/local/bin/conan"),
            Path("/usr/bin/conan"),
        ]
        
        for path in common_paths:
            if path.exists():
                log.debug(f"Found Conan at: {path}")
                return path
                
        raise RuntimeError("Conan executable not found. Please install Conan 2.x")
        
    def execute_conan_command(self, command: List[str], cwd: Optional[Path] = None) -> Tuple[int, List[str]]:
        """Execute Conan command with proper error handling"""
        conan_exe = self.get_conan_executable()
        full_command = [str(conan_exe)] + command
        
        log.info(f"Executing: {' '.join(full_command)}")
        
        try:
            result = subprocess.run(
                full_command,
                cwd=cwd,
                capture_output=True,
                text=True,
                check=False
            )
            
            output_lines = result.stdout.splitlines() if result.stdout else []
            error_lines = result.stderr.splitlines() if result.stderr else []
            
            # Log output
            for line in output_lines:
                if not line.startswith('WARN'):
                    log.info(line)
                    
            for line in error_lines:
                if not line.startswith('WARN'):
                    log.error(line)
                    
            return result.returncode, output_lines
            
        except Exception as e:
            log.error(f"Failed to execute Conan command: {e}")
            return 1, [str(e)]
            
    def setup_remotes(self):
        """Set up Conan remotes based on configuration"""
        remotes = self.config.get('conan', {}).get('remotes', [])
        
        # Clean existing remotes
        self.execute_conan_command(['remote', 'clean'])
        
        # Add configured remotes
        for remote in remotes:
            if remote.get('enabled', True):
                self.execute_conan_command([
                    'remote', 'add', remote['name'], remote['url']
                ])
                log.info(f"Added remote: {remote['name']}")
                
    def create_profile(self, profile_name: str, profile_config: Dict) -> bool:
        """Create Conan profile from configuration"""
        profile_path = self.conan_home / "profiles" / profile_name
        
        # Ensure profiles directory exists
        profile_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate profile content
        profile_content = []
        profile_content.append(f"[settings]")
        
        settings = profile_config.get('settings', {})
        for key, value in settings.items():
            profile_content.append(f"{key}={value}")
            
        # Add configuration
        if 'conf' in profile_config:
            profile_content.append(f"\n[conf]")
            for key, value in profile_config['conf'].items():
                profile_content.append(f"{key}={value}")
                
        # Write profile
        with open(profile_path, 'w') as f:
            f.write('\n'.join(profile_content))
            
        log.info(f"Created profile: {profile_name}")
        return True
        
    def setup_profiles(self):
        """Set up all configured Conan profiles"""
        profiles = self.config.get('conan', {}).get('profiles', [])
        
        for profile in profiles:
            profile_name = profile['name']
            profile_config = profile
            self.create_profile(profile_name, profile_config)
            
    def install_dependencies(self, conanfile_path: Path, profile: str = "default") -> bool:
        """Install dependencies for a Conan project"""
        log.info(f"Installing dependencies for {conanfile_path}")
        
        # Check if conanfile exists
        if not conanfile_path.exists():
            log.error(f"Conanfile not found: {conanfile_path}")
            return False
            
        # Install with profile
        returncode, output = self.execute_conan_command([
            'install', str(conanfile_path),
            '--profile', profile,
            '--build=missing'
        ], cwd=conanfile_path.parent)
        
        if returncode == 0:
            log.info("Dependencies installed successfully")
            return True
        else:
            log.error("Failed to install dependencies")
            return False
            
    def create_package(self, conanfile_path: Path, profile: str = "default") -> bool:
        """Create Conan package"""
        log.info(f"Creating package for {conanfile_path}")
        
        # Create package
        returncode, output = self.execute_conan_command([
            'create', str(conanfile_path),
            '--profile', profile,
            '--build=missing'
        ], cwd=conanfile_path.parent)
        
        if returncode == 0:
            log.info("Package created successfully")
            return True
        else:
            log.error("Failed to create package")
            return False
            
    def run_tests(self, conanfile_path: Path, profile: str = "default") -> bool:
        """Run tests for a Conan package"""
        log.info(f"Running tests for {conanfile_path}")
        
        # Run test package
        returncode, output = self.execute_conan_command([
            'test', str(conanfile_path),
            '--profile', profile
        ], cwd=conanfile_path.parent)
        
        if returncode == 0:
            log.info("Tests passed successfully")
            return True
        else:
            log.error("Tests failed")
            return False
            
    def generate_sbom(self, conanfile_path: Path) -> Optional[Path]:
        """Generate Software Bill of Materials"""
        if not self.config.get('security', {}).get('sbom', {}).get('enabled', False):
            return None
            
        log.info("Generating SBOM")
        
        # Create temporary file for SBOM output
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            sbom_path = Path(f.name)
            
        try:
            # Generate SBOM using Conan
            returncode, output = self.execute_conan_command([
                'graph', 'info', str(conanfile_path),
                '--format', 'json',
                '--output', str(sbom_path)
            ], cwd=conanfile_path.parent)
            
            if returncode == 0:
                log.info(f"SBOM generated: {sbom_path}")
                return sbom_path
            else:
                log.error("Failed to generate SBOM")
                return None
                
        except Exception as e:
            log.error(f"Error generating SBOM: {e}")
            return None
            
    def cleanup_cache(self, max_age_days: int = 7):
        """Clean up old cache entries"""
        log.info(f"Cleaning up cache entries older than {max_age_days} days")
        
        # Remove old packages
        returncode, output = self.execute_conan_command([
            'remove', '*',
            '--confirm'
        ])
        
        if returncode == 0:
            log.info("Cache cleanup completed")
        else:
            log.warning("Cache cleanup had issues")
            
    def collect_build_metrics(self, start_time: float, end_time: float) -> Dict:
        """Collect build metrics"""
        if not self.config.get('monitoring', {}).get('build_metrics', {}).get('enabled', False):
            return {}
            
        build_time = end_time - start_time
        
        metrics = {
            'build_time_seconds': build_time,
            'build_time_human': str(timedelta(seconds=int(build_time))),
            'timestamp': datetime.now().isoformat(),
            'conan_home': str(self.conan_home),
            'config_version': self.config.get('version', 'unknown')
        }
        
        # Save metrics
        metrics_path = Path("build_metrics.json")
        with open(metrics_path, 'w') as f:
            json.dump(metrics, f, indent=2)
            
        log.info(f"Build metrics saved: {metrics_path}")
        return metrics


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='OpenSSL Conan Automation')
    parser.add_argument('--config', type=Path, help='Configuration file path')
    parser.add_argument('--profile', default='default', help='Conan profile to use')
    parser.add_argument('--conanfile', type=Path, default=Path('conanfile.py'), 
                       help='Path to conanfile.py')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Set up Conan environment')
    
    # Install command
    install_parser = subparsers.add_parser('install', help='Install dependencies')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create package')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Run tests')
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Clean up cache')
    cleanup_parser.add_argument('--max-age', type=int, default=7, 
                               help='Maximum age in days for cache entries')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
        
    # Initialize automation
    automation = ConanAutomation(args.config)
    
    start_time = time.time()
    
    try:
        if args.command == 'setup':
            automation.setup_remotes()
            automation.setup_profiles()
            log.info("Conan environment setup completed")
            
        elif args.command == 'install':
            success = automation.install_dependencies(args.conanfile, args.profile)
            if not success:
                return 1
                
        elif args.command == 'create':
            success = automation.create_package(args.conanfile, args.profile)
            if not success:
                return 1
                
        elif args.command == 'test':
            success = automation.run_tests(args.conanfile, args.profile)
            if not success:
                return 1
                
        elif args.command == 'cleanup':
            automation.cleanup_cache(args.max_age)
            
        # Generate SBOM if enabled
        automation.generate_sbom(args.conanfile)
        
        # Collect metrics
        end_time = time.time()
        automation.collect_build_metrics(start_time, end_time)
        
        return 0
        
    except Exception as e:
        log.error(f"Command failed: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
