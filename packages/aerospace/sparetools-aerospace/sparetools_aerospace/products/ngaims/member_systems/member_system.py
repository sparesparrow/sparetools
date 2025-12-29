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
// File Name: member_system.py
//
// Program:   TITAN
//
// Purpose:   Member system representation class.
//
// Notes:     None
//
//********************************************************************************************
//********************************************************************************************
"""
import logging

import munch

from ngapy.exceptions.ngapy_exceptions import NgapyConfigurationError
from sparetools_aerospace.products.ngaims.common_functions import \
    set_status_for_multiple_entities, get_ldi_id_for_sequence_id, filter_empty_values
from sparetools_aerospace.products.ngaims.constants import MsDispStatus
from sparetools_aerospace.products.ngaims.filter_samples import search_by_attribute, Functor, equality
from sparetools_aerospace.products.ngaims.member_systems.channel import Channel, SystemConfig

log = logging.getLogger('__main__.' + __name__)


class OmsMemberSystem:
    """Represents Member System and its properties"""

    def __init__(self, item_description: dict, external_dependencies, internal_dependencies):
        self.external_dependencies = external_dependencies
        self.internal_dependencies = internal_dependencies
        self.id = item_description['Id']
        self.sequence_id = item_description['ContId']
        self.ata_sec_id = item_description['AtaMajorSecId']
        self.ata_sec_number = item_description['AtaSecNumber']
        # TODO: Finish discussion with System team about LDI and type of EquipId. Per current understanding this is
        #  transited as HEX string padded to 2chars, but with possibility to send 3 chars (Sdi is now 10bit)
        self.equipment_id = f'{item_description["EquipId"]:0>2X}'
        self.lru_id = item_description['LruId']
        self.mnemonic = item_description['Mnemonic']
        self.name = item_description['Name']
        self.comm_protocol = item_description['CommProtocol']
        self.dnld_protocol = item_description['DnldProtocol']
        # TODO: Finish discussion with System team about LDI and type of SDI. Per current understanding this is
        #  transited as Decadic string padded to 2chars
        self.sdi = f'{item_description["Sdi"]:0>2}'
        self.support_multi_session = item_description['SupMultiSession']
        self.support_act_fault = item_description['SupActFault']
        self.support_statusing = item_description['SupSts']
        self.support_download = item_description['SupDnld']
        self.support_config = item_description['SupCfg']
        self.support_diagnostics_test = item_description['SupDiagTest']
        self.support_direct_config = item_description['SupCfgDirect']
        self.ate_status = MsDispStatus.NO_STATUS
        self.ate_selected_channel = None
        self.system_config_mode = None
        self.ms_nvm_files = munch.munchify(item_description['NvmFiles'])
        self.ms_nvm_objects = internal_dependencies.nvm_files_manager.filter_by_attribute(
            Functor(equality, 'ms_db_id', self.id))
        configs = munch.munchify(item_description['MsCfgDefs'])
        if self.support_config:
            self.ms_configs = configs
            for ms_config in self.ms_configs:
                ms_config['Data'] = dict()
                ms_config['Signal'] = dict()
        else:
            if configs:
                log.warning(f'Ms: {self.mnemonic} has does not support config, but has a values in '
                            f'MsCfgDef: {configs}')
            self.ms_configs = []
            self.system_config_mode = SystemConfig.CONFIG_NOT_SUPPORTED

        # list of channel instances used for setting MS status and belonging to this MS
        self.channels = {}

        for channel_description in item_description['Channels']:
            channel = Channel(channel_description, self, self.external_dependencies, self.internal_dependencies)
            self.channels[channel.id] = channel

    def max_supported_config_len(self, function_id):
        channel_lengths = [channel.max_supported_config_len(function_id) for channel in self.channels.values()]
        if channel_lengths:
            return min(channel_lengths)
        else:
            return 0

    def delay_to_transmit_all_system_configs(self):
        channel_delays = [channel.delay_to_transmit_all_system_configs() for channel in self.channels.values()]
        if channel_delays:
            return max(channel_delays)
        else:
            return 0

    def set_system_config_data(self, function_id, value):
        for channel in self.channels.values():
            channel.set_system_config_data(function_id, value)

    def set_system_configs(self):
        for channel in self.channels.values():
            channel.set_system_configs()

    def set_status(self, status: MsDispStatus, validity=None):
        if not self.support_statusing:
            return
        set_status_for_multiple_entities(self.external_dependencies.input_io_manager,
                                         self.channels.values(),
                                         status,
                                         validity)

    def update_ate_status(self, ate_response):
        self.ate_status = MsDispStatus(ate_response.status)
        self.ate_selected_channel = ate_response.selectedChannelId
        if hasattr(ate_response, 'channels'):
            for channel in filter_empty_values(ate_response.channels, attribute='id'):
                try:
                    selected_channel = self.channels[get_ldi_id_for_sequence_id(self.channels.values(), channel.id)]
                    selected_channel.update_ate_status(channel)
                    selected_channel.ate_selected_channel = selected_channel.sequence_id == self.ate_selected_channel
                except AttributeError:
                    continue

    def get_status_by_ate(self):
        ate_response = self.external_dependencies.ate.get_selected_ms_sts(self.sequence_id)
        self.update_ate_status(ate_response.data)
        # TODO: It would be great if ATE is made consistent (Single API returns one value, GetAll.. API returns array of
        # SAME values.
        # self.update_ate_status(ate_response.data)
        return self.ate_status

    def get_ata_section(self):
        return self.internal_dependencies.ata_manager.get_ata_section_by_id(self.ata_sec_id)

    def check_ate_response(self, ate_entity_definition):
        ate_entity_definition.channels = filter_empty_values(ate_entity_definition.channels, attribute='dbId')
        if self.id != ate_entity_definition.dbId or \
                self.name != ate_entity_definition.name or \
                self.mnemonic != ate_entity_definition.mnemonic or \
                self.ata_sec_number != ate_entity_definition.ataSectionNumber or \
                self.get_ata_section().ata_chapter.number != ate_entity_definition.ataChapterNumber or \
                len(self.channels) != len(ate_entity_definition.channels):
            raise NgapyConfigurationError(f'Ate returned information not matching with LDI for MS: {self.name}!')
        for channel_definition in ate_entity_definition.channels:
            self.channels[channel_definition.dbId].check_ate_response(channel_definition)

    def check_ate_response_config_def(self, ate_entity_definition):
        if not self.support_config:
            return
        ldi_config = search_by_attribute(self.ms_configs, Functor(equality, 'FnId', ate_entity_definition.functionId))
        if self.sequence_id != ate_entity_definition.msId or \
                ldi_config.Name != ate_entity_definition.name or \
                ldi_config.FnId != ate_entity_definition.functionId:
            # self.CfgType != ate_entity_definit
            # ion.configType:
            raise NgapyConfigurationError(f'Ate returned information not matching with LDI for MS config: '
                                          f'{ate_entity_definition}!')

    def get_selected_channel(self) -> Channel:
        self.get_status_by_ate()
        return search_by_attribute(self.channels.values(), Functor(equality, 'sequence_id', self.ate_selected_channel))
