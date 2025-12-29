#              AUTHORIZED IN WRITING. THIS UNPUBLISHED WORK IS PROTECTED BY
#              THE LAWS OF THE UNITED STATES AND OTHER COUNTRIES. IN THE
#              EVENT OF PUBLICATION, THE FOLLOWING NOTICE SHALL APPLY:
#              COPR. 2020-2021 HONEYWELL INTERNATIONAL, INC. ALL RIGHTS RESERVED.
#
import logging
import os
import threading
import warnings
from pathlib import Path

import munch

from ngapy.bench.bench_factory import TestBenchContainer, measure_cpu
from ngapy.bench.bench_manager import BenchManager, BaseAppManager
from sparetools_aerospace.products.ngaims.ate_interface.cmcf_ate import AteFactory
from sparetools_aerospace.products.ngaims.common_functions import upload_tcrf_oem, upload_tcrf_services, \
    delete_tcrf_log_file, delete_tcrf_services_db, is_ase_run, upload_omi, upload_file, get_files_list, delete_file
from sparetools_aerospace.products.ngaims.file_transfer_apps.file_transfer_apps import Bdtte, Dlte
from sparetools_aerospace.products.ngaims.io_parameters.parameters_manager import InputParameterManager, \
    OutputParameterManagerTcrf
from sparetools_aerospace.products.ngaims.maintenance_model.maintenance_model_loader \
    import MaintenanceModelLoader
from sparetools_aerospace.products.ngaims.setup_environment import get_oms_repository_config
from sparetools_aerospace.products.ngaims.test_common import CommonNgaimsAppManager
from sparetools_aerospace.products.ngaims.test_execution.oms_repository_configuration import OmsRepositoryConfiguration
from sparetools_aerospace.products.ngaims.test_execution.run_test_functions import partition_to_not_equipped
from sparetools_aerospace.products.ngaims.test_execution.run_test_functions import wait_for_ate_init, \
    prepare_tcrf_bench
from ngapy.util.process import wait_for_application_start


class TcrfState:
    def __init__(self):
        self.oem = ''
        self.services = ''
        self.delete_logs = False
        self.omi = ''


class TcrfManager(BaseAppManager, CommonNgaimsAppManager):

    def __init__(self):
        super().__init__()
        self.bdtte = None
        self.dlte = None
        self.state = TcrfState()
        prepare_tcrf_bench()
        self.need_to_reload = True
        self.bm = None
        prod_dev = get_oms_repository_config()['PACKAGE_ROOT_ngaims-product-dev']
        self.switch_oem(Path(prod_dev, '_Build', 'SOURCE', 'SLDB', 'TCRF', 'tcrf_oem.db'))
        self.switch_omi(Path(prod_dev, '_Build', 'SOURCE', 'SLDB', 'OMI', 'oms_omi.db'))
        self.delete_services()
        self.delete_logs()
        self.cfg = OmsRepositoryConfiguration()
        if is_ase_run():
            self.setup_tcrf_to_not_equipped()
        self.log = logging.getLogger('__main__.' + __name__)

    def load_model(self):
        if self.need_to_reload:
            self.need_to_reload = False
            self.active_model = TcrfBenchModel()
            self.models = {'default': self.active_model}
            super().reload_targets(get_oms_repository_config().oms_repository_layout.omi_path)

    def set_bench_manager(self, bench_man: BenchManager):
        self.bm = bench_man

    def reset(self):
        self.state = TcrfState()

    def switch_oem(self, oem_path):
        if not self.state.oem == oem_path:
            self.need_to_reload = True
            self.state.oem = oem_path
            if self.bm:
                self.bm.bench_state.restart_needed = True
                self.bm.stop_bench()
            upload_tcrf_oem(oem_path)

    def switch_omi(self, omi_path):
        if not self.state.omi == omi_path:
            self.state.omi = omi_path
            if self.bm:
                self.bm.bench_state.restart_needed = True
                self.bm.stop_bench()
            upload_omi(omi_path)

    def switch_services(self, services_path):
        if not self.state.services == services_path:
            self.state.services = services_path
            if self.bm:
                self.bm.bench_state.restart_needed = True
                self.bm.stop_bench()
            upload_tcrf_services(services_path)

    def delete_logs(self):
        if self.bm:
            self.bm.bench_state.restart_needed = True
            self.bm.stop_bench()
        delete_tcrf_log_file()

    def delete_services(self):
        if self.bm:
            self.bm.bench_state.restart_needed = True
            self.bm.stop_bench()
        delete_tcrf_services_db()

    def set_up(self, oem_path='', omi_path='', services_path='', del_log=False, bdtte=True, dlte=False):
        if bdtte and is_ase_run() and self.bdtte is None:
            self.bdtte = Bdtte(Bdtte.BdtteInstance.TCRF)

        if dlte and is_ase_run() and self.dlte is None:
            self.dlte = Dlte()

        if not oem_path == '':
            if 'oem' not in str(oem_path).lower():
                warnings.warn('OEM path is suspicious - does not contain OEM')
            if not oem_path == self.state.oem:
                self.switch_oem(oem_path)

        if not omi_path == '':
            if 'omi' not in str(omi_path).lower():
                warnings.warn('OMI path is suspicious - does not contain OMI')
            if not omi_path == self.state.omi:
                self.switch_omi(omi_path)

        if not services_path == '':
            if 'services' not in str(services_path).lower():
                warnings.warn('SERVICES path is suspicious - does not contain SERVICES')
            if not services_path == self.state.services:
                self.switch_services(services_path)

        if del_log:
            self.delete_logs()

    def start_app(self):
        if is_ase_run():
            t = threading.Thread(target=self.start_tcrf_thread, daemon=True)
            t.start()
            wait_for_application_start(self.cfg.config.ossl, cmd_args=str(self.cfg.config.tcrf_partition_id))
            pass

    def start_tcrf_thread(self):
        try:
            os.system(
                f'start cmd /k "cd {self.cfg.config.apu} & {self.cfg.config.ossl} {self.cfg.config.tcrf_partition_id} & exit"')
        except Exception as ex:
            self.log.exception(ex)

    def setup_tcrf_to_not_equipped(self):
        config = get_oms_repository_config()
        partition_to_not_equipped(config.oms_runtime.oms_tcrf_partition_id)

    def upload_to_tcrf_record_storage(self, source_file):
        _, filename = os.path.split(source_file)
        upload_file(source_file, rf"APU\TCRF_01\{filename}")

    def get_files_list_from_tcrf_record_storage(self):
        files = get_files_list(rf"APU\TCRF_01/*")
        return files

    def clear_tcrf_record_storage(self):
        files = get_files_list(rf"APU\TCRF_01/*")
        for file in files:
            delete_file(file)

    def start_bdtte(self):
        if is_ase_run() and self.bdtte is None:
            self.bdtte = Bdtte(Bdtte.BdtteInstance.TCRF)
        elif self.bdtte is not None:
            self.bdtte.start()

    def __del__(self):
        if self.bdtte is not None:
            self.bdtte.stop()
        if self.dlte is not None:
            self.dlte.stop()


class TcrfBenchModel:
    def __init__(self):
        ate = AteFactory().get_ate_device()
        wait_for_ate_init(ate)
        self.ate_tcrf = ate
        self.external_dependencies = munch.munchify({'input_io_manager': None,
                                                     'output_io_manager': None,
                                                     'ate': ate})
        self.load_model()

    def start_bench(self):
        self.t1 = threading.Thread(target=measure_cpu, daemon=True)
        self.t1.start()
        self.bench_object = TestBenchContainer().get_instance()
        self.bench_object.stop()
        self.bench_object.start()

        ate = AteFactory().get_ate_device()
        wait_for_ate_init(ate)
        self.ate_tcrf = ate
        self.external_dependencies.ate = self.ate_tcrf

    def load_model(self):
        maintenance_model_loader = MaintenanceModelLoader()
        maintenance_model_loader.load_oem()
        self.model = maintenance_model_loader

        self.io_input_manager = InputParameterManager(maintenance_model_loader, get_oms_repository_config())
        self.io_output_manager = OutputParameterManagerTcrf(maintenance_model_loader, get_oms_repository_config())
        self.external_dependencies.input_io_manager = self.io_input_manager
        self.external_dependencies.output_io_manager = self.io_output_manager

        ate = AteFactory().get_ate_device()
        wait_for_ate_init(ate)
        self.ate_tcrf = ate
        self.external_dependencies.ate = self.ate_tcrf
