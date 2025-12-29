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
// File Name: flight_phase_manager.py
//
// Program:   TITAN
//
// Purpose:   Flight Phase manager
//
// Notes:     None
//
//********************************************************************************************
//********************************************************************************************
"""
import munch
from ngapy.exceptions.ngapy_exceptions import NgapyConfigurationError
from sparetools_aerospace.products.ngaims.flight_phase.flight_phase import OmsFlightPhase
from sparetools_aerospace.products.ngaims.maintenance_model.model_base_manager import ModelBaseManager


class OmsOmsFlightPhaseManager(ModelBaseManager):
    def __init__(self, maintenance_model, external_dependencies, internal_dependencies=None):
        super(OmsOmsFlightPhaseManager, self).__init__()
        self.external_dependencies = external_dependencies
        flight_phase_model = maintenance_model.get_table_dict('FlightPhaseDef')
        for key, value in flight_phase_model.items():
            self.model_dict[key] = OmsFlightPhase(value, external_dependencies, internal_dependencies)

    def get_all_flight_phases(self):
        return super(OmsOmsFlightPhaseManager, self).get_table_dict()

    def get_all_flight_phase_definitions(self):
        all_flight_phases_definitions = self.external_dependencies.ate.get_cmcf_all_flight_phases_defs()
        for flight_phase_definition in all_flight_phases_definitions.data.flightPhases:
            flight_phase_definition = munch.munchify(flight_phase_definition)
            if flight_phase_definition.dbId not in self.model_dict:
                raise NgapyConfigurationError(f'Ate returned not expected Flight Phase dbId: {flight_phase_definition.dbId}.'
                                              f' Have you used same LDI?')
            self.model_dict[flight_phase_definition.dbId].check_ate_response(flight_phase_definition)
