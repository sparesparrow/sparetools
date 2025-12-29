#!/usr/bin/env python3
"""
SpareTools Embedded Systems Integration Demo

Demonstrates how to use SpareTools for testing embedded systems,
particularly ESP32-based projects.
"""

import sys
import json
from pathlib import Path

# Add sparetools to path
sys.path.insert(0, str(Path(__file__).parent))

from sparetools.test_environments.providers.embedded import ESP32Environment, ESP32Config, FirmwareInfo
from sparetools.core.components.providers.embedded import SerialComponent, SerialConfig, GPIOComponent
from sparetools.test_environments.providers.embedded.factory import create_embedded_environment


def demo_basic_esp32_environment():
    """Demonstrate basic ESP32 environment setup and testing"""
    print("🔧 ESP32 Environment Demo")
    print("-" * 40)

    # Create ESP32 environment
    config = ESP32Config(
        port="/dev/ttyUSB0",
        baudrate=115200,
        chip="esp32"
    )

    env = ESP32Environment(config=config)
    print(f"✓ Created ESP32 environment for {config.chip}")

    # Test health check (will fail without actual hardware)
    print("Performing health check...")
    healthy = env.health_check()
    print(f"Health check result: {'PASS' if healthy else 'FAIL (expected without hardware)'}")

    # Save and restore state
    state = env.save_state()
    print(f"✓ Environment state saved ({len(state)} keys)")

    restored_env = ESP32Environment()
    restored = restored_env.restore_state(state)
    print(f"✓ Environment state restored: {'PASS' if restored else 'FAIL'}")

    return env


def demo_serial_component():
    """Demonstrate serial communication component"""
    print("\n🔌 Serial Component Demo")
    print("-" * 40)

    # Create serial component
    config = SerialConfig(
        port="/dev/ttyUSB0",
        baudrate=115200
    )

    serial = SerialComponent(config)
    print("✓ Created serial component")

    # Test connection (will fail without hardware)
    connected = serial.connect()
    print(f"Serial connection: {'PASS' if connected else 'FAIL (expected without hardware)'}")

    # Get connection info
    info = serial.get_connection_info()
    print(f"Connection info: {info['port']} at {info['baudrate']} baud")

    return serial


def demo_gpio_component():
    """Demonstrate GPIO testing component"""
    print("\n📍 GPIO Component Demo")
    print("-" * 40)

    # Create GPIO component with serial backend
    serial = SerialComponent(SerialConfig(port="/dev/ttyUSB0"))
    gpio = GPIOComponent(serial_component=serial)
    print("✓ Created GPIO component")

    # Simulate GPIO tests (would work with actual ESP32 firmware)
    print("Simulating GPIO tests...")
    test_results = []

    # Digital output test
    result = gpio.test_digital_output(pin=2, test_value=1, verify=False)
    test_results.append(result)
    print(f"GPIO digital output test: {'PASS' if result.passed else 'FAIL'}")

    # Digital input test
    result = gpio.test_digital_input(pin=4, configure=False)
    test_results.append(result)
    print(f"GPIO digital input test: {'PASS' if result.passed else 'FAIL'}")

    # Analog input test
    result = gpio.test_analog_input(pin=34, expected_range=(0, 4095))
    test_results.append(result)
    print(f"GPIO analog input test: {'PASS' if result.passed else 'FAIL'}")

    # Get test summary
    summary = gpio.get_test_summary()
    print(f"Test summary: {summary['passed_tests']}/{summary['total_tests']} passed")

    return gpio


def demo_factory_usage():
    """Demonstrate factory-based environment creation"""
    print("\n🏭 Factory Demo")
    print("-" * 40)

    # Create environment using factory
    env = create_embedded_environment(
        platform="esp32",
        port="/dev/ttyUSB0",
        baudrate=115200,
        firmware_path="/path/to/firmware.bin"
    )

    if env:
        print("✓ Created ESP32 environment via factory")
        print(f"Environment type: {type(env).__name__}")
        print(f"Serial port: {env.config.port}")
    else:
        print("❌ Failed to create environment")

    return env


def demo_project_integration():
    """Demonstrate integration with ESP32 projects"""
    print("\n🔗 Project Integration Demo")
    print("-" * 40)

    projects = [
        "/home/sparrow/projects/embedded-systems/esp32-bpm-detector",
        "/home/sparrow/projects/embedded-systems/nucleus-esp32",
        "/home/sparrow/projects/NucleusESP32"
    ]

    for project_path in projects:
        project_name = Path(project_path).name
        exists = Path(project_path).exists()

        print(f"📁 {project_name}: {'EXISTS' if exists else 'NOT FOUND'}")

        if exists:
            # Check for common embedded project files
            indicators = {
                "CMakeLists.txt": "CMake project",
                "platformio.ini": "PlatformIO project",
                "Makefile": "Make-based project",
                "run_tests.py": "Python test runner",
                "conanfile.py": "Conan package",
                "test_harness/": "Test harness directory"
            }

            found_indicators = []
            for indicator, description in indicators.items():
                if Path(project_path, indicator).exists():
                    found_indicators.append(description)

            if found_indicators:
                print(f"   Detected: {', '.join(found_indicators)}")

            # Look for firmware files
            firmware_files = list(Path(project_path).glob("*.bin"))
            if firmware_files:
                print(f"   Firmware files: {len(firmware_files)} found")
                for fw in firmware_files[:3]:  # Show first 3
                    size = fw.stat().st_size
                    print(f"     - {fw.name}: {size} bytes")

    print("\n💡 To integrate SpareTools with these projects:")
    print("   1. Install sparetools-embedded package")
    print("   2. Use ESP32Environment for hardware testing")
    print("   3. Integrate with existing test runners")
    print("   4. Add firmware flashing to CI/CD pipelines")


def main():
    """Main demonstration"""
    print("🚀 SpareTools Embedded Systems Integration Demo")
    print("=" * 50)
    print("This demo shows how SpareTools can be used to test ESP32 projects")
    print("Note: Hardware tests will fail without actual ESP32 devices\n")

    # Run demonstrations
    demo_basic_esp32_environment()
    demo_serial_component()
    demo_gpio_component()
    demo_factory_usage()
    demo_project_integration()

    print("\n" + "=" * 50)
    print("✅ Demo completed!")
    print("\n📚 Key Features Demonstrated:")
    print("   • ESP32 test environment with firmware flashing")
    print("   • Serial communication components")
    print("   • GPIO testing and control")
    print("   • Factory-based environment creation")
    print("   • Integration with existing ESP32 projects")

    print("\n🔧 Next Steps:")
    print("   1. Connect an ESP32 device to run hardware tests")
    print("   2. Adapt the firmware to respond to test commands")
    print("   3. Integrate with your CI/CD pipeline")
    print("   4. Extend for additional embedded platforms")


if __name__ == "__main__":
    main()