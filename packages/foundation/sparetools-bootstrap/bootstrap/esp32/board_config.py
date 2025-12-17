"""
ESP32 Board Configuration Manager

Manages ESP32 board configurations, pin mappings, and hardware-specific settings.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List

from ..exceptions import SharedDevToolsError


class ESP32BoardConfig:
    """Manages ESP32 board configurations and hardware mappings."""

    # Default ESP32 board configurations
    DEFAULT_BOARDS = {
        "esp32dev": {
            "name": "ESP32 DevKit V1",
            "chip": "esp32",
            "flash_size": "4MB",
            "psram": False,
            "pins": {
                "gpio_0": 0,   # Boot button
                "gpio_2": 2,   # Built-in LED
                "gpio_12": 12, # MTDI (JTAG)
                "gpio_13": 13, # MTCK (JTAG)
                "gpio_14": 14, # MTMS (JTAG)
                "gpio_15": 15, # MTDO (JTAG)
            }
        },
        "esp32-s3-devkitc-1": {
            "name": "ESP32-S3 DevKitC-1",
            "chip": "esp32-s3",
            "flash_size": "8MB",
            "psram": "8MB",
            "pins": {
                "gpio_0": 0,   # Boot button
                "gpio_3": 3,   # USB JTAG
                "gpio_4": 4,   # ADC
                "gpio_5": 5,   # SPI CS
                "gpio_18": 18, # SPI SCK
                "gpio_19": 19, # SPI MISO
                "gpio_23": 23, # SPI MOSI
            }
        },
        "esp32-c3-devkitc-02": {
            "name": "ESP32-C3 DevKitC-02",
            "chip": "esp32-c3",
            "flash_size": "4MB",
            "psram": False,
            "pins": {
                "gpio_0": 0,   # Boot button
                "gpio_2": 2,   # Built-in LED
                "gpio_8": 8,   # SPI flash
                "gpio_9": 9,   # SPI flash
                "gpio_10": 10, # SPI flash
            }
        }
    }

    def __init__(self, project_root: Path, dry_run: bool = False, verbose: bool = False):
        """
        Initialize ESP32 board configuration manager.

        Args:
            project_root: Root directory of the ESP32 project
            dry_run: Enable dry-run mode
            verbose: Enable verbose output
        """
        self.project_root = project_root
        self.dry_run = dry_run
        self.verbose = verbose
        self.boards_file = project_root / "boards" / "esp32-boards.json"

    def get_board_config(self, board_name: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration for a specific ESP32 board.

        Args:
            board_name: Name of the ESP32 board

        Returns:
            Dict containing board configuration or None if not found
        """
        # Check custom boards first
        custom_config = self._load_custom_boards()
        if custom_config and board_name in custom_config:
            return custom_config[board_name]

        # Check default boards
        if board_name in self.DEFAULT_BOARDS:
            return self.DEFAULT_BOARDS[board_name]

        return None

    def list_available_boards(self) -> List[str]:
        """
        List all available ESP32 board configurations.

        Returns:
            List of available board names
        """
        boards = list(self.DEFAULT_BOARDS.keys())

        # Add custom boards
        custom_config = self._load_custom_boards()
        if custom_config:
            boards.extend(custom_config.keys())

        return sorted(boards)

    def add_custom_board(self, board_name: str, config: Dict[str, Any]) -> bool:
        """
        Add a custom ESP32 board configuration.

        Args:
            board_name: Name of the custom board
            config: Board configuration dictionary

        Returns:
            bool: True if board added successfully
        """
        try:
            if self.dry_run:
                print(f"[DRY-RUN] Would add custom board: {board_name}")
                return True

            # Load existing custom boards
            custom_boards = self._load_custom_boards() or {}

            # Validate configuration
            if not self._validate_board_config(config):
                print(f"❌ Invalid board configuration for {board_name}")
                return False

            # Add the new board
            custom_boards[board_name] = config

            # Save custom boards
            self._save_custom_boards(custom_boards)

            if self.verbose:
                print(f"✅ Custom board added: {board_name}")

            return True

        except Exception as e:
            print(f"❌ Failed to add custom board {board_name}: {e}")
            return False

    def generate_platformio_board_config(self, board_name: str) -> Optional[Dict[str, Any]]:
        """
        Generate PlatformIO-compatible board configuration.

        Args:
            board_name: Name of the ESP32 board

        Returns:
            Dict containing PlatformIO board configuration or None if board not found
        """
        board_config = self.get_board_config(board_name)
        if not board_config:
            return None

        # Generate PlatformIO configuration
        pio_config = {
            "build": {
                "core": board_config["chip"],
                "variant": board_config["chip"]
            },
            "upload": {
                "maximum_size": self._parse_flash_size(board_config["flash_size"])
            }
        }

        # Add PSRAM configuration if available
        if board_config.get("psram"):
            pio_config["build"]["psram"] = "enabled"

        return pio_config

    def validate_board_compatibility(self, board_name: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate if a board meets specific requirements.

        Args:
            board_name: Name of the ESP32 board
            requirements: Dictionary of requirements to check

        Returns:
            Dict containing validation results
        """
        results = {
            'compatible': True,
            'errors': [],
            'warnings': []
        }

        board_config = self.get_board_config(board_name)
        if not board_config:
            results['errors'].append(f"Board not found: {board_name}")
            results['compatible'] = False
            return results

        # Check chip compatibility
        if 'chip' in requirements:
            required_chip = requirements['chip']
            if board_config['chip'] != required_chip:
                results['errors'].append(f"Chip mismatch: requires {required_chip}, board has {board_config['chip']}")
                results['compatible'] = False

        # Check flash size
        if 'min_flash_size' in requirements:
            min_flash = self._parse_flash_size(requirements['min_flash_size'])
            board_flash = self._parse_flash_size(board_config['flash_size'])
            if board_flash < min_flash:
                results['errors'].append(f"Insufficient flash: requires {min_flash}MB, board has {board_flash}MB")
                results['compatible'] = False

        # Check PSRAM
        if requirements.get('requires_psram', False):
            if not board_config.get('psram'):
                results['errors'].append("PSRAM required but not available on this board")
                results['compatible'] = False

        # Check GPIO availability
        if 'required_pins' in requirements:
            available_pins = set(board_config.get('pins', {}).keys())
            required_pins = set(requirements['required_pins'])
            missing_pins = required_pins - available_pins
            if missing_pins:
                results['errors'].append(f"Missing required pins: {missing_pins}")
                results['compatible'] = False

        return results

    def _load_custom_boards(self) -> Optional[Dict[str, Any]]:
        """Load custom board configurations from file."""
        if not self.boards_file.exists():
            return None

        try:
            with open(self.boards_file, 'r') as f:
                return json.load(f)
        except Exception:
            return None

    def _save_custom_boards(self, boards: Dict[str, Any]) -> bool:
        """Save custom board configurations to file."""
        try:
            self.boards_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.boards_file, 'w') as f:
                json.dump(boards, f, indent=2)
            return True
        except Exception:
            return False

    def _validate_board_config(self, config: Dict[str, Any]) -> bool:
        """Validate board configuration structure."""
        required_fields = ['name', 'chip', 'flash_size']
        for field in required_fields:
            if field not in config:
                return False

        # Validate chip type
        valid_chips = ['esp32', 'esp32-s2', 'esp32-s3', 'esp32-c3', 'esp32-c6']
        if config['chip'] not in valid_chips:
            return False

        return True

    def _parse_flash_size(self, size_str: str) -> int:
        """Parse flash size string to megabytes."""
        if isinstance(size_str, int):
            return size_str

        size_str = size_str.upper().replace('MB', '').replace('M', '')
        try:
            return int(size_str)
        except ValueError:
            return 4  # Default to 4MB