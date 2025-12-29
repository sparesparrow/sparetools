# Android Dev Tools MCP Server

A comprehensive MCP server for Android development workflow, providing tools for building, deploying, testing, and managing Android applications.

## Features

- **APK Build Operations**: Gradle-based APK building with progress monitoring
- **Device Management**: Automatic device detection and management
- **App Deployment**: ADB-based APK installation and management
- **Testing Framework**: Unit and instrumentation test execution
- **Log Monitoring**: Real-time logcat capture and filtering
- **App Management**: Data clearing and app uninstallation
- **Session Tracking**: Persistent session management across operations

## Prerequisites

- Python 3.8+
- Android SDK with ADB installed
- Android device or emulator connected
- Gradle wrapper in Android projects

## Installation

```bash
cd /home/sparrow/mcp/servers/android_dev_tools
pip install -r requirements.txt
```

## Configuration

Add to your `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "android-dev-tools": {
      "command": "uv",
      "args": ["run", "--with", "mcp", "python3", "/home/sparrow/mcp/servers/android_dev_tools/android_dev_tools_mcp_server.py"],
      "env": {
        "ANDROID_LOG_LEVEL": "INFO",
        "ANDROID_LOG_DIR": "/home/sparrow/android_logs",
        "ANDROID_SESSION_STORAGE": "/home/sparrow/.mcp/android_sessions.json"
      },
      "cwd": "${workspaceFolder}"
    }
  }
}
```

## Available Tools

### 1. build_android_apk
Build Android APK with Gradle
- **Parameters**: project_path, build_type (debug/release), terminal (boolean)
- **Returns**: Build session details with progress tracking

### 2. deploy_android_apk
Deploy APK to Android device using ADB
- **Parameters**: apk_path, device_id (optional), terminal (boolean)
- **Returns**: Deployment session details

### 3. run_android_tests
Execute Android unit and instrumentation tests
- **Parameters**: project_path, test_type (unit/instrumented), device_id (optional), terminal (boolean)
- **Returns**: Test execution session details

### 4. android_device_info
Get connected Android device information
- **Parameters**: None
- **Returns**: List of connected devices with details

### 5. android_logcat
Start Android logcat monitoring
- **Parameters**: device_id (optional), filter_spec (optional), terminal (boolean)
- **Returns**: Logcat session details

### 6. clear_android_data
Clear app data on Android device
- **Parameters**: package_name, device_id (optional)
- **Returns**: Clear data operation result

### 7. uninstall_android_app
Uninstall app from Android device
- **Parameters**: package_name, device_id (optional)
- **Returns**: Uninstall operation result

## Usage Examples

### Building an APK
```javascript
// Build debug APK in terminal
mcp_android-dev-tools_build_android_apk({
  project_path: "/path/to/android/project",
  build_type: "debug",
  terminal: true
})
```

### Deploying to Device
```javascript
// Deploy APK to connected device
mcp_android-dev-tools_deploy_android_apk({
  apk_path: "/path/to/app-debug.apk",
  device_id: "emulator-5554"
})
```

### Running Tests
```javascript
// Run unit tests
mcp_android-dev-tools_run_android_tests({
  project_path: "/path/to/android/project",
  test_type: "unit"
})
```

### Monitoring Logs
```javascript
// Start logcat with filtering
mcp_android-dev-tools_android_logcat({
  device_id: "emulator-5554",
  filter_spec: "*:E MyApp:D"
})
```

## Session Management

All operations create sessions that are tracked persistently:
- Session IDs for tracking long-running operations
- Progress updates and status monitoring
- Log file generation for all operations
- Automatic cleanup of stale sessions

## Error Handling

- Comprehensive error reporting with detailed messages
- Graceful handling of device disconnection
- Timeout management for long-running operations
- Recovery mechanisms for failed operations

## Logging

All operations generate logs stored in `~/android_logs/`:
- Build logs with Gradle output
- Deployment logs with ADB output
- Test execution logs
- Logcat capture files

## Troubleshooting

### No Devices Found
- Ensure Android device/emulator is connected
- Check ADB installation: `adb devices`
- Try restarting ADB: `adb kill-server && adb start-server`

### Build Failures
- Verify Gradle wrapper exists: `ls gradlew`
- Check Android project structure
- Review build logs for specific errors

### Permission Issues
- Ensure ADB has proper permissions
- Check device USB debugging is enabled
- Verify Android SDK path is correct