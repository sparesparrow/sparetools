# ESP32 Serial Monitor MCP Server

A comprehensive MCP (Model Context Protocol) server for ESP32 serial monitoring with robust session management, multi-strategy port detection, and cross-platform terminal support.

## Features

- **Session Management**: Persistent sessions with UUID-based tracking and automatic cleanup
- **Multi-Strategy Port Detection**: PlatformIO → PySerial → Manual fallback detection
- **Cross-Platform Terminal Support**: Auto-detection of gnome-terminal, xterm, konsole, kitty, alacritty
- **8 Comprehensive Tools**: Complete serial monitoring workflow
- **Thread-Safe Operations**: Concurrent session management with proper locking
- **Robust Error Handling**: Graceful degradation and clear error messages
- **Log Persistence**: All serial output saved to timestamped log files

## Installation

### Prerequisites

- **Python**: 3.8+ (for modern async features)
- **System Dependencies**:
  - PlatformIO Core (optional, for enhanced port detection)
  - Terminal emulator (gnome-terminal, xterm, konsole, kitty, or alacritty)
  - ESP32 USB drivers (varies by OS)

### Setup

1. **Clone or download** the server files to your MCP servers directory:
   ```bash
   cd /home/sparrow/mcp/servers/
   mkdir esp32_serial_monitor
   cd esp32_serial_monitor
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Update MCP Configuration** (see Configuration section below)

4. **Verify Installation**:
   ```bash
   python3 esp32_serial_monitor_mcp_server.py --help
   ```

## Configuration

### MCP Configuration

Add the following to your `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "esp32-serial-monitor": {
      "command": "python3",
      "args": ["/home/sparrow/mcp/servers/esp32_serial_monitor_mcp_server.py"],
      "env": {
        "ESP32_LOG_LEVEL": "INFO",
        "ESP32_LOG_DIR": "/home/sparrow/esp32_logs",
        "ESP32_SESSION_STORAGE": "/home/sparrow/.mcp/esp32_sessions.json"
      },
      "cwd": "/home/sparrow/projects/embedded-systems/esp32-bpm-detector"
    }
  }
}
```

### Environment Variables

- `ESP32_LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR) - default: INFO
- `ESP32_LOG_DIR`: Directory for serial output logs - default: ~/esp32_logs
- `ESP32_SESSION_STORAGE`: Path for session persistence - default: ~/.mcp/esp32_sessions.json

## Tools

The server provides 8 comprehensive tools for ESP32 serial monitoring:

### 1. `start_serial_monitor`

Start a new ESP32 serial monitor session.

**Parameters:**
- `port` (string, required): Serial port (e.g., `/dev/ttyUSB0`, `COM3`)
- `baud_rate` (integer, optional): Baud rate (default: 115200)
- `terminal` (boolean, optional): Spawn in terminal window (default: true)

**Example:**
```json
{
  "tool": "start_serial_monitor",
  "parameters": {
    "port": "/dev/ttyUSB0",
    "baud_rate": 115200,
    "terminal": true
  }
}
```

**Response:**
```json
{
  "session_id": "123e4567-e89b-12d3-a456-426614174000",
  "port": "/dev/ttyUSB0",
  "baud_rate": 115200,
  "status": "running",
  "log_file": "/home/sparrow/esp32_logs/esp32_session_123e4567-e89b-12d3-a456-426614174000.log",
  "terminal": true
}
```

### 2. `stop_serial_monitor`

Stop a serial monitor session gracefully.

**Parameters:**
- `session_id` (string, required): Session ID to stop
- `timeout` (integer, optional): Graceful shutdown timeout in seconds (default: 5)

**Example:**
```json
{
  "tool": "stop_serial_monitor",
  "parameters": {
    "session_id": "123e4567-e89b-12d3-a456-426614174000",
    "timeout": 5
  }
}
```

### 3. `kill_serial_monitor`

Force kill a stuck serial monitor session.

**Parameters:**
- `session_id` (string, required): Session ID to kill

### 4. `list_serial_sessions`

List all active and inactive serial sessions with health status.

**Parameters:** None

**Response:**
```json
[
  {
    "session_id": "123e4567-e89b-12d3-a456-426614174000",
    "port": "/dev/ttyUSB0",
    "baud_rate": 115200,
    "status": "running",
    "start_time": "2025-12-29T10:30:00",
    "uptime_seconds": 3600,
    "log_file": "/home/sparrow/esp32_logs/esp32_session_123e4567-e89b-12d3-a456-426614174000.log",
    "pid": 12345,
    "terminal_pid": 12346,
    "error_message": null
  }
]
```

### 5. `get_serial_status`

Get detailed status of a specific session including log preview.

**Parameters:**
- `session_id` (string, required): Session ID to check

**Response:**
```json
{
  "session_id": "123e4567-e89b-12d3-a456-426614174000",
  "port": "/dev/ttyUSB0",
  "baud_rate": 115200,
  "status": "running",
  "alive": true,
  "start_time": "2025-12-29T10:30:00",
  "uptime_seconds": 3600,
  "log_file": "/home/sparrow/esp32_logs/esp32_session_123e4567-e89b-12d3-a456-426614174000.log",
  "log_preview": [
    "ESP-ROM:esp32s3-20210327",
    "Build:Mar 27 2021",
    "rst:0x1 (POWERON),boot:0x8 (SPI_FAST_FLASH_BOOT)",
    "SPIWP:0xee",
    "mode:DIO, clock div:2"
  ],
  "pid": 12345,
  "terminal_pid": 12346,
  "error_message": null
}
```

### 6. `detect_esp32_ports`

Detect available ESP32 serial ports using multiple strategies.

**Parameters:** None

**Response:**
```json
[
  {
    "port": "/dev/ttyUSB0",
    "description": "USB Serial Device (VID:10C4 PID:EA60)",
    "method": "pyserial"
  },
  {
    "port": "/dev/ttyACM0",
    "description": "ESP32 (PlatformIO)",
    "method": "platformio"
  }
]
```

### 7. `read_serial_output`

Read serial output from a session's log file.

**Parameters:**
- `session_id` (string, required): Session ID to read from
- `lines` (integer, optional): Number of lines to read (default: 50)
- `tail` (boolean, optional): Read from end of file (default: true)

**Response:**
```json
{
  "session_id": "123e4567-e89b-12d3-a456-426614174000",
  "output": [
    "ESP-ROM:esp32s3-20210327",
    "Build:Mar 27 2021",
    "rst:0x1 (POWERON),boot:0x8 (SPI_FAST_FLASH_BOOT)"
  ],
  "total_lines": 150,
  "returned_lines": 50,
  "tail": true
}
```

### 8. `send_serial_command`

Send a command to the serial device (logged to session file).

**Parameters:**
- `session_id` (string, required): Session ID to send to
- `command` (string, required): Command to send

**Note:** Interactive command sending requires maintaining the serial connection. Currently logs commands for reference.

## Usage Examples

### Basic Serial Monitoring

1. **Detect available ports:**
   ```json
   {"tool": "detect_esp32_ports"}
   ```

2. **Start monitoring:**
   ```json
   {
     "tool": "start_serial_monitor",
     "parameters": {"port": "/dev/ttyUSB0"}
   }
   ```

3. **Check session status:**
   ```json
   {
     "tool": "get_serial_status",
     "parameters": {"session_id": "your-session-id"}
   }
   ```

4. **Read recent output:**
   ```json
   {
     "tool": "read_serial_output",
     "parameters": {"session_id": "your-session-id", "lines": 20}
   }
   ```

5. **Stop monitoring:**
   ```json
   {
     "tool": "stop_serial_monitor",
     "parameters": {"session_id": "your-session-id"}
   }
   ```

### Advanced Usage

**Monitor multiple ESP32 devices:**
```json
// Start first device
{"tool": "start_serial_monitor", "parameters": {"port": "/dev/ttyUSB0", "terminal": false}}
// Start second device
{"tool": "start_serial_monitor", "parameters": {"port": "/dev/ttyUSB1", "terminal": false}}
// List all sessions
{"tool": "list_serial_sessions"}
```

**Debug session issues:**
```json
// Check all sessions
{"tool": "list_serial_sessions"}
// Get detailed status
{"tool": "get_serial_status", "parameters": {"session_id": "problematic-session-id"}}
// Force kill if needed
{"tool": "kill_serial_monitor", "parameters": {"session_id": "problematic-session-id"}}
```

## Architecture

### SessionTracker Class

- **UUID-based session IDs** for unique identification
- **Thread-safe operations** with RLock for concurrent access
- **JSON persistence** with atomic writes to prevent corruption
- **Automatic cleanup** of stale sessions (60-minute timeout)
- **Metadata tracking** (PID, port, baud rate, start time, status)

### Port Detection Pipeline

1. **PlatformIO Priority**: `pio device list --json` for accurate detection
2. **PySerial Fallback**: VID/PID matching for ESP32 devices
3. **Manual Scanning**: Common port patterns as last resort
4. **10-second caching** with invalidation for performance

### Terminal Management

- **Auto-detection** of available terminal emulators
- **Cross-platform support** for Linux terminal environments
- **Proper process management** with cleanup on termination
- **Command escaping** to prevent shell injection

### Error Handling

- **Input validation** for all parameters
- **Graceful degradation** when dependencies unavailable
- **Clear error messages** with actionable suggestions
- **Resource cleanup** on failures
- **Process health monitoring** with automatic status updates

## Security Considerations

- **Input validation** prevents command injection
- **Safe file paths** with proper validation
- **No elevated privileges** required
- **Permission handling** for log files and device access
- **Process isolation** between sessions

## Performance

- **Lazy dependency loading** to reduce startup time
- **Efficient log reading** with tail implementation
- **Session state caching** for fast lookups
- **Minimal memory footprint** with cleanup routines
- **Fast startup time** under normal conditions

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues and solutions.

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### Code Style

- Follow PEP 8 for Python code
- Use type hints for function parameters and return values
- Add docstrings for all public functions and classes
- Keep functions focused on single responsibilities

## License

This project is licensed under the MIT License - see the LICENSE file for details.