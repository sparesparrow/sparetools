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
// File Name: flight_deck_effect.py
//
// Program:   TITAN
//
// Purpose:   FDE representing class.
//
// Notes:     None
//
//********************************************************************************************
//********************************************************************************************
"""
import re

from ngapy.exceptions.ngapy_exceptions import NgapyConfigurationError
from ngapy.io_platform.message_composition import get_complete_validity
from sparetools_aerospace.products.ngaims.common_functions import set_status_for_multiple_entities
from sparetools_aerospace.products.ngaims.fde_mm_common import FdeMmCommon


class OmsFdeCasSrcs:
    def __init__(self, item_description: dict, external_dependencies, parent):
        self.external_dependencies = external_dependencies
        self.id = item_description['Id']
        self.sequence_id = item_description['ContId']
        self.fde = parent
        self.msg_code = item_description['MsgCode']
        self.root_cause_code = item_description['RootCauseCode']
        self.fde_src_rcs = item_description['FdeSrcRcRcs']

        self.in_param_pre_id = item_description['InParamFpPreLink']['InParamLink']['Id']
        self.pre_inhibit_signal = external_dependencies.input_io_manager.get_parameter_by_id(self.in_param_pre_id)
        self.in_param_post_id = item_description['InParamFpPostLink']['InParamLink']['Id']
        self.post_inhibit_signal = external_dependencies.input_io_manager.get_parameter_by_id(self.in_param_post_id)
        self.pre_inhibit_signals_not_src_selected = dict()
        self.post_inhibit_signals_not_src_selected = dict()
        self._get_all_instances_params(external_dependencies)

    def _get_all_instances_params(self, external_dependencies):
        fde_manager = self.fde.parent
        instances = fde_manager.cas_master_instances
        pre_inhibit_base = self.__get_param_base(self.pre_inhibit_signal.logical_name)
        post_inhibit_base = self.__get_param_base(self.post_inhibit_signal.logical_name)

        for i in instances:
            try:
                self.pre_inhibit_signals_not_src_selected[i] = external_dependencies.input_io_manager. \
                    get_parameter_by_logical_name(f"{pre_inhibit_base}.{i}")
            except KeyError:
                pass
            try:
                self.post_inhibit_signals_not_src_selected[i] = external_dependencies.input_io_manager. \
                    get_parameter_by_logical_name(f"{post_inhibit_base}.{i}")
            except KeyError:
                pass

    @staticmethod
    def __get_param_base(in_param_name):
        return re.match(r"\w*", in_param_name).group()

    def set_status(self, status, validity=get_complete_validity(), **kwargs):
        instance = kwargs.get('instance', None)
        if isinstance(status, list):
            pre, post = status[0], status[1]
        else:
            pre, post = status, status

        for fde_instance in self.fde.parent.cas_master_instances:
            if instance is None or instance == fde_instance:
                self.external_dependencies.input_io_manager.set_values(
                    self.pre_inhibit_signals_not_src_selected.get(fde_instance), [(pre, validity)])
                self.external_dependencies.input_io_manager.set_values(
                    self.post_inhibit_signals_not_src_selected.get(fde_instance), [(post, validity)])

class OmsFdeGenericSrcs:
    def __init__(self, item_description: dict, external_dependencies, parent):
        self.external_dependencies = external_dependencies
        self.id = item_description['Id']
        self.sequence_id = item_description['ContId']
        self.fde = parent
        self.in_param = external_dependencies.input_io_manager.get_parameter_by_id(item_description['InParamId'])

    def set_status(self, status, validity=get_complete_validity()):
        self.external_dependencies.input_io_manager.set_values(self.in_param, (status, validity))


class OmsFlightDeckEffect(FdeMmCommon):
    def __init__(self, item_description: dict, external_dependencies, internal_dependencies, parent):
        super(OmsFlightDeckEffect, self).__init__()
        self.external_dependencies = external_dependencies
        self.internal_dependencies = internal_dependencies
        self.id = item_description['Id']
        self.sequence_id = item_description['ContId']
        self.description = item_description['Description']
        self.falling_edge_delay = item_description['FallingEdgeTimeDelay']
        self.number = item_description['FdeNumber']
        self.fde_sev_id = item_description['FdeSevId']
        self.is_cas = item_description['IsCas']
        self.name = item_description['Name']
        self.rising_edge_time_delay = item_description['RisingEdgeTimeDelay']
        self.storable_phases = item_description['StorablePhases']
        self.is_downlinkable = item_description['IsDownlinkable']
        self.occurrence_limit = item_description['OccurrenceLimit']
        self.downlink_phases = item_description['DownlinkPhases']
        # We need only references for MMs
        self.mms = item_description['FdeMmCorrMms']
        self.fde_type_id = item_description['FdeTypeId']
        self.last_ate_tick = 0
        self.parent = parent
        self.amtoss_references = []

        for amtoss_refs in item_description['FdeAmtossAmtossRefs']:
            self.amtoss_references.append(
                internal_dependencies.amtoss_reference_manager.search_by_id(amtoss_refs[1]['AmtossId']))

        self.fde_cas_src = []
        for fde_cas_src in item_description['FdeCasSrcs']:
            self.fde_cas_src.append(OmsFdeCasSrcs(fde_cas_src, external_dependencies, self))
        self.fde_generic_src = []
        for fde_generic_src in item_description['FdeGenericSrcs']:
            self.fde_generic_src.append(OmsFdeGenericSrcs(fde_generic_src, external_dependencies, self))

        if self.is_cas and len(self.fde_generic_src):
            # TODO: Report this to KMS?
            # raise NgapyConfigurationError(f'FDE configuration error. Element with IsCas == True has generic sources:'
            #                              f' {item_description}')
            pass
        if not self.is_cas and len(self.fde_cas_src):
            # TODO: Report this to KMS?
            # raise NgapyConfigurationError(f'FDE configuration error. Element with IsCas == False'
            #                              f' does not have cas links: {item_description}')
            pass

    def get_status_by_ate(self, tick=0):
        # TODO: currently don't know what is returned, only raw data are provided
        return self.external_dependencies.ate.get_fde_state(self.sequence_id)

    def get_rc_value_by_ate(self, tick=0):
        # TODO: currently don't know what is returned, only raw data are provided
        return self.external_dependencies.ate.get_fde_state(self.sequence_id)

    def set_status(self, status, validity=get_complete_validity(), **kwargs):
        if self.is_cas:
            set_status_for_multiple_entities(self.external_dependencies.input_io_manager,
                                             self.fde_cas_src,
                                             status,
                                             validity,
                                             **kwargs)
        else:
            set_status_for_multiple_entities(self.external_dependencies.input_io_manager,
                                             self.fde_generic_src,
                                             status,
                                             validity)

    def check_ate_response(self, ate_entity_definition):
        if self.id != ate_entity_definition.dbId or \
                self.name != ate_entity_definition.name or \
                self.description != ate_entity_definition.description or \
                self.number != ate_entity_definition.number or \
                self.fde_sev_id != ate_entity_definition.fdeSeverityId:
            raise NgapyConfigurationError(f'Ate returned information not matching with LDI for FDE: {self.name}!')
