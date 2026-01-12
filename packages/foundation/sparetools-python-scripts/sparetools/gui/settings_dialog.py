"""
Settings Dialog Component

Reusable settings dialog for developer tools.
Based on ngapy-dev/ngapy/gui/titan_developer_buddy_options.py
Adapted for SpareTools ecosystem.
"""

import logging
import os
import threading
from tkinter import *
from tkinter import messagebox as tk_messagebox
from tkinter.ttk import *

from .gui_common import create_tool_tip, expand_and_fill_x

log = logging.getLogger(__name__)


# Copied from ngapy/gui/titan_developer_buddy_options.py
class SettingsDialog:
    """
    Generic settings dialog for developer tools.
    
    Based on ngapy/gui/titan_developer_buddy_options.py BuddySettings class.
    Adapted to be more generic and reusable.
    """
    def __init__(self, parent, tk_parent, configuration=None, log_window=None, crash_observer=None):
        """
        Initialize settings dialog.
        
        Args:
            parent: Parent widget/object that owns this dialog
            tk_parent: Tkinter parent window
            configuration: Configuration object with data dict
            log_window: Console widget for logging output
            crash_observer: CrashObserver instance (optional)
        """
        self.parent = parent
        self.configuration = configuration
        self.log_window = log_window
        self.crash_observer = crash_observer
        
        self.root = Toplevel(tk_parent)
        self.root.resizable(False, False)
        self.top_frame = Frame(self.root)
        self.top_frame.pack(side='top', fill=BOTH)
        self.root.wait_visibility()
        self.root.grab_set()
        self.root.transient(tk_parent)
        
        self._setup_logging_options()
        self._setup_crash_observer_options()

    def _setup_logging_options(self):
        """Setup logging level selection."""
        if not self.configuration:
            return
            
        self.logging_options = LabelFrame(self.top_frame)
        self.logging_options.config(height='10', width='50', text='Logging')
        self.logging_options.pack(side='left', fill=BOTH)
        
        logging_modes = [
            ("DEBUG", logging.DEBUG),
            ("INFO", logging.INFO),
            ("WARNING", logging.WARNING),
            ("ERROR", logging.ERROR),
            ("CRITICAL", logging.CRITICAL),
        ]
        
        self.logging_mode = IntVar()
        self.logging_mode_buttons = []
        for index, (text, mode) in enumerate(logging_modes):
            self.logging_mode_buttons.append(Radiobutton(
                self.logging_options, text=text,
                variable=self.logging_mode, value=mode,
                command=self.logging_selection))
            self.logging_mode_buttons[index].pack(side='top', anchor=W)
        
        # Set initial selection
        if self.configuration.data.get('logging_selection'):
            try:
                level = int(self.configuration.data['logging_selection'])
                # Find matching button (levels are 10, 20, 30, 40, 50)
                index = level // 10 - 1
                if 0 <= index < len(self.logging_mode_buttons):
                    self.logging_mode_buttons[index].invoke()
                else:
                    self.logging_mode_buttons[0].invoke()
            except (ValueError, IndexError):
                self.logging_mode_buttons[0].invoke()
        else:
            self.logging_mode_buttons[0].invoke()

    def _setup_crash_observer_options(self):
        """Setup crash observer controls."""
        if not self.crash_observer:
            return
            
        self.crash_options = LabelFrame(self.top_frame)
        self.crash_options.config(height='10', width='50', text='Crash Observer')
        self.crash_options.pack(side='left', fill=BOTH)
        
        self.start_crash_observer = Button(
            self.crash_options, command=self.start_crash_observer, width=30)
        self.start_crash_observer.config(text='Start Crash observer')
        self.start_crash_observer.pack(side='top')
        create_tool_tip(
            self.start_crash_observer,
            'Starts crash observer. From this time, you will not see JIT '
            'debugger popup window (Application xyz stopped working)')
        
        self.stop_crash_observer = Button(
            self.crash_options, command=self.stop_crash_observer, width=30)
        self.stop_crash_observer.config(text='Stop Crash observer')
        self.stop_crash_observer.pack(side='top')
        create_tool_tip(
            self.stop_crash_observer,
            'Stops crash observer. From this time, you will see JIT '
            'debugger popup window (Application xyz stopped working)')

    def logging_selection(self):
        """Handle logging level selection change."""
        if self.log_window:
            self.log_window.set_logging_level(self.logging_mode.get())
        
        if self.configuration:
            os.environ['SPARETOOLS_LOGGING_LEVEL'] = str(self.logging_mode.get())
            self.configuration.data['logging_selection'] = str(self.logging_mode.get())
            self.configuration.save_config()

    def start_crash_observer(self):
        """Start crash observer service."""
        if self.crash_observer:
            try:
                self.crash_observer.start_service()
                if self.log_window:
                    self.log_window.put_to_read_only('Crash observer started\n')
            except Exception as e:
                log.error(f"Failed to start crash observer: {e}")
                tk_messagebox.showerror('Error', f'Failed to start crash observer: {e}')

    def stop_crash_observer(self):
        """Stop crash observer service."""
        if self.crash_observer:
            try:
                self.crash_observer.stop_service()
                if self.log_window:
                    self.log_window.put_to_read_only('Crash observer stopped\n')
            except Exception as e:
                log.error(f"Failed to stop crash observer: {e}")
                tk_messagebox.showerror('Error', f'Failed to stop crash observer: {e}')
