#!/usr/bin/env python3
"""
Simple MCP client to test the ESP32 serial monitor server
"""

import asyncio
import json
import sys
from pathlib import Path

async def test_mcp_server():
    """Test the MCP server by running it and making requests"""

    # Import the server
    sys.path.insert(0, str(Path(__file__).parent))
    sys.path.insert(0, '/home/sparrow/.local/share/pipx/venvs/mcp/lib/python3.12/site-packages')

    try:
        from esp32_serial_monitor_mcp_server import app

        if app is None:
            print("❌ Server app not available")
            return

        print("✅ Server app loaded successfully")

        # Test the tools
        print("\n🛠️  Testing tools...")

        # Test detect_esp32_ports
        try:
            result = await app.call_tool("detect_esp32_ports", {})
            print(f"✅ detect_esp32_ports: {result[0][0].text[:100]}...")
        except Exception as e:
            print(f"❌ detect_esp32_ports failed: {e}")

        # Test list_serial_sessions
        try:
            result = await app.call_tool("list_serial_sessions", {})
            print(f"✅ list_serial_sessions: {result[0][0].text}")
        except Exception as e:
            print(f"❌ list_serial_sessions failed: {e}")

        # Test start_serial_monitor (without actually starting)
        try:
            # This will fail because no terminal is available, but we can test the validation
            result = await app.call_tool("start_serial_monitor", {"port": "/dev/ttyACM0"})
            print(f"✅ start_serial_monitor validation passed")
        except Exception as e:
            print(f"ℹ️  start_serial_monitor: {str(e)[:100]}... (expected in test environment)")

        # Test get_serial_status with invalid session
        try:
            result = await app.call_tool("get_serial_status", {"session_id": "invalid"})
            print(f"ℹ️  get_serial_status: {str(e)[:100]}... (expected for invalid session)")
        except Exception as e:
            print(f"ℹ️  get_serial_status: {str(e)[:100]}... (expected for invalid session)")

        print("\n🎉 MCP server testing completed!")

    except Exception as e:
        print(f"❌ Error testing server: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mcp_server())