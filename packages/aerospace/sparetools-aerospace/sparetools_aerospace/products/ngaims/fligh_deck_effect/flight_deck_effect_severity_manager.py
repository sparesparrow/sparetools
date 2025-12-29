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
// File Name: flight_deck_effect_severity_manager.py
//
// Program:   TITAN
//
// Purpose:   Flight Deck Effect severity manager class.
//
// Notes:     None
//
//********************************************************************************************
//********************************************************************************************
"""
import munch

from ngapy.exceptions.ngapy_exceptions import NgapyConfigurationError
from sparetools_aerospace.products.ngaims.fligh_deck_effect.flight_deck_effect_severity import OmsFlightDeckEffectSeverity
from sparetools_aerospace.products.ngaims.maintenance_model.model_base_manager import ModelBaseManager


class OmsFlightDeckEffectSeverityManager(ModelBaseManager):
    def __init__(self, maintenance_model, external_dependencies):
        super(OmsFlightDeckEffectSeverityManager, self).__init__()
        fde_severity_model = maintenance_model.get_table_dict('FdeSev')
        self.external_dependencies = external_dependencies
        for key, value in fde_severity_model.items():
            self.model_dict[key] = OmsFlightDeckEffectSeverity(value, external_dependencies)

    def get_all_fde_severities(self):
        return super(OmsFlightDeckEffectSeverityManager, self).get_table_dict()

    def get_fde_severity_by_id(self, mm_id):
        return super(OmsFlightDeckEffectSeverityManager, self).search_by_id(mm_id)

    def get_all_fde_severity_definitions(self):
        all_sev_definitions = self.external_dependencies.ate.get_all_sev_defs()
        for sev_definition in all_sev_definitions.data.sevTypes:
            sev_definition = munch.munchify(sev_definition)
            if sev_definition.dbId not in self.model_dict:
                raise NgapyConfigurationError(f'Ate returned not expected FDE severity dbId: {sev_definition.dbId}.'
                                              f' Have you used same LDI?')
            self.model_dict[sev_definition.dbId].check_ate_response(sev_definition)