#!/usr/bin/env python3
"""
Simple test MCP server for ESP32 serial monitoring
"""

from mcp.server import FastMCP

app = FastMCP("esp32-serial-test")

@app.tool()
def detect_esp32_ports() -> str:
    """Detect available ESP32 serial ports"""
    return '["/dev/ttyACM0", "/dev/ttyACM1"]'

@app.tool()
def list_serial_sessions() -> str:
    """List all serial sessions"""
    return "[]"

if __name__ == "__main__":
    app.run()