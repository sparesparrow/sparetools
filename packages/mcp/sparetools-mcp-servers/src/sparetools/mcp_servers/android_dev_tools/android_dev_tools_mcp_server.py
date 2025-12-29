#!/usr/bin/env python3
"""
Android Development Tools MCP Server

A comprehensive MCP server for Android development workflow with:
- APK build operations with progress monitoring
- Device management and deployment
- Testing framework integration
- Log capture and filtering
- Session-based operation tracking
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
    from mcp.server import FastMCP
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

# Configuration
SESSION_TIMEOUT_MINUTES = 60
BUILD_TIMEOUT_MINUTES = 30
TEST_TIMEOUT_MINUTES = 15
DEPLOY_TIMEOUT_MINUTES = 5
LOG_MAX_LINES = 1000

@dataclass
class AndroidSession:
    """Represents an Android development session"""
    session_id: str
    session_type: str  # 'build', 'deploy', 'test', 'logcat'
    device_id: Optional[str] = None
    package_name: Optional[str] = None
    start_time: datetime = None
    status: str = "created"  # created, running, completed, failed, stopped
    pid: Optional[int] = None
    log_file: Optional[str] = None
    error_message: Optional[str] = None
    progress: Optional[str] = None

    def __post_init__(self):
        if self.start_time is None:
            self.start_time = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['start_time'] = self.start_time.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AndroidSession':
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

class SessionManager:
    """Thread-safe Android session management with persistence"""

    def __init__(self, storage_path: str = "~/.mcp/android_sessions.json"):
        self.storage_path = Path(storage_path).expanduser()
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._sessions: Dict[str, AndroidSession] = {}
        self._lock = threading.RLock()
        self._load_sessions()

    def _load_sessions(self):
        """Load sessions from persistent storage"""
        try:
            if self.storage_path.exists():
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    for session_data in data.get('sessions', []):
                        session = AndroidSession.from_dict(session_data)
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

    def create_session(self, session_type: str, device_id: Optional[str] = None,
                      package_name: Optional[str] = None) -> AndroidSession:
        """Create a new session"""
        with self._lock:
            session_id = str(uuid.uuid4())
            session = AndroidSession(
                session_id=session_id,
                session_type=session_type,
                device_id=device_id,
                package_name=package_name
            )
            self._sessions[session_id] = session
            self._save_sessions()
            return session

    def get_session(self, session_id: str) -> Optional[AndroidSession]:
        """Get session by ID"""
        with self._lock:
            return self._sessions.get(session_id)

    def update_session(self, session: AndroidSession):
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

    def list_sessions(self, session_type: Optional[str] = None) -> List[AndroidSession]:
        """List all sessions, optionally filtered by type"""
        with self._lock:
            # Clean up stale sessions
            for session in list(self._sessions.values()):
                if not session.is_alive() and session.status == "running":
                    session.status = "stopped"
                    self.update_session(session)

            if session_type:
                return [s for s in self._sessions.values() if s.session_type == session_type]
            return list(self._sessions.values())

    def cleanup_stale_sessions(self):
        """Remove sessions older than timeout"""
        with self._lock:
            cutoff = datetime.now() - timedelta(minutes=SESSION_TIMEOUT_MINUTES)
            to_remove = []
            for session in self._sessions.values():
                if session.start_time < cutoff and session.status in ["completed", "failed", "stopped"]:
                    to_remove.append(session.session_id)
            for session_id in to_remove:
                del self._sessions[session_id]
            if to_remove:
                self._save_sessions()

class DeviceDetector:
    """Android device detection and management"""

    def detect_devices(self) -> List[Dict[str, Any]]:
        """Detect connected Android devices"""
        try:
            result = subprocess.run(
                ['adb', 'devices', '-l'],
                capture_output=True,
                text=True,
                timeout=10
            )

            devices = []
            lines = result.stdout.strip().split('\n')[1:]  # Skip header

            for line in lines:
                if line.strip() and not line.startswith('*') and not line.startswith('List'):
                    parts = line.split()
                    if len(parts) >= 2:
                        device_id = parts[0]
                        status = parts[1]

                        # Parse additional info
                        device_info = {
                            'id': device_id,
                            'status': status,
                            'model': 'Unknown',
                            'manufacturer': 'Unknown',
                            'android_version': 'Unknown'
                        }

                        # Get device properties
                        try:
                            model_result = subprocess.run(
                                ['adb', '-s', device_id, 'shell', 'getprop', 'ro.product.model'],
                                capture_output=True,
                                text=True,
                                timeout=5
                            )
                            if model_result.returncode == 0:
                                device_info['model'] = model_result.stdout.strip()

                            manufacturer_result = subprocess.run(
                                ['adb', '-s', device_id, 'shell', 'getprop', 'ro.product.manufacturer'],
                                capture_output=True,
                                text=True,
                                timeout=5
                            )
                            if manufacturer_result.returncode == 0:
                                device_info['manufacturer'] = manufacturer_result.stdout.strip()

                            version_result = subprocess.run(
                                ['adb', '-s', device_id, 'shell', 'getprop', 'ro.build.version.release'],
                                capture_output=True,
                                text=True,
                                timeout=5
                            )
                            if version_result.returncode == 0:
                                device_info['android_version'] = version_result.stdout.strip()

                        except subprocess.TimeoutExpired:
                            pass

                        devices.append(device_info)

            return devices

        except (subprocess.TimeoutExpired, FileNotFoundError):
            return []

class TerminalManager:
    """Cross-platform terminal management for Android operations"""

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

    def spawn_terminal(self, command: str, title: str = "Android Dev Tools") -> Optional[int]:
        """Spawn a terminal with the given command"""
        if not self.available_terminals:
            raise RuntimeError("No terminal emulator found. Please install gnome-terminal, xterm, konsole, kitty, or alacritty.")

        terminal = self.available_terminals[0]  # Use first available
        cmd_template = self.TERMINAL_COMMANDS[terminal]

        # Build full command
        if terminal == 'gnome-terminal':
            full_cmd = cmd_template + [f'echo "Starting {title}..."; {command}; echo "Press Enter to exit."; read']
        elif terminal in ['xterm', 'konsole', 'alacritty']:
            full_cmd = cmd_template + [f'bash -c "echo \\"Starting {title}\\"; {command}; echo \\"Press Enter to exit.\\"; read"']
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

class AsyncExecutor:
    """Asynchronous operation executor with progress tracking"""

    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager

    async def run_command_async(self, session_id: str, command: List[str],
                               cwd: Optional[str] = None, timeout: Optional[int] = None) -> Dict[str, Any]:
        """Run a command asynchronously with progress tracking"""
        session = self.session_manager.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        try:
            session.status = "running"
            session.progress = "Starting..."
            self.session_manager.update_session(session)

            process = await asyncio.create_subprocess_exec(
                *command,
                cwd=cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            session.pid = process.pid
            self.session_manager.update_session(session)

            # Read output with progress updates
            stdout_lines = []
            stderr_lines = []

            async def read_stream(stream, lines_list, is_stderr=False):
                while True:
                    line = await stream.readline()
                    if not line:
                        break
                    line_str = line.decode('utf-8', errors='replace').rstrip()
                    lines_list.append(line_str)

                    # Update progress based on output
                    if "BUILD SUCCESSFUL" in line_str:
                        session.progress = "Build completed successfully"
                    elif "BUILD FAILED" in line_str:
                        session.progress = "Build failed"
                    elif "Installing APK" in line_str:
                        session.progress = "Installing APK..."
                    elif "Success" in line_str.lower():
                        session.progress = "Operation completed"
                    elif "error" in line_str.lower():
                        session.progress = f"Error: {line_str[:50]}..."

                    self.session_manager.update_session(session)

            await asyncio.gather(
                read_stream(process.stdout, stdout_lines),
                read_stream(process.stderr, stderr_lines, is_stderr=True)
            )

            return_code = await process.wait()

            # Update final status
            if return_code == 0:
                session.status = "completed"
                session.progress = "Operation completed successfully"
            else:
                session.status = "failed"
                session.progress = f"Operation failed with code {return_code}"
                session.error_message = '\n'.join(stderr_lines[-5:])  # Last 5 error lines

            self.session_manager.update_session(session)

            return {
                "return_code": return_code,
                "stdout": stdout_lines,
                "stderr": stderr_lines,
                "success": return_code == 0
            }

        except Exception as e:
            session.status = "failed"
            session.error_message = str(e)
            self.session_manager.update_session(session)
            raise

class LogManager:
    """Log capture and management for Android operations"""

    def __init__(self, log_dir: str = "~/android_logs"):
        self.log_dir = Path(log_dir).expanduser()
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def create_log_file(self, session_id: str, operation: str) -> str:
        """Create a log file for the session"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.log_dir / f"android_{operation}_{session_id}_{timestamp}.log"
        return str(log_file)

    def write_log(self, log_file: str, message: str):
        """Write a message to the log file"""
        try:
            with open(log_file, 'a') as f:
                timestamp = datetime.now().isoformat()
                f.write(f"[{timestamp}] {message}\n")
                f.flush()
        except Exception as e:
            logging.error(f"Failed to write to log file {log_file}: {e}")

    def read_log_tail(self, log_file: str, lines: int = 50) -> List[str]:
        """Read the last N lines from a log file"""
        try:
            if not Path(log_file).exists():
                return []

            with open(log_file, 'r') as f:
                all_lines = f.readlines()
                return [line.rstrip() for line in all_lines[-lines:]]
        except Exception as e:
            logging.error(f"Failed to read log file {log_file}: {e}")
            return []

class AndroidDevToolsServer:
    """Main MCP Server for Android Development Tools"""

    def __init__(self):
        if not MCP_AVAILABLE:
            raise ImportError("MCP package not available. Install with: pip install mcp")

        self.server = FastMCP("android-dev-tools")
        self.session_manager = SessionManager()
        self.device_detector = DeviceDetector()
        self.terminal_manager = TerminalManager()
        self.async_executor = AsyncExecutor(self.session_manager)
        self.log_manager = LogManager()

        # Register MCP tools
        self.create_tools()

        # Setup logging
        log_level = os.getenv('ANDROID_LOG_LEVEL', 'INFO').upper()
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    async def build_android_apk(self, project_path: str, build_type: str = "debug",
                               terminal: bool = True) -> Dict[str, Any]:
        """Build Android APK with Gradle"""
        try:
            project_path = Path(project_path).expanduser()
            if not project_path.exists():
                raise ValueError(f"Project path does not exist: {project_path}")

            # Create session
            session = self.session_manager.create_session("build")
            log_file = self.log_manager.create_log_file(session.session_id, "build")
            session.log_file = log_file
            self.session_manager.update_session(session)

            # Build command
            gradlew_path = project_path / "gradlew"
            if not gradlew_path.exists():
                raise ValueError(f"Gradle wrapper not found at: {gradlew_path}")

            build_command = [str(gradlew_path), "assembleDebug" if build_type == "debug" else "assembleRelease"]

            if terminal:
                # Run in terminal
                cmd_str = f"cd '{project_path}' && {' '.join(build_command)}"
                try:
                    terminal_pid = self.terminal_manager.spawn_terminal(cmd_str, f"Android Build - {build_type}")
                    session.pid = terminal_pid
                    session.status = "running"
                    self.session_manager.update_session(session)

                    return {
                        "session_id": session.session_id,
                        "status": "running",
                        "build_type": build_type,
                        "project_path": str(project_path),
                        "log_file": log_file,
                        "terminal": True,
                        "message": "Build started in terminal"
                    }
                except Exception as e:
                    session.status = "failed"
                    session.error_message = str(e)
                    self.session_manager.update_session(session)
                    raise
            else:
                # Run asynchronously
                result = await self.async_executor.run_command_async(
                    session.session_id, build_command, cwd=str(project_path)
                )

                return {
                    "session_id": session.session_id,
                    "status": session.status,
                    "build_type": build_type,
                    "project_path": str(project_path),
                    "log_file": log_file,
                    "terminal": False,
                    "success": result["success"],
                    "return_code": result["return_code"],
                    "output_lines": len(result["stdout"]) + len(result["stderr"])
                }

        except Exception as e:
            self.logger.error(f"Failed to build APK: {e}")
            raise

    async def deploy_android_apk(self, apk_path: str, device_id: Optional[str] = None,
                                terminal: bool = False) -> Dict[str, Any]:
        """Deploy APK to Android device"""
        try:
            apk_path = Path(apk_path).expanduser()
            if not apk_path.exists():
                raise ValueError(f"APK file does not exist: {apk_path}")

            # Detect devices if not specified
            devices = self.device_detector.detect_devices()
            if not devices:
                raise RuntimeError("No Android devices connected")

            if not device_id:
                device_id = devices[0]['id']

            # Validate device
            device_exists = any(d['id'] == device_id for d in devices)
            if not device_exists:
                raise ValueError(f"Device {device_id} not found")

            # Create session
            session = self.session_manager.create_session("deploy", device_id=device_id)
            log_file = self.log_manager.create_log_file(session.session_id, "deploy")
            session.log_file = log_file

            # Deploy command
            deploy_command = ["adb", "-s", device_id, "install", "-r", str(apk_path)]

            if terminal:
                cmd_str = " ".join(deploy_command)
                terminal_pid = self.terminal_manager.spawn_terminal(cmd_str, f"Android Deploy - {device_id}")
                session.pid = terminal_pid
                session.status = "running"
                self.session_manager.update_session(session)

                return {
                    "session_id": session.session_id,
                    "status": "running",
                    "device_id": device_id,
                    "apk_path": str(apk_path),
                    "log_file": log_file,
                    "terminal": True,
                    "message": "Deployment started in terminal"
                }
            else:
                result = await self.async_executor.run_command_async(session.session_id, deploy_command)

                return {
                    "session_id": session.session_id,
                    "status": session.status,
                    "device_id": device_id,
                    "apk_path": str(apk_path),
                    "log_file": log_file,
                    "terminal": False,
                    "success": result["success"],
                    "return_code": result["return_code"]
                }

        except Exception as e:
            self.logger.error(f"Failed to deploy APK: {e}")
            raise

    async def run_android_tests(self, project_path: str, test_type: str = "unit",
                               device_id: Optional[str] = None, terminal: bool = True) -> Dict[str, Any]:
        """Execute Android unit and instrumentation tests"""
        try:
            project_path = Path(project_path).expanduser()
            if not project_path.exists():
                raise ValueError(f"Project path does not exist: {project_path}")

            # Create session
            session = self.session_manager.create_session("test", device_id=device_id)
            log_file = self.log_manager.create_log_file(session.session_id, "test")
            session.log_file = log_file

            gradlew_path = project_path / "gradlew"
            if not gradlew_path.exists():
                raise ValueError(f"Gradle wrapper not found at: {gradlew_path}")

            # Build test command based on type
            if test_type == "unit":
                test_command = [str(gradlew_path), "testDebugUnitTest"]
            elif test_type == "instrumented":
                if not device_id:
                    devices = self.device_detector.detect_devices()
                    if not devices:
                        raise RuntimeError("No Android devices connected for instrumented tests")
                    device_id = devices[0]['id']
                test_command = [str(gradlew_path), "connectedDebugAndroidTest"]
            else:
                raise ValueError(f"Unknown test type: {test_type}")

            if terminal:
                cmd_str = f"cd '{project_path}' && {' '.join(test_command)}"
                terminal_pid = self.terminal_manager.spawn_terminal(cmd_str, f"Android Tests - {test_type}")
                session.pid = terminal_pid
                session.status = "running"
                self.session_manager.update_session(session)

                return {
                    "session_id": session.session_id,
                    "status": "running",
                    "test_type": test_type,
                    "device_id": device_id,
                    "project_path": str(project_path),
                    "log_file": log_file,
                    "terminal": True,
                    "message": "Tests started in terminal"
                }
            else:
                timeout = TEST_TIMEOUT_MINUTES * 60
                result = await self.async_executor.run_command_async(
                    session.session_id, test_command, cwd=str(project_path), timeout=timeout
                )

                return {
                    "session_id": session.session_id,
                    "status": session.status,
                    "test_type": test_type,
                    "device_id": device_id,
                    "project_path": str(project_path),
                    "log_file": log_file,
                    "terminal": False,
                    "success": result["success"],
                    "return_code": result["return_code"]
                }

        except Exception as e:
            self.logger.error(f"Failed to run tests: {e}")
            raise

    async def get_android_device_info(self) -> List[Dict[str, Any]]:
        """Get connected Android device information"""
        try:
            devices = self.device_detector.detect_devices()
            return devices
        except Exception as e:
            self.logger.error(f"Failed to get device info: {e}")
            raise

    async def start_android_logcat(self, device_id: Optional[str] = None,
                                  filter_spec: Optional[str] = None,
                                  terminal: bool = True) -> Dict[str, Any]:
        """Start Android logcat monitoring"""
        try:
            # Detect devices if not specified
            devices = self.device_detector.detect_devices()
            if not devices:
                raise RuntimeError("No Android devices connected")

            if not device_id:
                device_id = devices[0]['id']

            # Validate device
            device_exists = any(d['id'] == device_id for d in devices)
            if not device_exists:
                raise ValueError(f"Device {device_id} not found")

            # Create session
            session = self.session_manager.create_session("logcat", device_id=device_id)
            log_file = self.log_manager.create_log_file(session.session_id, "logcat")
            session.log_file = log_file

            # Build logcat command
            logcat_command = ["adb", "-s", device_id, "logcat"]
            if filter_spec:
                logcat_command.extend(filter_spec.split())

            if terminal:
                cmd_str = " ".join(logcat_command)
                terminal_pid = self.terminal_manager.spawn_terminal(cmd_str, f"Android Logcat - {device_id}")
                session.pid = terminal_pid
                session.status = "running"
                self.session_manager.update_session(session)

                return {
                    "session_id": session.session_id,
                    "status": "running",
                    "device_id": device_id,
                    "filter_spec": filter_spec,
                    "log_file": log_file,
                    "terminal": True,
                    "message": "Logcat started in terminal"
                }
            else:
                # For non-terminal mode, we'll run a background process that logs to file
                logcat_command.extend([">>", log_file, "2>&1"])

                process = await asyncio.create_subprocess_shell(
                    " ".join(logcat_command),
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL
                )

                session.pid = process.pid
                session.status = "running"
                self.session_manager.update_session(session)

                return {
                    "session_id": session.session_id,
                    "status": "running",
                    "device_id": device_id,
                    "filter_spec": filter_spec,
                    "log_file": log_file,
                    "terminal": False,
                    "message": "Logcat started in background"
                }

        except Exception as e:
            self.logger.error(f"Failed to start logcat: {e}")
            raise

    async def clear_android_data(self, package_name: str, device_id: Optional[str] = None) -> Dict[str, Any]:
        """Clear app data on Android device"""
        try:
            # Detect devices if not specified
            devices = self.device_detector.detect_devices()
            if not devices:
                raise RuntimeError("No Android devices connected")

            if not device_id:
                device_id = devices[0]['id']

            # Validate device
            device_exists = any(d['id'] == device_id for d in devices)
            if not device_exists:
                raise ValueError(f"Device {device_id} not found")

            # Create session
            session = self.session_manager.create_session("clear_data", device_id=device_id, package_name=package_name)
            log_file = self.log_manager.create_log_file(session.session_id, "clear_data")
            session.log_file = log_file

            # Clear data command
            clear_command = ["adb", "-s", device_id, "shell", "pm", "clear", package_name]

            result = await self.async_executor.run_command_async(session.session_id, clear_command)

            return {
                "session_id": session.session_id,
                "status": session.status,
                "device_id": device_id,
                "package_name": package_name,
                "log_file": log_file,
                "success": result["success"],
                "return_code": result["return_code"]
            }

        except Exception as e:
            self.logger.error(f"Failed to clear app data: {e}")
            raise

    async def uninstall_android_app(self, package_name: str, device_id: Optional[str] = None) -> Dict[str, Any]:
        """Uninstall app from Android device"""
        try:
            # Detect devices if not specified
            devices = self.device_detector.detect_devices()
            if not devices:
                raise RuntimeError("No Android devices connected")

            if not device_id:
                device_id = devices[0]['id']

            # Validate device
            device_exists = any(d['id'] == device_id for d in devices)
            if not device_exists:
                raise ValueError(f"Device {device_id} not found")

            # Create session
            session = self.session_manager.create_session("uninstall", device_id=device_id, package_name=package_name)
            log_file = self.log_manager.create_log_file(session.session_id, "uninstall")
            session.log_file = log_file

            # Uninstall command
            uninstall_command = ["adb", "-s", device_id, "uninstall", package_name]

            result = await self.async_executor.run_command_async(session.session_id, uninstall_command)

            return {
                "session_id": session.session_id,
                "status": session.status,
                "device_id": device_id,
                "package_name": package_name,
                "log_file": log_file,
                "success": result["success"],
                "return_code": result["return_code"]
            }

        except Exception as e:
            self.logger.error(f"Failed to uninstall app: {e}")
            raise

    def create_tools(self):
        """Create MCP tools"""

        @self.server.tool()
        async def build_android_apk(project_path: str, build_type: str = "debug",
                                   terminal: bool = True) -> str:
            """Build Android APK with Gradle

            Args:
                project_path: Path to Android project directory
                build_type: Build type - "debug" or "release" (default: debug)
                terminal: Whether to run in terminal window (default: true)

            Returns:
                JSON string with build session details
            """
            try:
                result = await self.build_android_apk(project_path, build_type, terminal)
                return json.dumps(result, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)

        @self.server.tool()
        async def deploy_android_apk(apk_path: str, device_id: str = "", terminal: bool = False) -> str:
            """Deploy APK to Android device using ADB

            Args:
                apk_path: Path to APK file
                device_id: Target device ID (optional, uses first device if not specified)
                terminal: Whether to run in terminal window (default: false)

            Returns:
                JSON string with deployment session details
            """
            try:
                device_id = device_id if device_id else None
                result = await self.deploy_android_apk(apk_path, device_id, terminal)
                return json.dumps(result, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)

        @self.server.tool()
        async def run_android_tests(project_path: str, test_type: str = "unit",
                                   device_id: str = "", terminal: bool = True) -> str:
            """Execute Android unit and instrumentation tests

            Args:
                project_path: Path to Android project directory
                test_type: Test type - "unit" or "instrumented" (default: unit)
                device_id: Target device ID for instrumented tests (optional)
                terminal: Whether to run in terminal window (default: true)

            Returns:
                JSON string with test session details
            """
            try:
                device_id = device_id if device_id else None
                result = await self.run_android_tests(project_path, test_type, device_id, terminal)
                return json.dumps(result, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)

        @self.server.tool()
        async def android_device_info() -> str:
            """Get connected Android device information

            Returns:
                JSON string with list of connected devices and their details
            """
            try:
                result = await self.get_android_device_info()
                return json.dumps(result, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)

        @self.server.tool()
        async def android_logcat(device_id: str = "", filter_spec: str = "",
                                terminal: bool = True) -> str:
            """Start/stop Android logcat monitoring

            Args:
                device_id: Target device ID (optional, uses first device if not specified)
                filter_spec: Logcat filter specification (optional)
                terminal: Whether to run in terminal window (default: true)

            Returns:
                JSON string with logcat session details
            """
            try:
                device_id = device_id if device_id else None
                filter_spec = filter_spec if filter_spec else None
                result = await self.start_android_logcat(device_id, filter_spec, terminal)
                return json.dumps(result, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)

        @self.server.tool()
        async def clear_android_data(package_name: str, device_id: str = "") -> str:
            """Clear app data on Android device

            Args:
                package_name: Android package name (e.g., com.example.app)
                device_id: Target device ID (optional, uses first device if not specified)

            Returns:
                JSON string with clear data operation result
            """
            try:
                device_id = device_id if device_id else None
                result = await self.clear_android_data(package_name, device_id)
                return json.dumps(result, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)

        @self.server.tool()
        async def uninstall_android_app(package_name: str, device_id: str = "") -> str:
            """Uninstall app from Android device

            Args:
                package_name: Android package name (e.g., com.example.app)
                device_id: Target device ID (optional, uses first device if not specified)

            Returns:
                JSON string with uninstall operation result
            """
            try:
                device_id = device_id if device_id else None
                result = await self.uninstall_android_app(package_name, device_id)
                return json.dumps(result, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)

# Create global server instance for MCP CLI tools
try:
    print("DEBUG: Creating Android Dev Tools Server...", flush=True)
    server_instance = AndroidDevToolsServer()
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
    import asyncio
    if app:
        print("Starting Android Dev Tools MCP Server...", flush=True)
        try:
            # Run the server using stdio transport for MCP
            asyncio.run(app.run_stdio_async())
        except Exception as e:
            print(f"Server failed: {e}", flush=True)
            import traceback
            traceback.print_exc()
    else:
        print("Server app not available", flush=True)