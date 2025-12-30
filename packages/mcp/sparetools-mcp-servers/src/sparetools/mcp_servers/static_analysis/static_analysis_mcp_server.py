#!/usr/bin/env python3
"""
Static Code Analysis MCP Server

A comprehensive MCP server for static code analysis tools with:
- Tool installation and management
- Analysis execution with progress tracking
- Result analysis and reporting
- Support for: cppcheck, valgrind, gdb, strace, uiautomator
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
import xml.etree.ElementTree as ET
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
SESSION_TIMEOUT_MINUTES = 120
ANALYSIS_TIMEOUT_MINUTES = 60
LOG_MAX_LINES = 5000

# Tool definitions
TOOLS = {
    "cppcheck": {
        "name": "cppcheck",
        "description": "Static analysis tool for C/C++ code",
        "install_command": {
            "linux": "sudo apt-get install -y cppcheck",
            "macos": "brew install cppcheck",
            "windows": "choco install cppcheck"
        },
        "check_command": "cppcheck --version",
        "default_args": ["--enable=all", "--xml", "--xml-version=2"]
    },
    "valgrind": {
        "name": "valgrind",
        "description": "Memory debugging and profiling tool",
        "install_command": {
            "linux": "sudo apt-get install -y valgrind",
            "macos": "brew install valgrind",
            "windows": None  # Not available on Windows
        },
        "check_command": "valgrind --version",
        "default_args": ["--leak-check=full", "--show-leak-kinds=all", "--track-origins=yes"]
    },
    "gdb": {
        "name": "gdb",
        "description": "GNU Debugger for debugging programs",
        "install_command": {
            "linux": "sudo apt-get install -y gdb",
            "macos": "brew install gdb",
            "windows": "choco install mingw"
        },
        "check_command": "gdb --version",
        "default_args": []
    },
    "strace": {
        "name": "strace",
        "description": "System call tracer for Linux",
        "install_command": {
            "linux": "sudo apt-get install -y strace",
            "macos": "brew install strace",  # Actually dtruss on macOS
            "windows": None  # Not available on Windows
        },
        "check_command": "strace --version",
        "default_args": ["-f", "-e", "trace=all"]
    },
    "uiautomator": {
        "name": "uiautomator",
        "description": "Android UI automation and testing tool",
        "install_command": {
            "linux": "pip install uiautomator2",
            "macos": "pip install uiautomator2",
            "windows": "pip install uiautomator2"
        },
        "check_command": "python -c 'import uiautomator2; print(uiautomator2.__version__)'",
        "default_args": []
    }
}

@dataclass
class AnalysisSession:
    """Represents a static analysis session"""
    session_id: str
    tool: str
    target_path: str
    command: str
    arguments: List[str]
    start_time: datetime = None
    status: str = "created"  # created, running, completed, failed, stopped
    pid: Optional[int] = None
    log_file: Optional[str] = None
    result_file: Optional[str] = None
    error_message: Optional[str] = None
    progress: Optional[str] = None
    exit_code: Optional[int] = None
    duration_seconds: Optional[float] = None

    def __post_init__(self):
        if self.start_time is None:
            self.start_time = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['start_time'] = self.start_time.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnalysisSession':
        """Create from dictionary"""
        data['start_time'] = datetime.fromisoformat(data['start_time'])
        return cls(**data)

    def is_alive(self) -> bool:
        """Check if session is still alive"""
        if self.pid and self.status == "running":
            try:
                os.kill(self.pid, 0)
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
    """Thread-safe analysis session management with persistence"""

    def __init__(self, storage_path: str = "~/.mcp/static_analysis_sessions.json"):
        self.storage_path = Path(storage_path).expanduser()
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._sessions: Dict[str, AnalysisSession] = {}
        self._lock = threading.RLock()
        self._load_sessions()

    def _load_sessions(self):
        """Load sessions from persistent storage"""
        try:
            if self.storage_path.exists():
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    for session_data in data.get('sessions', []):
                        session = AnalysisSession.from_dict(session_data)
                        # Only load active sessions
                        if session.is_alive() or session.status in ["created", "running"]:
                            self._sessions[session.session_id] = session
        except Exception as e:
            logging.warning(f"Failed to load sessions: {e}")

    def _save_sessions(self):
        """Save sessions to persistent storage"""
        try:
            with self._lock:
                data = {
                    'sessions': [session.to_dict() for session in self._sessions.values()],
                    'last_updated': datetime.now().isoformat()
                }
                with open(self.storage_path, 'w') as f:
                    json.dump(data, f, indent=2)
        except Exception as e:
            logging.warning(f"Failed to save sessions: {e}")

    def create_session(self, tool: str, target_path: str, arguments: List[str]) -> AnalysisSession:
        """Create a new analysis session"""
        session_id = str(uuid.uuid4())
        command = TOOLS[tool]["name"]
        
        session = AnalysisSession(
            session_id=session_id,
            tool=tool,
            target_path=target_path,
            command=command,
            arguments=arguments
        )
        
        with self._lock:
            self._sessions[session_id] = session
        self._save_sessions()
        return session

    def get_session(self, session_id: str) -> Optional[AnalysisSession]:
        """Get session by ID"""
        with self._lock:
            return self._sessions.get(session_id)

    def list_sessions(self) -> List[AnalysisSession]:
        """List all sessions"""
        with self._lock:
            return list(self._sessions.values())

    def update_session(self, session: AnalysisSession):
        """Update session"""
        with self._lock:
            self._sessions[session.session_id] = session
        self._save_sessions()

    def cleanup_old_sessions(self):
        """Remove old completed/failed sessions"""
        cutoff = datetime.now() - timedelta(minutes=SESSION_TIMEOUT_MINUTES)
        with self._lock:
            to_remove = [
                sid for sid, session in self._sessions.items()
                if session.status in ["completed", "failed", "stopped"] and
                session.start_time < cutoff
            ]
            for sid in to_remove:
                del self._sessions[sid]
        self._save_sessions()


def detect_platform() -> str:
    """Detect the current platform"""
    if sys.platform.startswith('linux'):
        return "linux"
    elif sys.platform == 'darwin':
        return "macos"
    elif sys.platform == 'win32':
        return "windows"
    return "unknown"


def check_tool_installed(tool: str) -> Tuple[bool, Optional[str]]:
    """Check if a tool is installed"""
    if tool not in TOOLS:
        return False, f"Unknown tool: {tool}"
    
    tool_info = TOOLS[tool]
    check_cmd = tool_info["check_command"]
    
    try:
        result = subprocess.run(
            check_cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            version = result.stdout.strip().split('\n')[0]
            return True, version
        return False, None
    except Exception as e:
        return False, str(e)


def install_tool(tool: str) -> Tuple[bool, str]:
    """Install a static analysis tool"""
    if tool not in TOOLS:
        return False, f"Unknown tool: {tool}"
    
    platform = detect_platform()
    tool_info = TOOLS[tool]
    install_cmd = tool_info["install_command"].get(platform)
    
    if not install_cmd:
        return False, f"Tool {tool} not available on {platform}"
    
    try:
        result = subprocess.run(
            install_cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=600  # 10 minutes for installation
        )
        if result.returncode == 0:
            return True, f"Successfully installed {tool}"
        return False, f"Installation failed: {result.stderr}"
    except subprocess.TimeoutExpired:
        return False, "Installation timed out"
    except Exception as e:
        return False, f"Installation error: {str(e)}"


def run_analysis(session: AnalysisSession, session_manager: SessionManager) -> None:
    """Run static analysis in background"""
    tool_info = TOOLS[session.tool]
    target_path = Path(session.target_path)
    
    # Create output directory
    output_dir = Path.home() / ".mcp" / "static_analysis" / session.session_id
    output_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = output_dir / "analysis.log"
    result_file = output_dir / "results.xml"
    
    session.log_file = str(log_file)
    session.result_file = str(result_file)
    session.status = "running"
    session_manager.update_session(session)
    
    # Build command
    cmd = [tool_info["name"]]
    cmd.extend(session.arguments)
    
    # Tool-specific command building
    if session.tool == "cppcheck":
        cmd.extend(["--xml", "--xml-version=2", f"--xml-output={result_file}"])
        cmd.append(str(target_path))
    elif session.tool == "valgrind":
        # Valgrind needs a program to run
        if target_path.is_file() and target_path.suffix in [".exe", ""]:
            cmd.extend([f"--log-file={result_file}", str(target_path)])
        else:
            session.status = "failed"
            session.error_message = "valgrind requires an executable file"
            session_manager.update_session(session)
            return
    elif session.tool == "gdb":
        # GDB needs special handling - create a script
        gdb_script = output_dir / "gdb_script.txt"
        with open(gdb_script, 'w') as f:
            f.write("run\nbt\ninfo registers\nquit\n")
        cmd.extend(["-batch", "-x", str(gdb_script), str(target_path)])
    elif session.tool == "strace":
        cmd.extend(["-o", str(result_file), str(target_path)])
    elif session.tool == "uiautomator":
        # uiautomator is Python-based
        cmd = ["python", "-m", "uiautomator2"] + session.arguments
    
    # Run analysis
    try:
        start_time = time.time()
        with open(log_file, 'w') as log:
            process = subprocess.Popen(
                cmd,
                stdout=log,
                stderr=subprocess.STDOUT,
                cwd=target_path.parent if target_path.is_file() else target_path,
                env=os.environ.copy()
            )
            session.pid = process.pid
            session_manager.update_session(session)
            
            # Wait for completion with timeout
            try:
                process.wait(timeout=ANALYSIS_TIMEOUT_MINUTES * 60)
                session.exit_code = process.returncode
                session.duration_seconds = time.time() - start_time
                
                if process.returncode == 0:
                    session.status = "completed"
                else:
                    session.status = "failed"
                    session.error_message = f"Analysis exited with code {process.returncode}"
            except subprocess.TimeoutExpired:
                process.kill()
                session.status = "failed"
                session.error_message = "Analysis timed out"
                session.duration_seconds = ANALYSIS_TIMEOUT_MINUTES * 60
    except Exception as e:
        session.status = "failed"
        session.error_message = str(e)
        session.duration_seconds = time.time() - start_time
    
    session_manager.update_session(session)


def analyze_cppcheck_results(result_file: Path) -> Dict[str, Any]:
    """Analyze cppcheck XML results"""
    try:
        tree = ET.parse(result_file)
        root = tree.getroot()
        
        errors = []
        warnings = []
        style = []
        performance = []
        portability = []
        information = []
        
        for error in root.findall('.//error'):
            severity = error.get('severity', 'unknown')
            msg = error.get('msg', '')
            file_path = error.get('file', '')
            line = error.get('line', '')
            
            issue = {
                "severity": severity,
                "message": msg,
                "file": file_path,
                "line": line
            }
            
            if severity == "error":
                errors.append(issue)
            elif severity == "warning":
                warnings.append(issue)
            elif severity == "style":
                style.append(issue)
            elif severity == "performance":
                performance.append(issue)
            elif severity == "portability":
                portability.append(issue)
            elif severity == "information":
                information.append(issue)
        
        return {
            "tool": "cppcheck",
            "total_issues": len(errors) + len(warnings) + len(style) + len(performance) + len(portability),
            "errors": len(errors),
            "warnings": len(warnings),
            "style": len(style),
            "performance": len(performance),
            "portability": len(portability),
            "information": len(information),
            "details": {
                "errors": errors[:100],  # Limit to first 100
                "warnings": warnings[:100],
                "style": style[:50],
                "performance": performance[:50],
                "portability": portability[:50]
            }
        }
    except Exception as e:
        return {"error": f"Failed to parse results: {str(e)}"}


def analyze_valgrind_results(result_file: Path) -> Dict[str, Any]:
    """Analyze valgrind results"""
    try:
        with open(result_file, 'r') as f:
            content = f.read()
        
        # Parse valgrind output
        leaks = re.findall(r'definitely lost: ([\d,]+) bytes', content)
        indirect_leaks = re.findall(r'indirectly lost: ([\d,]+) bytes', content)
        errors = re.findall(r'ERROR SUMMARY: ([\d]+) errors', content)
        
        return {
            "tool": "valgrind",
            "definitely_lost_bytes": int(leaks[0].replace(',', '')) if leaks else 0,
            "indirectly_lost_bytes": int(indirect_leaks[0].replace(',', '')) if indirect_leaks else 0,
            "error_count": int(errors[0]) if errors else 0,
            "summary": content[-2000:] if len(content) > 2000 else content  # Last 2000 chars
        }
    except Exception as e:
        return {"error": f"Failed to parse results: {str(e)}"}


def analyze_strace_results(result_file: Path) -> Dict[str, Any]:
    """Analyze strace results"""
    try:
        with open(result_file, 'r') as f:
            lines = f.readlines()
        
        syscalls = {}
        errors = []
        
        for line in lines:
            # Parse syscall patterns
            match = re.match(r'(\w+)\(', line)
            if match:
                syscall = match.group(1)
                syscalls[syscall] = syscalls.get(syscall, 0) + 1
            
            # Find errors
            if '= -1' in line or 'errno' in line.lower():
                errors.append(line.strip())
        
        return {
            "tool": "strace",
            "total_syscalls": sum(syscalls.values()),
            "unique_syscalls": len(syscalls),
            "top_syscalls": dict(sorted(syscalls.items(), key=lambda x: x[1], reverse=True)[:20]),
            "errors": errors[:50]
        }
    except Exception as e:
        return {"error": f"Failed to parse results: {str(e)}"}


def analyze_gdb_results(log_file: Path) -> Dict[str, Any]:
    """Analyze GDB results"""
    try:
        with open(log_file, 'r') as f:
            content = f.read()
        
        # Extract backtrace
        bt_match = re.search(r'#0\s+.*\n(?:#\d+\s+.*\n)*', content)
        backtrace = bt_match.group(0) if bt_match else ""
        
        # Extract signal
        signal_match = re.search(r'Program received signal (\w+)', content)
        signal = signal_match.group(1) if signal_match else None
        
        return {
            "tool": "gdb",
            "signal": signal,
            "backtrace": backtrace,
            "summary": content[-2000:] if len(content) > 2000 else content
        }
    except Exception as e:
        return {"error": f"Failed to parse results: {str(e)}"}


def analyze_results(session: AnalysisSession) -> Dict[str, Any]:
    """Analyze results based on tool type"""
    if not session.result_file:
        return {"error": "No result file available"}
    
    result_path = Path(session.result_file)
    if not result_path.exists():
        # Try log file
        if session.log_file and Path(session.log_file).exists():
            result_path = Path(session.log_file)
        else:
            return {"error": "Result file not found"}
    
    if session.tool == "cppcheck":
        return analyze_cppcheck_results(result_path)
    elif session.tool == "valgrind":
        return analyze_valgrind_results(result_path)
    elif session.tool == "strace":
        return analyze_strace_results(result_path)
    elif session.tool == "gdb":
        return analyze_gdb_results(result_path)
    elif session.tool == "uiautomator":
        # uiautomator results are typically JSON
        try:
            with open(result_path, 'r') as f:
                return {"tool": "uiautomator", "results": json.load(f)}
        except:
            return {"tool": "uiautomator", "raw": result_path.read_text()[:5000]}
    
    return {"error": f"Unknown tool: {session.tool}"}


def create_server():
    """Create and configure the MCP server"""
    if not MCP_AVAILABLE:
        raise ImportError("FastMCP is required. Install with: pip install mcp")
    
    mcp = FastMCP("Static Code Analysis Tools")
    session_manager = SessionManager()
    
    # Cleanup old sessions on startup
    session_manager.cleanup_old_sessions()
    
    @mcp.tool()
    def list_available_tools() -> str:
        """List all available static analysis tools"""
        tools_info = []
        for tool_name, tool_info in TOOLS.items():
            installed, version = check_tool_installed(tool_name)
            status = f"✅ Installed ({version})" if installed else "❌ Not installed"
            tools_info.append(f"- **{tool_name}**: {tool_info['description']} - {status}")
        return "\n".join(tools_info)
    
    @mcp.tool()
    def check_tool_status(tool: str) -> str:
        """Check if a specific tool is installed and get its version"""
        if tool not in TOOLS:
            return f"❌ Unknown tool: {tool}. Available tools: {', '.join(TOOLS.keys())}"
        
        installed, version = check_tool_installed(tool)
        if installed:
            return f"✅ {tool} is installed\nVersion: {version}"
        else:
            platform = detect_platform()
            install_cmd = TOOLS[tool]["install_command"].get(platform)
            if install_cmd:
                return f"❌ {tool} is not installed\nInstall with: {install_cmd}"
            else:
                return f"❌ {tool} is not installed\nNot available on {platform}"
    
    @mcp.tool()
    def install_analysis_tool(tool: str) -> str:
        """Install a static analysis tool"""
        if tool not in TOOLS:
            return f"❌ Unknown tool: {tool}. Available tools: {', '.join(TOOLS.keys())}"
        
        installed, _ = check_tool_installed(tool)
        if installed:
            return f"✅ {tool} is already installed"
        
        success, message = install_tool(tool)
        if success:
            return f"✅ {message}"
        else:
            return f"❌ {message}"
    
    @mcp.tool()
    def run_cppcheck(
        target_path: str,
        arguments: Optional[str] = None,
        enable_all: bool = True
    ) -> str:
        """Run cppcheck static analysis on C/C++ code
        
        Args:
            target_path: Path to source file or directory
            arguments: Additional cppcheck arguments (JSON array string)
            enable_all: Enable all checks (default: True)
        """
        args = []
        if enable_all:
            args.append("--enable=all")
        if arguments:
            try:
                args.extend(json.loads(arguments))
            except:
                args.extend(arguments.split())
        
        session = session_manager.create_session("cppcheck", target_path, args)
        
        # Run in background thread
        thread = threading.Thread(
            target=run_analysis,
            args=(session, session_manager),
            daemon=True
        )
        thread.start()
        
        return json.dumps({
            "session_id": session.session_id,
            "tool": "cppcheck",
            "target": target_path,
            "status": "started",
            "message": f"cppcheck analysis started. Check progress with get_analysis_progress"
        }, indent=2)
    
    @mcp.tool()
    def run_valgrind(
        executable_path: str,
        arguments: Optional[str] = None,
        leak_check: bool = True
    ) -> str:
        """Run valgrind memory analysis on an executable
        
        Args:
            executable_path: Path to executable file
            arguments: Program arguments to pass to executable
            leak_check: Enable full leak checking (default: True)
        """
        args = []
        if leak_check:
            args.extend(["--leak-check=full", "--show-leak-kinds=all"])
        if arguments:
            args.extend(arguments.split())
        
        session = session_manager.create_session("valgrind", executable_path, args)
        
        thread = threading.Thread(
            target=run_analysis,
            args=(session, session_manager),
            daemon=True
        )
        thread.start()
        
        return json.dumps({
            "session_id": session.session_id,
            "tool": "valgrind",
            "target": executable_path,
            "status": "started",
            "message": f"valgrind analysis started. Check progress with get_analysis_progress"
        }, indent=2)
    
    @mcp.tool()
    def run_gdb(
        executable_path: str,
        gdb_commands: Optional[str] = None
    ) -> str:
        """Run GDB debugger on an executable
        
        Args:
            executable_path: Path to executable file
            gdb_commands: GDB commands to execute (default: run, bt, quit)
        """
        args = []
        if gdb_commands:
            args.extend(["-ex", gdb_commands])
        
        session = session_manager.create_session("gdb", executable_path, args)
        
        thread = threading.Thread(
            target=run_analysis,
            args=(session, session_manager),
            daemon=True
        )
        thread.start()
        
        return json.dumps({
            "session_id": session.session_id,
            "tool": "gdb",
            "target": executable_path,
            "status": "started",
            "message": f"GDB session started. Check progress with get_analysis_progress"
        }, indent=2)
    
    @mcp.tool()
    def run_strace(
        command: str,
        trace_syscalls: Optional[str] = None
    ) -> str:
        """Run strace system call tracer
        
        Args:
            command: Command to trace (e.g., "./myapp arg1")
            trace_syscalls: Specific syscalls to trace (default: all)
        """
        args = ["-f"]  # Follow forks
        if trace_syscalls:
            args.extend(["-e", f"trace={trace_syscalls}"])
        else:
            args.extend(["-e", "trace=all"])
        
        session = session_manager.create_session("strace", command, args)
        
        thread = threading.Thread(
            target=run_analysis,
            args=(session, session_manager),
            daemon=True
        )
        thread.start()
        
        return json.dumps({
            "session_id": session.session_id,
            "tool": "strace",
            "target": command,
            "status": "started",
            "message": f"strace started. Check progress with get_analysis_progress"
        }, indent=2)
    
    @mcp.tool()
    def run_uiautomator(
        device_id: str,
        action: str,
        arguments: Optional[str] = None
    ) -> str:
        """Run uiautomator Android UI automation
        
        Args:
            device_id: Android device ID or serial
            action: Action to perform (dump, click, text, etc.)
            arguments: Additional arguments (JSON string)
        """
        args = [device_id, action]
        if arguments:
            try:
                args.extend(json.loads(arguments))
            except:
                args.extend(arguments.split())
        
        session = session_manager.create_session("uiautomator", device_id, args)
        
        thread = threading.Thread(
            target=run_analysis,
            args=(session, session_manager),
            daemon=True
        )
        thread.start()
        
        return json.dumps({
            "session_id": session.session_id,
            "tool": "uiautomator",
            "target": device_id,
            "action": action,
            "status": "started",
            "message": f"uiautomator started. Check progress with get_analysis_progress"
        }, indent=2)
    
    @mcp.tool()
    def get_analysis_progress(session_id: str) -> str:
        """Check progress of a running analysis session
        
        Args:
            session_id: Session ID from run_* tool
        """
        session = session_manager.get_session(session_id)
        if not session:
            return json.dumps({"error": f"Session {session_id} not found"}, indent=2)
        
        # Update status if process died
        if session.status == "running" and not session.is_alive():
            session.status = "completed" if session.exit_code == 0 else "failed"
            session_manager.update_session(session)
        
        uptime = session.get_uptime()
        result = {
            "session_id": session_id,
            "tool": session.tool,
            "target": session.target_path,
            "status": session.status,
            "uptime_seconds": uptime.total_seconds() if uptime else None,
            "progress": session.progress,
            "log_file": session.log_file,
            "result_file": session.result_file
        }
        
        if session.status == "completed":
            result["exit_code"] = session.exit_code
            result["duration_seconds"] = session.duration_seconds
        elif session.status == "failed":
            result["error"] = session.error_message
            result["exit_code"] = session.exit_code
        
        return json.dumps(result, indent=2)
    
    @mcp.tool()
    def list_analysis_sessions() -> str:
        """List all analysis sessions"""
        sessions = session_manager.list_sessions()
        return json.dumps({
            "total_sessions": len(sessions),
            "sessions": [session.to_dict() for session in sessions]
        }, indent=2, default=str)
    
    @mcp.tool()
    def analyze_analysis_results(session_id: str) -> str:
        """Analyze and summarize results from a completed analysis session
        
        Args:
            session_id: Session ID from run_* tool
        """
        session = session_manager.get_session(session_id)
        if not session:
            return json.dumps({"error": f"Session {session_id} not found"}, indent=2)
        
        if session.status != "completed":
            return json.dumps({
                "error": f"Session {session_id} is not completed (status: {session.status})",
                "status": session.status
            }, indent=2)
        
        analysis = analyze_results(session)
        return json.dumps({
            "session_id": session_id,
            "tool": session.tool,
            "target": session.target_path,
            "analysis": analysis
        }, indent=2)
    
    @mcp.tool()
    def get_analysis_log(session_id: str, max_lines: int = 100) -> str:
        """Get log output from an analysis session
        
        Args:
            session_id: Session ID from run_* tool
            max_lines: Maximum number of lines to return (default: 100)
        """
        session = session_manager.get_session(session_id)
        if not session:
            return json.dumps({"error": f"Session {session_id} not found"}, indent=2)
        
        if not session.log_file or not Path(session.log_file).exists():
            return json.dumps({"error": "Log file not found"}, indent=2)
        
        try:
            with open(session.log_file, 'r') as f:
                lines = f.readlines()
                if len(lines) > max_lines:
                    lines = lines[-max_lines:]  # Last N lines
                return json.dumps({
                    "session_id": session_id,
                    "log_lines": len(lines),
                    "log": "".join(lines)
                }, indent=2)
        except Exception as e:
            return json.dumps({"error": f"Failed to read log: {str(e)}"}, indent=2)
    
    @mcp.tool()
    def stop_analysis(session_id: str) -> str:
        """Stop a running analysis session
        
        Args:
            session_id: Session ID from run_* tool
        """
        session = session_manager.get_session(session_id)
        if not session:
            return json.dumps({"error": f"Session {session_id} not found"}, indent=2)
        
        if session.status != "running":
            return json.dumps({
                "error": f"Session {session_id} is not running (status: {session.status})"
            }, indent=2)
        
        if session.pid:
            try:
                os.kill(session.pid, 15)  # SIGTERM
                time.sleep(1)
                if session.is_alive():
                    os.kill(session.pid, 9)  # SIGKILL
            except OSError:
                pass
        
        session.status = "stopped"
        session_manager.update_session(session)
        
        return json.dumps({
            "session_id": session_id,
            "status": "stopped",
            "message": "Analysis session stopped"
        }, indent=2)
    
    return mcp


def main():
    """Main entry point"""
    if not MCP_AVAILABLE:
        print("Error: FastMCP is required. Install with: pip install mcp", file=sys.stderr)
        sys.exit(1)
    
    server = create_server()
    server.run()


if __name__ == "__main__":
    main()
