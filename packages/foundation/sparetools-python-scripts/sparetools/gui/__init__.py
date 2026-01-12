"""
GUI Module

GUI utilities for tkinter applications and crash monitoring.
Based on ngapy-dev/ngapy/gui patterns.
"""

from .gui_common import (
    ToolTip,
    create_tool_tip,
    expand_and_fill_x,
)

from .crash_observer import (
    CrashObserver,
)

from .developer_buddy import (
    Configuration,
    Checkbar,
    Console,
    remove_files,
    check_git_repository_validity,
)

from .settings_dialog import (
    SettingsDialog,
)

__all__ = [
    "ToolTip",
    "create_tool_tip",
    "expand_and_fill_x",
    "CrashObserver",
    "Configuration",
    "Checkbar",
    "Console",
    "remove_files",
    "check_git_repository_validity",
    "SettingsDialog",
]
