"""
PlatformIO Setup for ESP32 Projects

Handles PlatformIO installation, configuration, and ESP32 platform setup.
"""

import subprocess
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List

from ..execute_command import execute_command
from ..exceptions import SharedDevToolsError


class PlatformIOSetup:
    """Manages PlatformIO setup for ESP32 development."""

    def __init__(self, project_root: Path, dry_run: bool = False, verbose: bool = False):
        """
        Initialize PlatformIO setup manager.

        Args:
            project_root: Root directory of the ESP32 project
            dry_run: Enable dry-run mode
            verbose: Enable verbose output
        """
        self.project_root = project_root
        self.dry_run = dry_run
        self.verbose = verbose
        self.platformio_dir = project_root / ".platformio"

    def check_platformio_installed(self) -> bool:
        """
        Check if PlatformIO is installed and accessible.

        Returns:
            bool: True if PlatformIO is available
        """
        try:
            result = execute_command(
                ["pio", "--version"],
                cwd=self.project_root,
                capture_output=True,
                dry_run=self.dry_run
            )
            if self.verbose and not self.dry_run:
                version = result.stdout.strip().split('\n')[0] if result.stdout else "Unknown"
                print(f"✅ PlatformIO available: {version}")
            return result.returncode == 0
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def install_platformio(self) -> bool:
        """
        Install PlatformIO using pip.

        Returns:
            bool: True if installation successful
        """
        print("📦 Installing PlatformIO...")

        try:
            cmd = [sys.executable, "-m", "pip", "install", "--user", "platformio"]
            execute_command(cmd, cwd=self.project_root, dry_run=self.dry_run)
            print("✅ PlatformIO installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ PlatformIO installation failed: {e}")
            return False

    def install_esp32_platform(self) -> bool:
        """
        Install ESP32 platform for PlatformIO.

        Returns:
            bool: True if platform installation successful
        """
        print("🔧 Installing ESP32 platform...")

        try:
            # Check if ESP32 platform is already installed
            result = execute_command(
                ["pio", "platform", "show", "espressif32"],
                cwd=self.project_root,
                capture_output=True,
                dry_run=self.dry_run
            )

            if result.returncode == 0:
                print("✅ ESP32 platform already installed")
                return True

            # Install ESP32 platform
            cmd = ["pio", "platform", "install", "espressif32", "--with-package",
                   "framework-arduinoespressif32"]
            execute_command(cmd, cwd=self.project_root, dry_run=self.dry_run)
            print("✅ ESP32 platform installed")
            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ ESP32 platform installation failed: {e}")
            return False

    def configure_platformio(self, config: Dict[str, Any]) -> bool:
        """
        Configure PlatformIO with project-specific settings.

        Args:
            config: PlatformIO configuration dictionary

        Returns:
            bool: True if configuration successful
        """
        print("⚙️  Configuring PlatformIO...")

        try:
            # Set PlatformIO core directory
            if 'core_dir' in config:
                core_dir = Path(config['core_dir'])
                core_dir.mkdir(parents=True, exist_ok=True)

                cmd = ["pio", "settings", "set", "core_dir", str(core_dir)]
                execute_command(cmd, cwd=self.project_root, dry_run=self.dry_run)

            # Set other PlatformIO settings
            settings = config.get('settings', {})
            for key, value in settings.items():
                cmd = ["pio", "settings", "set", key, str(value)]
                execute_command(cmd, cwd=self.project_root, dry_run=self.dry_run)

            print("✅ PlatformIO configured")
            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ PlatformIO configuration failed: {e}")
            return False

    def verify_setup(self) -> Dict[str, Any]:
        """
        Verify PlatformIO setup is working correctly.

        Returns:
            Dict containing verification results
        """
        results = {
            'platformio_available': False,
            'esp32_platform_available': False,
            'configuration_valid': False,
            'errors': []
        }

        try:
            # Check PlatformIO availability
            if self.check_platformio_installed():
                results['platformio_available'] = True

                # Check ESP32 platform
                result = execute_command(
                    ["pio", "platform", "show", "espressif32"],
                    cwd=self.project_root,
                    capture_output=True,
                    dry_run=self.dry_run
                )
                if result.returncode == 0:
                    results['esp32_platform_available'] = True

                # Check configuration
                result = execute_command(
                    ["pio", "settings", "get"],
                    cwd=self.project_root,
                    capture_output=True,
                    dry_run=self.dry_run
                )
                if result.returncode == 0:
                    results['configuration_valid'] = True

        except Exception as e:
            results['errors'].append(str(e))

        return results

    def setup(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Complete PlatformIO setup for ESP32 development.

        Args:
            config: Optional PlatformIO configuration

        Returns:
            bool: True if setup successful
        """
        print("\n🔌 Setting up PlatformIO for ESP32 development...")

        success = True

        # Install PlatformIO if not available
        if not self.check_platformio_installed():
            if not self.install_platformio():
                return False

        # Install ESP32 platform
        if not self.install_esp32_platform():
            success = False

        # Configure PlatformIO
        if config and success:
            if not self.configure_platformio(config):
                success = False

        # Verify setup
        verification = self.verify_setup()
        if not all([verification['platformio_available'],
                   verification['esp32_platform_available'],
                   verification['configuration_valid']]):
            print("❌ PlatformIO setup verification failed")
            for error in verification['errors']:
                print(f"   Error: {error}")
            success = False
        else:
            print("✅ PlatformIO setup completed successfully")

        return success