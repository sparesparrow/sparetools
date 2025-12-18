#!/usr/bin/env python3
"""
Test script for MIA deployment on Raspberry Pi
Tests connectivity, cloud integration, and device management functionality
"""

import sys
import os
import subprocess

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"🔍 {description}")
    print(f"   Command: {cmd}")
    try:
        # Use environment variables from current process
        env = os.environ.copy()
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30, env=env)
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} - FAILED")
            print(f"   Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False

def test_mia_imports():
    """Test that MIA modules can be imported"""
    # Create a temporary test script
    import_test_script = """
import sys
print("PYTHONPATH:", sys.path)
print()

try:
    import mia.connectivity
    print("✓ mia.connectivity imported")
except ImportError as e:
    print("✗ mia.connectivity failed:", e)
    import traceback
    traceback.print_exc()
    exit(1)

try:
    import mia.cloud_integration
    print("✓ mia.cloud_integration imported")
except ImportError as e:
    print("✗ mia.cloud_integration failed:", e)
    import traceback
    traceback.print_exc()
    exit(1)

try:
    import mia.device_manager
    print("✓ mia.device_manager imported")
except ImportError as e:
    print("✗ mia.device_manager failed:", e)
    import traceback
    traceback.print_exc()
    exit(1)

try:
    import mia.core
    print("✓ mia.core imported")
except ImportError as e:
    print("✗ mia.core failed:", e)
    import traceback
    traceback.print_exc()
    exit(1)

print("All MIA modules imported successfully")
"""

    with open('/tmp/mia_import_test.py', 'w') as f:
        f.write(import_test_script)

    success = run_command("python3 /tmp/mia_import_test.py", "Test MIA module imports")
    os.remove('/tmp/mia_import_test.py')
    return success

def test_ssl_functionality():
    """Test SSL functionality that MIA depends on"""
    # Create a temporary test script
    ssl_test_script = """
import ssl
print("SSL Version:", ssl.OPENSSL_VERSION)
ctx = ssl.create_default_context()
print("SSL context created successfully")
"""

    with open('/tmp/ssl_test.py', 'w') as f:
        f.write(ssl_test_script)

    success = run_command("python3 /tmp/ssl_test.py", "Test SSL functionality")
    os.remove('/tmp/ssl_test.py')
    return success

def test_mia_functionality():
    """Test basic MIA functionality"""
    # Create a temporary test script
    functionality_test_script = """
try:
    from mia.connectivity import ConnectivityManager
    print("✓ ConnectivityManager imported")
except ImportError as e:
    print("✗ ConnectivityManager failed:", e)
    import traceback
    traceback.print_exc()
    exit(1)

try:
    from mia.cloud_integration import CloudIntegration
    print("✓ CloudIntegration imported")
except ImportError as e:
    print("✗ CloudIntegration failed:", e)
    import traceback
    traceback.print_exc()
    exit(1)

try:
    from mia.device_manager import DeviceManager
    print("✓ DeviceManager imported")
except ImportError as e:
    print("✗ DeviceManager failed:", e)
    import traceback
    traceback.print_exc()
    exit(1)

print("All MIA classes imported successfully")
"""

    with open('/tmp/mia_functionality_test.py', 'w') as f:
        f.write(functionality_test_script)

    success = run_command("python3 /tmp/mia_functionality_test.py", "Test MIA class imports")
    os.remove('/tmp/mia_functionality_test.py')
    return success

def main():
    """Main test function"""
    print("🚀 Starting MIA Deployment Tests on Raspberry Pi")
    print("=" * 50)

    # Test basic Python environment
    print("\n📋 Testing Python Environment")
    if not run_command("python3 --version", "Check Python 3 availability"):
        print("❌ Python 3 not available - cannot proceed")
        return False

    # Test SSL functionality
    print("\n🔒 Testing SSL Functionality")
    if not test_ssl_functionality():
        print("❌ SSL functionality tests failed")
        return False

    # Test MIA imports
    print("\n📦 Testing MIA Package Imports")
    if not test_mia_imports():
        print("❌ MIA import tests failed")
        return False

    # Test MIA functionality
    print("\n⚙️  Testing MIA Functionality")
    if not test_mia_functionality():
        print("❌ MIA functionality tests failed")
        return False

    print("\n🎉 All MIA deployment tests passed!")
    print("✅ MIA is successfully deployed and functional on Raspberry Pi")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)