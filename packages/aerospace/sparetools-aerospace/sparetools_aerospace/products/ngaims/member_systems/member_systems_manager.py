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
// File Name: member_systems_manager.py
//
// Program:   TITAN
//
// Purpose:   Member system manager class.
//
// Notes:     None
//
//********************************************************************************************
//********************************************************************************************
"""
import time
from threading import Thread, Event

import munch

from ngapy.exceptions.ngapy_exceptions import NgapyConfigurationError
from sparetools_aerospace.products.ngaims.common_functions import set_status_for_multiple_entities
from sparetools_aerospace.products.ngaims.constants import MsDispStatus
from sparetools_aerospace.products.ngaims.filter_samples import Functor, get_string_comparison_function
from sparetools_aerospace.products.ngaims.maintenance_model.model_base_manager import ModelBaseManager
from sparetools_aerospace.products.ngaims.member_systems.member_system import OmsMemberSystem
from ngapy.util.thread_helpers import periodic_thread


class OmsMemberSystemsManager(ModelBaseManager):
    def __init__(self, maintenance_model, external_dependencies, internal_dependencies=None):
        super(OmsMemberSystemsManager, self).__init__()
        self.external_dependencies = external_dependencies
        ms_model = maintenance_model.get_table_dict('Ms')
        for key, value in ms_model.items():
            self.model_dict[key] = OmsMemberSystem(value, external_dependencies, internal_dependencies)
        self.simulation_thread_end = Event()
        self.simulation_thread = None

    def __del__(self):
        self.stop_system_config_simulation()

    def get_all_mss(self):
        return super(OmsMemberSystemsManager, self).get_table_dict()

    def set_all_ms_status(self, status: MsDispStatus = MsDispStatus.NORM_OP, custom_list=None, validity=None):
        set_status_for_multiple_entities(self.external_dependencies.input_io_manager,
                                         self.get_execution_list(custom_list),
                                         status,
                                         validity)

    def get_all_ms_definitions(self):
        all_ms_definitions = self.external_dependencies.ate.get_all_ms_def()
        if not all_ms_definitions:
            raise NgapyConfigurationError("ATE didn't provide any MS definitions.")
        for ms_definition in all_ms_definitions.data.memberSystemsDefinitions:
            ms_definition = munch.munchify(ms_definition)
            if ms_definition.dbId not in self.model_dict:
                raise NgapyConfigurationError(f'Ate returned not expected MS dbId: {ms_definition.dbId}.'
                                              f' Have you used same LDI?')
            self.model_dict[ms_definition.dbId].check_ate_response(ms_definition)

    def get_all_ms_status(self):
        all_ms_status = self.external_dependencies.ate.get_all_ms_sts()
        for ms_status in all_ms_status.data.statuses:
            self.model_dict[self.get_ldi_id_for_sequence_id(ms_status.id)].update_ate_status(ms_status)

    def get_ms_by_mnemonic(self, mnemonic, case_sensitive=True):
        return super(OmsMemberSystemsManager, self).search_by_attribute(
            Functor(get_string_comparison_function(case_sensitive), 'mnemonic', mnemonic))

    def get_ms_by_name(self, name, case_sensitive=True):
        return super(OmsMemberSystemsManager, self).search_by_attribute(
            Functor(get_string_comparison_function(case_sensitive), 'name', name))

    def get_ms_by_id(self, ms_id) -> OmsMemberSystem:
        return super(OmsMemberSystemsManager, self).search_by_id(ms_id)

    def run_system_config_simulation_thread(self, ms_list):
        self.external_dependencies.input_io_manager.start_queued_mode()
        for ms in ms_list:
            ms.set_system_configs()
        self.external_dependencies.input_io_manager.stop_queued_mode()

    def run_system_config_simulation(self, custom_list=None):
        self.stop_system_config_simulation()
        selected_ms = self.get_execution_list(custom_list)
        self.simulation_thread = Thread(target=periodic_thread,
                                        name='System configuration thread',
                                        daemon=True,
                                        args=(1.0, self.run_system_config_simulation_thread,
                                              self.simulation_thread_end, selected_ms,))
        self.simulation_thread.start()

    def stop_system_config_simulation(self):
        if self.simulation_thread:
            self.simulation_thread_end.set()
            self.simulation_thread.join()
            self.simulation_thread_end.clear()
        self.simulation_thread = None

    def get_all_ms_config_definitions(self):
        all_ms_config_definitions = self.external_dependencies.ate.get_all_sys_cfg_defs()
        for ms_config_definition in all_ms_config_definitions.data.configs:
            ms_db_id = self.get_ldi_id_for_sequence_id(ms_config_definition.msId)
            if ms_db_id not in self.model_dict:
                raise NgapyConfigurationError(f'Ate returned not expected MS dbId: {ms_db_id}.'
                                              f' Have you used same LDI?')
            self.model_dict[ms_db_id].check_ate_response_config_def(ms_config_definition)
        return all_ms_config_definitions

    def get_all_lru_config_definitions(self):
        all_lru_config_defs = self.external_dependencies.ate.get_all_lru_cfg_defs()
        return all_lru_config_defs

    def get_all_ms_config_values(self):
        return self.external_dependencies.ate.get_all_ms_config_values()
