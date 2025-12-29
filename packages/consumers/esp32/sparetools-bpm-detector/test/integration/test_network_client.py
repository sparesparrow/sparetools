#!/usr/bin/env python3
"""
Test HTTP client for ESP32 BPM API
Validates network communication concepts
"""

import requests
import json
import time

def test_bpm_endpoint():
    """Test /api/bpm endpoint with error handling"""
    try:
        response = requests.get('http://127.0.0.1:8080/api/bpm', timeout=5)

        # Check for valid HTTP status codes
        if response.status_code in [200, 503]:
            data = response.json()
            required_fields = ['bpm', 'confidence', 'signal_level', 'status', 'timestamp']

            if all(field in data for field in required_fields):
                if response.status_code == 200:
                    print("✅ BPM endpoint: Valid response format (200 OK)")
                elif response.status_code == 503:
                    if 'error' in data:
                        print("✅ BPM endpoint: Proper error response (503 Service Unavailable)")
                    else:
                        print("❌ BPM endpoint: 503 response missing error field")
                        return False
                return True
            else:
                print("❌ BPM endpoint: Missing required fields")
                return False
        else:
            print(f"❌ BPM endpoint: Unexpected HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ BPM endpoint: Connection failed - {e}")
        return False

def test_settings_endpoint():
    """Test /api/settings endpoint with error handling"""
    try:
        response = requests.get('http://127.0.0.1:8080/api/settings', timeout=5)

        # Check for valid HTTP status codes
        if response.status_code in [200, 503]:
            data = response.json()
            required_fields = ['min_bpm', 'max_bpm', 'sample_rate', 'fft_size', 'version']

            if all(field in data for field in required_fields):
                if response.status_code == 200:
                    print("✅ Settings endpoint: Valid response format (200 OK)")
                elif response.status_code == 503:
                    if 'error' in data:
                        print("✅ Settings endpoint: Proper error response (503 Service Unavailable)")
                    else:
                        print("❌ Settings endpoint: 503 response missing error field")
                        return False
                return True
            else:
                print("❌ Settings endpoint: Missing required fields")
                return False
        else:
            print(f"❌ Settings endpoint: Unexpected HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Settings endpoint: Connection failed - {e}")
        return False

def test_health_endpoint():
    """Test /api/health endpoint with comprehensive health checks"""
    try:
        response = requests.get('http://127.0.0.1:8080/api/health', timeout=5)

        # Check for valid HTTP status codes
        if response.status_code in [200, 503]:
            data = response.json()

            # Check required top-level fields
            required_fields = ['status', 'uptime_seconds', 'timestamp']
            if not all(field in data for field in required_fields):
                print("❌ Health endpoint: Missing required fields")
                return False

            # Check component health sections
            component_sections = ['wifi', 'bpm_detector', 'display', 'memory']
            for section in component_sections:
                if section not in data:
                    print(f"❌ Health endpoint: Missing {section} health section")
                    return False
                if 'status' not in data[section]:
                    print(f"❌ Health endpoint: Missing status in {section} section")
                    return False

            if response.status_code == 200:
                print("✅ Health endpoint: System healthy (200 OK)")
            elif response.status_code == 503:
                print("✅ Health endpoint: System unhealthy (503 Service Unavailable)")
            return True
        else:
            print(f"❌ Health endpoint: Unexpected HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health endpoint: Connection failed - {e}")
        return False

def test_error_endpoints():
    """Test error handling for invalid endpoints and methods"""
    try:
        # Test 404 for invalid endpoint
        response = requests.get('http://127.0.0.1:8080/api/invalid', timeout=5)
        if response.status_code == 404:
            data = response.json()
            if 'error' in data and data['error'] == 'endpoint not found':
                print("✅ Error handling: Proper 404 for invalid endpoint")
            else:
                print("❌ Error handling: Invalid 404 response format")
                return False
        else:
            print(f"❌ Error handling: Expected 404, got {response.status_code}")
            return False

        # Test 405 for invalid method
        response = requests.post('http://127.0.0.1:8080/api/bpm', timeout=5)
        if response.status_code == 405:
            data = response.json()
            if 'error' in data and data['error'] == 'method not allowed':
                print("✅ Error handling: Proper 405 for invalid method")
                return True
            else:
                print("❌ Error handling: Invalid 405 response format")
                return False
        else:
            print(f"❌ Error handling: Expected 405, got {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error handling: Connection failed - {e}")
        return False

def test_json_serialization():
    """Test JSON serialization/deserialization"""
    test_data = {
        "bpm": 128.5,
        "confidence": 0.87,
        "signal_level": 0.72,
        "status": "detecting",
        "timestamp": int(time.time() * 1000)
    }
    
    try:
        # Serialize
        json_str = json.dumps(test_data)
        # Deserialize
        parsed_data = json.loads(json_str)
        # Validate
        if parsed_data == test_data:
            print("✅ JSON serialization: Round-trip successful")
            return True
        else:
            print("❌ JSON serialization: Data mismatch")
            return False
    except Exception as e:
        print(f"❌ JSON serialization: Failed - {e}")
        return False

if __name__ == '__main__':
    print("Testing ESP32 BPM Detector API Integration...")
    print("=" * 60)

    # Test JSON handling
    json_ok = test_json_serialization()

    # Test API endpoints (requires mock server to be running)
    print("\nTesting API Endpoints:")
    print("-" * 30)

    bpm_ok = test_bpm_endpoint()
    settings_ok = test_settings_endpoint()
    health_ok = test_health_endpoint()
    error_ok = test_error_endpoints()

    # Note: Server tests would require running server separately
    print("\nNote: API endpoint tests require mock server to be running")
    print("Run: python3 tests/integration/mock_esp32_server.py")
    print("Then run this test in another terminal")

    all_api_tests = bpm_ok and settings_ok and health_ok and error_ok

    if json_ok and all_api_tests:
        print("\n✅ All tests passed: Network communication and API integration validated")
    else:
        print("\n❌ Some tests failed: Check the error messages above")
        if not json_ok:
            print("  - JSON serialization issues")
        if not all_api_tests:
            print("  - API endpoint issues")
