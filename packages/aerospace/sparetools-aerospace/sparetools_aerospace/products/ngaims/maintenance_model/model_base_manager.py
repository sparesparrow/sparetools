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
// File Name: model_base_manager.py
//
// Program:   TITAN
//
// Purpose:   Model base manager class.
//
// Notes:     None
//
//********************************************************************************************
//********************************************************************************************
"""
from ngapy.exceptions.ngapy_exceptions import NgapyKeyError
from sparetools_aerospace.products.ngaims.filter_samples import combine_and, filter_by_attribute, search_by_attribute
from ngapy.util.miscellaneous_functions import make_list_from_variable
from operator import methodcaller
from sparetools_aerospace.products.ngaims.filter_samples import Functor, equality


class ModelBaseManager(object):
    def __init__(self):
        self.model_dict = {}

    def search_by_id(self, entity_id):
        if entity_id not in self.model_dict:
            raise NgapyKeyError(f'ModelBaseManager: Requested {entity_id} does not exists')
        return self.model_dict[entity_id]

    def get_table_dict(self):
        return self.model_dict

    def get_table_values(self):
        return self.model_dict.values()

    def get_table_data_in_list(self):
        return list(self.get_table_values())

    def search_by_attribute(self, filter_functions, combination_function=combine_and):
        return search_by_attribute(self.model_dict.values(), filter_functions, combination_function)

    def filter_by_attribute(self, filter_functions, combination_function=combine_and):
        return filter_by_attribute(self.model_dict.values(), filter_functions, combination_function)

    def get_execution_list(self, custom_list):
        if custom_list:
            return custom_list
        else:
            return self.model_dict.values()

    def get_ldi_id_for_sequence_id(self, sequence_id):
        return self.search_by_attribute(Functor(equality, 'sequence_id', sequence_id)).id
