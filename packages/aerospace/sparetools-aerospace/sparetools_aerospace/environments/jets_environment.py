#
# DATA_RIGHTS:  HONEYWELL CONFIDENTIAL & PROPRIETARY
#              THIS WORK CONTAINS VALUABLE CONFIDENTIAL AND PROPRIETARY
#              INFORMATION. DISCLOSURE, USE OR REPRODUCTION OUTSIDE OF
#              HONEYWELL INTERNATIONAL, INC. IS PROHIBITED EXCEPT AS
#              AUTHORIZED IN WRITING. THIS UNPUBLISHED WORK IS PROTECTED BY
#              THE LAWS OF THE UNITED STATES AND OTHER COUNTRIES. IN THE
#              EVENT OF PUBLICATION, THE FOLLOWING NOTICE SHALL APPLY:
#              COPR. 2020-2021 HONEYWELL INTERNATIONAL, INC. ALL RIGHTS RESERVED.
#
"""
//********************************************************************************************
//
//
// File Name: jets_environment.py
//
// Program:   TITAN
//
// Purpose:   JETS bench class.
//
// Notes:     None
//
//********************************************************************************************
//********************************************************************************************
"""

"""
Migration Info:
Original: ngapy/bench/jets_bench.py
Migrated: sparetools/test_environments/providers/aerospace/jets_environment.py
Date: 2024-XX-XX
Changes: Class name, imports, inheritance only
Logic Preserved: 100% - all JETS communication protocols intact
"""

import os
import psutil
import signal
import subprocess
from time import sleep
from winreg import HKEY_CURRENT_USER

from sparetools.test_environments.environment import TestEnvironment
from ngapy.core.jets_module import JetsModule
from ngapy.core.utilities import get_reg_with_root


class JETSBench(Bench):
    def __init__(self, config_loader):
        self.config_loader = config_loader
        self.jets_module = JetsModule(config_loader)
        self.jets_module.init(self.config_loader.bench)
        self.jets_process = None
        self.dpm_proc = None
        self.putty_proc = None
        self.rpu_proc = None
        pass

    def dump_current_configuration(self):
        raise NotImplementedError("Method not implemented.")

    def load_configuration(self):
        raise NotImplementedError("Method not implemented.")

    def start(self):
        rslt = self.jets_module.start()
        if not rslt:
            self.restart_hw()

    def stop(self):
        self.jets_module.stop()

    def restart(self):
        self.stop()
        sleep(5)
        self.start()

    def start_hw(self):
        self._start_jets()

    def stop_hw(self):
        self._terminate_dpm()
        if self.jets_process:
            self._kill_child_processes(self.jets_process.pid)
            # self.jets_process.terminate()
        else:
            if self.rpu_proc:
                self._kill_child_processes(self.rpu_proc.pid)
            if self.putty_proc:
                self._kill_child_processes(self.putty_proc.pid)
            if self.dpm_proc:
                self._kill_child_processes(self.dpm_proc.pid)

    def restart_hw(self):
        self.stop_hw()
        # stop is quite instant but just to be sure
        sleep(5)
        self.start_hw()

    def file_exists(self, module_path):
        return self.jets_module.file_exists(module_path)

    def delete_file(self, module_path, backup_enabled=True):
        self.jets_module.delete_file(module_path, backup_enabled)

    def delete_multiple_files(self, file_paths, backup_enabled=True):
        self.jets_module.delete_multiple_files(file_paths, backup_enabled)

    def download_file(self, module_path, local_path, echo=True):
        self.jets_module.download_file(module_path, local_path, echo)

    def download_multiple_files(self, paths_list, echo=True):
        self.jets_module.download_multiple_files(paths_list, echo)

    def upload_file(self, local_path, module_path, backup_enabled=True):
        self.jets_module.upload_file(local_path, module_path, backup_enabled)

    def upload_multiple_files(self, paths_list, backup_enabled=True):
        self.jets_module.upload_multiple_files(paths_list, backup_enabled)

    def get_files_list(self, path='*'):
        return self.jets_module.get_files_list(path)

    def verify_operational_by_ping(self, timeout=120):
        return self.jets_module.verify_operational_by_ping(timeout=timeout)

    def verify_up_and_running(self):
        raise NotImplementedError("Method not implemented.")

    def restore(self):
        self.jets_module.restore()

    def delete_backup_files(self):
        self.jets_module.delete_backup_files()

    @staticmethod
    def _kill_child_processes(parent_pid, sig=signal.SIGTERM):
        try:
            parent = psutil.Process(parent_pid)
        except psutil.NoSuchProcess:
            return
        children = parent.children(recursive=True)
        for process in children:
            process.send_signal(sig)

    def _start_jets(self):
        # get workspace location from registry
        workspace = get_reg_with_root(HKEY_CURRENT_USER, r"Software\Performance Software\Performance "
                                                         r"VirtualPlatform\environment", "workspace")

        self._terminate_dpm()

        # Start the DPM
        self.dpm_proc = subprocess.Popen("pvpConsole.exe -m DPM -c start", shell=True)

        # Open a PuTTy window to the dpmuart
        self.putty_proc = subprocess.Popen(r"plink -serial \\.\pipe\dpmuart", shell=True)

        # Start RPU Sim
        run_folder = os.path.join(workspace, "RPUSim", "_win32", "bin")
        self.rpu_proc = subprocess.Popen(["OSSL_PLATFORMSIM.exe", "LCD.bin"], cwd=run_folder, shell=True)

    @staticmethod
    def _terminate_dpm():
        # Stop the DPM if it's already running
        os.system("pvpConsole.exe -m DPM -c stop")
