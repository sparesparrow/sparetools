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
// File Name: ase_bench.py
//
// Program:   TITAN
//
// Purpose:   ASE bench class.
//
// Notes:     None
//
//********************************************************************************************
//********************************************************************************************
"""
import logging
import os
import time

from sparetools.test_environments.bench import Bench
from sparetools.test_environments.pmu_controller_ase import PMUController
from sparetools.test_environments.pmu_device_ase import PMUDevice
from ngapy.core.ase_module import AseModule
from ngapy.util.custom_logging import setup_logging_from_config
from ngapy.util.setup_environment import get_repository_config


log = logging.getLogger('__main__.' + __name__)


class ASEBench(Bench):
    def __init__(self, config_loader):
        self.pmu_device = PMUDevice(config_loader)
        if 'ENV_SKIP_PMU_CONTROLLER' not in os.environ:
            self.pmu_controller = PMUController(config_loader)
        self.ase_module = AseModule(config_loader)
        pass

    def dump_current_configuration(self):
        raise NotImplementedError("Method not implemented.")

    def load_configuration(self):
        raise NotImplementedError("Method not implemented.")

    def start(self):
        self.pmu_device.start()
        if 'ENV_SKIP_PMU_CONTROLLER' not in os.environ:
            self.pmu_controller.start()
        time.sleep(self.bench_start_delay())

    def stop(self):
        self.pmu_device.stop()
        if 'ENV_SKIP_PMU_CONTROLLER' not in os.environ:
            self.pmu_controller.stop()

    def restart(self):
        self.stop()
        self.start()

    def file_exists(self, module_path):
        return self.ase_module.file_exists(module_path)

    def delete_file(self, module_path, backup_enabled=True):
        self.ase_module.delete_file(module_path, backup_enabled)

    def delete_multiple_files(self, file_paths, backup_enabled=True):
        self.ase_module.delete_multiple_files(file_paths, backup_enabled)

    def download_file(self, module_path, local_path, echo=True):
        self.ase_module.download_file(module_path, local_path, echo)

    def download_multiple_files(self, paths_list, echo=True):
        self.ase_module.download_multiple_files(paths_list, echo)

    def upload_file(self, local_path, module_path, backup_enabled=True):
        self.ase_module.upload_file(local_path, module_path, backup_enabled)

    def upload_multiple_files(self, paths_list, backup_enabled=True):
        self.ase_module.upload_multiple_files(paths_list, backup_enabled)

    def get_files_list(self, path='*'):
        return self.ase_module.get_files_list(path)

    def verify_up_and_running(self):
        raise NotImplementedError("Method not implemented.")

    def db_upload_file(self, local_path, module_path, backup_enabled=True):
        self.ase_module.upload_file(local_path, module_path, backup_enabled)

    def db_download_file(self, module_path, local_path, echo=True):
        self.ase_module.download_file(module_path, local_path, echo)

    def delete_file_on_db_module(self, module_path, backup_enabled=True):
        self.ase_module.delete_file(module_path, backup_enabled)

    def restore(self):
        self.ase_module.restore()

    def delete_backup_files(self):
        self.ase_module.delete_backup_files()

    def bench_start_delay(self) -> int:
        return 5

    def bench_stop_when_download_file(self) -> bool:
        return False


def main():
    import time
    setup_logging_from_config()

    try:
        bench = ASEBench(get_repository_config())
        bench.start()
        time.sleep(20000)
    except Exception as e:
        log.error(e)


if __name__ == "__main__":
    main()
