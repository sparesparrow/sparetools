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
// File Name: bus_manager.py
//
// Program:   TITAN
//
// Purpose:   Bus manager
//
// Notes:     None
//
//********************************************************************************************
//********************************************************************************************
"""
import munch
from ngapy.exceptions.ngapy_exceptions import NgapyConfigurationError
from sparetools_aerospace.products.ngaims.bus.bus import OmsBus
from sparetools_aerospace.products.ngaims.maintenance_model.model_base_manager import ModelBaseManager


class OmsBusManager(ModelBaseManager):
    def __init__(self, maintenance_model, external_dependencies, internal_dependencies=None):
        super(OmsBusManager, self).__init__()
        self.external_dependencies = external_dependencies
        bus_model = maintenance_model.get_table_dict('Bus')
        for key, value in bus_model.items():
            self.model_dict[key] = OmsBus(value, external_dependencies, internal_dependencies)

    def get_all_buses(self):
        return super(OmsBusManager, self).get_table_dict()

    def get_all_bus_definitions(self):
        all_bus_definitions = self.external_dependencies.ate.get_cmcf_all_bus_defs()
        for bus_definition in all_bus_definitions.data.busDefs:
            bus_definition = munch.munchify(bus_definition)
            if bus_definition.dbId not in self.model_dict:
                raise NgapyConfigurationError(f'Ate returned not expected LRU dbId: {bus_definition.dbId}.'
                                              f' Have you used same LDI?')
            self.model_dict[bus_definition.dbId].check_ate_response(bus_definition)
