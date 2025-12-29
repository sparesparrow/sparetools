#!/usr/bin/env python3
"""
Conan & Cloudsmith MCP Server

A comprehensive MCP server for Conan package management and Cloudsmith integration,
providing tools for package creation, validation, upload, and remote management.
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
PACKAGE_BUILD_TIMEOUT_MINUTES = 30
UPLOAD_TIMEOUT_MINUTES = 15
SEARCH_TIMEOUT_SECONDS = 30

@dataclass
class ConanSession:
    """Represents a Conan package management session"""
    session_id: str
    session_type: str  # 'validate', 'create', 'upload', 'search', 'install', 'info', 'setup', 'cloudsmith_upload', 'list'
    package_name: Optional[str] = None
    package_version: Optional[str] = None
    remote_name: Optional[str] = None
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
    def from_dict(cls, data: Dict[str, Any]) -> 'ConanSession':
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
    """Thread-safe Conan session management with persistence"""

    def __init__(self, storage_path: str = "~/.mcp/conan_sessions.json"):
        self.storage_path = Path(storage_path).expanduser()
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._sessions: Dict[str, ConanSession] = {}
        self._lock = threading.RLock()
        self._load_sessions()

    def _load_sessions(self):
        """Load sessions from persistent storage"""
        try:
            if self.storage_path.exists():
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    for session_data in data.get('sessions', []):
                        session = ConanSession.from_dict(session_data)
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

    def create_session(self, session_type: str, package_name: Optional[str] = None,
                      package_version: Optional[str] = None, remote_name: Optional[str] = None) -> ConanSession:
        """Create a new session"""
        with self._lock:
            session_id = str(uuid.uuid4())
            session = ConanSession(
                session_id=session_id,
                session_type=session_type,
                package_name=package_name,
                package_version=package_version,
                remote_name=remote_name
            )
            self._sessions[session_id] = session
            self._save_sessions()
            return session

    def get_session(self, session_id: str) -> Optional[ConanSession]:
        """Get session by ID"""
        with self._lock:
            return self._sessions.get(session_id)

    def update_session(self, session: ConanSession):
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

    def list_sessions(self, session_type: Optional[str] = None) -> List[ConanSession]:
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

class ConanValidator:
    """Conan configuration and dependency validation"""

    def validate_conanfile(self, conanfile_path: str) -> Dict[str, Any]:
        """Validate conanfile.py syntax and dependencies"""
        try:
            conanfile_path = Path(conanfile_path).expanduser()
            if not conanfile_path.exists():
                raise ValueError(f"Conanfile not found: {conanfile_path}")

            # Basic syntax check by importing the file
            import importlib.util
            spec = importlib.util.spec_from_file_location("conanfile", conanfile_path)
            if spec is None or spec.loader is None:
                raise ValueError("Invalid Python file")

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Check for required Conan attributes
            conanfile_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if hasattr(attr, '__bases__') and any('ConanFile' in str(base) for base in attr.__bases__):
                    conanfile_class = attr
                    break

            if not conanfile_class:
                raise ValueError("No ConanFile class found in conanfile.py")

            # Check required attributes
            required_attrs = ['name', 'version']
            missing_attrs = []
            for attr in required_attrs:
                if not hasattr(conanfile_class, attr):
                    missing_attrs.append(attr)

            # Check for basic structure
            validation_result = {
                "valid": len(missing_attrs) == 0,
                "conanfile_path": str(conanfile_path),
                "has_conanfile_class": conanfile_class is not None,
                "missing_attributes": missing_attrs,
                "syntax_errors": []
            }

            if conanfile_class:
                # Check for optional but recommended attributes
                recommended_attrs = ['description', 'license', 'author', 'topics', 'homepage', 'url']
                present_recommended = []
                for attr in recommended_attrs:
                    if hasattr(conanfile_class, attr):
                        present_recommended.append(attr)

                validation_result["recommended_attributes"] = present_recommended

            return validation_result

        except Exception as e:
            return {
                "valid": False,
                "conanfile_path": str(conanfile_path),
                "error": str(e),
                "syntax_errors": [str(e)]
            }

class ConanManager:
    """Conan command execution and package management"""

    def __init__(self):
        self.conan_available = self._check_conan()

    def _check_conan(self) -> bool:
        """Check if Conan is available"""
        try:
            result = subprocess.run(
                ['conan', '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    async def run_conan_command(self, command: List[str], cwd: Optional[str] = None,
                               timeout: Optional[int] = None) -> Dict[str, Any]:
        """Run a Conan command asynchronously"""
        if not self.conan_available:
            raise RuntimeError("Conan is not installed or not available in PATH")

        try:
            process = await asyncio.create_subprocess_exec(
                'conan', *command,
                cwd=cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                raise RuntimeError(f"Command timed out after {timeout} seconds")

            stdout_str = stdout.decode('utf-8', errors='replace')
            stderr_str = stderr.decode('utf-8', errors='replace')

            return {
                "return_code": process.returncode,
                "stdout": stdout_str,
                "stderr": stderr_str,
                "success": process.returncode == 0
            }

        except Exception as e:
            raise RuntimeError(f"Failed to run Conan command: {e}")

class CloudsmithManager:
    """Cloudsmith remote management and package operations"""

    def __init__(self):
        self.api_url = "https://api.cloudsmith.io"
        # Will use environment variables for authentication
        self.api_key = os.getenv('CLOUDSMITH_API_KEY')
        self.org = os.getenv('CLOUDSMITH_ORG')

    def is_configured(self) -> bool:
        """Check if Cloudsmith is properly configured"""
        return bool(self.api_key and self.org)

    async def list_packages(self, repository: str) -> Dict[str, Any]:
        """List packages in a Cloudsmith repository"""
        if not self.is_configured():
            raise RuntimeError("Cloudsmith not configured. Set CLOUDSMITH_API_KEY and CLOUDSMITH_ORG environment variables")

        try:
            import aiohttp

            url = f"{self.api_url}/packages/{self.org}/{repository}/"
            headers = {
                'accept': 'application/json',
                'X-Api-Key': self.api_key
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        packages = await response.json()
                        return {
                            "success": True,
                            "packages": packages,
                            "count": len(packages)
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text}"
                        }

        except ImportError:
            return {
                "success": False,
                "error": "aiohttp not available. Install with: pip install aiohttp"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

class TerminalManager:
    """Cross-platform terminal management for Conan operations"""

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

    def spawn_terminal(self, command: str, title: str = "Conan Package Manager") -> Optional[int]:
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

    async def run_conan_async(self, session_id: str, conan_command: List[str],
                             cwd: Optional[str] = None, timeout: Optional[int] = None) -> Dict[str, Any]:
        """Run a Conan command asynchronously with progress tracking"""
        session = self.session_manager.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        try:
            session.status = "running"
            session.progress = "Starting Conan operation..."
            self.session_manager.update_session(session)

            conan_manager = ConanManager()
            result = await conan_manager.run_conan_command(conan_command, cwd, timeout)

            # Update progress based on output
            if "created package binary" in result["stdout"].lower():
                session.progress = "Package created successfully"
            elif "uploaded package" in result["stdout"].lower():
                session.progress = "Package uploaded successfully"
            elif "installed package" in result["stdout"].lower():
                session.progress = "Package installed successfully"
            elif result["return_code"] != 0:
                session.progress = f"Operation failed: {result['stderr'][:100]}..."

            # Update final status
            if result["success"]:
                session.status = "completed"
                session.progress = "Operation completed successfully"
            else:
                session.status = "failed"
                session.progress = f"Operation failed with code {result['return_code']}"
                session.error_message = result["stderr"][:500]  # First 500 chars of error

            self.session_manager.update_session(session)

            return result

        except Exception as e:
            session.status = "failed"
            session.error_message = str(e)
            self.session_manager.update_session(session)
            raise

class LogManager:
    """Log capture and management for Conan operations"""

    def __init__(self, log_dir: str = "~/conan_logs"):
        self.log_dir = Path(log_dir).expanduser()
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def create_log_file(self, session_id: str, operation: str) -> str:
        """Create a log file for the session"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.log_dir / f"conan_{operation}_{session_id}_{timestamp}.log"
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

class ConanCloudsmithServer:
    """Main MCP Server for Conan & Cloudsmith Package Management"""

    def __init__(self):
        if not MCP_AVAILABLE:
            raise ImportError("MCP package not available. Install with: pip install mcp")

        self.server = FastMCP("conan-cloudsmith")
        self.session_manager = SessionManager()
        self.conan_validator = ConanValidator()
        self.conan_manager = ConanManager()
        self.cloudsmith_manager = CloudsmithManager()
        self.terminal_manager = TerminalManager()
        self.async_executor = AsyncExecutor(self.session_manager)
        self.log_manager = LogManager()

        # Register MCP tools
        self.create_tools()

        # Setup logging
        log_level = os.getenv('CONAN_LOG_LEVEL', 'INFO').upper()
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    async def validate_conanfile(self, conanfile_path: str) -> Dict[str, Any]:
        """Validate conanfile.py syntax and dependencies"""
        try:
            # Create session
            session = self.session_manager.create_session("validate")
            log_file = self.log_manager.create_log_file(session.session_id, "validate")
            session.log_file = log_file

            # Perform validation
            validation_result = self.conan_validator.validate_conanfile(conanfile_path)

            # Log results
            self.log_manager.write_log(log_file, f"Validation result: {json.dumps(validation_result, indent=2)}")

            # Update session
            session.status = "completed" if validation_result.get("valid", False) else "failed"
            session.progress = "Validation completed"
            self.session_manager.update_session(session)

            return {
                "session_id": session.session_id,
                "status": session.status,
                "log_file": log_file,
                **validation_result
            }

        except Exception as e:
            self.logger.error(f"Failed to validate conanfile: {e}")
            raise

    async def create_conan_package(self, conanfile_path: str, terminal: bool = True) -> Dict[str, Any]:
        """Create Conan package from conanfile"""
        try:
            conanfile_path = Path(conanfile_path).expanduser()
            if not conanfile_path.exists():
                raise ValueError(f"Conanfile not found: {conanfile_path}")

            # Create session
            session = self.session_manager.create_session("create")
            log_file = self.log_manager.create_log_file(session.session_id, "create")
            session.log_file = log_file

            # Build create command
            create_command = ["create", str(conanfile_path.parent), "--build=missing"]

            if terminal:
                # Run in terminal
                cmd_str = f"cd '{conanfile_path.parent}' && conan {' '.join(create_command)}"
                try:
                    terminal_pid = self.terminal_manager.spawn_terminal(cmd_str, f"Conan Create Package")
                    session.pid = terminal_pid
                    session.status = "running"
                    self.session_manager.update_session(session)

                    return {
                        "session_id": session.session_id,
                        "status": "running",
                        "conanfile_path": str(conanfile_path),
                        "log_file": log_file,
                        "terminal": True,
                        "message": "Package creation started in terminal"
                    }
                except Exception as e:
                    session.status = "failed"
                    session.error_message = str(e)
                    self.session_manager.update_session(session)
                    raise
            else:
                # Run asynchronously
                timeout = PACKAGE_BUILD_TIMEOUT_MINUTES * 60
                result = await self.async_executor.run_conan_async(
                    session.session_id, create_command, cwd=str(conanfile_path.parent), timeout=timeout
                )

                return {
                    "session_id": session.session_id,
                    "status": session.status,
                    "conanfile_path": str(conanfile_path),
                    "log_file": log_file,
                    "terminal": False,
                    "success": result["success"],
                    "return_code": result["return_code"]
                }

        except Exception as e:
            self.logger.error(f"Failed to create Conan package: {e}")
            raise

    async def upload_conan_package(self, package_reference: str, remote_name: str = "conancenter",
                                  terminal: bool = False) -> Dict[str, Any]:
        """Upload package to Conan remote"""
        try:
            # Parse package reference (name/version@user/channel)
            parts = package_reference.split('@')
            if len(parts) != 2:
                raise ValueError("Invalid package reference format. Use: name/version@user/channel")

            package_name_version = parts[0]
            user_channel = parts[1]

            # Create session
            session = self.session_manager.create_session("upload", remote_name=remote_name)
            log_file = self.log_manager.create_log_file(session.session_id, "upload")
            session.log_file = log_file

            # Build upload command
            upload_command = ["upload", package_reference, "-r", remote_name, "--force"]

            if terminal:
                cmd_str = f"conan {' '.join(upload_command)}"
                terminal_pid = self.terminal_manager.spawn_terminal(cmd_str, f"Conan Upload - {package_reference}")
                session.pid = terminal_pid
                session.status = "running"
                self.session_manager.update_session(session)

                return {
                    "session_id": session.session_id,
                    "status": "running",
                    "package_reference": package_reference,
                    "remote_name": remote_name,
                    "log_file": log_file,
                    "terminal": True,
                    "message": "Upload started in terminal"
                }
            else:
                timeout = UPLOAD_TIMEOUT_MINUTES * 60
                result = await self.async_executor.run_conan_async(
                    session.session_id, upload_command, timeout=timeout
                )

                return {
                    "session_id": session.session_id,
                    "status": session.status,
                    "package_reference": package_reference,
                    "remote_name": remote_name,
                    "log_file": log_file,
                    "terminal": False,
                    "success": result["success"],
                    "return_code": result["return_code"]
                }

        except Exception as e:
            self.logger.error(f"Failed to upload Conan package: {e}")
            raise

    async def search_conan_packages(self, query: str, remote_name: str = "conancenter") -> Dict[str, Any]:
        """Search available Conan packages"""
        try:
            # Create session
            session = self.session_manager.create_session("search")
            log_file = self.log_manager.create_log_file(session.session_id, "search")
            session.log_file = log_file

            # Build search command
            search_command = ["search", query, "-r", remote_name]

            timeout = SEARCH_TIMEOUT_SECONDS
            result = await self.async_executor.run_conan_async(
                session.session_id, search_command, timeout=timeout
            )

            # Parse search results
            packages = []
            if result["success"]:
                lines = result["stdout"].strip().split('\n')
                for line in lines:
                    if line.strip() and not line.startswith('Existing'):
                        packages.append(line.strip())

            return {
                "session_id": session.session_id,
                "status": session.status,
                "query": query,
                "remote_name": remote_name,
                "log_file": log_file,
                "packages": packages,
                "count": len(packages),
                "success": result["success"]
            }

        except Exception as e:
            self.logger.error(f"Failed to search Conan packages: {e}")
            raise

    async def install_conan_dependencies(self, conanfile_path: str, install_folder: str = "build",
                                        terminal: bool = False) -> Dict[str, Any]:
        """Install dependencies from conanfile"""
        try:
            conanfile_path = Path(conanfile_path).expanduser()
            if not conanfile_path.exists():
                raise ValueError(f"Conanfile not found: {conanfile_path}")

            install_path = Path(install_folder).expanduser()
            install_path.mkdir(parents=True, exist_ok=True)

            # Create session
            session = self.session_manager.create_session("install")
            log_file = self.log_manager.create_log_file(session.session_id, "install")
            session.log_file = log_file

            # Build install command
            install_command = ["install", str(conanfile_path), "--build=missing", "-if", str(install_path)]

            if terminal:
                cmd_str = f"conan {' '.join(install_command)}"
                terminal_pid = self.terminal_manager.spawn_terminal(cmd_str, f"Conan Install - {conanfile_path.name}")
                session.pid = terminal_pid
                session.status = "running"
                self.session_manager.update_session(session)

                return {
                    "session_id": session.session_id,
                    "status": "running",
                    "conanfile_path": str(conanfile_path),
                    "install_folder": str(install_path),
                    "log_file": log_file,
                    "terminal": True,
                    "message": "Installation started in terminal"
                }
            else:
                result = await self.async_executor.run_conan_async(
                    session.session_id, install_command
                )

                return {
                    "session_id": session.session_id,
                    "status": session.status,
                    "conanfile_path": str(conanfile_path),
                    "install_folder": str(install_path),
                    "log_file": log_file,
                    "terminal": False,
                    "success": result["success"],
                    "return_code": result["return_code"]
                }

        except Exception as e:
            self.logger.error(f"Failed to install Conan dependencies: {e}")
            raise

    async def get_conan_info(self, package_reference: str, remote_name: str = "conancenter") -> Dict[str, Any]:
        """Get package information"""
        try:
            # Create session
            session = self.session_manager.create_session("info")
            log_file = self.log_manager.create_log_file(session.session_id, "info")
            session.log_file = log_file

            # Build info command
            info_command = ["info", package_reference, "-r", remote_name]

            result = await self.async_executor.run_conan_async(
                session.session_id, info_command
            )

            # Parse info output
            info_data = {}
            if result["success"]:
                # Basic parsing of conan info output
                lines = result["stdout"].strip().split('\n')
                current_section = None
                for line in lines:
                    line = line.strip()
                    if ':' in line and not line.startswith(' '):
                        key, value = line.split(':', 1)
                        info_data[key.strip()] = value.strip()
                        current_section = key.strip()

            return {
                "session_id": session.session_id,
                "status": session.status,
                "package_reference": package_reference,
                "remote_name": remote_name,
                "log_file": log_file,
                "info": info_data,
                "success": result["success"],
                "raw_output": result["stdout"]
            }

        except Exception as e:
            self.logger.error(f"Failed to get Conan package info: {e}")
            raise

    async def setup_cloudsmith_remote(self, remote_name: str, repository: str) -> Dict[str, Any]:
        """Configure Cloudsmith remote"""
        try:
            if not self.cloudsmith_manager.is_configured():
                raise RuntimeError("Cloudsmith not configured. Set CLOUDSMITH_API_KEY and CLOUDSMITH_ORG environment variables")

            # Create session
            session = self.session_manager.create_session("setup", remote_name=remote_name)
            log_file = self.log_manager.create_log_file(session.session_id, "setup")
            session.log_file = log_file

            # Build Cloudsmith remote URL
            cloudsmith_url = f"https://cloudsmith.io/~{self.cloudsmith_manager.org}/repos/{repository}/packages/"

            # Add remote command
            remote_command = ["remote", "add", remote_name, cloudsmith_url]

            result = await self.async_executor.run_conan_async(
                session.session_id, remote_command
            )

            return {
                "session_id": session.session_id,
                "status": session.status,
                "remote_name": remote_name,
                "repository": repository,
                "cloudsmith_url": cloudsmith_url,
                "log_file": log_file,
                "success": result["success"],
                "return_code": result["return_code"]
            }

        except Exception as e:
            self.logger.error(f"Failed to setup Cloudsmith remote: {e}")
            raise

    async def upload_to_cloudsmith(self, package_reference: str, remote_name: str) -> Dict[str, Any]:
        """Upload package to Cloudsmith"""
        try:
            # Create session
            session = self.session_manager.create_session("cloudsmith_upload", remote_name=remote_name)
            log_file = self.log_manager.create_log_file(session.session_id, "cloudsmith_upload")
            session.log_file = log_file

            # Use the same upload logic as regular Conan upload
            return await self.upload_conan_package(package_reference, remote_name, terminal=False)

        except Exception as e:
            self.logger.error(f"Failed to upload to Cloudsmith: {e}")
            raise

    async def list_cloudsmith_packages(self, repository: str) -> Dict[str, Any]:
        """List packages in Cloudsmith repository"""
        try:
            # Create session
            session = self.session_manager.create_session("list", remote_name=repository)
            log_file = self.log_manager.create_log_file(session.session_id, "list")
            session.log_file = log_file

            # Use Cloudsmith API
            result = await self.cloudsmith_manager.list_packages(repository)

            # Log results
            self.log_manager.write_log(log_file, f"Cloudsmith list result: {json.dumps(result, indent=2)}")

            # Update session
            session.status = "completed" if result.get("success", False) else "failed"
            session.progress = "Package listing completed"
            self.session_manager.update_session(session)

            return {
                "session_id": session.session_id,
                "status": session.status,
                "repository": repository,
                "log_file": log_file,
                **result
            }

        except Exception as e:
            self.logger.error(f"Failed to list Cloudsmith packages: {e}")
            raise

    def create_tools(self):
        """Create MCP tools"""

        @self.server.tool()
        async def validate_conanfile(conanfile_path: str) -> str:
            """Validate conanfile.py syntax and dependencies

            Args:
                conanfile_path: Path to conanfile.py

            Returns:
                JSON string with validation results
            """
            try:
                result = await self.validate_conanfile(conanfile_path)
                return json.dumps(result, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)

        @self.server.tool()
        async def create_conan_package(conanfile_path: str, terminal: bool = True) -> str:
            """Create Conan package from conanfile

            Args:
                conanfile_path: Path to conanfile.py
                terminal: Whether to run in terminal window (default: true)

            Returns:
                JSON string with package creation session details
            """
            try:
                result = await self.create_conan_package(conanfile_path, terminal)
                return json.dumps(result, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)

        @self.server.tool()
        async def upload_conan_package(package_reference: str, remote_name: str = "conancenter",
                                     terminal: bool = False) -> str:
            """Upload package to Conan remote

            Args:
                package_reference: Package reference (name/version@user/channel)
                remote_name: Remote name (default: conancenter)
                terminal: Whether to run in terminal window (default: false)

            Returns:
                JSON string with upload session details
            """
            try:
                result = await self.upload_conan_package(package_reference, remote_name, terminal)
                return json.dumps(result, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)

        @self.server.tool()
        async def search_conan_packages(query: str, remote_name: str = "conancenter") -> str:
            """Search available Conan packages

            Args:
                query: Search query (package name pattern)
                remote_name: Remote name (default: conancenter)

            Returns:
                JSON string with search results
            """
            try:
                result = await self.search_conan_packages(query, remote_name)
                return json.dumps(result, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)

        @self.server.tool()
        async def install_conan_dependencies(conanfile_path: str, install_folder: str = "build",
                                           terminal: bool = False) -> str:
            """Install dependencies from conanfile

            Args:
                conanfile_path: Path to conanfile.py
                install_folder: Installation folder (default: build)
                terminal: Whether to run in terminal window (default: false)

            Returns:
                JSON string with installation session details
            """
            try:
                result = await self.install_conan_dependencies(conanfile_path, install_folder, terminal)
                return json.dumps(result, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)

        @self.server.tool()
        async def conan_info(package_reference: str, remote_name: str = "conancenter") -> str:
            """Get package information

            Args:
                package_reference: Package reference (name/version@user/channel)
                remote_name: Remote name (default: conancenter)

            Returns:
                JSON string with package information
            """
            try:
                result = await self.get_conan_info(package_reference, remote_name)
                return json.dumps(result, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)

        @self.server.tool()
        async def setup_cloudsmith_remote(remote_name: str, repository: str) -> str:
            """Configure Cloudsmith remote

            Args:
                remote_name: Name for the remote
                repository: Cloudsmith repository name

            Returns:
                JSON string with remote setup result
            """
            try:
                result = await self.setup_cloudsmith_remote(remote_name, repository)
                return json.dumps(result, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)

        @self.server.tool()
        async def upload_to_cloudsmith(package_reference: str, remote_name: str) -> str:
            """Upload package to Cloudsmith

            Args:
                package_reference: Package reference (name/version@user/channel)
                remote_name: Cloudsmith remote name

            Returns:
                JSON string with upload result
            """
            try:
                result = await self.upload_to_cloudsmith(package_reference, remote_name)
                return json.dumps(result, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)

        @self.server.tool()
        async def list_cloudsmith_packages(repository: str) -> str:
            """List packages in Cloudsmith repository

            Args:
                repository: Cloudsmith repository name

            Returns:
                JSON string with package list
            """
            try:
                result = await self.list_cloudsmith_packages(repository)
                return json.dumps(result, indent=2)
            except Exception as e:
                return json.dumps({"error": str(e)}, indent=2)

# Create global server instance for MCP CLI tools
try:
    print("DEBUG: Creating Conan & Cloudsmith Server...", flush=True)
    server_instance = ConanCloudsmithServer()
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
        print("Starting Conan & Cloudsmith MCP Server...", flush=True)
        try:
            # Run the server using stdio transport for MCP
            asyncio.run(app.run_stdio_async())
        except Exception as e:
            print(f"Server failed: {e}", flush=True)
            import traceback
            traceback.print_exc()
    else:
        print("Server app not available", flush=True)