"""
Crash Observer

Application crash monitoring and dump collection utilities.
Based on ngapy-dev/ngapy/gui/crash_observer.py
Adapted for SpareTools ecosystem.
"""

import os
import sys
import tempfile
import time
from pathlib import Path
from typing import Optional, Callable, List

import logging

log = logging.getLogger(__name__)

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    log.warning("psutil not available, some crash observer functions will be limited")

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    log.warning("requests not available, crash dump upload will be limited")

from ..util.execute_command import execute_command
from ..fs.core import archive_files, remove_directory_tree


def make_list_from_variable(var):
    """Convert variable to list if not already."""
    if isinstance(var, (list, tuple)):
        return var
    return [var]


# Copied from ngapy/gui/crash_observer.py (adapted for SpareTools)
class CrashObserver:
    """
    Crash observer for monitoring application crashes and collecting dumps.
    
    Based on ngapy/gui/crash_observer.py CrashObserver class.
    Adapted to use SpareTools utilities instead of ngapy dependencies.
    """
    def __init__(self, current_folder, register_file_callback=None, 
                 crash_dump_created_callback=None, crash_dump_uploaded_callback=None,
                 dump_folder_name='Dumps', dump_check_interval_seconds=3,
                 debug_diag_path=None):
        """
        Initialize crash observer.

        Args:
            current_folder: Base folder for crash dumps
            register_file_callback: Callback to gather additional files
            crash_dump_created_callback: Callback when dump is created
            crash_dump_uploaded_callback: Callback when dump is uploaded
            dump_folder_name: Name of dump folder
            dump_check_interval_seconds: Interval to check for new dumps
            debug_diag_path: Path to debug diagnostics tools (optional)
        """
        self.register_file_callback = []
        self.crash_dump_created_callback = crash_dump_created_callback
        self.crash_dump_uploaded_callback = crash_dump_uploaded_callback
        if register_file_callback:
            self.add_register_file_callback(register_file_callback)

        self.dump_folder = Path(current_folder) / dump_folder_name
        self.dump_check_interval_seconds = dump_check_interval_seconds
        self.path_to_debug_diagnostics = debug_diag_path
        if self.path_to_debug_diagnostics:
            self.path_to_debug_diagnostics = Path(self.path_to_debug_diagnostics)
            if not self.path_to_debug_diagnostics.exists():
                log.warning(f"Debug diagnostics path does not exist: {self.path_to_debug_diagnostics}")
                self.path_to_debug_diagnostics = None
            else:
                log.info(f'Using Debug Diag application from this location: {self.path_to_debug_diagnostics}')

    def add_register_file_callback(self, register_file_callback):
        """Add callback for gathering additional files."""
        self.register_file_callback.extend(make_list_from_variable(register_file_callback))

    @staticmethod
    def is_dbg_service_running():
        """
        Check if debug service is running.
        
        Based on ngapy/gui/crash_observer.py is_dbg_service_running method.
        """
        if not HAS_PSUTIL:
            return False
        
        try:
            service = psutil.win_service_get('DbgSvc')
            service = service.as_dict()
            if service and service['status'] == 'running':
                return True
            else:
                return False
        except:
            return False

    def start_service(self, collection_app=None, config_file=None, register_file=None):
        """
        Start crash dump collection service.
        
        Based on ngapy/gui/crash_observer.py start_service method.
        
        Args:
            collection_app: Path to collection application
            config_file: Path to config file
            register_file: Path to registration file
        """
        if not self.path_to_debug_diagnostics:
            log.warning("Debug diagnostics path not configured")
            return
        
        if not collection_app or not config_file or not register_file:
            log.warning("Service configuration incomplete")
            return
        
        # Format config file with dump path
        config_path = self.path_to_debug_diagnostics / config_file
        if config_path.exists():
            with open(config_path, 'r') as config_file_handle:
                config_file_content = config_file_handle.read()
                formatted_config = config_file_content.format(
                    DumpPath='"' + str(self.dump_folder) + r'\"'
                )
            
            os.makedirs(self.dump_folder, exist_ok=True)
            with open(self.dump_folder / config_file, 'w') as formatted_config_file_handle:
                formatted_config_file_handle.write(formatted_config)

        register_path = self.path_to_debug_diagnostics / register_file
        execute_command(str(register_path), cwd=str(self.path_to_debug_diagnostics))

        collection_path = self.path_to_debug_diagnostics / collection_app
        execute_command(
            f'{collection_path} /importConfig "{self.dump_folder / config_file}" –DoNotPrompt',
            cwd=str(self.path_to_debug_diagnostics)
        )

    def stop_service(self, register_file=None):
        """
        Stop crash dump collection service.
        
        Based on ngapy/gui/crash_observer.py stop_service method.
        
        Args:
            register_file: Path to registration file
        """
        if not self.path_to_debug_diagnostics or not register_file:
            return
        
        register_path = self.path_to_debug_diagnostics / register_file
        execute_command(str(register_path), cwd=str(self.path_to_debug_diagnostics))

    def application_crash_observer(self, upload_url=None, upload_endpoint=None):
        """
        Monitor for application crashes and handle dump collection.
        
        Based on ngapy/gui/crash_observer.py application_crash_observer method.
        
        Args:
            upload_url: URL for crash dump upload server
            upload_endpoint: Endpoint for crash dump upload
        """
        remove_directory_tree(self.dump_folder)
        original_glob = []
        
        while True:
            current_glob = list(self.dump_folder.glob(r'*.dmp'))
            difference = set(current_glob) - set(original_glob)
            original_glob = current_glob
            time.sleep(self.dump_check_interval_seconds)

            if difference:
                log.info(f'New dump file(s) found. Path(s) : {difference}')

                for gather_file_callback in self.register_file_callback:
                    added_files = gather_file_callback()
                    if added_files:
                        difference.update(set(added_files))

                with tempfile.TemporaryDirectory() as tmp_dir_name:
                    archive_name = Path(tmp_dir_name) / 'CrashDumpArchive.zip'
                    archive_files(archive_name, difference)

                    if self.crash_dump_created_callback:
                        self.crash_dump_created_callback(
                            archive_name=archive_name,
                            url=upload_url
                        )
                    
                    if upload_endpoint and HAS_REQUESTS:
                        try:
                            with open(archive_name, 'rb') as f:
                                r = requests.post(upload_endpoint, files={'file': f}, verify=False)
                                log.debug(f'Dump uploaded to {upload_endpoint}. '
                                          f'Result: {r.content.decode("ascii")}')
                                if self.crash_dump_uploaded_callback:
                                    self.crash_dump_uploaded_callback(
                                        archive_name=archive_name,
                                        url=upload_url
                                    )
                        except Exception as e:
                            log.error(f"Failed to upload crash dump: {e}")
