#!/usr/bin/env python3
"""
Test Audio Data Serialization and BPM Metadata Exchange
Validates audio data handling concepts between ESP32 and client applications
"""

import json
import base64
import numpy as np
from typing import Dict, List, Optional

def generate_test_audio_data(samples: int = 1024, frequency: float = 440.0, sample_rate: float = 25000.0) -> List[float]:
    """Generate test audio data (sine wave)"""
    t = np.linspace(0, samples/sample_rate, samples, endpoint=False)
    audio_data = np.sin(2 * np.pi * frequency * t).tolist()
    return audio_data

def test_bpm_metadata_serialization():
    """Test BPM detection result serialization"""
    bpm_data = {
        "bpm": 128.5,
        "confidence": 0.87,
        "signal_level": 0.72,
        "status": "detecting",
        "timestamp": 1640995200000,  # Unix timestamp in ms
        "metadata": {
            "sample_rate": 25000,
            "fft_size": 1024,
            "min_bpm": 60,
            "max_bpm": 200,
            "detection_method": "fft_envelope"
        }
    }
    
    try:
        # Serialize to JSON
        json_str = json.dumps(bpm_data, indent=2)
        
        # Deserialize from JSON
        parsed_data = json.loads(json_str)
        
        # Validate structure
        required_fields = ["bpm", "confidence", "signal_level", "status", "timestamp"]
        metadata_fields = ["sample_rate", "fft_size", "min_bpm", "max_bpm"]
        
        if not all(field in parsed_data for field in required_fields):
            return False, "Missing required BPM fields"
        
        if "metadata" not in parsed_data:
            return False, "Missing metadata section"
            
        if not all(field in parsed_data["metadata"] for field in metadata_fields):
            return False, "Missing metadata fields"
        
        # Validate data types
        if not isinstance(parsed_data["bpm"], (int, float)):
            return False, "BPM not numeric"
        
        if not (0.0 <= parsed_data["confidence"] <= 1.0):
            return False, "Confidence out of range"
        
        print("✅ BPM metadata serialization: Valid structure and types")
        return True, "BPM metadata serialization successful"
        
    except Exception as e:
        return False, f"BPM metadata serialization failed: {e}"

def test_audio_sample_serialization():
    """Test raw audio sample data serialization"""
    # Generate test audio data
    audio_samples = generate_test_audio_data(1024, 440.0, 25000.0)
    
    audio_packet = {
        "type": "audio_samples",
        "format": "float32",
        "sample_rate": 25000,
        "channels": 1,
        "samples": audio_samples,
        "timestamp": 1640995200000,
        "sequence_number": 1
    }
    
    try:
        # Test JSON serialization (inefficient but works)
        json_str = json.dumps(audio_packet)
        json_size = len(json_str)
        
        # Test base64 encoding for binary efficiency
        audio_bytes = np.array(audio_samples, dtype=np.float32).tobytes()
        b64_encoded = base64.b64encode(audio_bytes).decode('ascii')
        
        binary_packet = {
            "type": "audio_samples",
            "format": "float32_base64",
            "sample_rate": 25000,
            "channels": 1,
            "data": b64_encoded,
            "timestamp": 1640995200000,
            "sequence_number": 1
        }
        
        binary_json = json.dumps(binary_packet)
        binary_size = len(binary_json)
        
        # Validate base64 round-trip
        decoded_bytes = base64.b64decode(b64_encoded)
        decoded_samples = np.frombuffer(decoded_bytes, dtype=np.float32).tolist()
        
        if np.allclose(decoded_samples, audio_samples, rtol=1e-6):
            compression_ratio = json_size / binary_size
            print(f"✅ Audio sample serialization: Base64 encoding {compression_ratio:.1f}x more efficient")
            return True, f"Audio serialization successful, {compression_ratio:.1f}x compression"
        else:
            return False, "Base64 round-trip failed"
        
    except Exception as e:
        return False, f"Audio sample serialization failed: {e}"

def test_configuration_exchange():
    """Test module configuration data exchange"""
    config_data = {
        "esp32_core": {
            "wifi_ssid": "MyNetwork",
            "wifi_password": "secret123",
            "microphone_pin": 32,
            "min_bpm": 60,
            "max_bpm": 200,
            "sample_rate": 25000,
            "fft_size": 1024
        },
        "qt_client": {
            "server_ip": "192.168.1.100",
            "server_port": 80,
            "update_interval_ms": 100,
            "visualization_mode": "spectrum",
            "theme": "dark"
        },
        "network_server": {
            "multicast_group": "239.0.0.1",
            "multicast_port": 5004,
            "rtp_enabled": True,
            "max_clients": 10
        }
    }
    
    try:
        # Serialize configuration
        config_json = json.dumps(config_data, indent=2)
        
        # Parse configuration
        parsed_config = json.loads(config_json)
        
        # Validate all modules present
        required_modules = ["esp32_core", "qt_client", "network_server"]
        if not all(module in parsed_config for module in required_modules):
            return False, "Missing required configuration modules"
        
        # Validate ESP32 core config
        esp32_config = parsed_config["esp32_core"]
        required_esp32_fields = ["wifi_ssid", "min_bpm", "max_bpm", "sample_rate"]
        if not all(field in esp32_config for field in required_esp32_fields):
            return False, "Missing ESP32 configuration fields"
        
        print("✅ Configuration exchange: Valid module configurations")
        return True, "Configuration exchange successful"
        
    except Exception as e:
        return False, f"Configuration exchange failed: {e}"

def main():
    """Run all audio data serialization tests"""
    print("Testing Audio Data Serialization Concepts...")
    print("=" * 50)
    
    tests = [
        ("BPM Metadata Serialization", test_bpm_metadata_serialization),
        ("Audio Sample Serialization", test_audio_sample_serialization),
        ("Configuration Exchange", test_configuration_exchange)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\nRunning: {test_name}")
        success, message = test_func()
        results.append((test_name, success, message))
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {message}")
    
    print("\n" + "=" * 50)
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ Audio data serialization concepts: All tests passed")
        return True
    else:
        print("❌ Audio data serialization concepts: Some tests failed")
        return False

if __name__ == '__main__':
    main()
