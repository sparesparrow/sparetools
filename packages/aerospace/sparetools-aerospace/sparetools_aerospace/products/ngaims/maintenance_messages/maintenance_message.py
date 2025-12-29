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
// File Name: maintenance_message.py
//
// Program:   TITAN
//
// Purpose:   Maintenance message representation class.
//
// Notes:     None
//
//********************************************************************************************
//********************************************************************************************
"""
from ngapy.exceptions.ngapy_exceptions import NgapyConfigurationError
from ngapy.io_platform.message_composition import get_complete_validity
from sparetools_aerospace.products.ngaims.common_functions import set_status_for_multiple_entities
from sparetools_aerospace.products.ngaims.maintenance_messages.fault_report import OmsFaultReport
from sparetools_aerospace.products.ngaims.fde_mm_common import FdeMmCommon


class OmsMaintenanceMessage(FdeMmCommon):
    def __init__(self, item_description: dict, external_dependencies, internal_dependencies, parent):
        super(OmsMaintenanceMessage, self).__init__()
        self.external_dependencies = external_dependencies
        self.internal_dependencies = internal_dependencies
        self.id = item_description['Id']
        self.sequence_id = item_description['ContId']
        self.parent = parent
        #self.ms_id = item_description['MsId']
        self.name = item_description['Name']
        self.number = item_description['Number']
        self.description = item_description['Description']
        self.storable_phases = item_description['StorablePhases']
        self.ata_section_id = item_description['AtaMajorSecId']
        self.type = item_description['MmTypeLink']
        self.last_ate_tick = 0
        self.mm_transition_list = []
        self.fault_reports = []
        self.amtoss_references = []
        self.is_downlinkable = item_description['IsDownlinkable']
        self.occurrence_limit = item_description['OccurrenceLimit']
        self.downlink_phases = item_description['DownlinkPhases']

        for amtoss_refs in item_description['MmAmtossAmtossRefs']:
            self.amtoss_references.append(internal_dependencies.amtoss_reference_manager.search_by_id(amtoss_refs[1]['AmtossId']))

        for fault_report in item_description['Frs']:
            self.fault_reports.append(OmsFaultReport(fault_report, external_dependencies, self))

    def set_status(self, status, validity=get_complete_validity()):
        self.set_all_fault_reports(status, validity)

    def set_all_fault_reports(self, status, validity=get_complete_validity()):
        set_status_for_multiple_entities(self.external_dependencies.input_io_manager,
                                         self.fault_reports,
                                         status,
                                         validity)

    def get_status_by_ate(self, tick=0):
        # Discussed and promised by PavelU, that we can get single MM state API in ATE.
        # mm_status2 = self.external_dependencies.ate.get_mm_detail(self.id)
        active_mms = self.parent.get_all_active_mms(tick)
        if self in active_mms:
            return True
        else:
            return False

    def get_current_status_by_ate(self):
        return self.external_dependencies.ate.get_mm_detail(self.sequence_id)

    def check_ate_response(self, ate_entity_definition):
        if self.id != ate_entity_definition.dbId or \
                self.name != ate_entity_definition.name or \
                self.description != ate_entity_definition.description or \
                self.number != ate_entity_definition.code or \
                self.type != ate_entity_definition.type or \
                self.ata_section_id != ate_entity_definition.ataSectionId:
            raise NgapyConfigurationError(f'Ate returned information not matching with LDI for MM: {self.name}!')

    @property
    def contributing_ms_list(self):
        if self.last_transition:
            return self.last_transition.contributingMsList
        else:
            return []
