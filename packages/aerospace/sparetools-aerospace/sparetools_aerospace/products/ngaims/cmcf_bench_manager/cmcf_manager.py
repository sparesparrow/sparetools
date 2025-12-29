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
from sparetools_aerospace.products.ngaims.common_functions import upload_ldi, upload_omi, upload_hdb, \
    upload_pdb, delete_hdb, delete_cmcf_log_file, delete_hdb_journal_file, delete_pdb, is_ase_run
from sparetools_aerospace.products.ngaims.file_transfer_apps.file_transfer_apps import Bdtte, Dlte
from sparetools_aerospace.products.ngaims.io_parameters.parameters_manager import InputParameterManager, OutputParameterManager
from sparetools_aerospace.products.ngaims.maintenance_model.maintenance_model_composition import MaintenanceModelComposition
from sparetools_aerospace.products.ngaims.maintenance_model.maintenance_model_loader import MaintenanceModelLoader
from sparetools_aerospace.products.ngaims.setup_environment import get_oms_repository_config
from sparetools_aerospace.products.ngaims.test_common import CommonNgaimsAppManager
from sparetools_aerospace.products.ngaims.test_execution.oms_repository_configuration import OmsRepositoryConfiguration
from sparetools_aerospace.products.ngaims.test_execution.run_test_functions import partition_to_not_equipped
from sparetools_aerospace.products.ngaims.test_execution.run_test_functions import wait_for_cmcf_init


class CmcfState:
    def __init__(self):
        self.ldi = ''
        self.hdb = ''
        self.omi = ''
        self.pdb = ''
        self.delete_logs = False


class CmcfManager(BaseAppManager, CommonNgaimsAppManager):
    def __init__(self, invalid_db=False, reset_dbs=True):
        super().__init__()
        self.bdtte = None
        self.dlte = None
        self.bm = None
        self.state = CmcfState()
        self.invalid_db = invalid_db
        self.reload_model = False
        self.active_model = None
        self.models = {}
        self.model_is_loaded = False

        prod_dev = get_oms_repository_config()['PACKAGE_ROOT_ngaims-product-dev']
        if reset_dbs:
            self.switch_ldi(Path(prod_dev, '_Build', 'SOURCE', 'SLDB', 'LDI', 'cmcf_ldi.db'))
            self.switch_omi(Path(prod_dev, '_Build', 'SOURCE', 'SLDB', 'OMI', 'oms_omi.db'))
        self.delete_hdb()
        self.delete_pdb()
        self.delete_logs()
        self.cfg = OmsRepositoryConfiguration()
        if is_ase_run():
            self.setup_cmcf_to_not_equipped()
        self.log = logging.getLogger('__main__.' + __name__)

    def load_model(self):
        try:
            model = CmcfBenchModel(invalid_db=self.invalid_db, reload_model=self.reload_model,
                                   model_is_loaded=self.model_is_loaded)
            if model.is_model_load_bypassed():
                self.active_model.ate_cmcf = model.ate_cmcf
                self.active_model.external_dependencies.ate = model.external_dependencies.ate
            else:
                self.active_model = model

            self.model_is_loaded = True
            self.models = {'default': self.active_model}
            super().reload_targets(get_oms_repository_config().oms_repository_layout.omi_path)
        except Exception as e:
            self.log.exception(e)

    def set_bench_manager(self, bench_man: BenchManager):
        self.bm = bench_man

    def reset(self):
        self.state = CmcfState()

    def switch_ldi(self, ldi_path):
        if not self.state.ldi == ldi_path:
            self.state.ldi = ldi_path
            if self.bm:
                self.bm.bench_state.restart_needed = True
                self.bm.stop_bench()
                self.reload_model = True
            upload_ldi(ldi_path)

    def switch_omi(self, omi_path):
        if not self.state.omi == omi_path:
            self.state.omi = omi_path
            if self.bm:
                self.bm.bench_state.restart_needed = True
                self.bm.stop_bench()
            upload_omi(omi_path)

    def switch_hdb(self, hdb_path):
        if not self.state.hdb == hdb_path:
            self.state.hdb = hdb_path
            if self.bm:
                self.bm.bench_state.restart_needed = True
                self.bm.stop_bench()
            upload_hdb(hdb_path)

    def delete_hdb(self):
        self.state.hdb = 'empty'
        if self.bm:
            self.bm.bench_state.restart_needed = True
            self.bm.stop_bench()
        delete_hdb()

    def switch_pdb(self, pdb_path):
        if not self.state.pdb == pdb_path:
            self.state.pdb = pdb_path
            if self.bm:
                self.bm.bench_state.restart_needed = True
                self.bm.stop_bench()
            upload_pdb(pdb_path)

    def delete_pdb(self):
        self.state.pdb = 'empty'
        if self.bm:
            self.bm.bench_state.restart_needed = True
            self.bm.stop_bench()
        delete_pdb()

    def delete_logs(self):
        if self.bm:
            self.bm.bench_state.restart_needed = True
            self.bm.stop_bench()
        delete_cmcf_log_file()

    def delete_journal_file(self):
        if self.bm:
            self.bm.bench_state.restart_needed = True
            self.bm.stop_bench()
        delete_hdb_journal_file()

    def set_up(self, ldi_path='', hdb_path='', omi_path='', pdb_path='', del_hdb=False, del_pdb=False, del_log=False,
               del_journal=False, invalid_db=False, bdtte=True, dlte=False, reload_model=False):
        self.reload_model = reload_model

        if bdtte and is_ase_run() and self.bdtte is None:
            self.bdtte = Bdtte()

        if dlte and is_ase_run() and self.dlte is None:
            self.dlte = Dlte()

        if not ldi_path == '':
            if 'ldi' not in str(ldi_path).lower():
                warnings.warn('LDI path is suspicious - does not contain LDI')
            if not ldi_path == self.state.ldi:
                self.switch_ldi(ldi_path)

        if not hdb_path == '':
            if 'hdb' not in str(hdb_path).lower():
                warnings.warn('HDB path is suspicious - does not contains HDB')
            if not hdb_path == self.state.hdb:
                self.switch_hdb(hdb_path)

        if not omi_path == '':
            if 'omi' not in str(omi_path).lower():
                warnings.warn('OMI path is suspicious - does not contains OMI')
            if not omi_path == self.state.omi:
                self.switch_omi(omi_path)

        if not pdb_path == '':
            if 'pdb' not in str(pdb_path).lower():
                warnings.warn('PDB path is suspicious - does not contains PDB ')
            if not pdb_path == self.state.pdb:
                self.switch_pdb(pdb_path)

        if del_hdb:
            self.delete_hdb()

        if del_pdb:
            self.delete_pdb()

        if del_log:
            self.delete_logs()

        if del_journal:
            self.delete_journal_file()

        self.invalid_db = invalid_db

    def start_app(self):
        if is_ase_run():
            config = get_oms_repository_config()
            t = threading.Thread(target=self.start_cmcf_thread, daemon=True)
            t.start()
            ate = AteFactory().get_ate_device(config)
            try:
                wait_for_cmcf_init(ate)
            except Exception as e:
                self.log.exception(e)

    def start_cmcf_thread(self):
        try:
            os.system(
                f'start cmd /k "cd {self.cfg.config.apu} & {self.cfg.config.ossl} {self.cfg.config.cmc_partition_id} & exit"')
        except Exception as ex:
            self.log.exception(ex)

    def setup_cmcf_to_not_equipped(self):
        config = get_oms_repository_config()
        partition_to_not_equipped(config.oms_runtime.oms_cmcf_partition_id)

    def get_active_model(self):
        self.bm.start_bench()
        return self.active_model

    def __del__(self):
        if self.bdtte is not None:
            self.bdtte.stop()
        if self.dlte is not None:
            self.dlte.stop()


class CmcfBenchModel:
    def __init__(self, invalid_db=False, reload_model=False, model_is_loaded=False):
        ate = AteFactory().get_ate_device()
        wait_for_cmcf_init(ate)
        self.ate_cmcf = ate
        self.external_dependencies = munch.munchify({'input_io_manager': None,
                                                     'output_io_manager': None,
                                                     'ate': ate})

        self.invalid_db = invalid_db
        self.model_is_loaded = model_is_loaded
        self.reload_model = reload_model
        self.model_load_bypassed = False

        self.load_model()

    def is_model_load_bypassed(self):
        return self.model_load_bypassed

    def start_bench(self):
        self.t1 = threading.Thread(target=measure_cpu, daemon=True)
        self.t1.start()
        self.bench_object = TestBenchContainer().get_instance()
        self.bench_object.stop()
        self.bench_object.start()

        ate = AteFactory().get_ate_device()
        wait_for_cmcf_init(ate)
        self.ate_cmcf = ate
        self.external_dependencies.ate = self.ate_cmcf

    def load_model(self):
        if not self.invalid_db and (not self.model_is_loaded or self.reload_model):
            maintenance_model_loader = MaintenanceModelLoader()
            maintenance_model_loader.load_ldi()
            self.model = maintenance_model_loader
            self.io_input_manager = InputParameterManager(maintenance_model_loader, get_oms_repository_config())
            self.io_output_manager = OutputParameterManager(maintenance_model_loader, get_oms_repository_config())
            self.external_dependencies.input_io_manager = self.io_input_manager
            self.external_dependencies.output_io_manager = self.io_output_manager
            self.compose_model()
            self.model_is_loaded = True
            self.model_load_bypassed = False
        else:
            self.model_load_bypassed = True

        ate = AteFactory().get_ate_device()
        wait_for_cmcf_init(ate)
        self.ate_cmcf = ate
        self.external_dependencies.ate = self.ate_cmcf

    def compose_model(self):
        self.model_manager = MaintenanceModelComposition(self.model, self.external_dependencies)
        self.fde_manager = self.model_manager.flight_deck_effects_manager
        self.ms_manager = self.model_manager.member_systems_manager
        self.mm_manager = self.model_manager.maintenance_messages_manager
        self.corr_manager = self.model_manager.fde_mm_correlation_manager
        self.lru_manager = self.model_manager.lru_manager
        self.bus_manager = self.model_manager.bus_manager
