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
// File Name: pmu_device.py
//
// Program:   TITAN
//
// Purpose:   PMU device for ASE class.
//
// Notes:     None
//
//********************************************************************************************
//********************************************************************************************
"""
import logging
import mmap
import os
import traceback
from ctypes import *

from ngapy.util import process
from ngapy.util.execute_command import execute_command

log = logging.getLogger('__main__.' + __name__)


# Shared memory file definition is coming from PMU_Control_Data.h and is aligned with platforms-vs17-ase.2000.75.10
# Here is a copy, just FYI.

# class PMUControlData
# {
# public:
#   enum Command
#   {
#      RUN = 0,
#      PAUSE = 1,
#      RUN_UNTIL = 2 //for STEP incr d_param1 % 80
#   };
#   enum Module_Operating_Mode
#   {
#      OP_NORMAL_MODE_e = 1,
#      OP_DOWNLOAD_MODE_e = 2,
#      OP_BOOT_MODE_e = 3,
#      OP_UNKNOWN_MODE_e
#   };
#   enum Operating_Mode
#   {
#      FRAME_SYNC_MODE = 1,
#      FREE_RUN_MODE = 2
#   };
#   uInt16 d_id; //in
#   uInt16 d_cmd;//in
#   uInt16 d_param1;//in
#   uInt16 d_PMU_sleep;//in  (milli sec)
#   uInt16 d_base_rate_hz;//in
#   uInt16 d_operating_mode;//in
#   uInt16 d_module_operating_mode;
#   uInt16 d_extender_board_present;
#   uInt16 d_debug_enabled;
#   uInt16 d_module_id;
#   uInt16 d_aircraft_id;
#   uInt8  d_module_network;
#   uInt16 d_curent_PMU_frame; //out
#   uInt16 d_curent_RPU0_frame; //out
#   uInt16 d_curent_RPU1_frame; //out
#   uInt16 d_curent_RPU2_frame; //out
#   uInt16 d_curent_BOOT_frame; //out
#   uInt16 d_curent_TIU_frame;  //out
#   uInt16 d_curent_APU0_frame; //out
#   uInt16 d_curent_APU1_frame; //out
#   uInt16 d_curent_APU2_frame; //out
#   uInt16 d_curent_APU3_frame; //out
#   uInt16 d_curent_APU4_frame; //out
#   uInt16 d_curent_APU5_frame; //out
#   uInt16 d_curent_APU6_frame; //out
# };


class PMUControlDataStruct(Structure):
    _fields_ = [
        ("d_id", c_uint16, 16),
        ("d_cmd", c_uint16, 16),
        ("d_param1", c_uint16, 16),
        ("d_PMU_sleep", c_uint16, 16),
        ("d_base_rate_hz", c_uint16, 16),
        ("d_operating_mode", c_uint16, 16),
        ("d_module_operating_mode", c_uint16, 16),
        ("d_extender_board_present", c_uint16, 16),
        ("d_debug_enabled", c_uint16, 16),
        ("d_module_id", c_uint16, 16),
        ("d_aircraft_id", c_uint16, 16),
        ("d_module_network", c_uint16, 16),
        ("d_curent_PMU_frame", c_uint16, 16),
        ("d_curent_RPU0_frame", c_uint16, 16),
        ("d_curent_RPU1_frame", c_uint16, 16),
        ("d_curent_RPU2_frame", c_uint16, 16),
        ("d_curent_BOOT_frame", c_uint16, 16),
        ("d_curent_TIU_frame", c_uint16, 16),
        ("d_curent_APU0_frame", c_uint16, 16),
        ("d_curent_APU1_frame", c_uint16, 16),
        ("d_curent_APU2_frame", c_uint16, 16),
        ("d_curent_APU3_frame", c_uint16, 16),
        ("d_curent_APU4_frame", c_uint16, 16),
        ("d_curent_APU5_frame", c_uint16, 16),
        ("d_curent_APU6_frame", c_uint16, 16),
    ]

    # There is likely much better way than this
    def convert_from_dict(self, dictionary):
        self.d_id = dictionary['d_id']
        self.d_cmd = dictionary['d_cmd']
        self.d_param1 = dictionary['d_param1']
        self.d_PMU_sleep = dictionary['d_PMU_sleep']
        self.d_base_rate_hz = dictionary['d_base_rate_hz']
        self.d_operating_mode = dictionary['d_operating_mode']
        self.d_module_operating_mode = dictionary['d_module_operating_mode']
        self.d_extender_board_present = dictionary['d_extender_board_present']
        self.d_debug_enabled = dictionary['d_debug_enabled']
        self.d_module_id = dictionary['d_module_id']
        self.d_aircraft_id = dictionary['d_aircraft_id']
        self.d_module_network = dictionary['d_module_network']
        self.d_curent_PMU_frame = dictionary['d_curent_PMU_frame']
        self.d_curent_RPU0_frame = dictionary['d_curent_RPU0_frame']
        self.d_curent_RPU1_frame = dictionary['d_curent_RPU1_frame']
        self.d_curent_RPU2_frame = dictionary['d_curent_RPU2_frame']
        self.d_curent_BOOT_frame = dictionary['d_curent_BOOT_frame']
        self.d_curent_TIU_frame = dictionary['d_curent_TIU_frame']
        self.d_curent_APU0_frame = dictionary['d_curent_APU0_frame']
        self.d_curent_APU1_frame = dictionary['d_curent_APU1_frame']
        self.d_curent_APU2_frame = dictionary['d_curent_APU2_frame']
        self.d_curent_APU3_frame = dictionary['d_curent_APU3_frame']
        self.d_curent_APU4_frame = dictionary['d_curent_APU4_frame']
        self.d_curent_APU5_frame = dictionary['d_curent_APU5_frame']
        self.d_curent_APU6_frame = dictionary['d_curent_APU6_frame']


class PMUControlData:
    pmu_struct: PMUControlDataStruct = PMUControlDataStruct()

    def set_default_params(self) -> 'PMUControlData':
        self.pmu_struct.d_base_rate_hz = 80
        self.pmu_struct.d_operating_mode = 1
        self.pmu_struct.d_module_operating_mode = 1
        self.pmu_struct.d_extender_board_present = 1
        self.pmu_struct.d_debug_enabled = 1
        self.pmu_struct.d_module_id = 1
        self.pmu_struct.d_aircraft_id = 1
        self.pmu_struct.d_module_network = 1
        return self

    def deserialize(self, buffer: bytes) -> 'PMUControlData':
        size = min(len(buffer), sizeof(self.pmu_struct))
        memmove(addressof(self.pmu_struct), buffer, size)
        return self

    def serialize(self) -> bytes:
        return bytes(self.pmu_struct)[:]


class PMUSmo:
    smo = None

    def __init__(self):
        if self.smo is None:
            self.smo = mmap.mmap(0, 128, "Global\\PMU_CONTROL_OBJECT")

    def read(self) -> PMUControlData:
        if self.smo:
            pmu_data = PMUControlData()
            return pmu_data.deserialize(self.smo.read(128))

    def write(self, pmu_data: PMUControlData) -> None:
        if self.smo:
            self.smo.seek(0)
            self.smo.write(pmu_data.serialize())
            self.smo.flush()


class PMUDevice:
    def __init__(self, config_loader):
        self.pmu_device_config = config_loader.bench.pmu_device
        self.stop()
        self.process_handle = None

    def __del__(self):
        self.stop()
        self.process_handle.wait()

    def start(self) -> None:
        self.pmu_smo = PMUSmo()
        read_data = self.pmu_smo.read()
        read_data.pmu_struct.convert_from_dict(self.pmu_device_config.smo_settings)
        self.pmu_smo.write(read_data)
        _, _, self.process_handle = execute_command(self.pmu_device_config['pmu_exe_path'],
                                                    cwd=os.path.dirname(self.pmu_device_config.pmu_exe_path),
                                                    wait_till_finish=False)

    def stop(self) -> None:
        log.debug(f'PmuDevice stopped by: {traceback.format_stack()}')
        process.kill_processes_by_name(self.pmu_device_config.kill_exes_when_finish)
