"""
Mock Hardware for WiFi Sensing Testing
Provides hardware simulation without physical devices
"""

import numpy as np
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import random


@dataclass
class MockCSIFrame:
    """Mock CSI frame data"""
    amplitudes: np.ndarray
    phases: np.ndarray
    timestamp: float
    frame_count: int
    rssi: float = -50.0
    noise_floor: float = -90.0


class MockWiFiInterface:
    """Mock WiFi interface for testing"""

    def __init__(self, interface_name: str = "wlan0"):
        self.interface_name = interface_name
        self.is_up = True
        self.frequency = 2412  # Channel 1
        self.channel = 1
        self.tx_power = 20
        self.supported_channels = list(range(1, 14))

    def scan_networks(self) -> List[Dict[str, Any]]:
        """Mock network scan"""
        networks = []
        for i in range(random.randint(3, 10)):
            networks.append({
                'ssid': f'TestNetwork_{i}',
                'bssid': f'00:11:22:33:44:{i:02X}',
                'frequency': 2412 + (i * 5),
                'channel': 1 + i,
                'signal': random.randint(-90, -30),
                'encryption': random.choice(['WPA2', 'WPA3', 'OPEN'])
            })
        return networks

    def set_channel(self, channel: int) -> bool:
        """Mock channel setting"""
        if channel in self.supported_channels:
            self.channel = channel
            self.frequency = 2412 + (channel - 1) * 5
            return True
        return False

    def get_signal_strength(self) -> float:
        """Mock signal strength reading"""
        return random.uniform(-80, -40)


class MockCSIProcessor:
    """Mock CSI processor for testing"""

    def __init__(self, num_subcarriers: int = 30, num_antennas: int = 3):
        self.num_subcarriers = num_subcarriers
        self.num_antennas = num_antennas
        self.frame_count = 0

    def generate_csi_frame(self, add_noise: bool = True, add_motion: bool = False) -> MockCSIFrame:
        """Generate mock CSI frame"""
        self.frame_count += 1

        # Base CSI amplitudes (simulating channel response)
        amplitudes = np.random.rayleigh(1.0, (self.num_subcarriers, self.num_antennas))

        # Add frequency-dependent fading
        freq_response = np.exp(-0.1 * np.arange(self.num_subcarriers))
        amplitudes *= freq_response[:, np.newaxis]

        # Generate phases
        phases = np.random.uniform(-np.pi, np.pi, (self.num_subcarriers, self.num_antennas))

        # Add motion artifacts if requested
        if add_motion:
            motion_phase = 0.5 * np.sin(2 * np.pi * 0.1 * self.frame_count)
            phases += motion_phase

        # Add noise
        if add_noise:
            amplitudes += 0.1 * np.random.randn(*amplitudes.shape)
            phases += 0.1 * np.random.randn(*phases.shape)

        return MockCSIFrame(
            amplitudes=amplitudes,
            phases=phases,
            timestamp=time.time(),
            frame_count=self.frame_count,
            rssi=random.uniform(-70, -40)
        )

    def process_csi_batch(self, csi_data: np.ndarray) -> Dict[str, Any]:
        """Mock batch processing"""
        return {
            'processed_frames': len(csi_data),
            'average_amplitude': float(np.mean(np.abs(csi_data))),
            'phase_stability': float(np.std(np.angle(csi_data))),
            'motion_detected': random.random() > 0.7
        }


class MockFlipperZero:
    """Mock Flipper Zero device for testing"""

    def __init__(self):
        self.connected = True
        self.firmware_version = "1.0.0-mock"
        self.hardware_version = "DVT1"
        self.serial_number = "MZ001122334455"

    def get_device_info(self) -> Dict[str, str]:
        """Mock device info"""
        return {
            'firmware': self.firmware_version,
            'hardware': self.hardware_version,
            'serial': self.serial_number
        }

    def send_command(self, command: str) -> str:
        """Mock command execution"""
        if command == "device_info":
            return f"Hardware: {self.hardware_version}\\nFirmware: {self.firmware_version}"
        elif command.startswith("subghz"):
            return "SubGHz command executed"
        elif command.startswith("nfc"):
            return "NFC command executed"
        else:
            return f"Command '{command}' executed"

    def disconnect(self):
        """Mock disconnect"""
        self.connected = False


class MockGPSDevice:
    """Mock GPS device for testing"""

    def __init__(self):
        self.latitude = 37.7749  # San Francisco
        self.longitude = -122.4194
        self.altitude = 10.0
        self.speed = 0.0
        self.heading = 0.0
        self.satellites = 8

    def get_location(self) -> Dict[str, float]:
        """Get mock GPS location"""
        # Add small random movement
        self.latitude += random.uniform(-0.0001, 0.0001)
        self.longitude += random.uniform(-0.0001, 0.0001)

        return {
            'latitude': self.latitude,
            'longitude': self.longitude,
            'altitude': self.altitude,
            'speed': self.speed,
            'heading': self.heading,
            'satellites': self.satellites
        }

    def get_nmea_sentence(self) -> str:
        """Generate mock NMEA sentence"""
        lat_deg = int(self.latitude)
        lat_min = (self.latitude - lat_deg) * 60
        lon_deg = int(abs(self.longitude))
        lon_min = (abs(self.longitude) - lon_deg) * 60

        return ".2f"".2f"".2f"".2f"f"{self.altitude:05.1f}"


class MockHardwareManager:
    """Central mock hardware manager"""

    def __init__(self):
        self.wifi_interface = MockWiFiInterface()
        self.csi_processor = MockCSIProcessor()
        self.flipper_zero = MockFlipperZero()
        self.gps_device = MockGPSDevice()

    def initialize_all(self) -> bool:
        """Initialize all mock hardware"""
        print("Mock hardware initialized successfully")
        return True

    def shutdown_all(self):
        """Shutdown all mock hardware"""
        self.flipper_zero.disconnect()
        print("Mock hardware shutdown")

    def get_system_status(self) -> Dict[str, Any]:
        """Get status of all mock hardware"""
        return {
            'wifi_interface': {
                'available': True,
                'channel': self.wifi_interface.channel,
                'signal_strength': self.wifi_interface.get_signal_strength()
            },
            'csi_processor': {
                'available': True,
                'subcarriers': self.csi_processor.num_subcarriers,
                'antennas': self.csi_processor.num_antennas
            },
            'flipper_zero': {
                'connected': self.flipper_zero.connected,
                'firmware': self.flipper_zero.firmware_version
            },
            'gps': {
                'available': True,
                'fix': True,
                'satellites': self.gps_device.satellites
            }
        }


# Global mock hardware instance
mock_hardware = MockHardwareManager()

# Convenience functions for tests
def get_mock_csi_processor():
    """Get mock CSI processor instance"""
    return mock_hardware.csi_processor

def get_mock_wifi_interface():
    """Get mock WiFi interface instance"""
    return mock_hardware.wifi_interface

def get_mock_flipper_zero():
    """Get mock Flipper Zero instance"""
    return mock_hardware.flipper_zero

def get_mock_gps():
    """Get mock GPS device instance"""
    return mock_hardware.gps_device

def initialize_mock_hardware():
    """Initialize all mock hardware for testing"""
    return mock_hardware.initialize_all()

def get_mock_system_status():
    """Get mock system status"""
    return mock_hardware.get_system_status()