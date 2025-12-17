"""
ESP32 Configuration Manager

Manages ESP32-specific configuration including toolchain paths, board settings,
and development environment setup.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List

from ..execute_command import execute_command
from ..exceptions import SharedDevToolsError


class ESP32ConfigManager:
    """Manages ESP32 development environment configuration."""

    def __init__(self, project_root: Path, dry_run: bool = False, verbose: bool = False):
        """
        Initialize ESP32 configuration manager.

        Args:
            project_root: Root directory of the ESP32 project
            dry_run: Enable dry-run mode
            verbose: Enable verbose output
        """
        self.project_root = project_root
        self.dry_run = dry_run
        self.verbose = verbose
        self.config_file = project_root / ".esp32-config.json"

    def generate_config(self, project_name: str, project_type: str = "embedded/esp32") -> Dict[str, Any]:
        """
        Generate ESP32 configuration for the project.

        Args:
            project_name: Name of the ESP32 project
            project_type: Type of ESP32 project

        Returns:
            Dict containing ESP32 configuration
        """
        config = {
            "project": {
                "name": project_name,
                "type": project_type,
                "version": "0.1.0"
            },
            "esp32": {
                "chip_models": ["esp32", "esp32-s2", "esp32-s3", "esp32-c3", "esp32-c6"],
                "default_chip": "esp32",
                "idf_version": "5.0+",
                "arduino_core_version": "3.0.0"
            },
            "platformio": {
                "core_dir": str(self.project_root / ".platformio"),
                "platforms_dir": str(self.project_root / ".platformio" / "platforms"),
                "packages_dir": str(self.project_root / ".platformio" / "packages"),
                "cache_dir": str(self.project_root / ".platformio" / "cache")
            },
            "toolchain": {
                "gcc_version": "8.4.0",
                "binutils_version": "2.35",
                "python_version": "3.12.7"
            },
            "development": {
                "debug_level": "INFO",
                "serial_monitor": {
                    "port": "auto",
                    "baudrate": 115200,
                    "rts": 0,
                    "dtr": 0
                },
                "upload": {
                    "speed": 921600,
                    "reset_method": "nodemcu"
                }
            },
            "paths": {
                "firmware_output": ".pio/build",
                "test_output": "test-results",
                "logs": "logs"
            }
        }

        return config

    def save_config(self, config: Dict[str, Any]) -> bool:
        """
        Save ESP32 configuration to file.

        Args:
            config: Configuration dictionary to save

        Returns:
            bool: True if save successful
        """
        try:
            if self.dry_run:
                print(f"[DRY-RUN] Would save ESP32 config to {self.config_file}")
                return True

            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)

            if self.verbose:
                print(f"✅ ESP32 configuration saved to {self.config_file}")

            return True

        except Exception as e:
            print(f"❌ Failed to save ESP32 configuration: {e}")
            return False

    def load_config(self) -> Optional[Dict[str, Any]]:
        """
        Load ESP32 configuration from file.

        Returns:
            Dict containing configuration or None if not found
        """
        if not self.config_file.exists():
            return None

        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            return config

        except Exception as e:
            print(f"❌ Failed to load ESP32 configuration: {e}")
            return None

    def setup_environment_variables(self, config: Dict[str, Any]) -> Dict[str, str]:
        """
        Set up environment variables for ESP32 development.

        Args:
            config: ESP32 configuration dictionary

        Returns:
            Dict of environment variables to set
        """
        env_vars = {}

        # PlatformIO paths
        platformio_config = config.get('platformio', {})
        if 'core_dir' in platformio_config:
            env_vars['PLATFORMIO_CORE_DIR'] = platformio_config['core_dir']

        # ESP32-specific paths
        paths_config = config.get('paths', {})
        if 'firmware_output' in paths_config:
            env_vars['ESP32_FIRMWARE_DIR'] = str(self.project_root / paths_config['firmware_output'])

        # Project information
        project_config = config.get('project', {})
        env_vars['ESP32_PROJECT_NAME'] = project_config.get('name', 'unknown')
        env_vars['ESP32_PROJECT_TYPE'] = project_config.get('type', 'embedded/esp32')

        return env_vars

    def generate_env_file(self, config: Dict[str, Any], env_file: Path) -> bool:
        """
        Generate .env file with ESP32 environment variables.

        Args:
            config: ESP32 configuration dictionary
            env_file: Path to the .env file to generate

        Returns:
            bool: True if generation successful
        """
        try:
            if self.dry_run:
                print(f"[DRY-RUN] Would generate .env file at {env_file}")
                return True

            env_vars = self.setup_environment_variables(config)

            with open(env_file, 'w') as f:
                f.write("# ESP32 Development Environment Variables\n")
                f.write("# Generated by SpareTools ESP32 Bootstrap\n\n")

                for key, value in env_vars.items():
                    f.write(f'{key}="{value}"\n')

            if self.verbose:
                print(f"✅ Environment file generated: {env_file}")

            return True

        except Exception as e:
            print(f"❌ Failed to generate environment file: {e}")
            return False

    def verify_configuration(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify ESP32 configuration is valid.

        Args:
            config: Configuration to verify

        Returns:
            Dict containing verification results
        """
        results = {
            'valid': True,
            'errors': [],
            'warnings': []
        }

        # Check required sections
        required_sections = ['project', 'esp32', 'platformio', 'toolchain']
        for section in required_sections:
            if section not in config:
                results['errors'].append(f"Missing required section: {section}")
                results['valid'] = False

        # Validate ESP32 configuration
        esp32_config = config.get('esp32', {})
        if 'chip_models' in esp32_config:
            supported_chips = ["esp32", "esp32-s2", "esp32-s3", "esp32-c3", "esp32-c6"]
            for chip in esp32_config['chip_models']:
                if chip not in supported_chips:
                    results['warnings'].append(f"Unsupported ESP32 chip model: {chip}")

        # Validate PlatformIO configuration
        platformio_config = config.get('platformio', {})
        required_pio_paths = ['core_dir', 'platforms_dir', 'packages_dir']
        for path_key in required_pio_paths:
            if path_key not in platformio_config:
                results['warnings'].append(f"Missing PlatformIO path: {path_key}")

        return results