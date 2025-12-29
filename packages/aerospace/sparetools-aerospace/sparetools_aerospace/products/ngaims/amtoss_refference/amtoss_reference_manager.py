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
// Copyright: Honeywell International, 2021
//
// File Name: amtoss_reference_manager.py
//
// Program:   TITAN
//
// Purpose:   Amtoss Reference manager representation class.
//
// Notes:     None
//
//********************************************************************************************
//********************************************************************************************
"""
from sparetools_aerospace.products.ngaims.amtoss_refference.amtoss_reference import OmsAmtossReference
from sparetools_aerospace.products.ngaims.maintenance_model.model_base_manager import ModelBaseManager


class OmsAmtossReferenceManager(ModelBaseManager):
    def __init__(self, maintenance_model, external_dependencies, internal_dependencies=None):
        super(OmsAmtossReferenceManager, self).__init__()
        self.external_dependencies = external_dependencies
        amtoss_reference_model = maintenance_model.get_table_dict('AmtossRef')
        for key, value in amtoss_reference_model.items():
            self.model_dict[key] = OmsAmtossReference(value, external_dependencies, internal_dependencies)

    def get_all_amtoss_references(self):
        return super(OmsAmtossReferenceManager, self).get_table_dict()
