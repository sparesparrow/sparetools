import unittest
from dataclasses import dataclass
from pathlib import Path

from ngapy.exceptions.ngapy_exceptions import NgapyRuntimeError
from ngapy.util.custom_logging import setup_logging_from_config
from ngapy.util.execute_command import execute_command
from ngapy.util.process import kill_processes_by_name


@dataclass
class FlashConfiguration:
    flash_binary: Path
    flash_fsbl: Path
    offset: str
    jtag_id: str
    flash_mode: str = 'qspi-x8-dual_parallel'
    cable_type: str = 'xilinx_tcf'
    flash_server: str = 'TCP:127.0.0.1:3121'
    device_number: int = 1


class ProgramFlash:
    def __init__(self, program_flash_cli: Path = Path(r'C:\Xilinx\SDK\2018.3\bin\program_flash'), retry_count: int = 3):
        self.program_flash_cli = program_flash_cli
        self.retry_count = retry_count
        self.current_retries_available = self.retry_count

    def run_flash_command(self, flash_config: FlashConfiguration):
        kill_processes_by_name('hw_server.exe')
        command = f'-f {flash_config.flash_binary} ' \
                  f'-offset {flash_config.offset} ' \
                  f'-flash_type {flash_config.flash_mode} ' \
                  f'-fsbl {flash_config.flash_fsbl} ' \
                  f'-cable type {flash_config.cable_type} ' \
                  f'url {flash_config.flash_server} ' \
                  f'esn Digilent/{flash_config.jtag_id}/ ' \
                  f'-debugdevice deviceNr {flash_config.device_number}'
        rc, result = execute_command(f'{self.program_flash_cli} {command}', continuous_print=True, shell=True)
        if rc != 0 or r'Program Operation successful.' not in ' '.join(result):
            if self.current_retries_available > 0:
                self.current_retries_available -= 1
                return self.run_flash_command(flash_config)
            raise NgapyRuntimeError(f'JTAG Flash error: Log:{result}')
        else:
            self.current_retries_available = self.retry_count
        return rc, result


class TestProgramFlash(unittest.TestCase):
    def test_manager(self):
        program_flash = ProgramFlash()
        config = FlashConfiguration(r'd:\User\Michal\Builds\RR-PRVT-ISB749\Boot_MP\DPM_BOOT.bin',
                                    r'\\az18stns04\AEROSPS\PLATFORMS\NGPLATFORM_B\Builds\ENGINEERING'
                                    r'\V1_2022-75-004\SOURCE\EXTERNAL_DEPENDENCIES\BUILD_XILINX_HW_ABS_SVCS_APU_FSBL'
                                    r'\link_output\HW_ABS_SVCS_APU_FSBL.elf',
                                    '0x0',
                                    '210251AAB4EF')
        program_flash.run_flash_command(config)

