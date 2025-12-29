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
// File Name: discrete.py
//
// Program:   TITAN
//
// Purpose:   DISCRETE representation class.
//
// Notes:     None
//
//********************************************************************************************
//********************************************************************************************
"""
import logging

from ngapy.core.utilities import get_bit, set_bit
from ngapy.io_platform.message_composition import get_complete_validity

log = logging.getLogger('__main__.' + __name__)


class OmsDiscrete:
    def __init__(self, item_description: dict, external_dependencies, parent):
        self.external_dependencies = external_dependencies
        self.id = item_description['Id']
        self.sequence_id = item_description['ContId']
        self.fr_id = item_description['FrId']
        self.fr_parent = parent
        self.bit_offset = 0  # item_description['InParamFpLink']['Offset']
        self.channel_id = item_description['ChannelId']
        if item_description['InParamFpLink']:
            self.in_param_id = item_description['InParamFpLink']['InParamLink']['Id']
            self.in_param = external_dependencies.input_io_manager.get_parameter_by_id(self.in_param_id)
        self.stored_status = None

    def get_stored_status(self):
        return self.stored_status

    def set_status(self, status, validity=get_complete_validity()):
        values = self.external_dependencies.input_io_manager.get_values(self.in_param)
        read_value, read_validity = values[0]
        if read_value is not None:
            new_value = set_bit(status, int(read_value), self.bit_offset)
        else:
            log.warning(f'Could not set Discrete {self.id} related to signal: {self.in_param.logical_name}')
            return
        self.external_dependencies.input_io_manager.set_values(self.in_param, [(new_value, validity)])
        self.stored_status = status

    def get_status(self):
        values = self.external_dependencies.input_io_manager.get_values(self.in_param)
        read_value, read_validity = values[0]
        decoded_bit = get_bit(int(read_value), self.bit_offset)
        self.stored_status = decoded_bit
        return self.get_stored_status()
