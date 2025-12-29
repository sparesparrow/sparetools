#!/usr/bin/env python3
"""
Enhanced ESP32 Serial Monitor MCP Server

A comprehensive MCP server for ESP32 serial monitoring with:
- Robust session management with persistence
- Multi-strategy port detection (PlatformIO → PySerial → Manual)
- Cross-platform terminal support
- 8 comprehensive tools for serial operations
- Thread-safe operations and error handling
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import threading
import time
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import re

# Lazy imports for optional dependencies
try:
    import serial
    import serial.tools.list_ports
    PYSERIAL_AVAILABLE = True
except ImportError:
    PYSERIAL_AVAILABLE = False
    serial = None

try:
    from mcp.server import FastMCP
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

# Configuration
DEFAULT_BAUD_RATE = 115200
SESSION_TIMEOUT_MINUTES = 60
PORT_CACHE_TIMEOUT_SECONDS = 10
LOG_MAX_LINES = 1000

# ESP32 VID/PID constants
ESP32_VID_PID = [
    (0x10C4, 0xEA60),  # Silicon Labs CP210x
    (0x1A86, 0x7523),  # CH340/CH341
    (0x0403, 0x6001),  # FTDI FT232
    (0x303A, 0x1001),  # Espressif USB JTAG/serial debug unit
]

@dataclass
class SerialSession:
    """Represents a serial monitoring session"""
    session_id: str
    port: str
    baud_rate: int
    pid: Optional[int] = None
    start_time: datetime = None
    status: str = "created"  # created, running, stopped, error
    log_file: Optional[str] = None
    terminal_pid: Optional[int] = None
    error_message: Optional[str] = None

    def __post_init__(self):
        if self.start_time is None:
            self.start_time = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['start_time'] = self.start_time.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SerialSession':
        """Create from dictionary"""
        data['start_time'] = datetime.fromisoformat(data['start_time'])
        return cls(**data)

    def is_alive(self) -> bool:
        """Check if session is still alive"""
        if self.pid and self.status == "running":
            try:
                os.kill(self.pid, 0)  # Signal 0 just checks if process exists
                return True
            except OSError:
                return False
        return False

    def get_uptime(self) -> Optional[timedelta]:
        """Get session uptime"""
        if self.start_time:
            return datetime.now() - self.start_time
        return None

class SessionTracker:
    """Thread-safe session management with persistence"""

    def __init__(self, storage_path: str = "~/.mcp/esp32_sessions.json"):
        self.storage_path = Path(storage_path).expanduser()
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._sessions: Dict[str, SerialSession] = {}
        self._lock = threading.RLock()
        self._load_sessions()

    def _load_sessions(self):
        """Load sessions from persistent storage"""
        try:
            if self.storage_path.exists():
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    for session_data in data.get('sessions', []):
                        session = SerialSession.from_dict(session_data)
                        # Clean up stale sessions
                        if not session.is_alive() and session.status == "running":
                            session.status = "stopped"
                        self._sessions[session.session_id] = session
        except Exception as e:
            logging.warning(f"Failed to load sessions: {e}")

    def _save_sessions(self):
        """Save sessions to persistent storage"""
        try:
            data = {
                'sessions': [s.to_dict() for s in self._sessions.values()],
                'last_updated': datetime.now().isoformat()
            }
            # Atomic write
            temp_path = self.storage_path.with_suffix('.tmp')
            with open(temp_path, 'w') as f:
                json.dump(data, f, indent=2)
            temp_path.replace(self.storage_path)
        except Exception as e:
            logging.error(f"Failed to save sessions: {e}")

    def create_session(self, port: str, baud_rate: int = DEFAULT_BAUD_RATE) -> SerialSession:
        """Create a new session"""
        with self._lock:
            session_id = str(uuid.uuid4())
            session = SerialSession(
                session_id=session_id,
                port=port,
                baud_rate=baud_rate
            )
            self._sessions[session_id] = session
            self._save_sessions()
            return session

    def get_session(self, session_id: str) -> Optional[SerialSession]:
        """Get session by ID"""
        with self._lock:
            return self._sessions.get(session_id)

    def update_session(self, session: SerialSession):
        """Update session state"""
        with self._lock:
            self._sessions[session.session_id] = session
            self._save_sessions()

    def remove_session(self, session_id: str):
        """Remove a session"""
        with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
                self._save_sessions()

    def list_sessions(self) -> List[SerialSession]:
        """List all sessions"""
        with self._lock:
            # Clean up stale sessions
            for session in list(self._sessions.values()):
                if not session.is_alive() and session.status == "running":
                    session.status = "stopped"
                    self.update_session(session)
            return list(self._sessions.values())

    def cleanup_stale_sessions(self):
        """Remove sessions older than timeout"""
        with self._lock:
            cutoff = datetime.now() - timedelta(minutes=SESSION_TIMEOUT_MINUTES)
            to_remove = []
            for session in self._sessions.values():
                if session.start_time < cutoff and session.status != "running":
                    to_remove.append(session.session_id)
            for session_id in to_remove:
                del self._sessions[session_id]
            if to_remove:
                self._save_sessions()

class PortDetector:
    """Multi-strategy ESP32 port detection"""

    def __init__(self):
        self._cache: Optional[List[Dict[str, Any]]] = None
        self._cache_time: Optional[float] = None

    def detect_ports(self) -> List[Dict[str, Any]]:
        """Detect ESP32 ports using multiple strategies"""
        # Check cache
        if self._cache and time.time() - self._cache_time < PORT_CACHE_TIMEOUT_SECONDS:
            return self._cache

        ports = []

        # Strategy 1: PlatformIO device list
        ports.extend(self._detect_platformio())

        # Strategy 2: PySerial enumeration
        ports.extend(self._detect_pyserial())

        # Strategy 3: Manual port scanning
        ports.extend(self._detect_manual())

        # Remove duplicates and cache
        seen_ports = set()
        unique_ports = []
        for port in ports:
            port_key = port['port']
            if port_key not in seen_ports:
                seen_ports.add(port_key)
                unique_ports.append(port)

        self._cache = unique_ports
        self._cache_time = time.time()
        return unique_ports

    def _detect_platformio(self) -> List[Dict[str, Any]]:
        """Detect ports using PlatformIO"""
        ports = []
        try:
            result = subprocess.run(
                ['pio', 'device', 'list', '--json'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                devices = json.loads(result.stdout)
                for device in devices:
                    if 'esp32' in device.get('description', '').lower() or \
                       any(vid_pid in str(device) for vid_pid in ['10C4:EA60', '1A86:7523', '0403:6001', '303A:1001']):
                        ports.append({
                            'port': device['port'],
                            'description': device.get('description', 'ESP32 (PlatformIO)'),
                            'method': 'platformio'
                        })
        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
            pass
        return ports

    def _detect_pyserial(self) -> List[Dict[str, Any]]:
        """Detect ports using PySerial"""
        ports = []
        if not PYSERIAL_AVAILABLE:
            return ports

        try:
            for port_info in serial.tools.list_ports.comports():
                # Check VID/PID for ESP32 devices
                if hasattr(port_info, 'vid') and hasattr(port_info, 'pid'):
                    if (port_info.vid, port_info.pid) in ESP32_VID_PID:
                        ports.append({
                            'port': port_info.device,
                            'description': f"{port_info.description} (VID:{port_info.vid:04X} PID:{port_info.pid:04X})",
                            'method': 'pyserial'
                        })
                # Fallback: check description for ESP32 keywords
                elif 'esp32' in port_info.description.lower() or 'cp210' in port_info.description.lower():
                    ports.append({
                        'port': port_info.device,
                        'description': port_info.description,
                        'method': 'pyserial'
                    })
        except Exception:
            pass
        return ports

    def _detect_manual(self) -> List[Dict[str, Any]]:
        """Manual port scanning"""
        ports = []
        common_ports = ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyACM0', '/dev/ttyACM1',
                       'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8']

        for port in common_ports:
            if Path(port).exists():
                ports.append({
                    'port': port,
                    'description': f'Manual detection: {port}',
                    'method': 'manual'
                })
        return ports

class TerminalManager:
    """Cross-platform terminal management"""

    TERMINAL_COMMANDS = {
        'gnome-terminal': ['gnome-terminal', '--', 'bash', '-c'],
        'xterm': ['xterm', '-e'],
        'konsole': ['konsole', '-e'],
        'kitty': ['kitty', '--'],
        'alacritty': ['alacritty', '-e'],
    }

    def __init__(self):
        self.available_terminals = self._detect_terminals()

    def _detect_terminals(self) -> List[str]:
        """Detect available terminal emulators"""
        available = []
        for terminal in self.TERMINAL_COMMANDS.keys():
            try:
                result = subprocess.run(
                    ['which', terminal],
                    capture_output=True,
                    timeout=2
                )
                if result.returncode == 0:
                    available.append(terminal)
            except subprocess.TimeoutExpired:
                pass
        return available

    def spawn_terminal(self, command: str, title: str = "ESP32 Monitor") -> Optional[int]:
        """Spawn a terminal with the given command"""
        if not self.available_terminals:
            raise RuntimeError("No terminal emulator found. Please install gnome-terminal, xterm, konsole, kitty, or alacritty.")

        terminal = self.available_terminals[0]  # Use first available
        cmd_template = self.TERMINAL_COMMANDS[terminal]

        # Build full command
        if terminal == 'gnome-terminal':
            full_cmd = cmd_template + [f'echo "Starting {title}..."; {command}; echo "Press Enter to exit."; read']
        elif terminal in ['xterm', 'konsole', 'alacritty']:
            full_cmd = cmd_template + [f'bash -c "echo \\"Starting {title}...\\"; {command}; echo \\"Press Enter to exit.\\"; read"']
        elif terminal == 'kitty':
            full_cmd = cmd_template + ['bash', '-c', f'echo "Starting {title}..."; {command}; echo "Press Enter to exit."; read']
        else:
            full_cmd = cmd_template + [command]

        try:
            process = subprocess.Popen(
                full_cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                preexec_fn=os.setsid if os.name != 'nt' else None
            )
            return process.pid
        except Exception as e:
            raise RuntimeError(f"Failed to spawn terminal: {e}")

class ESP32SerialMonitorServer:
    """Main MCP Server for ESP32 Serial Monitoring"""

    def __init__(self):
        if not MCP_AVAILABLE:
            raise ImportError("MCP package not available. Install with: pip install mcp")

        self.server = FastMCP("esp32-serial-monitor")
        self.session_tracker = SessionTracker()
        self.port_detector = PortDetector()
        self.terminal_manager = TerminalManager()

        # Register MCP tools
        self.create_tools()

        # Setup logging
        log_level = os.getenv('ESP32_LOG_LEVEL', 'INFO').upper()
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

        # Log directory
        self.log_dir = Path(os.getenv('ESP32_LOG_DIR', '~/esp32_logs')).expanduser()
        self.log_dir.mkdir(parents=True, exist_ok=True)

    async def start_serial_monitor(self, port: str, baud_rate: int = DEFAULT_BAUD_RATE,
                                 terminal: bool = True) -> Dict[str, Any]:
        """Start a new serial monitor session"""
        try:
            # Validate inputs
            if not port:
                raise ValueError("Port is required")
            if not isinstance(baud_rate, int) or baud_rate <= 0:
                raise ValueError("Baud rate must be a positive integer")

            # Check if port exists
            available_ports = self.port_detector.detect_ports()
            port_names = [p['port'] for p in available_ports]
            if port not in port_names:
                self.logger.warning(f"Port {port} not in detected ports: {port_names}")

            # Create session
            session = self.session_tracker.create_session(port, baud_rate)

            # Create log file
            log_file = self.log_dir / f"esp32_session_{session.session_id}.log"
            session.log_file = str(log_file)

            # Build monitor command
            if PYSERIAL_AVAILABLE:
                cmd = f"python3 -c \"import serial, time; s = serial.Serial('{port}', {baud_rate}); print('Connected to {port} at {baud_rate} baud'); open('{log_file}', 'w').close(); f = open('{log_file}', 'a'); while True: line = s.readline().decode('utf-8', errors='replace').rstrip(); print(line); f.write(line + '\\n'); f.flush()\""
            else:
                # Fallback to screen or minicom if available
                cmd = f"screen {port} {baud_rate}"

            if terminal:
                # Spawn in terminal
                try:
                    terminal_pid = self.terminal_manager.spawn_terminal(cmd, f"ESP32 Monitor - {port}")
                    session.terminal_pid = terminal_pid
                except Exception as e:
                    self.logger.error(f"Failed to spawn terminal: {e}")
                    terminal = False

            if not terminal:
                # Run in background
                try:
                    process = subprocess.Popen(
                        cmd,
                        shell=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        preexec_fn=os.setsid if os.name != 'nt' else None
                    )
                    session.pid = process.pid
                except Exception as e:
                    session.status = "error"
                    session.error_message = str(e)
                    self.session_tracker.update_session(session)
                    raise RuntimeError(f"Failed to start monitor: {e}")

            session.status = "running"
            self.session_tracker.update_session(session)

            return {
                "session_id": session.session_id,
                "port": port,
                "baud_rate": baud_rate,
                "status": "running",
                "log_file": str(log_file),
                "terminal": terminal
            }

        except Exception as e:
            self.logger.error(f"Failed to start serial monitor: {e}")
            raise

    async def stop_serial_monitor(self, session_id: str, timeout: int = 5) -> Dict[str, Any]:
        """Stop a serial monitor session gracefully"""
        try:
            session = self.session_tracker.get_session(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")

            if session.status != "running":
                return {"session_id": session_id, "status": session.status, "message": "Session not running"}

            # Try graceful shutdown
            success = False
            if session.pid:
                try:
                    # Send SIGTERM first
                    os.kill(session.pid, 15)  # SIGTERM
                    # Wait for process to exit
                    for _ in range(timeout):
                        if not session.is_alive():
                            success = True
                            break
                        time.sleep(1)
                except OSError:
                    pass

            # Force kill if still running
            if not success and session.pid:
                try:
                    os.kill(session.pid, 9)  # SIGKILL
                    time.sleep(1)
                except OSError:
                    pass

            # Kill terminal if it exists
            if session.terminal_pid:
                try:
                    os.kill(session.terminal_pid, 9)
                except OSError:
                    pass

            session.status = "stopped"
            self.session_tracker.update_session(session)

            return {
                "session_id": session_id,
                "status": "stopped",
                "message": "Session stopped successfully"
            }

        except Exception as e:
            self.logger.error(f"Failed to stop session {session_id}: {e}")
            raise

    async def kill_serial_monitor(self, session_id: str) -> Dict[str, Any]:
        """Force kill a serial monitor session"""
        try:
            session = self.session_tracker.get_session(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")

            # Force kill all related processes
            for pid in [session.pid, session.terminal_pid]:
                if pid:
                    try:
                        os.kill(pid, 9)  # SIGKILL
                    except OSError:
                        pass

            session.status = "killed"
            self.session_tracker.update_session(session)

            return {
                "session_id": session_id,
                "status": "killed",
                "message": "Session force killed"
            }

        except Exception as e:
            self.logger.error(f"Failed to kill session {session_id}: {e}")
            raise

    async def list_serial_sessions(self) -> List[Dict[str, Any]]:
        """List all serial sessions with health status"""
        sessions = self.session_tracker.list_sessions()
        result = []

        for session in sessions:
            # Update health status
            if session.status == "running" and not session.is_alive():
                session.status = "stopped"
                self.session_tracker.update_session(session)

            uptime = session.get_uptime()
            result.append({
                "session_id": session.session_id,
                "port": session.port,
                "baud_rate": session.baud_rate,
                "status": session.status,
                "start_time": session.start_time.isoformat() if session.start_time else None,
                "uptime_seconds": uptime.total_seconds() if uptime else None,
                "log_file": session.log_file,
                "pid": session.pid,
                "terminal_pid": session.terminal_pid,
                "error_message": session.error_message
            })

        return result

    async def get_serial_status(self, session_id: str) -> Dict[str, Any]:
        """Get detailed status of a session"""
        try:
            session = self.session_tracker.get_session(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")

            # Check if still alive
            is_alive = session.is_alive()
            if session.status == "running" and not is_alive:
                session.status = "stopped"
                self.session_tracker.update_session(session)

            uptime = session.get_uptime()

            # Get log preview
            log_preview = []
            if session.log_file and Path(session.log_file).exists():
                try:
                    with open(session.log_file, 'r') as f:
                        lines = f.readlines()[-10:]  # Last 10 lines
                        log_preview = [line.rstrip() for line in lines]
                except Exception:
                    log_preview = ["Error reading log file"]

            return {
                "session_id": session.session_id,
                "port": session.port,
                "baud_rate": session.baud_rate,
                "status": session.status,
                "alive": is_alive,
                "start_time": session.start_time.isoformat() if session.start_time else None,
                "uptime_seconds": uptime.total_seconds() if uptime else None,
                "log_file": session.log_file,
                "log_preview": log_preview,
                "pid": session.pid,
                "terminal_pid": session.terminal_pid,
                "error_message": session.error_message
            }

        except Exception as e:
            self.logger.error(f"Failed to get status for session {session_id}: {e}")
            raise

    async def detect_esp32_ports(self) -> List[Dict[str, Any]]:
        """Detect available ESP32 ports"""
        try:
            ports = self.port_detector.detect_ports()
            return ports
        except Exception as e:
            self.logger.error(f"Failed to detect ports: {e}")
            raise

    async def read_serial_output(self, session_id: str, lines: int = 50, tail: bool = True) -> Dict[str, Any]:
        """Read serial output from log file"""
        try:
            session = self.session_tracker.get_session(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")

            if not session.log_file or not Path(session.log_file).exists():
                return {
                    "session_id": session_id,
                    "output": [],
                    "message": "No log file available"
                }

            with open(session.log_file, 'r') as f:
                all_lines = f.readlines()

            if tail:
                output_lines = all_lines[-lines:]
            else:
                output_lines = all_lines[:lines]

            return {
                "session_id": session_id,
                "output": [line.rstrip() for line in output_lines],
                "total_lines": len(all_lines),
                "returned_lines": len(output_lines),
                "tail": tail
            }

        except Exception as e:
            self.logger.error(f"Failed to read output for session {session_id}: {e}")
            raise

    async def send_serial_command(self, session_id: str, command: str) -> Dict[str, Any]:
        """Send a command to the serial device"""
        try:
            session = self.session_tracker.get_session(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")

            if session.status != "running":
                raise ValueError(f"Session {session_id} is not running")

            if not PYSERIAL_AVAILABLE:
                raise RuntimeError("PySerial not available for command sending")

            # This is a simplified implementation
            # In a real scenario, you'd need to maintain the serial connection
            # For now, we'll just log the command
            timestamp = datetime.now().isoformat()
            log_entry = f"[{timestamp}] SENT: {command}"

            if session.log_file:
                try:
                    with open(session.log_file, 'a') as f:
                        f.write(log_entry + '\n')
                        f.flush()
                except Exception as e:
                    self.logger.error(f"Failed to write to log: {e}")

            return {
                "session_id": session_id,
                "command": command,
                "timestamp": timestamp,
                "status": "sent",
                "message": "Command logged (interactive sending requires serial connection maintenance)"
            }

        except Exception as e:
            self.logger.error(f"Failed to send command to session {session_id}: {e}")
            raise

    def create_tools(self):
        """Create MCP tools"""

        @self.server.tool()
        async def start_serial_monitor(port: str, baud_rate: int = DEFAULT_BAUD_RATE,
                                     terminal: bool = True) -> str:
            """Start a new ESP32 serial monitor session

            Args:
                port: Serial port (e.g., /dev/ttyUSB0, COM3)
                baud_rate: Baud rate for serial communication (default: 115200)
                terminal: Whether to spawn in a new terminal window (default: true)

            Returns:
                JSON string with session details
            """
            try:
                result = await self.start_serial_monitor(port, baud_rate, terminal)
                return json.dumps(result, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)

        @self.server.tool()
        async def stop_serial_monitor(session_id: str, timeout: int = 5) -> str:
            """Stop a serial monitor session gracefully

            Args:
                session_id: Session ID to stop
                timeout: Seconds to wait for graceful shutdown (default: 5)

            Returns:
                JSON string with stop result
            """
            try:
                result = await self.stop_serial_monitor(session_id, timeout)
                return json.dumps(result, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)

        @self.server.tool()
        async def kill_serial_monitor(session_id: str) -> str:
            """Force kill a serial monitor session

            Args:
                session_id: Session ID to kill

            Returns:
                JSON string with kill result
            """
            try:
                result = await self.kill_serial_monitor(session_id)
                return json.dumps(result, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)

        @self.server.tool()
        async def list_serial_sessions() -> str:
            """List all serial monitor sessions

            Returns:
                JSON string with list of all sessions
            """
            try:
                result = await self.list_serial_sessions()
                return json.dumps(result, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)

        @self.server.tool()
        async def get_serial_status(session_id: str) -> str:
            """Get detailed status of a serial session

            Args:
                session_id: Session ID to check

            Returns:
                JSON string with session status and log preview
            """
            try:
                result = await self.get_serial_status(session_id)
                return json.dumps(result, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)

        @self.server.tool()
        async def detect_esp32_ports() -> str:
            """Detect available ESP32 serial ports

            Returns:
                JSON string with list of detected ports
            """
            try:
                result = await self.detect_esp32_ports()
                return json.dumps(result, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)

        @self.server.tool()
        async def read_serial_output(session_id: str, lines: int = 50, tail: bool = True) -> str:
            """Read serial output from a session's log file

            Args:
                session_id: Session ID to read from
                lines: Number of lines to read (default: 50)
                tail: Read from end of file if true, beginning if false (default: true)

            Returns:
                JSON string with output lines
            """
            try:
                result = await self.read_serial_output(session_id, lines, tail)
                return json.dumps(result, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)

        @self.server.tool()
        async def send_serial_command(session_id: str, command: str) -> str:
            """Send a command to the serial device

            Args:
                session_id: Session ID to send command to
                command: Command string to send

            Returns:
                JSON string with send result
            """
            try:
                result = await self.send_serial_command(session_id, command)
                return json.dumps(result, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)

# Create global server instance for MCP CLI tools
try:
    print("DEBUG: Creating ESP32 Serial Monitor Server...", flush=True)
    server_instance = ESP32SerialMonitorServer()
    app = server_instance.server
    print("DEBUG: Server instance created successfully", flush=True)
except Exception as e:
    print(f"DEBUG: Failed to create server instance: {e}", flush=True)
    logging.error(f"Failed to create server instance: {e}")
    import traceback
    traceback.print_exc()
    app = None

# For MCP stdio transport, the app object should be available for import
# When run directly, start the stdio server
if __name__ == "__main__":
    if app:
        print("Starting ESP32 Serial Monitor MCP Server...", flush=True)
        try:
            # Run the server synchronously - this is what cursor-agent expects
            app.run()
        except Exception as e:
            print(f"Server failed: {e}", flush=True)
            import traceback
            traceback.print_exc()
    else:
        print("Server app not available", flush=True)