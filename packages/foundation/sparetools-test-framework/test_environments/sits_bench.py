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
// File Name: sits_bench.py
//
// Program:   TITAN
//
// Purpose:   SITS bench class.
//
// Notes:     None
//
//********************************************************************************************
//********************************************************************************************
"""
import logging
import time

from sparetools.test_environments.bench import Bench
from ngapy.core.deos_module import DeosModule
from ngapy.util.ssh_msg import send_start_stop_all_ssh_msg

log = logging.getLogger('__main__.' + __name__)


class SITSBench(Bench):
    def __init__(self, config_loader, **kwargs):

        super().__init__(**kwargs)
        self.deos_module = {}
        self.loader = config_loader
        self.selected_module = None
        self.selected_module_name = ""
        module_count = self.loader.bench.module_count
        log.info("Initializing " + str(module_count) + " modules...")
        for module_config in self.loader.bench.modules:
            self.deos_module[module_config.name] = DeosModule(self.loader)
            self.deos_module[module_config.name].init(module_config)

        self.default_module_name = "DPM2"

    def dump_current_configuration(self):
        raise NotImplementedError("Method not implemented.")

    def load_configuration(self):
        raise NotImplementedError("Method not implemented.")

    def start(self):
        if self.selected_module:
            self.selected_module.start()
        else:
            log.info("No module selected, starting all modules")
            self.start_all()
        time.sleep(self.bench_start_delay())

    def stop(self):
        if self.selected_module:
            self.selected_module.stop()
        else:
            log.info("No module selected, stopping all modules")
            self.stop_all()

    def restart(self):
        if self.selected_module:
            self.selected_module.restart()
        else:
            log.info("No module selected, restarting all modules")
            self.restart_all()

    def start_all(self):
        for d_name, d_module in self.deos_module.items():
            d_module.start()

    def stop_all(self):
        for d_name, d_module in self.deos_module.items():
            d_module.stop()

    def restart_all(self):
        for d_name, d_module in self.deos_module.items():
            d_module.restart()

    def hw_start(self):
        if self.selected_module:
            self.selected_module.hw_start()
        else:
            log.info("No module selected, starting all modules")
            self.hw_start_all()

    def hw_stop(self):
        if self.selected_module:
            self.selected_module.hw_stop()
        else:
            log.info("No module selected, stopping all modules")
            self.hw_stop_all()

    def hw_restart(self):
        if self.selected_module:
            self.selected_module.hw_restart()
        else:
            log.info("No module selected, restarting all modules")
            self.hw_restart_all()

    @staticmethod
    def hw_start_all():
        # TODO: Need future fix: this is not good approach as we skipp deos_module.py
        send_start_stop_all_ssh_msg(True)

    @staticmethod
    def hw_stop_all():
        # TODO: Need future fix: this is not good approach as we skipp deos_module.py
        send_start_stop_all_ssh_msg(False)

    def hw_restart_all(self):
        # TODO: Need future fix: this is not good approach as we skipp deos_module.py
        self.hw_stop_all()
        time.sleep(1)
        self.hw_start_all()

    def file_exists(self, module_path):
        if self.selected_module:
            return self.selected_module.file_exists(module_path)
        else:
            log.info("No module selected, selecting default")
            return self.deos_module[self.default_module_name].file_exists(module_path)

    def delete_file(self, module_path, backup_enabled=True):
        if self.selected_module:
            return self.selected_module.delete_file(module_path, backup_enabled)
        else:
            log.info("No module selected, selecting default")
            return self.deos_module[self.default_module_name].delete_file(module_path, backup_enabled)

    def delete_multiple_files(self, file_paths, backup_enabled=True):
        if self.selected_module:
            return self.selected_module.delete_multiple_files(file_paths, backup_enabled)
        else:
            log.info("No module selected, selecting default")
            return self.deos_module[self.default_module_name].delete_multiple_files(file_paths, backup_enabled)

    def download_file(self, module_path, local_path, echo=True):
        if self.selected_module:
            return self.selected_module.download_file(module_path, local_path, echo)
        else:
            log.info("No module selected, selecting default")
            return self.deos_module[self.default_module_name].download_file(module_path, local_path, echo)

    def download_multiple_files(self, paths_list, echo=True):
        if self.selected_module:
            return self.selected_module.download_multiple_files(paths_list, echo)
        else:
            log.info("No module selected, selecting default")
            return self.deos_module[self.default_module_name].download_multiple_files(paths_list, echo)

    def upload_file(self, local_path, module_path, backup_enabled=True):
        if self.selected_module:
            return self.selected_module.upload_file(local_path, module_path, backup_enabled)
        else:
            log.info("No module selected, selecting default")
            return self.deos_module[self.default_module_name].upload_file(local_path, module_path, backup_enabled)

    def upload_multiple_files(self, paths_list, backup_enabled=True):
        if self.selected_module:
            return self.selected_module.upload_multiple_files(paths_list, backup_enabled)
        else:
            log.info("No module selected, selecting default")
            return self.deos_module[self.default_module_name].upload_multiple_files(paths_list, backup_enabled)

    def get_files_list(self, path='*'):
        if self.selected_module:
            return self.selected_module.get_files_list(path)
        else:
            log.info("No module selected, selecting default")
            return self.deos_module[self.default_module_name].get_files_list(path)

    def select_module(self, module_name):
        self.selected_module = self.deos_module[module_name]
        self.selected_module_name = module_name

    def get_selected_module_name(self):
        return self.selected_module_name

    def get_selected_module(self):
        return self.selected_module

    def verify_up_and_running(self):
        raise NotImplementedError("Method not implemented.")

    def db_upload_file(self, local_path, module_path, backup_enabled=True):
        self.upload_file(local_path, module_path, backup_enabled)

    def db_download_file(self, module_path, local_path, echo=True):
        self.download_file(module_path, local_path, echo)

    def delete_file_on_db_module(self, module_path, backup_enabled=True):
        self.delete_file(module_path, backup_enabled)

    def restore(self):
        if self.selected_module:
            return self.selected_module.restore()
        else:
            log.info("No module selected, selecting default")
            return self.deos_module[self.default_module_name].restore()

    def delete_backup_files(self):
        if self.selected_module:
            return self.selected_module.delete_backup_files()
        else:
            log.info("No module selected, selecting default")
            return self.deos_module[self.default_module_name].delete_backup_files()

    def bench_start_delay(self) -> int:
        return 100

    def bench_stop_when_download_file(self) -> bool:
        return False
