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
// File Name: channel.py
//
// Program:   TITAN
//
// Purpose:   Channel representation class.
//
// Notes:     None
//
//********************************************************************************************
//********************************************************************************************
"""
import copy
import itertools
import logging
from enum import Enum, IntEnum

from ngapy.exceptions.ngapy_exceptions import NgapyConfigurationError, NgapyKeyError
from ngapy.io_platform.message_composition import get_complete_validity
from sparetools_aerospace.products.ngaims.constants import MsDispStatus

log = logging.getLogger('__main__.' + __name__)


class SystemConfig(Enum):
    INVALID_CONFIGURATION = 1
    ITERATIVE = 2
    DIRECT = 3
    CONFIG_NOT_SUPPORTED = 1


class PredefinedFunctionIds(IntEnum):
    EQUIPMENT_ID = 1
    DESTINATION_ID = 2
    HARDWARE_PN = 3
    SOFTWARE_PN = 4
    SERIAL_NUMBER = 5


class Channel:
    def __init__(self, item_description: dict, parent,
                 external_dependencies, internal_dependencies):
        self.external_dependencies = external_dependencies
        self.internal_dependencies = internal_dependencies
        self.id = item_description['Id']
        self.sequence_id = item_description['ContId']
        self.name = item_description['Name']
        self.ate_status = MsDispStatus.NO_STATUS
        self.io_expected_status = MsDispStatus.NO_STATUS
        self.io_validity = None
        self.ate_selected_channel = False
        if item_description['InParamId']:
            self.in_param = external_dependencies.input_io_manager.get_parameter_by_id(item_description['InParamId'])
            self.in_param.get_callbacks.append(self.io_finished)
            self.in_param.monitor_callbacks.append(self.io_finished)
            self.in_param.set_callbacks.append(self.io_finished)
        self.cmcf_frs = []
        for cmcf_fr_description in item_description['CmcFrs']:
            self.cmcf_frs.append(
                self.internal_dependencies.cmcf_fault_report_manager.search_by_id(cmcf_fr_description['Id']))

        self.ms_configs = parent.ms_configs
        for ms_config in self.ms_configs:
            if ms_config['FnId'] == PredefinedFunctionIds.EQUIPMENT_ID:
                ms_config['Data'][self.name] = parent.equipment_id
            elif ms_config['FnId'] == PredefinedFunctionIds.DESTINATION_ID:
                ms_config['Data'][self.name] = parent.sdi
            else:
                ms_config['Data'][self.name] = ''
        if not parent.support_config:
            self.system_config_mode = SystemConfig.CONFIG_NOT_SUPPORTED
        elif item_description['MsCfgSignals']:
            try:
                self.system_config_mode = SystemConfig.ITERATIVE
                self.iterative_frames = None
                self.current_iterative_index = 0
                self.reset_iterative_execution()
                if not self.iterative_frames:
                    log.warning(
                        f'Ms: {parent.name}, Channel: {self.name} could not create frames for iterative system '
                        f'config method. Most likely it does not have any system configs configured.')
                self.high_ascii_signal = external_dependencies.input_io_manager.get_parameter_by_id(
                    item_description['MsCfgSignals'][0]['HighAsciiInParamId'])
                self.low_ascii_signal = external_dependencies.input_io_manager.get_parameter_by_id(
                    item_description['MsCfgSignals'][0]['LowAsciiInParamId'])
                self.sequence_ascii_signal = external_dependencies.input_io_manager.get_parameter_by_id(
                    item_description['MsCfgSignals'][0]['SeqCountInParamId'])
            except NgapyKeyError:
                log.warning(f'Signal cannot be found when binding Iterative Config:'
                                                       f' {item_description["MsCfgSignals"][0]}')
                self.system_config_mode = SystemConfig.INVALID_CONFIGURATION
        elif item_description['MsCfgDirectSrcInParams']:
            try:
                self.system_config_mode = SystemConfig.DIRECT
                for ms_config in self.ms_configs:
                    ms_config['Signal'][self.name] = external_dependencies.input_io_manager.get_parameter_by_id(
                        ms_config['MsCfgDirectSrcInParams'][0][0]['Id'])
            except NgapyKeyError:
                log.warning(f'Signal cannot be found when binding Direct Config:'
                                                       f' {ms_config["MsCfgDirectSrcInParams"][0][0]["Id"]}')
                self.system_config_mode = SystemConfig.INVALID_CONFIGURATION
            except IndexError as ex:
                log.error(ex)
        else:
            log.warning(f'Channel {parent.name}/{self.name} ({parent.id}/{self.id})'
                                                   f' does not support any system config method.')
            self.system_config_mode = SystemConfig.INVALID_CONFIGURATION

    def reset_iterative_execution(self):
        self.iterative_frames = self.create_frames()
        self.current_iterative_index = 0

    def delay_to_transmit_all_system_configs(self):
        if self.system_config_mode == SystemConfig.INVALID_CONFIGURATION:
            return 0
        elif self.system_config_mode == SystemConfig.DIRECT:
            return 1
        elif self.system_config_mode == SystemConfig.ITERATIVE:
            return len(self.iterative_frames)

    def max_supported_config_len(self, function_id):
        for ms_config in self.ms_configs:
            if ms_config['FnId'] == function_id:
                if self.system_config_mode == SystemConfig.INVALID_CONFIGURATION:
                    return 0
                elif self.system_config_mode == SystemConfig.DIRECT:
                    io_metadata = self.external_dependencies.input_io_manager.io_interface.logical_to_buffer_structure
                    return int(io_metadata[ms_config['Signal'][self.name].logical_name]['Data Size'])
                elif self.system_config_mode == SystemConfig.ITERATIVE:
                    # Basically unlimited, but there is 25B limit in Cmcf.
                    return 1024

    def set_system_config_data(self, function_id, value):
        for ms_config in self.ms_configs:
            if ms_config['FnId'] == function_id:
                self.updated_iterative_data(ms_config, value)
                break
        # This case covers undefined configs related to CAID_OMS_CMCF_CONFIG_NON_DEFINED_FIDS_ENABLED
        else:
            if self.system_config_mode == SystemConfig.ITERATIVE:
                self.ms_configs.append(copy.deepcopy(self.ms_configs[0]))
                newly_added = self.ms_configs[-1]
                newly_added.FnId = function_id
                self.updated_iterative_data(newly_added, value)

    def updated_iterative_data(self, ms_config, value):
        ms_config['Data'][self.name] = value
        self.reset_iterative_execution()

    def set_system_configs(self):
        if self.system_config_mode == SystemConfig.INVALID_CONFIGURATION:
            pass
        elif self.system_config_mode == SystemConfig.DIRECT:
            input_io_manager = self.external_dependencies.input_io_manager
            for ms_config in self.ms_configs:
                try:
                    input_io_manager.set_values(ms_config['Signal'][self.name],
                                                (str.encode(ms_config['Data'][self.name]), get_complete_validity()))
                except KeyError as ke:
                    log.error(ke)
        elif self.system_config_mode == SystemConfig.ITERATIVE:
            if len(self.iterative_frames) == 0:
                return
            input_io_manager = self.external_dependencies.input_io_manager
            iterative_index = self.current_iterative_index % len(self.iterative_frames)
            self.current_iterative_index += 1
            input_io_manager.set_values(self.high_ascii_signal,
                                        (ord(self.iterative_frames[iterative_index]['highAscii']),
                                         get_complete_validity()))
            input_io_manager.set_values(self.low_ascii_signal,
                                        (ord(self.iterative_frames[iterative_index]['lowAscii']),
                                         get_complete_validity()))
            input_io_manager.set_values(self.sequence_ascii_signal,
                                        (self.iterative_frames[iterative_index]['count'], get_complete_validity()))
        else:
            pass

    def io_finished(self):
        self.io_expected_status = MsDispStatus(self.in_param.io_data_value.value)
        self.io_validity = self.in_param.io_data_value.validity

    def set_status(self, status: MsDispStatus, validity=None):
        if not validity:
            validity = MsDispStatus.validity(status)
        self.external_dependencies.input_io_manager.set_values(self.in_param, (0, validity))

    def update_ate_status(self, ate_channel_status):
        self.ate_status = MsDispStatus(ate_channel_status.status)

    def check_ate_response(self, ate_entity_definition):
        if self.name != ate_entity_definition.name:
            raise NgapyConfigurationError(
                f'Ate returned information not matching with LDI for MS channel: {self.name}!')

    @staticmethod
    def sort_key(ms_config):
        return ms_config['FnId']

    def create_frames(self):
        frames = []
        for ms_config in sorted(self.ms_configs, key=self.sort_key):
            frames.extend(self.create_function_frames(ms_config['FnId'], ms_config['Data'][self.name]))
        return frames

    def create_function_frames(self, func_id, data):
        sub_frame = list()
        null = '\00'
        counter = self.counter_increment()
        # Start NULL NULL synchronization pattern
        sub_frame.append({'highAscii': null, 'lowAscii': null, 'count': next(counter)})
        # End NULL NULL synchronization pattern

        # Start Function ID
        two_chars_to_send = self.char_grouper(2, str(func_id), fill_value='0').__next__()
        '''
        If the Function ID is less than 10 (decimal), the most
        significant digit shall[ 118_00] be represented as a 0 ( this ensures that the Function ID is a two digit
        number). Function ID numbers shall[ 121_01] start at 01 and count up using an incrementing sequence.
        The largest Function ID that may be used by the Member System is 99. The Sequence Count for this
        transmission shall[ 123_01] be set to 01 (binary).
        '''
        if int(func_id) > 9:
            two_chars_swapped = two_chars_to_send
            two_chars_to_send = (two_chars_swapped[1], two_chars_swapped[0])

        sub_frame.append({'highAscii': two_chars_to_send[1],
                          'lowAscii': two_chars_to_send[0],
                          'count': next(counter)})
        # End Function ID

        # Start Total Character
        two_chars_to_send = self.char_grouper(2, str(len(data)), fill_value='0').__next__()
        # Hot FIX
        if len(data) > 9:
            two_chars_swapped = two_chars_to_send
            two_chars_to_send = (two_chars_swapped[1], two_chars_swapped[0])

        sub_frame.append({'highAscii': two_chars_to_send[1],
                          'lowAscii': two_chars_to_send[0],
                          'count': next(counter)})
        # End Total Character

        # Start data content
        two_chars_to_send = self.char_grouper(2, data, fill_value=null)
        for pair in two_chars_to_send:
            sub_frame.append({'highAscii': pair[0],
                              'lowAscii': pair[1],
                              'count': next(counter)})
        # End data content

        return sub_frame

    @staticmethod
    def char_grouper(n, string, fill_value=r'\0'):
        """Collect data into fixed-length chunks or blocks"""
        # grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx
        args = [iter(string)] * n
        return itertools.zip_longest(fillvalue=fill_value, *args)

    @staticmethod
    def counter_increment():
        counter = 0
        while 1:
            yield counter % 4  # counter sequence is 0 1 2 3
            counter += 1
