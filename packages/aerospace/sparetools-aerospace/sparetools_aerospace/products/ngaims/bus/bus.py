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
// File Name: bus.py
//
// Program:   TITAN
//
// Purpose:   Line-replaceable unit representation class.
//
// Notes:     None
//
//********************************************************************************************
//********************************************************************************************
"""
from ngapy.exceptions.ngapy_exceptions import NgapyConfigurationError


class OmsBus:
    def __init__(self, item_description: dict, external_dependencies, internal_dependencies):
        self.external_dependencies = external_dependencies
        self.internal_dependencies = internal_dependencies
        self.id = item_description['Id']
        self.sequence_id = item_description['ContId']
        self.name = item_description['Name']

    def check_ate_response(self, ate_entity_definition):
        if self.id != ate_entity_definition.dbId or \
                self.name != ate_entity_definition.name:
            raise NgapyConfigurationError(f'Ate returned information not matching with LDI for Bus: {self.name}!')
