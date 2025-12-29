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
// File Name: input_parameters_manager.py
//
// Program:   TITAN
//
// Purpose:   Input parameters manager class.
//
// Notes:     None
//
//********************************************************************************************
//********************************************************************************************
"""
from enum import IntEnum

import ngapy.exceptions.ngapy_exceptions as ngapy_exceptions
from ngapy.io_platform.io_configuration_driver import IoConfigurationDriver
from ngapy.io_platform.io_interface import get_module_name
from ngapy.io_platform.message_composition import IoDataValue
from sparetools_aerospace.products.ngaims.maintenance_model.model_base_manager import ModelBaseManager
from ngapy.util.miscellaneous_functions import make_list_from_variable


# TODO: This is taken from platforms code and it is used in LDI.
class IoParameterType(IntEnum):
    VT_DONT_CARE_e = 0
    VT_FLOAT64_e = 1
    VT_FLOAT32_e = 2
    VT_UINT32_e = 3
    VT_SINT32_e = 4
    VT_BOOL_e = 5
    VT_STRING_e = 6
    VT_DATE_TIME_e = 7
    VT_TIME_SPAN_e = 8
    VT_UNSPECIFIED_e = 9
    VT_VO_LIST_e = 10
    VT_VO_PTR_e = 240
    VT_SET_e = 241


class IoParameterHandle:
    def __init__(self, parameter_id: int, logical_name: str, logical_instance: int, logical_crc: int, port_id: int,
                 port_type: IoParameterType):
        self.parameter_id = parameter_id
        self.logical_name = logical_name
        self.logical_instance = logical_instance
        self.logical_crc = logical_crc
        self.port_id = port_id
        self.port_type = port_type
        self.set_callbacks = []
        self.get_callbacks = []
        self.monitor_callbacks = []
        self.io_data_value = IoDataValue(self.logical_name)

    def set_finished(self):
        for callback in self.set_callbacks:
            callback()

    def get_finished(self):
        for callback in self.get_callbacks:
            callback()

    def monitor_finished(self):
        for callback in self.monitor_callbacks:
            callback()


class IoParameterManager(ModelBaseManager):
    def __init__(self, parameter_model, config, external_io_interface, path_suffix=None):
        if not path_suffix:
            path_suffix = f' ({get_module_name()})'
        super(IoParameterManager, self).__init__()
        self.io_interface = IoConfigurationDriver(external_io_interface).get_io_interface()
        self.logical_name_map = {}
        self.path_suffix = path_suffix

        for key, parameter in parameter_model.items():
            if parameter['Id'] in self.model_dict:
                raise ngapy_exceptions.NgapyConfigurationError(f'InputParameterManager: Parameter {parameter} '
                                                               f'already exists in internal dictionary. '
                                                               f'Check your LDI/Configuration for duplicates')
            try:
                parameter['LogicalName'] += self.path_suffix
                self.model_dict[parameter['Id']] = IoParameterHandle(parameter['Id'],
                                                                     parameter['LogicalName'],
                                                                     parameter['LogicalInstance'],
                                                                     parameter['LogicalCrc'],
                                                                     parameter['PortId'],
                                                                     parameter['Type'])
                self.logical_name_map[parameter['LogicalName']] = self.model_dict[parameter['Id']]
            except AttributeError:
                raise ngapy_exceptions.NgapyConfigurationError(f'InputParameterManager: Parameter {parameter} '
                                                               f'does not have expected attributes')

    def get_all_params(self):
        return super(IoParameterManager, self).get_table_dict()

    def get_parameter_by_id(self, parameter_id) -> IoParameterHandle:
        return super(IoParameterManager, self).search_by_id(parameter_id)

    def get_parameter_by_logical_name(self, parameter_name) -> IoParameterHandle:
        return self.logical_name_map[parameter_name + self.path_suffix]

    def set_values(self, parameter_list, values):
        parameter_list = make_list_from_variable(parameter_list)
        values = make_list_from_variable(values)
        if len(parameter_list) != len(values):
            raise ngapy_exceptions.NgapyRuntimeError(f'InputParameterManager: '
                                                     f'parameter_list size does not match with values size')
        set_values = []
        for index, parameter in enumerate(parameter_list):
            parameter.io_data_value.value = values[index][0]
            parameter.io_data_value.complete_validity = values[index][1]
            set_values.append(parameter.io_data_value)
        self.io_interface.set_values(set_values)
        for parameter in parameter_list:
            parameter.set_finished()

    def get_value(self, param_instance):
        return self.get_values([param_instance, ])

    def get_values(self, parameter_list):
        get_values = []
        parameter_list = make_list_from_variable(parameter_list)
        for index, parameter in enumerate(parameter_list):
            get_values.append(parameter.io_data_value)
        self.io_interface.get_values(get_values)
        for parameter in parameter_list:
            parameter.get_finished()
        return [(value.value, value.complete_validity) for value in get_values]

    def start_queued_mode(self):
        self.io_interface.start_queued_mode()

    def stop_queued_mode(self):
        self.io_interface.stop_queued_mode()


class InputParameterManager(IoParameterManager):
    def __init__(self, maintenance_model, config, external_io_interface=None):
        in_param_model = maintenance_model.get_table_dict('InParam')
        super(InputParameterManager, self).__init__(in_param_model, config,
                                                    external_io_interface=external_io_interface)


class OutputParameterManager(IoParameterManager):
    def __init__(self, maintenance_model, config, external_io_interface=None):
        out_param_model = maintenance_model.get_table_dict('OutParam')
        super(OutputParameterManager, self).__init__(out_param_model, config,
                                                     external_io_interface=external_io_interface)


class OutputParameterManagerTcrf(IoParameterManager):
    def __init__(self, maintenance_model, config, external_io_interface=None):
        out_param_model = maintenance_model.maintenance_model['OutParam']
        super(OutputParameterManagerTcrf, self).__init__(out_param_model, config,
                                                         external_io_interface=external_io_interface)
