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
// File Name: root_cause_manager.py
//
// Program:   TITAN
//
// Purpose:   Root Cause manager class.
//
// Notes:     None
//
//********************************************************************************************
//********************************************************************************************
"""
import munch

from ngapy.exceptions.ngapy_exceptions import NgapyConfigurationError
from sparetools_aerospace.products.ngaims.fligh_deck_effect.root_cause import OmsRootCause
from sparetools_aerospace.products.ngaims.maintenance_model.model_base_manager import ModelBaseManager


class OmsRootCauseManager(ModelBaseManager):
    def __init__(self, maintenance_model, external_dependencies):
        super(OmsRootCauseManager, self).__init__()
        self.external_dependencies = external_dependencies
        rc_model = maintenance_model.get_table_dict('Rc')
        for key, value in rc_model.items():
            self.model_dict[key] = OmsRootCause(value, external_dependencies)

    def get_all_rcs(self):
        return super(OmsRootCauseManager, self).get_table_dict()

    def get_rc_by_id(self, mm_id):
        return super(OmsRootCauseManager, self).search_by_id(mm_id)

    def get_all_rc_definitions(self):
        all_rc_definitions = self.external_dependencies.ate.get_all_rc_defs()
        for rc_definition in all_rc_definitions.data.rcDefs:
            rc_definition = munch.munchify(rc_definition)
            if rc_definition.dbId not in self.model_dict:
                raise NgapyConfigurationError(f'Ate returned not expected RC dbId: {rc_definition.dbId}.'
                                              f' Have you used same LDI?')
            self.model_dict[rc_definition.dbId].check_ate_response(rc_definition)
