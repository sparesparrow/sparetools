# Troubleshooting Guide

This guide covers common issues and solutions when using the ESP32 Serial Monitor MCP Server.

## Port Detection Issues

### No Ports Detected

**Symptoms:**
- `detect_esp32_ports` returns empty array
- Error messages about no ESP32 devices found

**Solutions:**

1. **Check USB Connection:**
   ```bash
   # Linux
   lsusb | grep -i esp32
   dmesg | tail -20 | grep tty

   # Check permissions
   ls -la /dev/ttyUSB* /dev/ttyACM*
   ```

2. **Install USB Drivers:**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install linux-tools-generic
   sudo apt-get install usbutils

   # Or install specific drivers for your ESP32
   sudo apt-get install cp210x-dkms  # For Silicon Labs CP210x
   ```

3. **Add User to Dialout Group:**
   ```bash
   sudo usermod -a -G dialout $USER
   # Log out and back in, or reboot
   ```

4. **Check PlatformIO Installation:**
   ```bash
   pio device list
   # If not installed: pip install platformio
   ```

### Wrong Ports Detected

**Symptoms:**
- Ports detected but not the correct ESP32 device
- Connection fails or shows wrong device data

**Solutions:**

1. **Verify Device VID/PID:**
   ```bash
   lsusb -v | grep -A 10 -B 5 "ESP32\|CP210\|CH340"
   ```

2. **Check Multiple Devices:**
   - Unplug other USB devices
   - Use `dmesg` to see device assignment order
   - Try different ports on the ESP32 board

3. **Manual Port Specification:**
   ```bash
   # List all available ports
   python3 -c "import serial.tools.list_ports; print([p.device for p in serial.tools.list_ports.comports()])"
   ```

## Session Management Issues

### Session Won't Start

**Symptoms:**
- `start_serial_monitor` returns error
- "Permission denied" or "Device busy" errors

**Solutions:**

1. **Check Port Permissions:**
   ```bash
   ls -la /dev/ttyUSB0  # Replace with your port
   sudo chmod 666 /dev/ttyUSB0  # Temporary fix
   ```

2. **Kill Existing Processes:**
   ```bash
   # Find processes using the port
   lsof /dev/ttyUSB0
   fuser -k /dev/ttyUSB0  # Kill processes using the port
   ```

3. **Check for Other Serial Monitors:**
   ```bash
   ps aux | grep -i serial
   ps aux | grep -i screen
   ps aux | grep -i minicom
   ```

4. **Try Different Baud Rate:**
   - Common rates: 9600, 115200, 230400, 460800, 921600
   - Check your ESP32 firmware configuration

### Session Appears Running But No Output

**Symptoms:**
- Session status shows "running" but no serial data
- Log file exists but is empty or not updating

**Solutions:**

1. **Check ESP32 Power and Programming:**
   - Ensure ESP32 is powered on
   - Check if ESP32 is in programming mode (BOOT button)
   - Reset the ESP32 after starting monitor

2. **Verify Serial Connection:**
   ```bash
   # Test with basic tools
   screen /dev/ttyUSB0 115200
   # Or
   minicom -b 115200 -D /dev/ttyUSB0
   ```

3. **Check Baud Rate Mismatch:**
   - Ensure baud rate matches ESP32 firmware
   - Common ESP32 default: 115200

4. **Hardware Issues:**
   - Try different USB cable
   - Test on different USB port
   - Check ESP32 board for damage

## Terminal Issues

### Terminal Won't Open

**Symptoms:**
- Session starts but no terminal window appears
- "No terminal emulator found" error

**Solutions:**

1. **Install Terminal Emulator:**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install gnome-terminal
   # Or alternatives
   sudo apt-get install xterm
   sudo apt-get install konsole
   sudo apt-get install kitty
   sudo apt-get install alacritty
   ```

2. **Check Display Environment:**
   ```bash
   echo $DISPLAY
   # Should show something like :0 or :1
   ```

3. **Use Non-Terminal Mode:**
   ```json
   {
     "tool": "start_serial_monitor",
     "parameters": {
       "port": "/dev/ttyUSB0",
       "terminal": false
     }
   }
   ```

### Terminal Opens But Closes Immediately

**Symptoms:**
- Terminal window flashes and disappears
- Session starts then immediately stops

**Solutions:**

1. **Check Serial Port Access:**
   - Verify user has permission to access the port
   - Try running as root (not recommended for production)

2. **Test Manual Connection:**
   ```bash
   # Test if port is accessible
   timeout 5 screen /dev/ttyUSB0 115200 || echo "Port access failed"
   ```

3. **Check Dependencies:**
   - Ensure `screen` or `minicom` is installed
   - `sudo apt-get install screen`

## Log File Issues

### Log Files Not Created

**Symptoms:**
- Sessions run but no log files in `esp32_logs/`
- "Permission denied" for log directory

**Solutions:**

1. **Check Directory Permissions:**
   ```bash
   ls -la ~/esp32_logs/
   chmod 755 ~/esp32_logs/
   ```

2. **Check Environment Variable:**
   ```bash
   echo $ESP32_LOG_DIR
   # Should point to writable directory
   ```

3. **Create Directory Manually:**
   ```bash
   mkdir -p ~/esp32_logs
   chmod 755 ~/esp32_logs
   ```

### Log Files Empty

**Symptoms:**
- Log files exist but contain no data
- Session appears running but no output captured

**Solutions:**

1. **Check Serial Data Flow:**
   - Verify ESP32 is actually sending data
   - Try `read_serial_output` tool to check file contents

2. **File Permission Issues:**
   ```bash
   ls -la ~/esp32_logs/esp32_session_*.log
   # Should be writable by the user
   ```

3. **Process Issues:**
   - Check if background process is actually running
   - Use `ps aux | grep python` to find monitor processes

## MCP Server Issues

### Server Won't Start

**Symptoms:**
- MCP server fails to initialize
- Import errors for dependencies

**Solutions:**

1. **Install Dependencies:**
   ```bash
   cd /home/sparrow/mcp/servers/esp32_serial_monitor/
   pip install -r requirements.txt
   ```

2. **Check Python Version:**
   ```bash
   python3 --version
   # Should be 3.8 or higher
   ```

3. **Check MCP Installation:**
   ```bash
   python3 -c "import mcp; print('MCP version:', mcp.__version__)"
   ```

4. **Environment Issues:**
   ```bash
   # Check if virtual environment is activated
   which python3
   echo $PYTHONPATH
   ```

### Tools Not Available

**Symptoms:**
- MCP server starts but tools don't appear in Cursor
- "Tool not found" errors

**Solutions:**

1. **Restart MCP Server:**
   - Close and reopen Cursor
   - Or restart MCP server process

2. **Check MCP Configuration:**
   ```json
   // ~/.cursor/mcp.json
   {
     "mcpServers": {
       "esp32-serial-monitor": {
         "command": "python3",
         "args": ["/home/sparrow/mcp/servers/esp32_serial_monitor_mcp_server.py"],
         "cwd": "/path/to/your/esp32/project"
       }
     }
   }
   ```

3. **Validate Server Path:**
   ```bash
   ls -la /home/sparrow/mcp/servers/esp32_serial_monitor_mcp_server.py
   python3 /home/sparrow/mcp/servers/esp32_serial_monitor_mcp_server.py --help 2>/dev/null || echo "Server validation failed"
   ```

## Performance Issues

### Slow Port Detection

**Symptoms:**
- `detect_esp32_ports` takes a long time
- UI becomes unresponsive

**Solutions:**

1. **Check PlatformIO:**
   ```bash
   time pio device list --json >/dev/null
   # Should complete in < 5 seconds
   ```

2. **Disable Strategies:**
   - Temporarily disable slow detection methods
   - Focus on manual port specification

3. **Cache Issues:**
   - Clear port detection cache (restart server)
   - Check for stale cached data

### High Memory Usage

**Symptoms:**
- Server process uses excessive memory
- System becomes slow

**Solutions:**

1. **Check Log File Sizes:**
   ```bash
   du -sh ~/esp32_logs/
   find ~/esp32_logs/ -name "*.log" -size +10M  # Find large files
   ```

2. **Clean Old Sessions:**
   ```bash
   # Use list_serial_sessions to find old sessions
   # Manually clean up old log files
   find ~/esp32_logs/ -name "*.log" -mtime +7 -delete
   ```

3. **Reduce Log Retention:**
   - Set shorter session timeouts
   - Implement log rotation

## ESP32-Specific Issues

### Bootloader Messages Only

**Symptoms:**
- Only see ESP32 ROM bootloader output
- No application output

**Solutions:**

1. **Check Firmware:**
   - Ensure ESP32 has firmware flashed
   - Check if firmware includes serial output

2. **Reset Sequence:**
   - Press EN button to reset ESP32
   - Try BOOT + EN for programming mode

3. **Baud Rate Issues:**
   - Bootloader often uses 115200
   - Application may use different rate

### Garbled Output

**Symptoms:**
- Serial output shows random characters
- Unreadable text

**Solutions:**

1. **Baud Rate Mismatch:**
   - Try different baud rates: 9600, 115200, 230400
   - Check ESP32 firmware documentation

2. **Encoding Issues:**
   - Ensure UTF-8 compatibility
   - Check for binary data in serial stream

3. **Hardware Issues:**
   - Check USB cable quality
   - Try different USB port
   - Test with different ESP32 board

## System-Specific Issues

### Linux Issues

**Common problems and solutions for Linux systems:**

1. **udev Rules:**
   ```bash
   # Create udev rule for ESP32
   sudo tee /etc/udev/rules.d/99-esp32.rules << EOF
   SUBSYSTEM=="tty", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", MODE="0666"
   SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", MODE="0666"
   EOF
   sudo udevadm control --reload-rules
   sudo udevadm trigger
   ```

2. **ModemManager Conflicts:**
   ```bash
   # Disable ModemManager for ESP32 ports
   sudo systemctl stop ModemManager
   sudo systemctl disable ModemManager
   ```

### Permission Issues

**General permission solutions:**

```bash
# Add user to required groups
sudo usermod -a -G dialout,tty,uucp $USER

# Set permissions on serial ports
sudo chmod 666 /dev/ttyUSB*
sudo chmod 666 /dev/ttyACM*

# For persistent permissions, create udev rule
sudo tee /etc/udev/rules.d/50-serial-permissions.rules << EOF
KERNEL=="ttyUSB*", MODE="0666"
KERNEL=="ttyACM*", MODE="0666"
EOF
sudo udevadm control --reload-rules
```

## Getting Help

If these solutions don't resolve your issue:

1. **Check Logs:**
   ```bash
   # Server logs
   tail -f ~/.cursor/logs/mcp-esp32-serial-monitor.log

   # System logs
   journalctl -f | grep -i esp32
   ```

2. **Gather Information:**
   ```bash
   # System info
   uname -a
   python3 --version
   pip list | grep -E "(pyserial|mcp)"

   # ESP32 info
   lsusb | grep -i esp
   ls -la /dev/ttyUSB* /dev/ttyACM* 2>/dev/null || echo "No serial ports found"
   ```

3. **Test Basic Functionality:**
   ```bash
   # Test Python imports
   python3 -c "import serial; print('PySerial OK')"
   python3 -c "import mcp; print('MCP OK')"

   # Test port access
   python3 -c "import serial; s=serial.Serial('/dev/ttyUSB0', 115200, timeout=1); print('Port access OK'); s.close()"
   ```

4. **Report Issues:**
   - Include full error messages
   - Provide system information
   - Describe steps to reproduce
   - Include relevant log excerpts

## Quick Diagnostic Script

Run this script to diagnose common issues:

```bash
#!/bin/bash
echo "=== ESP32 Serial Monitor Diagnostics ==="
echo "Python version: $(python3 --version)"
echo "PySerial installed: $(python3 -c 'import serial; print("Yes")' 2>/dev/null || echo 'No')"
echo "MCP installed: $(python3 -c 'import mcp; print("Yes")' 2>/dev/null || echo 'No')"
echo "PlatformIO available: $(which pio >/dev/null && echo 'Yes' || echo 'No')"
echo ""
echo "Serial ports found:"
ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null || echo "None found"
echo ""
echo "USB devices:"
lsusb | grep -i -E "(esp|cp210|ch340)" || echo "No ESP32 devices found"
echo ""
echo "Terminal emulators:"
for term in gnome-terminal xterm konsole kitty alacritty; do
    which $term >/dev/null && echo "✓ $term" || echo "✗ $term"
done
echo ""
echo "User groups: $(groups)"
echo "Log directory: $(ls -la ~/esp32_logs/ 2>/dev/null || echo 'Not created')"
echo ""
echo "=== End Diagnostics ==="
```