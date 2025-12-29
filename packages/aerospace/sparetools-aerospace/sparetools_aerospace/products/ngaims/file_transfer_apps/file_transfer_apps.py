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
import subprocess
import time
import io
import re
import os
from pathlib import Path
from enum import Enum

from ngapy.exceptions import ngapy_exceptions


class FileTransferInfo:
    def __init__(self, dest=None):
        if dest is None:
            self.destination = ""
        else:
            self.destination = dest
        self.result = False


class FileTransferApp():
    def __init__(self, root, ip, port, prefix, app_name, map_file):
        self.root = root
        self.ip = ip
        self.port = port
        self.prefix = prefix
        self.app_name = app_name
        self.map_file = map_file
        # Reports in cmcf do not generate (non existent folder) in folder that is in default Bdtte mapping,
        # so mapping csv file is added (contains default + reports mapping)
        command = ' '.join([os.path.join(self.root, self.app_name), self.ip, str(self.port), self.map_file, '--start_server'])
        self.stdout = open(os.path.join(self.root, "stdout.txt"), "w+b")
        self.proc = subprocess.Popen(command, cwd=self.root, stdout=self.stdout)
        self.stdout.seek(0)
        self.wait_for_app_start()

    def __del__(self):
        self.proc.wait()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stdout.close()
        self.proc.terminate()

    def get_stdout(self):
        return self.stdout

    def stop(self):
        self.stdout.close()
        self.proc.terminate()

    def start(self):
        try:
            self.stdout.close()
            self.proc.terminate()
        except:
            pass
        command = ' '.join(
            [os.path.join(self.root, self.app_name), self.ip, str(self.port), self.map_file, '--start_server'])
        self.stdout = open(os.path.join(self.root, "stdout.txt"), "w+b")
        self.proc = subprocess.Popen(command, cwd=self.root, stdout=self.stdout)
        self.wait_for_app_start()

    def get_file_transfer_info(self):
        if self.stdout.seek(0, io.SEEK_END) == 0:
            return None
        transfer = FileTransferInfo()
        self.stdout.seek(0, io.SEEK_SET)
        line = self.stdout.readline()
        while self.stdout.tell() != 0:
            if line.find(b"Destination path:") != -1:
                match = re.search(b"\"(.*)\"", line)
                if match:
                    transfer.destination = Path(self.root) / Path(match.group(1).decode())
                else:
                    raise ngapy_exceptions.NgapyRuntimeError(str(self.prefix) + " couldn't find destination path")
            elif line.find(b"request result:") != -1:
                if line.find(b"Success") != -1:
                    transfer.result = True
            line = self.stdout.readline()
        return transfer

    def get_file_transfers(self):
        transfers = []
        transfer = self.get_file_transfer_info()
        while transfer is not None:
            transfers.append(transfer)
            transfer = self.get_file_transfer_info()
        return transfers

    def flush(self):
        self.stdout.flush()

    def wait_for_app_start(self):
        line = self.stdout.readline()
        while self.stdout.tell() != 0:
            if line.find(b'Trying to start server at') != -1:
                if line.find(b'success') != -1:
                    break
                else:
                    raise ngapy_exceptions.NgapyRuntimeError(str(self.prefix) + " couldn't start server")
            line = self.stdout.readline()
        line = self.stdout.readline()


class Bdtte(FileTransferApp):
    class BdtteInstance(Enum):
        CMCF = 0
        TCRF = 1
    
    def __init__(self, instance=BdtteInstance.CMCF, config=None):
        from sparetools_aerospace.products.ngaims.setup_environment import get_oms_repository_config
        if not config:
            config = get_oms_repository_config()
        if not self.check_expected_attribute_config(config):
            raise ngapy_exceptions.NgapyConfigurationError(f'BdtteFactory: '
                                                           f'Config is missing expected attributes')
        if instance == Bdtte.BdtteInstance.CMCF:
            bdtte_ip = config.oms_runtime.bdtte_ip_cmcf
            bdtte_port = config.oms_runtime.bdtte_port_cmcf
        elif instance == Bdtte.BdtteInstance.TCRF:
            bdtte_ip = config.oms_runtime.bdtte_ip_tcrf
            bdtte_port = config.oms_runtime.bdtte_port_tcrf
        else:
            raise ngapy_exceptions.NgapyConfigurationError(f'BdtteFactory: '
                                                           f'Unknown Bdtte Instance: {instance}')
        FileTransferApp.__init__(self, config.oms_repository_layout.bdtte_root, bdtte_ip, bdtte_port,
                             'bdtte', 'BDTTEAppTest', config.oms_runtime.bdtte_file_map)

    @staticmethod
    def check_expected_attribute_config(config):
        return (hasattr(config, 'oms_repository_layout') and
                hasattr(config, 'oms_runtime') and
                hasattr(config.oms_runtime, 'bdtte_ip_cmcf') and
                hasattr(config.oms_runtime, 'bdtte_ip_tcrf') and
                hasattr(config.oms_runtime, 'bdtte_port_cmcf') and
                hasattr(config.oms_runtime, 'bdtte_port_tcrf') and
                hasattr(config.oms_runtime, 'bdtte_file_map'))


class Dlte(FileTransferApp):

    def __init__(self, config=None):
        from sparetools_aerospace.products.ngaims.setup_environment import get_oms_repository_config
        if not config:
            config = get_oms_repository_config()
        if not self.check_expected_attribute_config(config):
            raise ngapy_exceptions.NgapyConfigurationError(f'DlteFactory: '
                                                           f'Config is missing expected attributes')
        FileTransferApp.__init__(self, config.oms_repository_layout.dlte_root, config.oms_runtime.dlte_ip,
                             config.oms_runtime.dlte_port,
                             'dlte', 'DLTEAppTest', config.oms_runtime.dlte_file_map)

    @staticmethod
    def check_expected_attribute_config(config):
        return (hasattr(config, 'oms_repository_layout') and
                hasattr(config, 'oms_runtime') and
                hasattr(config.oms_runtime, 'dlte_ip') and
                hasattr(config.oms_runtime, 'dlte_port') and
                hasattr(config.oms_runtime, 'dlte_file_map'))
