"""
Process Management Core

Command execution and process management utilities.
Re-exports from util modules for backward compatibility.
"""

# Import from util modules
from ..util.execute_command import (
    remove_console_color_codes,
    execute_command,
    run_command_with_timeout,
    execute_command_silently,
    run_command_async,
    wait_for_process,
    build_command_args,
)

from ..util.process import (
    Logger,
    run_independent_process,
    get_processes_info_by_names,
    get_processes_info_by_pids,
    is_process_running_by_pid,
    is_process_running_by_name,
    kill_proc_tree,
    kill_processes_by_name,
    kill_processes_by_pid,
    get_process_windows_titles,
    get_process_by_name,
    wait_for_application_start,
)

# Re-export everything
__all__ = [
    "remove_console_color_codes",
    "execute_command",
    "run_command_with_timeout",
    "execute_command_silently",
    "run_command_async",
    "wait_for_process",
    "build_command_args",
    "Logger",
    "run_independent_process",
    "get_processes_info_by_names",
    "get_processes_info_by_pids",
    "is_process_running_by_pid",
    "is_process_running_by_name",
    "kill_proc_tree",
    "kill_processes_by_name",
    "kill_processes_by_pid",
    "get_process_windows_titles",
    "get_process_by_name",
    "wait_for_application_start",
]
