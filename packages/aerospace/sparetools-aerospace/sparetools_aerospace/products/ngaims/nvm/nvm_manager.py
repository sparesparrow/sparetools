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
// File Name: member_systems_manager.py
//
// Program:   TITAN
//
// Purpose:   Member system manager class.
//
// Notes:     None
//
//********************************************************************************************
//********************************************************************************************
"""
import logging

from ngapy.exceptions.ngapy_exceptions import NgapyRuntimeError
from sparetools_aerospace.products.ngaims.maintenance_model.model_base_manager import ModelBaseManager

log = logging.getLogger('__main__.' + __name__)


class OmsNvmFile:
    def __init__(self, item_description: dict):
        self.id = item_description['Id']
        self.sequence_id = item_description['ContId']
        self.ms_db_id = item_description['MsId']
        self.description = item_description['Description']
        self.dest_file_name = item_description['DestFileName']
        self.file_size = item_description['FileSize']
        self.log_error = item_description['LogError']
        self.is_display = item_description['IsDisplay']
        self.is_compressed = item_description['IsCompressed']


class NvmFileBdt(OmsNvmFile):
    def __init__(self, item_description: dict):
        super(NvmFileBdt, self).__init__(item_description)
        array_len = len(item_description['NvmBdtSrcs'])
        if array_len != 1:
            raise NgapyRuntimeError(
                f'Amount of rows linked to NvmBdtSrc with Id: {self.id} is not correct: {array_len}')
        item_description_bdt = item_description['NvmBdtSrcs'][0]
        self.system_name = item_description_bdt['SystemName']
        self.bdt_dir_file_filter = item_description_bdt['BdtDirFileFilter']
        # Kept there for backward compatibility.
        self.dirList_pre_filter = item_description_bdt['DirListPreFilter']
        self.dir_list_pre_filter = item_description_bdt['DirListPreFilter']
        self.file_ext_post_filter = item_description_bdt['FileExtPostFilter']
        self.is_intg = item_description_bdt['IsIntg']


class NvmFileDataLoader(OmsNvmFile):
    def __init__(self, item_description: dict):
        super(NvmFileDataLoader, self).__init__(item_description)
        array_len = len(item_description['NvmDataLoaderSrcs'])
        if array_len != 1:
            raise NgapyRuntimeError(
                f'Amount of rows linked to NvmDataLoaderSrc with Id: {self.id} is not correct: {array_len}')
        item_description_data_loader = item_description['NvmDataLoaderSrcs'][0]
        self.target_hardware_id = item_description_data_loader['TargetHardwareId']
        self.position_id = item_description_data_loader['PositionId']
        self.file_name = item_description_data_loader['FileName']
        self.file_ext_postFilter = item_description_data_loader['FileExtPostFilter']
        self.is_intg = item_description_data_loader['IsIntg']


class NvmFileWilliamsburg(OmsNvmFile):
    def __init__(self, item_description: dict):
        super(NvmFileWilliamsburg, self).__init__(item_description)
        array_len = len(item_description['NvmWmsbrgSrcs'])
        if array_len != 1:
            raise NgapyRuntimeError(
                f'Amount of rows linked to NvmWmsbrgSrc with Id: {self.id} is not correct: {array_len}')
        item_description_data_loader = item_description['NvmWmsbrgSrcs'][0]
        self.file_number = item_description_data_loader['FileNumber']
        self.in_param_id = item_description_data_loader['InParamId']


class NvmFileFactory:
    @staticmethod
    def get_nvm_file(item_description: dict):
        is_bdt = len(item_description['NvmBdtSrcs'])
        is_data_loader = len(item_description['NvmDataLoaderSrcs'])
        is_williamsburg = len(item_description['NvmWmsbrgSrcs'])
        if is_bdt and not is_data_loader and not is_williamsburg:
            return NvmFileBdt(item_description)
        elif not is_bdt and is_data_loader and not is_williamsburg:
            return NvmFileDataLoader(item_description)
        elif not is_bdt and not is_data_loader and is_williamsburg:
            return NvmFileWilliamsburg(item_description)
        else:
            log.warning(
                f'Nvm file has not exactly one connection to specific tables. Creating base class only. '
                f'Details: {item_description}.')
            return OmsNvmFile(item_description)


class OmsNvmFilesManager(ModelBaseManager):
    def __init__(self, maintenance_model, external_dependencies, internal_dependencies=None):
        super(OmsNvmFilesManager, self).__init__()
        self.external_dependencies = external_dependencies
        nvm_files = maintenance_model.get_table_dict('NvmFile')
        for key, value in nvm_files.items():
            self.model_dict[key] = NvmFileFactory().get_nvm_file(value)

    def get_all_nvm_files(self):
        return super(OmsNvmFilesManager, self).get_table_dict()


class OmsNvmCollection:
    def __init__(self, item_description: dict, external_dependencies, internal_dependencies):
        pass


class OmsNvmCollectionManager(ModelBaseManager):
    def __init__(self, maintenance_model, external_dependencies, internal_dependencies=None):
        super(OmsNvmCollectionManager, self).__init__()
        self.external_dependencies = external_dependencies
        nvm_collections = maintenance_model.get_table_dict('NvmColl')
        for key, value in nvm_collections.items():
            self.model_dict[key] = OmsNvmCollection(value, external_dependencies, internal_dependencies)

    def get_all_nvm_files(self):
        return super(OmsNvmCollectionManager, self).get_table_dict()
