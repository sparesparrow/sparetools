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
class OmsCmcfFaultReport:
    def __init__(self, item_description: dict, external_dependencies):
        self.external_dependencies = external_dependencies
        self.id = item_description['Id']
        self.sequence_id = item_description['ContId']
        self.channel_id = item_description['ChannelId']
        self.type = item_description['Type']
        self.stored_status = None
        if item_description['OutParamId']:
            self.out_param = external_dependencies.output_io_manager.get_parameter_by_id(item_description['OutParamId'])
            self.out_param_id = item_description['OutParamId']

    def get_stored_status(self):
        return self.stored_status

    def get_status(self):
        values = self.external_dependencies.output_io_manager.get_values(self.out_param)
        read_value, read_validity = values[0]
        self.stored_status = read_value
        return self.get_stored_status()
