import os
import unittest
from enum import Enum, IntEnum
from pathlib import Path
from typing import Union

import paramiko

from ngapy.util.execute_command import execute_command


class ConnectionMode(Enum):
    SSH_PARAMIKO = 1
    PUTTY = 2


class NodeType(IntEnum):
    DPM = 0
    SW = 1
    TDU = 2
    PIDU = 3
    # SPEECH = 4
    STIM = 5


class ModeType(IntEnum):
    NORMAL = 0x0
    BOOT = 0x3
    DOWNLOAD = 0x5
    JTAG = 0x80


class SwitchModeType(IntEnum):
    NORMAL = 0x0
    GROUND = 0x2
    SHOP = 0x4


class ModeControl:
    def __init__(self, connection_mode=ConnectionMode.SSH_PARAMIKO,
                 plink: Path = Path(r'C:\Program Files\PuTTY\plink.exe'),
                 putty_key: Path = Path('c:\sshkey.ppk'),
                 ssh_key: Path = Path('c:\ids_rsa'),
                 user: str = 'user',
                 vcte: str = os.environ['vcte'],
                 dss: str = os.environ['dss']):
        self.connection_mode = connection_mode
        self.plink = plink
        self.putty_key = putty_key
        self.ssh_key = ssh_key
        self.user = user
        self.vcte = vcte
        self.dss = dss

    @staticmethod
    def compose_command(node_type: NodeType, instance: int, mode: ModeType, with_debug: bool = False):
        c_data = mode
        d_data = 0
        if with_debug:
            c_data &= 0x8
        if mode == ModeType.JTAG:
            d_data = 0x80
        return f'@{node_type}{instance:1x} #C:{c_data:02x}#D:{d_data:02x}'

    @staticmethod
    def compose_module_name(node_type: NodeType, instance: int):
        return f'{node_type.name} #{instance}'

    @staticmethod
    def enable_module(module_name: str):
        return f'On({module_name})'

    @staticmethod
    def disable_module(module_name: str):
        return f'Off({module_name})'

    @staticmethod
    def compose_switch_command(instance: int, mode: SwitchModeType):
        c_data = mode
        d_data = 0
        return f'@{NodeType.SW}{instance:1x} #C:{c_data:02x}#D:{d_data:02x}'

    @staticmethod
    def add_write_command(string):
        return f'WriteCommand("{string}")'

    def execute_vcte_command(self, command):
        complete_command = f'(setenv DISPLAY {self.dss}:0.0;' \
                           f' cd python;./titan.py --command=\'{command}\')' \
                           f' >& /dev/null </dev/null &'

        if self.connection_mode == ConnectionMode.SSH_PARAMIKO:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=self.vcte, username=self.user,
                        pkey=paramiko.RSAKey.from_private_key_file(str(self.ssh_key)))
            ssh.exec_command(complete_command)

        elif self.connection_mode == ConnectionMode.PUTTY:
            execute_command(f'{self.plink} -ssh -i {self.ssh_key} {self.user}@{self.vcte} "{complete_command}"')


def restart_with_mode(mode_control: ModeControl, node_type: NodeType, instance: int,
                      mode_type: Union[ModeType, SwitchModeType]):
    disable_module(mode_control, node_type, instance)
    if node_type == NodeType.SW:
        set_switch_mode(mode_control, instance, mode_type)
    else:
        set_module_mode(mode_control, node_type, instance, mode_type)
    enable_module(mode_control, node_type, instance)


def enable_module(mode_control: ModeControl, node_type: NodeType, instance: int):
    mode_control.execute_vcte_command(ModeControl.enable_module(ModeControl.compose_module_name(node_type, instance)))


def disable_module(mode_control: ModeControl, node_type: NodeType, instance: int):
    mode_control.execute_vcte_command(ModeControl.disable_module(ModeControl.compose_module_name(node_type, instance)))


def set_module_mode(mode_control: ModeControl, node_type: NodeType, instance: int, mode_type: ModeType):
    mode_control.execute_vcte_command(
        ModeControl.add_write_command(ModeControl.compose_command(node_type, instance, mode_type)))


def set_switch_mode(mode_control: ModeControl, instance: int, mode_type: SwitchModeType):
    mode_control.execute_vcte_command(
        ModeControl.add_write_command(ModeControl.compose_switch_command(instance, mode_type)))


def enable_all(mode_control: ModeControl):
    mode_control.execute_vcte_command('AllModulesOn()')


def disable_all(mode_control: ModeControl):
    mode_control.execute_vcte_command('AllModulesOff()')


class TestMode(unittest.TestCase):
    def test_ssh(self):
        mode_control = ModeControl(connection_mode=ConnectionMode.SSH_PARAMIKO)

        disable_all(mode_control)
        enable_all(mode_control)
        set_module_mode(mode_control, NodeType.DPM, 1, ModeType.DOWNLOAD)
        set_module_mode(mode_control, NodeType.DPM, 1, ModeType.JTAG)
        set_switch_mode(mode_control, 1, SwitchModeType.SHOP)
        set_switch_mode(mode_control, 1, SwitchModeType.GROUND)

        disable_module(mode_control, NodeType.DPM, 1)

    def test_putty(self):
        mode_control = ModeControl(connection_mode=ConnectionMode.PUTTY)
        mode_control.execute_vcte_command('On(DPM #1)')
        mode_control.execute_vcte_command('On(DPM #2)')
        mode_control.execute_vcte_command('On(DPM #3)')
