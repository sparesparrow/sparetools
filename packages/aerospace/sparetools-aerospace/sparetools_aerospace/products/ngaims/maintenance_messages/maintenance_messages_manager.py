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
// File Name: maintenance_message_manager.py
//
// Program:   TITAN
//
// Purpose:   MM manager
//
// Notes:     None
//
//********************************************************************************************
//********************************************************************************************
"""
import munch

from ngapy.exceptions.ngapy_exceptions import NgapyConfigurationError
from ngapy.io_platform.message_composition import get_complete_validity
from sparetools_aerospace.products.ngaims.common_functions import set_status_for_multiple_entities
from sparetools_aerospace.products.ngaims.filter_samples import Functor, equality, get_string_comparison_function
from sparetools_aerospace.products.ngaims.maintenance_messages.maintenance_message import OmsMaintenanceMessage
from sparetools_aerospace.products.ngaims.maintenance_model.model_base_manager import ModelBaseManager


class OmsMaintenanceMessageManager(ModelBaseManager):
    def __init__(self, maintenance_model, external_dependencies, internal_dependencies=None):
        super(OmsMaintenanceMessageManager, self).__init__()
        self.external_dependencies = external_dependencies
        self.maintenance_model = maintenance_model
        mm_model = self.maintenance_model.get_table_dict('Mm')
        self.end_tick = 0
        for key, value in mm_model.items():
            self.model_dict[key] = OmsMaintenanceMessage(value, external_dependencies, internal_dependencies, self)


    def get_all_mms(self):
        return super(OmsMaintenanceMessageManager, self).get_table_dict()

    def get_all_mms_definitions(self):
        all_mms_definitions = self.external_dependencies.ate.get_all_mm_defs()
        for mm_definition in all_mms_definitions.data.mmDefs:
            mm_definition = munch.munchify(mm_definition)
            if mm_definition.dbId not in self.model_dict:
                raise NgapyConfigurationError(f'Ate returned not expected MM dbId: {mm_definition.dbId}.'
                                              f' Have you used same LDI?')
            self.model_dict[mm_definition.dbId].check_ate_response(mm_definition)

    def get_mm_by_id(self, mm_id):
        return super(OmsMaintenanceMessageManager, self).search_by_id(mm_id)

    def get_all_active_mms(self, tick=0):
        self.get_transitions_mms(tick)
        return self.filter_by_attribute(Functor(equality, 'ate_status', True))

    def get_transitions_mms(self, tick=0):
        mm_status = self.external_dependencies.ate.get_active_mms(tick)
        self.end_tick = mm_status.data.endTick
        transitions = []
        for key, mm in self.model_dict.items():
            mm_transition_list = list(filter(lambda transition: transition.type == 'Mm' and
                                                                transition.mmId == mm.sequence_id,
                                             mm_status.data.transitions))
            mm.store_transition_list(mm_transition_list, self.end_tick)
            if mm_transition_list:
                transitions.append(mm)
        return transitions

    def set_all_mms(self, status=True, custom_list=None, validity=get_complete_validity()):
        set_status_for_multiple_entities(self.external_dependencies.input_io_manager,
                                         self.get_execution_list(custom_list),
                                         status,
                                         validity)

    def get_mm_by_name(self, name, case_sensitive=True):
        return super(OmsMaintenanceMessageManager, self).search_by_attribute(
            Functor(get_string_comparison_function(case_sensitive), 'name', name))
