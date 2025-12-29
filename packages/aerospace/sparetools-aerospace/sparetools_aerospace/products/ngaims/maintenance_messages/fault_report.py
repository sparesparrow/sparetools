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
// File Name: fault_report.py
//
// Program:   TITAN
//
// Purpose:   FAULT REPORT representation class.
//
// Notes:     None
//
//********************************************************************************************
//********************************************************************************************
"""
from ngapy.io_platform.message_composition import get_complete_validity
from sparetools_aerospace.products.ngaims.common_functions import set_status_for_multiple_entities
from sparetools_aerospace.products.ngaims.maintenance_messages.discrete import OmsDiscrete


class OmsFaultReport:
    def __init__(self, item_description: dict, external_dependencies, parent):
        self.external_dependencies = external_dependencies
        self.id = item_description['Id']
        self.sequence_id = item_description['ContId']
        self.mm_parent = parent
        self.mm_id = item_description['MmId']
        self.ms_id = item_description['MsId']
        self.retd = item_description['RisingEdgeTd']
        self.fetd = item_description['FallingEdgeTd']
        self.crtd = item_description['CascadeRemovalTd']
        self.cdtd = item_description['CascadeDisappearTd']
        self.stored_status = None

        # list of discrete instances used for setting FR status and belonging to this FR
        self.discretes = []
        for discrete in item_description['Discretes']:
            self.discretes.append(OmsDiscrete(discrete, self.external_dependencies, self))

    def get_stored_status(self):
        return self.stored_status

    def set_status(self, status, validity=get_complete_validity()):
        set_status_for_multiple_entities(self.external_dependencies.input_io_manager,
                                         self.discretes,
                                         status,
                                         validity)

    def get_status(self):
        # TODO: Implement this once ATE API is available
        return self.get_stored_status()
