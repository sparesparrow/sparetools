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
// File Name: flight_deck_effect_manager.py
//
// Program:   TITAN
//
// Purpose:   Flight Deck Effect manager class.
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
from sparetools_aerospace.products.ngaims.filter_samples import Functor, equality
from sparetools_aerospace.products.ngaims.fligh_deck_effect.flight_deck_effect import OmsFlightDeckEffect
from sparetools_aerospace.products.ngaims.maintenance_model.model_base_manager import ModelBaseManager


class OmsFlightDeckEffectManager(ModelBaseManager):
    def __init__(self, maintenance_model, external_dependencies, internal_dependencies=None):
        super(OmsFlightDeckEffectManager, self).__init__()
        self.cas_master_instances = list()
        self.external_dependencies = external_dependencies
        self.maintenance_model = maintenance_model
        fde_model = self.maintenance_model.get_table_dict('Fde')
        self.in_param_model = self.maintenance_model.get_table_dict('InParam')
        self._load_cas_instances()

        self.end_tick = 0
        for key, value in fde_model.items():
            self.model_dict[key] = OmsFlightDeckEffect(value, external_dependencies, internal_dependencies, self)
        self.cas_master_priority = None
        self.cas_master_validity = None

        self.active_cas_master = None

    def _load_cas_instances(self):
        self.cas_master_instances.clear()
        for key, value in self.in_param_model.items():
            if "cas_priority." in value.get("LogicalName"):
                self.cas_master_instances.append(value.get("LogicalInstance"))

    def set_active_cas_master_instance(self, instance=0, set_signals=True):
        self.active_cas_master = instance
        if set_signals:
            if instance == 0:
                instance = self.cas_master_instances[0]
            for inst in self.cas_master_instances:
                if inst == instance:
                    self.set_cas_master_validity(instance=inst, value=True)
                    self.set_cas_master_priority(instance=inst, value=True)
                else:
                    self.set_cas_master_validity(instance=inst, value=False)
                    self.set_cas_master_priority(instance=inst, value=False)

    def get_all_fdes(self):
        return super(OmsFlightDeckEffectManager, self).get_table_dict()

    def get_fde_by_id(self, fde_id):
        return super(OmsFlightDeckEffectManager, self).search_by_id(fde_id)

    def set_all_fdes(self, status=True, custom_list=None, validity=get_complete_validity(), **kwargs):
        set_status_for_multiple_entities(self.external_dependencies.input_io_manager,
                                         self.get_execution_list(custom_list),
                                         status,
                                         validity,
                                         **kwargs)

    @staticmethod
    def get_functor_for_cas_fdes():
        return Functor(equality, 'is_cas', True)

    @staticmethod
    def get_functor_for_generic_fdes():
        return Functor(equality, 'is_cas', False)

    def get_all_active_fdes(self, tick=0):
        self.get_transitions_fdes(tick)
        return self.filter_by_attribute(Functor(equality, 'ate_status', True))

    def get_all_inhibited_fdes(self, tick=0):
        self.get_transitions_fdes(tick)
        return self.filter_by_attribute(Functor(equality, 'ate_status_raw', 'Inhibited'))

    def get_transitions_fdes(self, tick=0):
        fde_status = self.external_dependencies.ate.get_active_fdes(tick)
        self.end_tick = fde_status.data.endTick
        transitions = []
        for key, fde in self.model_dict.items():
            fde_transition_list = list(filter(lambda transition: transition.type == 'Fde' and
                                                                 transition.fdeId == fde.sequence_id,
                                              fde_status.data.transitions))
            fde.store_transition_list(fde_transition_list, self.end_tick)
            if fde_transition_list:
                transitions.append(fde)
        return transitions

    def get_all_fde_definitions(self):
        all_mms_definitions = self.external_dependencies.ate.get_all_fde_defs()
        for fde_definition in all_mms_definitions.data.fdeDefs:
            mm_definition = munch.munchify(fde_definition)
            if fde_definition.dbId not in self.model_dict:
                raise NgapyConfigurationError(f'Ate returned not expected FDE dbId: {fde_definition.dbId}.'
                                              f' Have you used same LDI?')
            self.model_dict[fde_definition.dbId].check_ate_response(fde_definition)

    def set_cas_master_priority(self, value=1, validity=get_complete_validity(), instance=0):
        self.cas_master_priority = self.external_dependencies.input_io_manager.get_parameter_by_logical_name(
            f'cas_priority.{instance}')
        self.external_dependencies.input_io_manager.set_values(self.cas_master_priority, [(value, validity)])

    def set_cas_master_validity(self, value=1, validity=get_complete_validity(), instance=0):
        self.cas_master_validity = self.external_dependencies.input_io_manager.get_parameter_by_logical_name(
            f'cas_validity.{instance}')
        self.external_dependencies.input_io_manager.set_values(self.cas_master_validity, [(value, validity)])
