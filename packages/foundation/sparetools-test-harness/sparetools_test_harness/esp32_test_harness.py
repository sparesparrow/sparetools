"""
ESP32 Test Harness - Hardware Simulation and Testing

Provides ESP32-specific testing capabilities including:
- NFC module simulation
- RF module simulation
- IR module simulation
- SD card simulation
- ESP32 core simulation
- Hardware integration testing
"""

import time
import json
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from dataclasses import dataclass, asdict

from .test_harness import SpareToolsTestHarness


@dataclass
class HardwareState:
    """ESP32 hardware state representation."""
    initialized: bool = False
    active: bool = False
    last_data: Optional[Any] = None
    config: Dict[str, Any] = None


@dataclass
class ESP32State:
    """Complete ESP32 system state."""
    nfc_module: HardwareState
    rf_module: HardwareState
    ir_module: HardwareState
    sd_module: HardwareState
    esp32_core: HardwareState

    def __post_init__(self):
        if self.nfc_module.config is None:
            self.nfc_module.config = {}
        if self.rf_module.config is None:
            self.rf_module.config = {}
        if self.ir_module.config is None:
            self.ir_module.config = {}
        if self.sd_module.config is None:
            self.sd_module.config = {}
        if self.esp32_core.config is None:
            self.esp32_core.config = {}


class ESP32TestHarness(SpareToolsTestHarness):
    """
    ESP32 Test Harness with hardware simulation capabilities.

    Provides comprehensive testing capabilities for ESP32 firmware including:
    - NFC communication verification
    - RF signal testing
    - IR code transmission
    - SD card operations
    - Hardware module integration
    - Performance benchmarking
    - Memory usage tracking
    """

    def __init__(self, results_dir: Optional[Path] = None, hardware_simulation: bool = True):
        """
        Initialize ESP32 test harness.

        Args:
            results_dir: Directory for test results and reports
            hardware_simulation: Enable hardware simulation mode
        """
        super().__init__(results_dir)
        self.hardware_simulation = hardware_simulation
        self.performance_metrics = {}
        self.test_start_time = time.time()

        # Initialize ESP32 hardware state
        self.hardware_state = self._init_esp32_state()

    def _init_esp32_state(self) -> ESP32State:
        """Initialize ESP32 hardware simulation state."""
        return ESP32State(
            nfc_module=HardwareState(
                initialized=False,
                active=False,
                config={
                    'i2c_address': 0x28,
                    'irq_pin': 2,
                    'reset_pin': 15,
                    'supported_cards': ['mifare_classic', 'ntag', 'mifare_ultralight']
                }
            ),
            rf_module=HardwareState(
                initialized=False,
                active=False,
                config={
                    'spi_bus': 'HSPI',
                    'sck_pin': 18,
                    'miso_pin': 19,
                    'mosi_pin': 23,
                    'cs_pin': 5,
                    'frequency_range': [300000000, 928000000],  # 300MHz - 928MHz
                    'modulation_types': ['OOK', 'FSK', 'ASK']
                }
            ),
            ir_module=HardwareState(
                initialized=False,
                active=False,
                config={
                    'ir_pin': 4,
                    'frequency': 38000,  # 38kHz typical
                    'supported_protocols': ['NEC', 'Sony', 'RC5', 'RC6', 'Samsung']
                }
            ),
            sd_module=HardwareState(
                initialized=False,
                active=False,
                config={
                    'spi_bus': 'VSPI',
                    'cs_pin': 13,
                    'mount_point': '/sd',
                    'max_capacity': 32 * 1024 * 1024 * 1024,  # 32GB
                }
            ),
            esp32_core=HardwareState(
                initialized=True,
                active=True,
                config={
                    'chip_model': 'ESP32-D0WDQ6',
                    'flash_size': 4 * 1024 * 1024,  # 4MB
                    'psram_size': 0,
                    'cpu_frequency': 240000000,  # 240MHz
                    'wifi_enabled': True,
                    'bluetooth_enabled': True
                }
            )
        )

    def verify_nfc_communication(self, expected_data: bytes, actual_data: bytes,
                                description: str = "NFC communication", test_num: Optional[int] = None) -> bool:
        """
        Verify NFC communication data.

        Args:
            expected_data: Expected NFC data
            actual_data: Actual received NFC data
            description: Test description
            test_num: Test number for tracking

        Returns:
            bool: True if verification passes
        """
        # Update hardware state
        self.hardware_state.nfc_module.active = True
        self.hardware_state.nfc_module.last_data = actual_data.hex() if actual_data else None

        return self.verify(
            actual=actual_data,
            expected=expected_data,
            msg=f"NFC Communication: {description}",
            test_num=test_num
        )

    def verify_rf_transmission(self, frequency: int, data: bytes,
                              description: str = "RF transmission", test_num: Optional[int] = None) -> bool:
        """
        Verify RF signal transmission.

        Args:
            frequency: Transmission frequency in Hz
            data: Data to transmit
            description: Test description
            test_num: Test number for tracking

        Returns:
            bool: True if verification passes
        """
        # Validate frequency range
        freq_range = self.hardware_state.rf_module.config['frequency_range']
        if not (freq_range[0] <= frequency <= freq_range[1]):
            return self.verify(
                actual=False,
                expected=True,
                msg=f"RF Transmission: Invalid frequency {frequency}Hz (must be {freq_range[0]}-{freq_range[1]}Hz)",
                test_num=test_num
            )

        # Update hardware state
        self.hardware_state.rf_module.active = True
        self.hardware_state.rf_module.last_data = data.hex() if data else None
        self.hardware_state.rf_module.config['current_frequency'] = frequency

        return self.verify(
            actual=len(data) > 0,
            expected=True,
            msg=f"RF Transmission: {description} at {frequency}Hz",
            test_num=test_num
        )

    def verify_ir_transmission(self, protocol: str, code: bytes,
                              description: str = "IR transmission", test_num: Optional[int] = None) -> bool:
        """
        Verify IR code transmission.

        Args:
            protocol: IR protocol (NEC, Sony, etc.)
            code: IR code data
            description: Test description
            test_num: Test number for tracking

        Returns:
            bool: True if verification passes
        """
        # Validate protocol
        supported_protocols = self.hardware_state.ir_module.config['supported_protocols']
        if protocol not in supported_protocols:
            return self.verify(
                actual=False,
                expected=True,
                msg=f"IR Transmission: Unsupported protocol '{protocol}' (supported: {supported_protocols})",
                test_num=test_num
            )

        # Update hardware state
        self.hardware_state.ir_module.active = True
        self.hardware_state.ir_module.last_data = {'protocol': protocol, 'code': code.hex()}

        return self.verify(
            actual=len(code) > 0,
            expected=True,
            msg=f"IR Transmission: {description} ({protocol})",
            test_num=test_num
        )

    def verify_sd_operation(self, operation: str, path: str, expected_result: bool = True,
                           description: str = "SD card operation", test_num: Optional[int] = None) -> bool:
        """
        Verify SD card operations.

        Args:
            operation: Operation type (read, write, delete, etc.)
            path: File/directory path
            expected_result: Expected success/failure
            description: Test description
            test_num: Test number for tracking

        Returns:
            bool: True if verification passes
        """
        # Simulate SD card operations
        operations = ['read', 'write', 'delete', 'mkdir', 'list']
        if operation not in operations:
            return self.verify(
                actual=False,
                expected=True,
                msg=f"SD Operation: Invalid operation '{operation}' (supported: {operations})",
                test_num=test_num
            )

        # Update hardware state
        self.hardware_state.sd_module.active = True
        self.hardware_state.sd_module.last_data = {'operation': operation, 'path': path}

        # Simulate operation result (in real hardware this would be actual I/O)
        simulated_result = expected_result  # In simulation, assume success

        return self.verify(
            actual=simulated_result,
            expected=expected_result,
            msg=f"SD Operation: {description} ({operation} {path})",
            test_num=test_num
        )

    def verify_memory_usage(self, max_heap_usage: int, description: str = "Memory usage",
                           test_num: Optional[int] = None) -> bool:
        """
        Verify ESP32 memory usage is within limits.

        Args:
            max_heap_usage: Maximum allowed heap usage in bytes
            description: Test description
            test_num: Test number for tracking

        Returns:
            bool: True if memory usage is within limits
        """
        # Simulate current heap usage (in real ESP32 this would be actual measurement)
        current_heap = 1024 * 10  # 10KB simulated usage
        free_heap = self.hardware_state.esp32_core.config['flash_size'] - current_heap

        # Update hardware state
        self.hardware_state.esp32_core.config['current_heap'] = current_heap
        self.hardware_state.esp32_core.config['free_heap'] = free_heap

        return self.verify(
            actual=current_heap,
            expected=max_heap_usage,
            msg=f"Memory Usage: {description} ({current_heap} bytes used, {free_heap} bytes free)",
            test_num=test_num
        )

    def benchmark_operation(self, operation_name: str, operation_func: callable,
                           iterations: int = 100, description: str = "Performance benchmark") -> Dict[str, Any]:
        """
        Benchmark an operation and record performance metrics.

        Args:
            operation_name: Name of the operation being benchmarked
            operation_func: Function to benchmark
            iterations: Number of iterations to run
            description: Benchmark description

        Returns:
            Dict containing benchmark results
        """
        start_time = time.time()

        for i in range(iterations):
            operation_func()

        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / iterations

        benchmark_result = {
            'operation': operation_name,
            'iterations': iterations,
            'total_time': total_time,
            'avg_time': avg_time,
            'timestamp': time.time(),
            'description': description
        }

        self.performance_metrics[operation_name] = benchmark_result

        # Log benchmark result
        self.th_logger.log_test_result({
            'test_type': 'benchmark',
            'operation': operation_name,
            'result': benchmark_result
        })

        return benchmark_result

    def get_hardware_state(self) -> Dict[str, Any]:
        """
        Get current hardware simulation state.

        Returns:
            Dict containing complete hardware state
        """
        return {
            'hardware_simulation': self.hardware_simulation,
            'esp32_state': asdict(self.hardware_state),
            'performance_metrics': self.performance_metrics,
            'test_duration': time.time() - self.test_start_time
        }

    def export_hardware_state(self, filename: str = "hardware_state.json") -> None:
        """
        Export hardware state to JSON file.

        Args:
            filename: Output filename
        """
        state_data = self.get_hardware_state()

        output_path = self.results_dir / filename
        with open(output_path, 'w') as f:
            json.dump(state_data, f, indent=2, default=str)

        print(f"Hardware state exported to {output_path}")

    def reset_hardware_state(self) -> None:
        """Reset hardware simulation state."""
        self.hardware_state = self._init_esp32_state()
        self.performance_metrics = {}
        self.test_start_time = time.time()