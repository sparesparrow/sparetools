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
// File Name: lru_manager.py
//
// Program:   TITAN
//
// Purpose:   LRU manager
//
// Notes:     None
//
//********************************************************************************************
//********************************************************************************************
"""
import munch
from ngapy.exceptions.ngapy_exceptions import NgapyConfigurationError
from sparetools_aerospace.products.ngaims.lru.lru import Lru
from sparetools_aerospace.products.ngaims.maintenance_model.model_base_manager import ModelBaseManager


class OmsLruManager(ModelBaseManager):
    def __init__(self, maintenance_model, external_dependencies, internal_dependencies=None):
        super(OmsLruManager, self).__init__()
        self.external_dependencies = external_dependencies
        lru_model = maintenance_model.get_table_dict('Lru')
        for key, value in lru_model.items():
            self.model_dict[key] = Lru(value, external_dependencies, internal_dependencies)

    def get_all_lrus(self):
        return super(OmsLruManager, self).get_table_dict()

    def get_all_lru_definitions(self):
        all_lru_definitions = self.external_dependencies.ate.get_cmcf_all_lru_defs()
        for lru_definition in all_lru_definitions.data.lruDefs:
            lru_definition = munch.munchify(lru_definition)
            if lru_definition.dbId not in self.model_dict:
                raise NgapyConfigurationError(f'Ate returned not expected LRU dbId: {lru_definition.dbId}.'
                                              f' Have you used same LDI?')
            self.model_dict[lru_definition.dbId].check_ate_response(lru_definition)
