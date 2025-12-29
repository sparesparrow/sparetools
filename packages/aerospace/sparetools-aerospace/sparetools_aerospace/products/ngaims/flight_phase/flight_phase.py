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
// File Name: flight_phase.py
//
// Program:   TITAN
//
// Purpose:   Flight Phase unit representation class.
//
// Notes:     None
//
//********************************************************************************************
//********************************************************************************************
"""
from ngapy.exceptions.ngapy_exceptions import NgapyConfigurationError


class OmsFlightPhase():
    def __init__(self, item_description: dict, external_dependencies, internal_dependencies):
        self.external_dependencies = external_dependencies
        self.internal_dependencies = internal_dependencies
        self.id = item_description['Id']
        self.sequence_id = item_description['ContId']
        self.flight_phase = item_description['FlightPhase']
        self.text = item_description['Text'].title()
        self.mnemonic = item_description['Mnemonic']
        self.download = item_description['Download']

    def check_ate_response(self, ate_entity_definition):
        if self.id != ate_entity_definition.dbId or \
                self.flight_phase != ate_entity_definition.flightPhase or \
                self.text != ate_entity_definition.name or \
                self.mnemonic != ate_entity_definition.mnemonic or \
                self.download != ate_entity_definition.download:
            raise NgapyConfigurationError(f'Ate returned information not matching with LDI for Flight Phase: {self.text}!')
