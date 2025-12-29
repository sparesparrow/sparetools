#              AUTHORIZED IN WRITING. THIS UNPUBLISHED WORK IS PROTECTED BY
#              THE LAWS OF THE UNITED STATES AND OTHER COUNTRIES. IN THE
#              EVENT OF PUBLICATION, THE FOLLOWING NOTICE SHALL APPLY:
#              COPR. 2020-2021 HONEYWELL INTERNATIONAL, INC. ALL RIGHTS RESERVED.
#
"""
//********************************************************************************************
//
//
// File Name: cmcf_bench_manager.py
//
// Program:   TITAN
//
// Purpose:   Maintenance model container unifying preparation of cmcf
//
// Notes:     None
//
//********************************************************************************************
//********************************************************************************************
"""
import munch
import threading

from sparetools_aerospace.products.ngaims.maintenance_model.maintenance_model_composition import MaintenanceModelComposition
from sparetools_aerospace.products.ngaims.maintenance_model.maintenance_model_loader import MaintenanceModelLoader
from sparetools_aerospace.products.ngaims.test_execution.run_test_functions import wait_for_cmcf_init, prepare_cmcf_bench, \
    prepare_tcrf_bench
from sparetools_aerospace.products.ngaims.ate_interface.cmcf_ate import AteFactory
from sparetools_aerospace.products.ngaims.io_parameters.parameters_manager import InputParameterManager, OutputParameterManager
from sparetools_aerospace.products.ngaims.setup_environment import get_oms_repository_config
from sparetools_aerospace.products.ngaims.common_functions import upload_ldi, delete_log_file, upload_omi, upload_hdb, \
    upload_pdb, delete_hdb, stop_bench, upload_tcrf_services, upload_tcrf_oem, delete_cmcf_log_file, \
    delete_hdb_journal_file
from ngapy.bench.bench_factory import TestBenchContainer, measure_cpu


class CmcfState:
    def __init__(self):
        self.ldi = ''
        self.hdb = ''
        self.omi = ''
        self.pdb = ''
        self.delete_logs = False


class TcrfState:
    def __init__(self):
        self.oem = ''
        self.services = ''
        self.delete_logs = False


class BenchState:
    def __init__(self):
        self.bench_running = False


class BenchManager:
    def __init__(self, selected_modules):
        self.managers = selected_modules
        self.bench_object = TestBenchContainer().get_instance()
        self.bench_object.stop()
        self.bench_state = BenchState()
        self.restart_needed = True

        for mngr in self.managers:
            self.managers[mngr].set_bench_manager(self)

    def set_up(self, bench_running=True):
        if bench_running:
            self.start_bench()
        else:
            self.stop_bench()

    def get_modules(self):
        return self.managers

    def stop_bench(self):
        if self.bench_state.bench_running:
            self.bench_object.stop()
            self.bench_state.bench_running = False

    def start_bench(self):
        if not self.bench_state.bench_running:
            self.bench_object.start()
            self.bench_state.bench_running = True
            if self.restart_needed:
                for mngr in self.managers:
                    self.managers[mngr].load_model()
                self.restart_needed = False


class CmcfBenchManagerT:
    def __init__(self):
        self.state = CmcfState()
        prepare_cmcf_bench()

    def load_model(self):
        self.active_model = CmcfBenchModel()
        self.models = {'default': self.active_model}

    def set_bench_manager(self, bench_man: BenchManager):
        self.bm = bench_man

    def switch_ldi(self, ldi_path):
        if not self.state.ldi == ldi_path:
            self.state.ldi = ldi_path
            self.bm.bench_state.restart_needed = True
            self.bm.stop_bench()
            upload_ldi(ldi_path)

    def switch_omi(self, omi_path):
        if not self.state.omi == omi_path:
            self.state.omi = omi_path
            self.bm.bench_state.restart_needed = True
            self.bm.stop_bench()
            upload_omi(omi_path)

    def switch_hdb(self, hdb_path):
        if not self.state.hdb == hdb_path:
            self.state.hdb = hdb_path
            self.bm.bench_state.restart_needed = True
            self.bm.stop_bench()
            upload_hdb(hdb_path)

    def delete_hdb(self):
        self.state.hdb = 'empty'
        self.bm.bench_state.restart_needed = True
        self.bm.stop_bench()
        delete_hdb()

    def switch_pdb(self, pdb_path):
        if not self.state.pdb == pdb_path:
            self.state.pdb = pdb_path
            self.bm.bench_state.restart_needed = True
            self.bm.stop_bench()
            upload_pdb(pdb_path)

    def delete_pdb(self, pdb_path):
        self.state.pdb = 'empty'
        self.bm.bench_state.restart_needed = True
        self.bm.stop_bench()
        upload_pdb(pdb_path)

    def delete_logs(self):
        self.bm.bench_state.restart_needed = True
        self.bm.stop_bench()
        delete_cmcf_log_file()

    def delete_journal_file(self):
        self.bm.bench_state.restart_needed = True
        self.bm.stop_bench()
        delete_hdb_journal_file()

    def set_up(self, ldi_path='', hdb_path='', omi_path='', pdb_path='', del_hdb=False, del_pdb=False, del_log=False, del_journal=False):
        if not ldi_path == '' and not ldi_path == self.state.ldi:
            self.switch_ldi(ldi_path)

        if not hdb_path == '' and not hdb_path == self.state.hdb:
            self.switch_hdb(hdb_path)

        if not omi_path == '' and not omi_path == self.state.ommi:
            self.switch_omi(omi_path)

        if not pdb_path == '' and not pdb_path == self.bstate.pdb:
            self.switch_pdb(pdb_path)

        if del_hdb:
            self.delete_hdb()

        if del_pdb:
            self.delete_pdb()

        if del_log:
            self.delete_logs()

        if del_journal:
            self.delete_journal_file()


class CmcfBenchManager:

    def __init__(self, ldi_path=None):
        prepare_cmcf_bench()
        prepare_tcrf_bench()
        self.default_ldi_str = None
        if ldi_path is not None:
            upload_ldi(ldi_path)
            self.default_ldi_str = ldi_path
        self.start_bench()
        self.active_model = CmcfBenchModel()
        self.models = {'default': self.active_model}

    def switch_ldi(self, ldi_path, switch_model=True):
        self.stop_bench()
        upload_ldi(ldi_path)
        self.start_bench()
        if switch_model:
            if ldi_path in self.models.keys():
                self.active_model = self.models[ldi_path]
            else:
                self.active_model = CmcfBenchModel()
                self.models[ldi_path] = self.active_model

    def switch_omi(self, omi_path):
        self.stop_bench()
        upload_omi(omi_path)
        self.start_bench()

    def switch_hdb(self, hdb_path):
        self.stop_bench()
        upload_hdb(hdb_path)
        self.start_bench()

    def switch_pdb(self, pdb_path):
        self.stop_bench()
        upload_pdb(pdb_path)
        self.start_bench()

    def restore_default_dbs(self):
        self.stop_bench()
        self.bench_object.restore()
        self.bench_object.delete_backup_files()
        if self.default_ldi_str:
            upload_ldi(self.default_ldi_str)
        self.start_bench()
        self.active_model = self.models['default']

    def stop_bench(self):
        self.bench_object.stop()

    def start_bench(self):
        delete_log_file()
        self.t1 = threading.Thread(target=measure_cpu, daemon=True)
        self.t1.start()
        self.bench_object = TestBenchContainer().get_instance()
        self.bench_object.stop()
        self.bench_object.start()

        ate = AteFactory().get_ate_device()
        wait_for_cmcf_init(ate)

    def restart_bench(self):
        self.stop_bench()
        self.start_bench()

    def __del__(self, *args, **kwargs):
        self.stop_bench()
        self.bench_object.restore()
        self.bench_object.delete_backup_files()

    def __getattr__(self, k):
        return getattr(self.active_model, k)


class CmcfBenchModel:
    def __init__(self):
        ate = AteFactory().get_ate_device()
        wait_for_cmcf_init(ate)
        self.ate_cmcf = ate
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
        wait_for_cmcf_init(ate)
        self.ate_cmcf = ate
        self.external_dependencies.ate = self.ate_cmcf

    def load_model(self):
        maintenance_model_loader = MaintenanceModelLoader()
        maintenance_model_loader.load_ldi()
        self.model = maintenance_model_loader
        self.io_input_manager = InputParameterManager(maintenance_model_loader, get_oms_repository_config())
        self.io_output_manager = OutputParameterManager(maintenance_model_loader, get_oms_repository_config())
        self.external_dependencies.input_io_manager = self.io_input_manager
        self.external_dependencies.output_io_manager = self.io_output_manager
        self.compose_model()

    def compose_model(self):
        self.model_manager = MaintenanceModelComposition(self.model, self.external_dependencies)
        self.fde_manager = self.model_manager.flight_deck_effects_manager
        self.ms_manager = self.model_manager.member_systems_manager
        self.mm_manager = self.model_manager.maintenance_messages_manager
        self.corr_manager = self.model_manager.fde_mm_correlation_manager
        self.lru_manager = self.model_manager.lru_manager
        self.bus_manager = self.model_manager.bus_manager
