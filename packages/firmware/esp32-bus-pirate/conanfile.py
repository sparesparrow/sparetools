import os
import shutil
import subprocess
from pathlib import Path

from conans import ConanFile, tools


class Esp32BusPirateConan(ConanFile):
    name = "esp32-bus-pirate"
    version = "1.0.0"
    description = "ESP32 Bus Pirate - Multi-protocol hacker's tool firmware"
    url = "https://github.com/geo-tp/ESP32-Bus-Pirate"
    license = "MIT"
    author = "geo-tp"
    topics = ("esp32", "bus-pirate", "firmware", "multi-protocol", "hacking-tools")

    # Package type: application (firmware) with source code
    package_type = "application"

    # Options for board variants and build configuration
    options = {
        "board": ["s3-devkit", "cardputer", "m5stick", "cardputer-adv", "t-embed-s3", "atom-lite-s3", "xiao-esp32s3", "m5stack-stamps3", "all"],
        "build_firmware": [True, False],
        "with_libs": [True, False],  # Include PlatformIO libraries
    }

    default_options = {
        "board": "s3-devkit",
        "build_firmware": True,
        "with_libs": True,
    }

    # Build requirements
    build_requires = [
        "platformio/6.1.6"
    ]

    # Settings for cross-compilation
    settings = "os", "arch", "compiler", "build_type"

    # Source repository path (local clone)
    _source_path = "/home/sparrow/Documents/github/ESP32-Bus-Pirate"

    # Board mapping to PlatformIO environments
    _board_envs = {
        "s3-devkit": ["s3-devkit", "s3-devkit-n16-r8"],
        "cardputer": ["cardputer"],
        "cardputer-adv": ["cardputer-adv"],
        "m5stick": ["m5stick"],
        "t-embed-s3": ["t-embed-s3", "t-embed-s3-cc1101"],
        "atom-lite-s3": ["atom-lite-s3"],
        "xiao-esp32s3": ["xiao-esp32s3"],
        "m5stack-stamps3": ["m5stack-stamps3"],
        "all": ["s3-devkit", "s3-devkit-n16-r8", "cardputer", "cardputer-adv", "m5stick",
                "t-embed-s3", "t-embed-s3-cc1101", "atom-lite-s3", "xiao-esp32s3", "m5stack-stamps3"]
    }

    def source(self):
        """Export source from local ESP32-Bus-Pirate repository"""
        self.output.info(f"Exporting source from: {self._source_path}")

        if not Path(self._source_path).exists():
            raise ConanException(f"ESP32-Bus-Pirate source path not found: {self._source_path}")

        # Copy entire source tree to build folder
        source_path = Path(self._source_path)
        dest_path = Path(self.source_folder)

        # Copy main source files
        for item in source_path.iterdir():
            if item.name not in ['.git', '.pio', '__pycache__', '.vscode']:
                if item.is_file():
                    shutil.copy2(item, dest_path / item.name)
                else:
                    shutil.copytree(item, dest_path / item.name, dirs_exist_ok=True)

        # Verify essential files are present
        required_files = ['platformio.ini', 'src/main.cpp']
        for file in required_files:
            if not (dest_path / file).exists():
                raise ConanException(f"Required file not found: {file}")

        self.output.info("Source export completed successfully")

    def build(self):
        """Build firmware using PlatformIO"""
        if not self.options.build_firmware:
            self.output.info("Firmware building disabled, skipping build step")
            return

        self.output.info("Building ESP32-Bus-Pirate firmware...")

        # Get environments to build
        board_selection = str(self.options.board)
        if board_selection not in self._board_envs:
            raise ConanException(f"Unknown board: {board_selection}")

        environments = self._board_envs[board_selection]
        self.output.info(f"Building for environments: {environments}")

        # Build each environment
        for env in environments:
            self.output.info(f"Building environment: {env}")
            try:
                # Run PlatformIO build
                cmd = ["pio", "run", "-e", env, "--verbose"]
                result = subprocess.run(cmd, cwd=self.source_folder,
                                      capture_output=True, text=True, check=True)
                self.output.info(f"Successfully built {env}")
            except subprocess.CalledProcessError as e:
                self.output.error(f"Failed to build {env}: {e}")
                self.output.error(f"STDOUT: {e.stdout}")
                self.output.error(f"STDERR: {e.stderr}")
                raise

        self.output.info("Firmware build completed successfully")

    def package(self):
        """Package source code and firmware binaries"""
        source_path = Path(self.source_folder)
        package_path = Path(self.package_folder)

        # Package source code
        self.output.info("Packaging source code...")
        for item in source_path.iterdir():
            if item.name not in ['.pio', '__pycache__']:
                if item.is_file():
                    shutil.copy2(item, package_path / item.name)
                else:
                    shutil.copytree(item, package_path / item.name, dirs_exist_ok=True)

        # Package firmware binaries if built
        if self.options.build_firmware:
            self.output.info("Packaging firmware binaries...")
            pio_build_dir = source_path / ".pio" / "build"

            if pio_build_dir.exists():
                firmware_dir = package_path / "firmware"
                firmware_dir.mkdir(exist_ok=True)

                # Copy firmware binaries from each environment
                board_selection = str(self.options.board)
                environments = self._board_envs[board_selection]

                for env in environments:
                    env_build_dir = pio_build_dir / env
                    if env_build_dir.exists():
                        firmware_file = env_build_dir / "firmware.bin"
                        partition_file = env_build_dir / "partitions.bin"

                        if firmware_file.exists():
                            dest_name = f"esp32-bus-pirate-{env}.bin"
                            shutil.copy2(firmware_file, firmware_dir / dest_name)
                            self.output.info(f"Packaged firmware: {dest_name}")

                        if partition_file.exists():
                            part_name = f"esp32-bus-pirate-{env}-partitions.bin"
                            shutil.copy2(partition_file, firmware_dir / part_name)
                            self.output.info(f"Packaged partitions: {part_name}")

        # Create firmware info file
        self._create_firmware_info()

        self.output.info("Packaging completed successfully")

    def _create_firmware_info(self):
        """Create firmware information file"""
        info_file = Path(self.package_folder) / "firmware" / "README.md"

        info_content = f"""# ESP32 Bus Pirate Firmware

Version: {self.version}
Board: {self.options.board}
Built: {tools.get_datetime()}

## Available Firmware Files

"""

        firmware_dir = Path(self.package_folder) / "firmware"
        if firmware_dir.exists():
            for bin_file in firmware_dir.glob("*.bin"):
                if bin_file.name.startswith("esp32-bus-pirate-"):
                    env_name = bin_file.name.replace("esp32-bus-pirate-", "").replace(".bin", "").replace("-partitions", "")
                    file_type = "Partitions" if "partitions" in bin_file.name else "Firmware"
                    info_content += f"- {bin_file.name} ({file_type} for {env_name})\n"

        info_content += """

## Flashing Instructions

Use PlatformIO, Arduino IDE, or esptool.py to flash the firmware:

```bash
# Using esptool.py
esptool.py --chip esp32s3 --port /dev/ttyUSB0 --baud 921600 \\
  --before default_reset --after hard_reset write_flash \\
  0x0 firmware/esp32-bus-pirate-s3-devkit.bin \\
  0x8000 firmware/esp32-bus-pirate-s3-devkit-partitions.bin

# Using PlatformIO
pio run -e s3-devkit --target upload
```

## Source Code

The source code for this firmware is included in this package for reference and modification.
"""

        with open(info_file, 'w') as f:
            f.write(info_content)

    def package_info(self):
        """Package information for consumers"""
        # Set package info for consumers
        self.cpp_info.libs = []
        self.cpp_info.libdirs = []
        self.cpp_info.bindirs = ["firmware"]
        self.cpp_info.includedirs = ["src", "lib"]

        # Set environment variables for consumers
        firmware_dir = os.path.join(self.package_folder, "firmware")
        self.env_info.ESP32_BUS_PIRATE_FIRMWARE_DIR = firmware_dir

        # User info for package consumers
        self.user_info.firmware_version = self.version
        self.user_info.board = str(self.options.board)
        self.user_info.source_available = True

        self.output.info(f"Firmware directory available at: {firmware_dir}")

    def package_id(self):
        """Package ID generation"""
        # Include board option in package ID for different variants
        self.info.options.board = self.options.board


