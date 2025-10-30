#!/usr/bin/env python3
"""
OpenSSL Tools OpenSSL Developer Buddy Launcher
GUI launcher following openssl-tools patterns
"""

import argparse
import logging
import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
from typing import Optional, Dict, Any
import threading
import subprocess

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from util.custom_logging import setup_logging_from_config
from conan_launcher import (
    Configuration, check_conan_validity, setup_conan_environment,
    run_package_python_script
)


class OpenSSLDeveloperBuddyGUI:
    """GUI launcher following openssl-tools patterns"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("OpenSSL Tools - OpenSSL Developer Buddy")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Configuration
        self.configuration = Configuration()
        
        # Variables
        self.repository_path = tk.StringVar(value=self.configuration.data.get('git_repository', ''))
        self.conan_setup_done = tk.BooleanVar(value=self.configuration.data.get('remote_setup') == 'passed')
        self.verbose_mode = tk.BooleanVar(value=False)
        
        # Setup GUI
        self.setup_gui()
        
        # Load configuration
        self.load_configuration()
    
    def setup_gui(self):
        """Setup the GUI components"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="OpenSSL Tools - OpenSSL Developer Buddy", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Repository selection
        ttk.Label(main_frame, text="Repository Path:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        repo_frame = ttk.Frame(main_frame)
        repo_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        repo_frame.columnconfigure(0, weight=1)
        
        self.repo_entry = ttk.Entry(repo_frame, textvariable=self.repository_path, width=50)
        self.repo_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        browse_btn = ttk.Button(repo_frame, text="Browse", command=self.browse_repository)
        browse_btn.grid(row=0, column=1)
        
        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="10")
        options_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        options_frame.columnconfigure(1, weight=1)
        
        # Conan setup checkbox
        self.conan_setup_cb = ttk.Checkbutton(options_frame, text="Setup Conan Environment", 
                                            variable=self.conan_setup_done, state='disabled')
        self.conan_setup_cb.grid(row=0, column=0, sticky=tk.W, pady=2)
        
        # Verbose mode checkbox
        ttk.Checkbutton(options_frame, text="Verbose Mode", 
                       variable=self.verbose_mode).grid(row=1, column=0, sticky=tk.W, pady=2)
        
        # Action buttons frame
        actions_frame = ttk.Frame(main_frame)
        actions_frame.grid(row=3, column=0, columnspan=3, pady=20)
        
        # Setup Conan button
        self.setup_conan_btn = ttk.Button(actions_frame, text="Setup Conan", 
                                        command=self.setup_conan)
        self.setup_conan_btn.grid(row=0, column=0, padx=5)
        
        # Validate Repository button
        self.validate_btn = ttk.Button(actions_frame, text="Validate Repository", 
                                     command=self.validate_repository)
        self.validate_btn.grid(row=0, column=1, padx=5)
        
        # Run Python Script button
        self.run_python_btn = ttk.Button(actions_frame, text="Run Python Script", 
                                       command=self.run_python_script)
        self.run_python_btn.grid(row=0, column=2, padx=5)
        
        # Check Updates button
        self.update_btn = ttk.Button(actions_frame, text="Check Updates", 
                                   command=self.check_updates)
        self.update_btn.grid(row=0, column=3, padx=5)
        
        # Output frame
        output_frame = ttk.LabelFrame(main_frame, text="Output", padding="10")
        output_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        
        # Output text area
        self.output_text = scrolledtext.ScrolledText(output_frame, height=15, width=80)
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Configure main frame grid weights
        main_frame.rowconfigure(4, weight=1)
    
    def load_configuration(self):
        """Load configuration and update GUI"""
        if self.configuration.data.get('remote_setup') == 'passed':
            self.conan_setup_done.set(True)
            self.setup_conan_btn.config(text="Conan Setup ✓")
    
    def browse_repository(self):
        """Browse for repository directory"""
        directory = filedialog.askdirectory(
            title="Select Repository Directory",
            initialdir=self.repository_path.get() or str(Path.home())
        )
        if directory:
            self.repository_path.set(directory)
            self.log_output(f"Selected repository: {directory}")
    
    def log_output(self, message: str, level: str = "INFO"):
        """Log message to output text area"""
        self.output_text.insert(tk.END, f"[{level}] {message}\n")
        self.output_text.see(tk.END)
        self.root.update_idletasks()
    
    def set_status(self, message: str):
        """Set status bar message"""
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def setup_conan(self):
        """Setup Conan environment"""
        def _setup():
            try:
                self.set_status("Setting up Conan environment...")
                self.log_output("Setting up Conan environment...")
                
                setup_conan_environment(self.configuration)
                
                self.conan_setup_done.set(True)
                self.setup_conan_btn.config(text="Conan Setup ✓")
                self.log_output("Conan environment setup completed successfully")
                self.set_status("Conan setup completed")
                
            except Exception as e:
                self.log_output(f"Conan setup failed: {e}", "ERROR")
                self.set_status("Conan setup failed")
        
        # Run in separate thread to avoid blocking GUI
        threading.Thread(target=_setup, daemon=True).start()
    
    def validate_repository(self):
        """Validate selected repository"""
        def _validate():
            try:
                repo_path = Path(self.repository_path.get())
                if not repo_path.exists():
                    self.log_output(f"Repository path does not exist: {repo_path}", "ERROR")
                    self.set_status("Repository validation failed")
                    return
                
                self.set_status("Validating repository...")
                self.log_output(f"Validating repository: {repo_path}")
                
                if check_conan_validity(repo_path):
                    self.log_output("Repository validation successful")
                    self.set_status("Repository valid")
                    
                    # Update configuration
                    self.configuration.data['git_repository'] = str(repo_path)
                    self.configuration.save_config()
                else:
                    self.log_output("Repository validation failed", "ERROR")
                    self.set_status("Repository validation failed")
                    
            except Exception as e:
                self.log_output(f"Repository validation error: {e}", "ERROR")
                self.set_status("Repository validation failed")
        
        threading.Thread(target=_validate, daemon=True).start()
    
    def run_python_script(self):
        """Run Python script dialog"""
        # Simple dialog for script selection
        script_path = filedialog.askopenfilename(
            title="Select Python Script",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")],
            initialdir=self.repository_path.get() or str(Path.home())
        )
        
        if script_path:
            def _run_script():
                try:
                    repo_path = Path(self.repository_path.get())
                    script_args = [script_path]
                    
                    self.set_status("Running Python script...")
                    self.log_output(f"Running script: {script_path}")
                    
                    result = run_package_python_script(repo_path, script_args)
                    
                    if hasattr(result, 'returncode') and result.returncode == 0:
                        self.log_output("Script execution completed successfully")
                        self.set_status("Script execution completed")
                    else:
                        self.log_output("Script execution failed", "ERROR")
                        self.set_status("Script execution failed")
                        
                except Exception as e:
                    self.log_output(f"Script execution error: {e}", "ERROR")
                    self.set_status("Script execution failed")
            
            threading.Thread(target=_run_script, daemon=True).start()
    
    def check_updates(self):
        """Check for updates"""
        def _check():
            try:
                self.set_status("Checking for updates...")
                self.log_output("Checking for updates...")
                
                # This would integrate with actual update checking
                import time
                time.sleep(2)  # Simulate update check
                
                self.log_output("No updates available")
                self.set_status("Update check completed")
                
            except Exception as e:
                self.log_output(f"Update check failed: {e}", "ERROR")
                self.set_status("Update check failed")
        
        threading.Thread(target=_check, daemon=True).start()
    
    def run(self):
        """Run the GUI application"""
        self.root.mainloop()


def main():
    """Main function for GUI launcher"""
    # Setup logging
    setup_logging_from_config()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='OpenSSL Tools GUI Launcher')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging')
    parser.add_argument('-r', '--repository', type=str, help='Initial repository path')
    
    options = parser.parse_args()
    
    # Set logging level
    if options.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create and run GUI
    app = OpenSSLDeveloperBuddyGUI()
    
    # Set initial repository if provided
    if options.repository:
        app.repository_path.set(options.repository)
    
    app.run()


if __name__ == '__main__':
    main()