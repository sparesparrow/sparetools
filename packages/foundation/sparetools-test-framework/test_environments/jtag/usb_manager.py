import re
import unittest
from pathlib import Path

from ngapy.util.custom_logging import setup_logging_from_config
from ngapy.util.execute_command import execute_command


class UsbManager:
    def __init__(self, usb_manager_cli: Path = Path(r'C:\MicroSITS\USB_Manager\UsbManager_CLI.exe')):
        self.usb_manager_cli = usb_manager_cli

    def run_usb_manager_command(self, command: str):
        return execute_command(f'{self.usb_manager_cli} {command}', cwd=self.usb_manager_cli.parent)

    @staticmethod
    def zero_means_all(self, instance):
        if instance == 0:
            instance = 'All'
        return instance

    # From some reason "All" works only with DPMs, not with other types (TDU, INSU)
    def enable_dpm_instance(self, instance: int):
        instance = self.zero_means_all(instance)
        return self.run_usb_manager_command(f'DPM{instance} ON')

    def disable_dpm_instance(self, instance: int):
        instance = self.zero_means_all(instance)
        return self.run_usb_manager_command(f'DPM{instance} OFF')

    def enable_tdu_instance(self, instance: int):
        return self.run_usb_manager_command(f'TDU{instance} ON')

    def disable_tdu_instance(self, instance: int):
        return self.run_usb_manager_command(f'TDU{instance} OFF')

    def enable_insu_instance(self, instance: int):
        return self.run_usb_manager_command(f'INSU{instance} ON')

    def disable_insu_instance(self, instance: int):
        return self.run_usb_manager_command(f'INSU{instance} OFF')

    def parse_config_file(self, config_file_path: Path = None):
        if config_file_path is None:
            config_file_path = self.usb_manager_cli.parent / 'Config.txt'
        with open(config_file_path, 'r') as cfg_file:
            cfg_file_data = cfg_file.read()
        config_dict = {}
        for line in cfg_file_data.splitlines():
            match_line = re.match(r'([^&]*)&([^\\]*)\\([^:]*):([^ ]*) ([^ ]*) ([^ ]*)', line)
            config_dict[(match_line[4], match_line[5])] = (match_line[1], match_line[2], match_line[3])
        return config_dict


def enable_dpm_instance(usb_manager: UsbManager, instance: int):
    return usb_manager.enable_dpm_instance(instance)


def disable_dpm_instance(usb_manager: UsbManager, instance: int):
    return usb_manager.disable_dpm_instance(instance)


class TestUsbManager(unittest.TestCase):
    def test_manager(self):
        setup_logging_from_config()
        manager = UsbManager()
        enable_dpm_instance(manager, 1)
        enable_dpm_instance(manager, 0)
        disable_dpm_instance(manager, 1)
        disable_dpm_instance(manager, 0)

    def test_config_load(self):
        setup_logging_from_config()
        manager = UsbManager()
        manager.parse_config_file(Path(r'c:\_Work\_Titan\_GIT\Config.txt'))
