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
from typing import Optional
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

# Import enhanced tool system
try:
    from .tool_adapters import (
        BaseToolAdapter, ToolCapabilities, ToolResult,
        CppcheckAdapter, ClangTidyAdapter, ValgrindAdapter,
        GdbAdapter, StraceAdapter, PytestAdapter, GtestAdapter,
        JestAdapter, DockerAdapter
    )
    from .mcp_client import MCPPromptsClient, InterpretationEngine, InterpretationContext
    from .workflow_manager import WorkflowManager, WorkflowSession, WorkflowStatus
    ENHANCED_TOOLS_AVAILABLE = True
except ImportError:
    ENHANCED_TOOLS_AVAILABLE = False

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

    # Enhanced tools (Phase 2)
    if ENHANCED_TOOLS_AVAILABLE:
        # Tool registry for enhanced adapters
        tool_registry = {
            'cppcheck': CppcheckAdapter(),
            'clang-tidy': ClangTidyAdapter(),
            'valgrind': ValgrindAdapter(),
            'gdb': GdbAdapter(),
            'strace': StraceAdapter(),
            'pytest': PytestAdapter(),
            'gtest': GtestAdapter(),
            'jest': JestAdapter(),
            'docker': DockerAdapter(),
        }

        # MCP-Prompts integration
        prompts_client = MCPPromptsClient()
        interpretation_engine = InterpretationEngine(prompts_client)

        # Workflow manager for multi-tool orchestration
        workflow_manager = WorkflowManager(tool_registry)

        @mcp.tool()
        def discover_tools() -> str:
            """Comprehensive tool discovery - scan system for available analysis tools"""
            discovered_tools = []

            for tool_name, adapter in tool_registry.items():
                available, version = adapter.is_available()
                capabilities = adapter.get_capabilities()

                status = {
                    'name': tool_name,
                    'available': available,
                    'version': version,
                    'category': capabilities.category.value,
                    'supported_languages': capabilities.supported_languages,
                    'description': capabilities.metadata.get('description', ''),
                }
                discovered_tools.append(status)

            return json.dumps({
                'total_tools': len(discovered_tools),
                'available_tools': len([t for t in discovered_tools if t['available']]),
                'tools': discovered_tools
            }, indent=2)

        @mcp.tool()
        def analyze_static(analyzer: str, target_path: str, **kwargs) -> str:
            """Unified static analysis dispatcher - run analysis with specified tool"""
            if analyzer not in tool_registry:
                return json.dumps({
                    'error': f'Unknown analyzer: {analyzer}',
                    'available_analyzers': list(tool_registry.keys())
                }, indent=2)

            adapter = tool_registry[analyzer]

            # Validate target
            valid, error_msg = adapter.validate_target(target_path)
            if not valid:
                return json.dumps({'error': error_msg}, indent=2)

            try:
                # Run analysis
                result = adapter.execute_sync(target_path, **kwargs)

                # Store result for learning
                asyncio.create_task(
                    prompts_client.store_analysis_result(
                        analyzer, result, {'target_path': target_path, **kwargs}
                    )
                )

                return json.dumps({
                    'tool_name': result.tool_name,
                    'success': result.success,
                    'issues_found': len(result.issues),
                    'execution_time': result.execution_time,
                    'result': result.to_dict()
                }, indent=2, default=str)

            except Exception as e:
                return json.dumps({
                    'error': f'Analysis failed: {str(e)}',
                    'tool': analyzer,
                    'target': target_path
                }, indent=2)

        @mcp.tool()
        def configure_tool(tool_name: str, project_type: str, language: Optional[str] = None) -> str:
            """Tool configuration management - get project-specific tool settings"""
            if tool_name not in tool_registry:
                return json.dumps({
                    'error': f'Unknown tool: {tool_name}',
                    'available_tools': list(tool_registry.keys())
                }, indent=2)

            try:
                # Get configuration template from MCP-Prompts
                config = prompts_client.get_configuration_template_sync(
                    tool_name, project_type, language
                )

                if config:
                    return json.dumps({
                        'tool': tool_name,
                        'project_type': project_type,
                        'language': language,
                        'configuration': config
                    }, indent=2)
                else:
                    # Fallback to basic configuration
                    adapter = tool_registry[tool_name]
                    basic_config = adapter.get_default_config()
                    return json.dumps({
                        'tool': tool_name,
                        'project_type': project_type,
                        'language': language,
                        'configuration': basic_config,
                        'note': 'Using default configuration (MCP-Prompts unavailable)'
                    }, indent=2)

            except Exception as e:
                return json.dumps({
                    'error': f'Configuration failed: {str(e)}',
                    'tool': tool_name
                }, indent=2)

        @mcp.tool()
        def get_recommendations(project_path: str) -> str:
            """AI-powered workflow suggestions - analyze project and recommend tools"""
            try:
                # Basic project analysis
                project_context = analyze_project_context(project_path)

                # Get workflow recommendations from MCP-Prompts
                workflows = prompts_client.get_workflow_recommendations_sync(project_context)

                if workflows:
                    return json.dumps({
                        'project_analysis': project_context,
                        'recommended_workflows': workflows
                    }, indent=2)
                else:
                    # Fallback recommendations
                    fallback_workflows = generate_fallback_recommendations(project_context)
                    return json.dumps({
                        'project_analysis': project_context,
                        'recommended_workflows': fallback_workflows,
                        'note': 'Using fallback recommendations (MCP-Prompts unavailable)'
                    }, indent=2)

            except Exception as e:
                return json.dumps({
                    'error': f'Recommendation generation failed: {str(e)}',
                    'project_path': project_path
                    }, indent=2)

        # Workflow orchestration tools
        @mcp.tool()
        def create_workflow(name: str, steps: str, description: Optional[str] = None) -> str:
            """Define multi-step analysis workflows with tool chaining and dependencies"""
            try:
                # Parse steps JSON
                steps_data = json.loads(steps)

                # Validate steps
                for step in steps_data:
                    if 'tool_name' not in step or 'target_path' not in step:
                        return json.dumps({
                            'error': 'Each step must have tool_name and target_path',
                            'step': step
                        }, indent=2)

                    if step['tool_name'] not in tool_registry:
                        return json.dumps({
                            'error': f'Unknown tool: {step["tool_name"]}',
                            'available_tools': list(tool_registry.keys())
                        }, indent=2)

                # Create workflow
                workflow = workflow_manager.create_workflow(name, steps_data, description)

                return json.dumps({
                    'workflow_id': workflow.workflow_id,
                    'name': workflow.name,
                    'description': workflow.description,
                    'steps_count': len(workflow.steps),
                    'status': workflow.status.value,
                    'created_at': workflow.created_at.isoformat()
                }, indent=2)

            except json.JSONDecodeError as e:
                return json.dumps({
                    'error': f'Invalid steps JSON: {str(e)}'
                }, indent=2)
            except Exception as e:
                return json.dumps({
                    'error': f'Workflow creation failed: {str(e)}'
                }, indent=2)

        @mcp.tool()
        def execute_workflow(workflow_id: str) -> str:
            """Run predefined analysis sequences with dependency management"""
            workflow = workflow_manager.get_workflow(workflow_id)
            if not workflow:
                return json.dumps({
                    'error': f'Workflow {workflow_id} not found'
                }, indent=2)

            if workflow.status != WorkflowStatus.CREATED:
                return json.dumps({
                    'error': f'Workflow is {workflow.status.value}, cannot start',
                    'status': workflow.status.value
                }, indent=2)

            # Start workflow execution
            success = workflow_manager.start_workflow(workflow_id)

            if success:
                return json.dumps({
                    'workflow_id': workflow_id,
                    'status': 'started',
                    'message': f'Workflow "{workflow.name}" execution started',
                    'steps_count': len(workflow.steps)
                }, indent=2)
            else:
                return json.dumps({
                    'error': 'Failed to start workflow execution'
                }, indent=2)

        @mcp.tool()
        def workflow_status(workflow_id: str) -> str:
            """Track progress of complex analysis workflows"""
            workflow = workflow_manager.get_workflow(workflow_id)
            if not workflow:
                return json.dumps({
                    'error': f'Workflow {workflow_id} not found'
                }, indent=2)

            # Get step details
            steps_status = []
            for step in workflow.steps:
                step_info = {
                    'step_id': step.step_id,
                    'tool_name': step.tool_name,
                    'target_path': str(step.target_path),
                    'status': step.status.value,
                    'start_time': step.start_time.isoformat() if step.start_time else None,
                    'end_time': step.end_time.isoformat() if step.end_time else None,
                }
                if step.result:
                    step_info['issues_found'] = len(step.result.issues)
                    step_info['success'] = step.result.success
                if step.error_message:
                    step_info['error'] = step.error_message
                steps_status.append(step_info)

            execution_time = workflow.get_execution_time()

            return json.dumps({
                'workflow_id': workflow.workflow_id,
                'name': workflow.name,
                'description': workflow.description,
                'status': workflow.status.value,
                'progress': workflow.progress,
                'current_step': workflow.current_step,
                'created_at': workflow.created_at.isoformat(),
                'started_at': workflow.started_at.isoformat() if workflow.started_at else None,
                'completed_at': workflow.completed_at.isoformat() if workflow.completed_at else None,
                'execution_time_seconds': execution_time.total_seconds() if execution_time else None,
                'total_steps': len(workflow.steps),
                'completed_steps': len([s for s in workflow.steps if s.status == 'completed']),
                'failed_steps': len([s for s in workflow.steps if s.status == 'failed']),
                'steps': steps_status,
                'error_message': workflow.error_message
            }, indent=2, default=str)

        @mcp.tool()
        def list_workflows() -> str:
            """List all available workflows"""
            workflows = workflow_manager.list_workflows()

            workflow_list = []
            for workflow in workflows:
                workflow_list.append({
                    'workflow_id': workflow.workflow_id,
                    'name': workflow.name,
                    'description': workflow.description,
                    'status': workflow.status.value,
                    'progress': workflow.progress,
                    'steps_count': len(workflow.steps),
                    'created_at': workflow.created_at.isoformat(),
                    'execution_time_seconds': workflow.get_execution_time().total_seconds() if workflow.get_execution_time() else None
                })

            return json.dumps({
                'total_workflows': len(workflows),
                'workflows': workflow_list
            }, indent=2, default=str)

        @mcp.tool()
        def cancel_workflow(workflow_id: str) -> str:
            """Cancel a running workflow"""
            success = workflow_manager.cancel_workflow(workflow_id)

            if success:
                return json.dumps({
                    'workflow_id': workflow_id,
                    'status': 'cancelled',
                    'message': 'Workflow execution cancelled'
                }, indent=2)
            else:
                return json.dumps({
                    'error': f'Failed to cancel workflow {workflow_id}'
                }, indent=2)

        # Testing framework integration
        @mcp.tool()
        def run_test_suite(test_framework: str, target_path: str, **kwargs) -> str:
            """Unified test execution supporting pytest, gtest, jest, etc."""
            if test_framework not in tool_registry:
                return json.dumps({
                    'error': f'Unknown test framework: {test_framework}',
                    'available_frameworks': [name for name, adapter in tool_registry.items()
                                           if adapter.tool_category.value == 'testing']
                }, indent=2)

            adapter = tool_registry[test_framework]

            # Validate target
            valid, error_msg = adapter.validate_target(target_path)
            if not valid:
                return json.dumps({'error': error_msg}, indent=2)

            try:
                # Run test suite
                result = adapter.execute_sync(target_path, **kwargs)

                # Enhanced result analysis for testing
                test_metrics = {}
                if hasattr(result, 'metrics') and result.metrics:
                    test_metrics = result.metrics

                # Categorize test results
                passed = test_metrics.get('passed_tests', 0) + test_metrics.get('passed', 0)
                failed = test_metrics.get('failed_tests', 0) + test_metrics.get('failed', 0)
                skipped = test_metrics.get('skipped_tests', 0) + test_metrics.get('skipped', 0)
                total = test_metrics.get('total_tests', 0) + test_metrics.get('total', 0)

                # Calculate success rate
                success_rate = (passed / total * 100) if total > 0 else 0

                return json.dumps({
                    'test_framework': test_framework,
                    'target_path': target_path,
                    'success': result.success,
                    'execution_time': result.execution_time,
                    'test_results': {
                        'total': total,
                        'passed': passed,
                        'failed': failed,
                        'skipped': skipped,
                        'success_rate': success_rate
                    },
                    'issues': [issue.__dict__ for issue in result.issues],
                    'raw_output': result.raw_output,
                    'session_id': result.session_id
                }, indent=2, default=str)

            except Exception as e:
                return json.dumps({
                    'error': f'Test execution failed: {str(e)}',
                    'framework': test_framework,
                    'target': target_path
                }, indent=2)

        # Result interpretation and reporting
        @mcp.tool()
        def analyze_results_with_context(session_ids: str, project_context: Optional[str] = None) -> str:
            """Use MCP-prompts for intelligent interpretation of analysis results"""
            try:
                # Parse session IDs
                session_id_list = json.loads(session_ids) if isinstance(session_ids, str) else session_ids

                # Get results from sessions
                results = []
                for session_id in session_id_list:
                    session = session_manager.get_session(session_id)
                    if session and session.status == "completed":
                        analysis = analyze_results(session)
                        if analysis and 'error' not in analysis:
                            result = ToolResult(
                                tool_name=session.tool,
                                success=True,
                                issues=[],  # Would need to reconstruct from analysis
                                metrics=analysis.get('analysis', {}).get('metrics', {}),
                                session_id=session_id
                            )
                            results.append(result)

                if not results:
                    return json.dumps({
                        'error': 'No valid completed sessions found',
                        'requested_sessions': session_id_list
                    }, indent=2)

                # Parse project context
                context_dict = {}
                if project_context:
                    try:
                        context_dict = json.loads(project_context)
                    except json.JSONDecodeError:
                        context_dict = {'description': project_context}

                # Create interpretation context
                interp_context = InterpretationContext(
                    project_type=context_dict.get('project_type', 'unknown'),
                    language=context_dict.get('language'),
                    framework=context_dict.get('framework'),
                    severity_threshold=context_dict.get('severity_threshold', 'medium'),
                    include_suggestions=True,
                    domain_context=context_dict
                )

                # Get intelligent interpretation
                interpretation = interpretation_engine.interpret_results_sync(
                    results[0].tool_name, results, interp_context
                )

                return json.dumps({
                    'interpretation': {
                        'summary': interpretation.summary,
                        'key_findings': interpretation.key_findings,
                        'recommendations': interpretation.recommendations,
                        'risk_assessment': interpretation.risk_assessment,
                        'contextual_insights': interpretation.contextual_insights,
                        'next_steps': interpretation.next_steps
                    },
                    'metadata': interpretation.metadata,
                    'analyzed_sessions': len(results)
                }, indent=2)

            except Exception as e:
                return json.dumps({
                    'error': f'Interpretation failed: {str(e)}',
                    'session_ids': session_ids
                }, indent=2)

        @mcp.tool()
        def generate_report(session_ids: str, format: str = "markdown", include_recommendations: bool = True) -> str:
            """Create comprehensive analysis reports in multiple formats"""
            try:
                # Parse session IDs
                session_id_list = json.loads(session_ids) if isinstance(session_ids, str) else session_ids

                # Collect all session data
                report_data = {
                    'sessions': [],
                    'summary': {
                        'total_sessions': 0,
                        'successful_sessions': 0,
                        'failed_sessions': 0,
                        'total_issues': 0,
                        'tools_used': set()
                    },
                    'generated_at': datetime.now().isoformat(),
                    'format': format
                }

                for session_id in session_id_list:
                    session = session_manager.get_session(session_id)
                    if session:
                        session_data = {
                            'session_id': session.session_id,
                            'tool': session.tool,
                            'target': session.target_path,
                            'status': session.status,
                            'start_time': session.start_time.isoformat() if session.start_time else None,
                            'duration': session.duration_seconds,
                            'exit_code': session.exit_code,
                            'error': session.error_message
                        }

                        if session.status == "completed":
                            analysis = analyze_results(session)
                            if analysis and 'error' not in analysis:
                                session_data['analysis'] = analysis
                                report_data['summary']['total_issues'] += analysis.get('total_issues', 0)

                        report_data['sessions'].append(session_data)
                        report_data['summary']['total_sessions'] += 1
                        report_data['summary']['tools_used'].add(session.tool)

                        if session.status == "completed" and session.exit_code == 0:
                            report_data['summary']['successful_sessions'] += 1
                        elif session.status == "failed":
                            report_data['summary']['failed_sessions'] += 1

                # Convert set to list for JSON serialization
                report_data['summary']['tools_used'] = list(report_data['summary']['tools_used'])

                # Generate formatted report
                if format.lower() == "markdown":
                    report = generate_markdown_report(report_data, include_recommendations)
                elif format.lower() == "json":
                    report = json.dumps(report_data, indent=2, default=str)
                elif format.lower() == "html":
                    report = generate_html_report(report_data, include_recommendations)
                else:
                    report = json.dumps(report_data, indent=2, default=str)

                return json.dumps({
                    'report': report,
                    'format': format,
                    'summary': report_data['summary']
                }, indent=2, default=str)

            except Exception as e:
                return json.dumps({
                    'error': f'Report generation failed: {str(e)}',
                    'session_ids': session_ids
                }, indent=2)

        @mcp.tool()
        def compare_results(base_session_ids: str, compare_session_ids: str, comparison_type: str = "trends") -> str:
            """Show trends and differences across multiple analysis runs"""
            try:
                # Parse session ID lists
                base_ids = json.loads(base_session_ids) if isinstance(base_session_ids, str) else base_session_ids
                compare_ids = json.loads(compare_session_ids) if isinstance(compare_session_ids, str) else compare_session_ids

                # Collect data from both sets
                def collect_session_data(session_ids):
                    data = {}
                    for session_id in session_ids:
                        session = session_manager.get_session(session_id)
                        if session and session.status == "completed":
                            analysis = analyze_results(session)
                            if analysis and 'error' not in analysis:
                                data[session_id] = {
                                    'tool': session.tool,
                                    'target': session.target_path,
                                    'analysis': analysis,
                                    'timestamp': session.start_time
                                }
                    return data

                base_data = collect_session_data(base_ids)
                compare_data = collect_session_data(compare_ids)

                if not base_data and not compare_data:
                    return json.dumps({
                        'error': 'No valid session data found for comparison'
                    }, indent=2)

                # Perform comparison based on type
                if comparison_type == "trends":
                    comparison = compare_trends(base_data, compare_data)
                elif comparison_type == "differences":
                    comparison = compare_differences(base_data, compare_data)
                elif comparison_type == "improvements":
                    comparison = compare_improvements(base_data, compare_data)
                else:
                    comparison = {'error': f'Unknown comparison type: {comparison_type}'}

                return json.dumps({
                    'comparison_type': comparison_type,
                    'base_sessions': len(base_data),
                    'compare_sessions': len(compare_data),
                    'comparison': comparison
                }, indent=2, default=str)

            except Exception as e:
                return json.dumps({
                    'error': f'Comparison failed: {str(e)}',
                    'base_session_ids': base_session_ids,
                    'compare_session_ids': compare_session_ids
                }, indent=2)

    return mcp


def analyze_project_context(project_path: str) -> Dict[str, Any]:
    """Analyze project structure to determine context for recommendations"""
    from pathlib import Path

    path = Path(project_path)
    if not path.exists():
        return {'error': 'Project path does not exist'}

    context = {
        'project_path': str(project_path),
        'languages': [],
        'build_systems': [],
        'frameworks': [],
        'size': {'files': 0, 'lines': 0},
        'has_tests': False,
        'has_docker': False,
    }

    # Detect languages and frameworks
    if (path / 'package.json').exists():
        context['languages'].append('javascript')
        context['build_systems'].append('npm')
        try:
            with open(path / 'package.json') as f:
                package_data = json.load(f)
                if 'dependencies' in package_data:
                    deps = package_data['dependencies']
                    if 'react' in deps:
                        context['frameworks'].append('react')
                    if 'jest' in deps:
                        context['has_tests'] = True
        except:
            pass

    if (path / 'requirements.txt').exists() or (path / 'pyproject.toml').exists():
        context['languages'].append('python')
        context['build_systems'].append('pip')

    if (path / 'CMakeLists.txt').exists() or (path / 'Makefile').exists():
        context['languages'].append('c++')
        context['build_systems'].append('make')

    if (path / 'Dockerfile').exists():
        context['has_docker'] = True

    # Count files and estimate size
    try:
        total_files = 0
        total_lines = 0
        for file_path in path.rglob('*'):
            if file_path.is_file() and not file_path.name.startswith('.'):
                total_files += 1
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        total_lines += sum(1 for _ in f)
                except:
                    pass
        context['size'] = {'files': total_files, 'lines': total_lines}
    except:
        pass

    return context


def generate_fallback_recommendations(project_context: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate basic workflow recommendations when MCP-Prompts is unavailable"""
    recommendations = []

    languages = project_context.get('languages', [])
    has_tests = project_context.get('has_tests', False)
    has_docker = project_context.get('has_docker', False)

    if 'javascript' in languages:
        recommendations.append({
            'name': 'JavaScript Analysis Workflow',
            'description': 'Static analysis and testing for JavaScript projects',
            'tools': ['jest', 'eslint'],
            'priority': 'high' if has_tests else 'medium'
        })

    if 'python' in languages:
        recommendations.append({
            'name': 'Python Analysis Workflow',
            'description': 'Code quality and testing analysis for Python projects',
            'tools': ['pytest', 'pylint'],
            'priority': 'high'
        })

    if 'c++' in languages:
        recommendations.append({
            'name': 'C++ Analysis Workflow',
            'description': 'Static analysis and memory checking for C++ projects',
            'tools': ['cppcheck', 'clang-tidy', 'valgrind'],
            'priority': 'high'
        })

    if has_docker:
        recommendations.append({
            'name': 'Container Security Analysis',
            'description': 'Security scanning and analysis for containerized applications',
            'tools': ['docker'],
            'priority': 'medium'
        })

    return recommendations


def generate_markdown_report(report_data: Dict[str, Any], include_recommendations: bool) -> str:
    """Generate a markdown formatted report"""
    lines = []

    # Header
    lines.append("# Static Analysis Report")
    lines.append(f"Generated at: {report_data['generated_at']}")
    lines.append("")

    # Summary
    summary = report_data['summary']
    lines.append("## Summary")
    lines.append(f"- **Total Sessions**: {summary['total_sessions']}")
    lines.append(f"- **Successful**: {summary['successful_sessions']}")
    lines.append(f"- **Failed**: {summary['failed_sessions']}")
    lines.append(f"- **Total Issues**: {summary['total_issues']}")
    lines.append(f"- **Tools Used**: {', '.join(summary['tools_used'])}")
    lines.append("")

    # Session Details
    lines.append("## Session Details")
    lines.append("")

    for session in report_data['sessions']:
        lines.append(f"### {session['tool']} - {session['target']}")
        lines.append(f"- **Status**: {session['status']}")
        lines.append(f"- **Session ID**: {session['session_id']}")

        if session.get('start_time'):
            lines.append(f"- **Start Time**: {session['start_time']}")

        if session.get('duration'):
            lines.append(f"- **Duration**: {session['duration']:.2f}s")

        if session.get('error'):
            lines.append(f"- **Error**: {session['error']}")

        if 'analysis' in session:
            analysis = session['analysis']
            lines.append(f"- **Issues Found**: {analysis.get('total_issues', 0)}")

            # Show top issues
            if 'details' in analysis:
                details = analysis['details']
                for severity in ['errors', 'warnings']:
                    if severity in details and details[severity]:
                        lines.append(f"  - **{severity.title()}**: {len(details[severity])}")
                        # Show first few
                        for issue in details[severity][:3]:
                            lines.append(f"    - {issue.get('file', 'unknown')}:{issue.get('line', '?')} - {issue.get('message', '')[:100]}")

        lines.append("")

    if include_recommendations:
        lines.append("## Recommendations")
        lines.append("")
        lines.append("### General Recommendations")
        lines.append("- Review all issues by severity (critical/high first)")
        lines.append("- Address root causes rather than symptoms")
        lines.append("- Consider automated fixes where available")
        lines.append("- Schedule regular analysis to track improvements")
        lines.append("")

    return "\n".join(lines)


def generate_html_report(report_data: Dict[str, Any], include_recommendations: bool) -> str:
    """Generate an HTML formatted report"""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Static Analysis Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .summary {{ background: #f0f0f0; padding: 10px; border-radius: 5px; }}
            .session {{ margin: 10px 0; padding: 10px; border: 1px solid #ddd; }}
            .success {{ border-color: #4CAF50; }}
            .failed {{ border-color: #f44336; }}
            .issues {{ color: #ff9800; }}
        </style>
    </head>
    <body>
        <h1>Static Analysis Report</h1>
        <p>Generated at: {report_data['generated_at']}</p>

        <div class="summary">
            <h2>Summary</h2>
            <ul>
                <li>Total Sessions: {report_data['summary']['total_sessions']}</li>
                <li>Successful: {report_data['summary']['successful_sessions']}</li>
                <li>Failed: {report_data['summary']['failed_sessions']}</li>
                <li>Total Issues: {report_data['summary']['total_issues']}</li>
                <li>Tools Used: {', '.join(report_data['summary']['tools_used'])}</li>
            </ul>
        </div>

        <h2>Session Details</h2>
    """

    for session in report_data['sessions']:
        status_class = "success" if session['status'] == "completed" else "failed"
        html += f"""
        <div class="session {status_class}">
            <h3>{session['tool']} - {session['target']}</h3>
            <p><strong>Status:</strong> {session['status']}</p>
            <p><strong>Session ID:</strong> {session['session_id']}</p>
        """

        if session.get('start_time'):
            html += f"<p><strong>Start Time:</strong> {session['start_time']}</p>"

        if session.get('duration'):
            html += f"<p><strong>Duration:</strong> {session['duration']:.2f}s</p>"

        if session.get('error'):
            html += f"<p><strong>Error:</strong> {session['error']}</p>"

        if 'analysis' in session:
            analysis = session['analysis']
            issues = analysis.get('total_issues', 0)
            html += f"<p class='issues'><strong>Issues Found:</strong> {issues}</p>"

        html += "</div>"

    html += """
    </body>
    </html>
    """

    return html


def compare_trends(base_data: Dict[str, Any], compare_data: Dict[str, Any]) -> Dict[str, Any]:
    """Compare trends between two sets of analysis results"""
    # Simple trend analysis
    base_issues = sum(data['analysis'].get('total_issues', 0) for data in base_data.values())
    compare_issues = sum(data['analysis'].get('total_issues', 0) for data in compare_data.values())

    trend = "improving" if compare_issues < base_issues else "worsening" if compare_issues > base_issues else "stable"

    return {
        'trend': trend,
        'base_total_issues': base_issues,
        'compare_total_issues': compare_issues,
        'change': compare_issues - base_issues,
        'change_percent': ((compare_issues - base_issues) / base_issues * 100) if base_issues > 0 else 0
    }


def compare_differences(base_data: Dict[str, Any], compare_data: Dict[str, Any]) -> Dict[str, Any]:
    """Compare differences between analysis runs"""
    differences = {
        'new_issues': [],
        'resolved_issues': [],
        'persistent_issues': [],
        'changed_issues': []
    }

    # This is a simplified comparison - real implementation would need more sophisticated
    # issue matching and tracking
    return differences


def compare_improvements(base_data: Dict[str, Any], compare_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze improvements between analysis runs"""
    improvements = {
        'issues_resolved': 0,
        'success_rate_improved': False,
        'performance_improved': False,
        'recommendations': []
    }

    # Calculate improvements
    base_success = sum(1 for data in base_data.values() if data['analysis'].get('success', False))
    compare_success = sum(1 for data in compare_data.values() if data['analysis'].get('success', False))

    if len(compare_data) > 0 and len(base_data) > 0:
        base_rate = base_success / len(base_data)
        compare_rate = compare_success / len(compare_data)
        improvements['success_rate_improved'] = compare_rate > base_rate

    return improvements


def main():
    """Main entry point"""
    if not MCP_AVAILABLE:
        print("Error: FastMCP is required. Install with: pip install mcp", file=sys.stderr)
        sys.exit(1)
    
    server = create_server()
    server.run()


if __name__ == "__main__":
    main()
