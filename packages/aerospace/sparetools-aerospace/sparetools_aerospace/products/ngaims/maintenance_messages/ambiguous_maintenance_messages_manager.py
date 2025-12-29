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
from sparetools_aerospace.products.ngaims.maintenance_messages.ambiguous_maintenance_message import OmsAmbiguousMm
from sparetools_aerospace.products.ngaims.maintenance_model.model_base_manager import ModelBaseManager


class OmsAmbiguousMaintenanceMessageManager(ModelBaseManager):
    def __init__(self, maintenance_model, external_dependencies, internal_dependencies=None):
        super(OmsAmbiguousMaintenanceMessageManager, self).__init__()
        self.external_dependencies = external_dependencies
        ambiguous_mm_model = maintenance_model.get_table_dict('AmbiguousMm')
        self.end_tick = 0
        for key, value in ambiguous_mm_model.items():
            self.model_dict[key] = OmsAmbiguousMm(value, external_dependencies, internal_dependencies, self)

    def get_all_ambiguous_mms(self):
        return super(OmsAmbiguousMaintenanceMessageManager, self).get_table_dict()
