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
// File Name: pmu_controller_ase.py
//
// Program:   TITAN
//
// Purpose:   PMU controller for ASE class.
//
// Notes:     None
//
//********************************************************************************************
//********************************************************************************************
"""
import os

from ngapy.util import process
from ngapy.util.execute_command import execute_command


class PMUController:
    def __init__(self, config_loader):
        self.pmu_controller_config = config_loader.bench.pmu_controller
        self.pmu_device_config = config_loader.bench.pmu_device
        self.stop()
        self.process_handle = None

    def __del__(self):
        self.stop()
        self.process_handle.wait()

    def start(self) -> None:
        _, _, self.process_handle = execute_command(
            [self.pmu_controller_config.executable_path], wait_till_finish=False)

    @staticmethod
    def stop() -> None:
        process.kill_processes_by_name(["PmuControllerII.exe"])
