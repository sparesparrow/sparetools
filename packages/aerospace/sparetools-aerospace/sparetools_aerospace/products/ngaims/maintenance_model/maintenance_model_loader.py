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
// File Name: maintenance_model_loader.py
//
// Program:   TITAN
//
// Purpose:   Maintenance model loader class.
//
// Notes:     None
//
//********************************************************************************************
//********************************************************************************************
"""
import logging
import time

from ngapy.database.database_tools import convert_database_to_python, link_1_n_mapping, link_1_1_mapping, \
    link_n_n_mapping
from ngapy.io_platform.io_configuration_driver import IoConfigurationDriver
from sparetools_aerospace.products.ngaims.ate_interface.cmcf_ate import AteFactory, DbIds
from sparetools_aerospace.products.ngaims.setup_environment import get_oms_repository_config

log = logging.getLogger('__main__.' + __name__)


class MaintenanceModelLoader:
    def __init__(self):
        self.maintenance_model = dict()
        self.table_connections = dict()

    def get_table_dict(self, table_name):
        return self.maintenance_model[table_name]

    def get_table_values(self, table_name):
        return self.maintenance_model[table_name].values()

    def get_table_data_in_list(self, table_name):
        return list(self.get_table_values(table_name))

    def get_model_data(self):
        return self.maintenance_model

    def get_back_reference(self, src_table_name, dst_table_name, id_value):
        column_name = self.table_connections[(src_table_name, dst_table_name)]
        src_table = self.maintenance_model[src_table_name]
        dst_table = self.maintenance_model[dst_table_name]
        return src_table[dst_table[id_value][column_name]]

    def load_custom_model(self, model):
        self.maintenance_model = model
        self.make_relations_ldi()

    def load_ldi(self):
        ate = AteFactory().get_ate_device()
        time.sleep(1)
        ate.send_connect_request()
        if ate.is_session_connected():
            self.maintenance_model = convert_database_to_python(ate.get_database(DbIds.ldiMem))
            self.make_relations_ldi()
        else:
            raise RuntimeError(f'Session Not Connected')

    def load_omi(self):
        ate = AteFactory().get_ate_device()
        ate.send_connect_request()
        if ate.is_session_connected():
            self.maintenance_model = convert_database_to_python(ate.get_database(DbIds.omiMem))
            self.make_relations_omi()
        else:
            raise RuntimeError(f'Session Not Connected')

    def load_tcrf(self):
        self.maintenance_model = convert_database_to_python(
            get_oms_repository_config().oms_repository_layout.runtime_files.ase.tcrf_oem_path)
        self.make_relations_tcrf()

    def load_oem(self):
        self.maintenance_model = convert_database_to_python(
            get_oms_repository_config().oms_repository_layout.runtime_files.ase.tcrf_oem_path)
        self.make_relations_tcrf()

    def load_output_model(self, partition):
        io_interface = IoConfigurationDriver().get_io_interface()
        io_information = io_interface.logical_to_buffer_structure
        samioc_tree = io_interface.samioc_tree

        counter = 1000000
        for container in samioc_tree['INSU_1'][partition]['Out'].values():
            for group in container.values():
                for param in group.keys():
                    self.maintenance_model['OutParam'][counter] = {'Id': counter, 'LogicalCrc': 0, 'LogicalInstance': 0,
                                                                   'LogicalName': param.split(' ')[0], 'PortId': 0,
                                                                   'Type': io_information[param]['Data Type Enum'],
                                                                   'CmcFrs': []}
                    counter += 1

    def make_relations_ldi(self):
        # TODO: Is making "joins" this way ok? Anyway, we can stabilize the API and under the hood, it could be \
        # anything including this code, which is definitely not most efficient. But on the other hand, it it nicely \
        # abstracting all remaining code from execution of LDI queries.

        # Please make this alphabetically sorted (By second param)
        # AmbiguousMm
        self.link_1_n_mapping('Mm', 'AmbiguousMm')
        self.link_1_n_mapping('Mm', 'AmbiguousMm', 'AmbiguousMmDefaults', 'DefaultMmId')
        # AmbiguousMmPattern is MN
        self.link_n_n_mapping('AmbiguousMm', 'Fr', 'AmbiguousMmPattern', 'AmbiguousMmId', 'FrId')
        # AmtossRef
        self.link_1_n_mapping('AtaCh', 'AmtossRef', dst_key='AtaChapterId')
        # AtaCh is leaf
        # AtaMajorSec
        self.link_1_n_mapping('AtaCh', 'AtaMajorSec')
        # Bus is leaf
        # BusAtFault
        self.link_1_n_mapping('Bus', 'BusAtFault')
        self.link_1_n_mapping('Mm', 'BusAtFault')
        # Cer is MN
        self.link_n_n_mapping('Fr', 'Fr', 'Cer', 'HeadFrId', 'CascadedFrId')
        # Channel
        self.link_1_n_mapping('Ms', 'Channel')
        self.link_1_n_mapping('InParam', 'Channel')
        # CmcFr
        self.link_1_n_mapping('Channel', 'CmcFr')
        self.link_1_n_mapping('OutParam', 'CmcFr')
        if 'OutParam' not in self.maintenance_model:
            self.maintenance_model['OutParam'] = {}

        self.load_output_model('Partition_IO_MaintenanceCMCF')

        # Discrete
        self.link_1_n_mapping('Fr', 'Discrete')
        self.link_1_n_mapping('InParamFp', 'Discrete')
        self.link_1_n_mapping('Channel', 'Discrete')
        # Eq
        self.link_1_n_mapping('EqNode', 'Eq', dst_key='RootNodeId')
        self.link_n_n_mapping('Eq', 'EqNode', 'EqNodeOwner')
        self.link_1_n_mapping('EqNode', 'EqEdge', dst_key='ParentId')
        self.link_n_n_mapping('EqNode', 'EqDefault', 'EqLiteral')
        self.link_n_n_mapping('EqNode', 'SrcSelect', 'EqParamIn')
        self.link_n_n_mapping('SrcSelect', 'InParam', 'SrcSelectInParam')

        # EqAnsCmd is MN - TODO
        # EqAnsFde is MN - TODO
        # EqAnsFr is MN - TODO
        # EqAnsInhibit is MN - TODO
        # EqAnsRpt
        # self.link_1_n_mapping('EqNode', 'EqAnsRpt')
        # EqDefault is leaf
        # EqEdge is MN - TODO
        # EqFdeSrc is MN - TODO
        # EqFrSrc is MN - TODO
        # EqLiteral is MN - TODO
        # EqMsSrc is MN - TODO
        # EqNode is leaf
        # EqParamSrc is MN? - TODO
        # EqVar is MN - TODO
        # Fde
        self.link_1_n_mapping('FdeSev', 'Fde')
        # FdeAmtoss is MN
        self.link_n_n_mapping('Fde', 'AmtossRef', 'FdeAmtoss', 'FdeId', 'AmtossId')
        # FdeCasSrc
        self.link_1_n_mapping('Fde', 'FdeCasSrc')
        self.link_1_n_mapping('InParamFp', 'FdeCasSrc', dst_key='InParamFpPreId')
        self.link_1_n_mapping('InParamFp', 'FdeCasSrc', dst_key='InParamFpPostId')
        # FdeGenericSrc
        self.link_1_n_mapping('Fde', 'FdeGenericSrc')
        self.link_1_n_mapping('InParam', 'FdeGenericSrc')

        # FdeMmCorr is MN
        self.link_n_n_mapping('Fde', 'Mm', 'FdeMmCorr', 'FdeId', 'MmId')
        # FdeSev is leaf
        # FdeSrcRc is MN
        self.link_n_n_mapping('FdeCasSrc', 'Rc', 'FdeSrcRc', 'FdeCasSrcId', 'RcId')
        # FlightPhase is leaf
        # Fr
        self.link_1_n_mapping('Mm', 'Fr')
        self.link_1_n_mapping('Ms', 'Fr')
        # Inhibit is leaf
        # InParam is leaf
        self.link_1_n_mapping('InParam', 'InParamFp', dst_key='InParamId')
        self.link_1_1_mapping('InParamFp', 'InParam')
        self.link_1_1_mapping('Discrete', 'InParamFp')
        self.link_1_1_mapping('FdeCasSrc', 'InParamFp', src_table_name_key='InParamFpPreId',
                              src_table_dst_key='InParamFpPreLink')
        self.link_1_1_mapping('FdeCasSrc', 'InParamFp', src_table_name_key='InParamFpPostId',
                              src_table_dst_key='InParamFpPostLink')
        self.link_1_1_mapping('FdeCasSrc', 'InParamFp', src_table_name_key='InParamFpRcId',
                              src_table_dst_key='InParamFpRcLink')

        # IsolatedMmPattern is MN - TODO
        self.link_n_n_mapping('Mm', 'AmbiguousMm', 'IsolatedMmPattern', 'IsolatedMmId', 'AmbiguousMmId')
        # Lru is leaf
        # LruAtFault is MN
        self.link_n_n_mapping('Mm', 'Lru', 'LruAtFault', 'MmId', 'LruId')
        # LruCfg is MN
        self.link_n_n_mapping('Lru', 'MsCfgDef', 'LruCfg', rel_table_dst_key='MsCfgId')
        # Mm
        self.link_1_n_mapping('AtaMajorSec', 'Mm')
        self.link_1_1_mapping('Mm', 'MmType')

        # self.link_1_n_mapping('Ms', 'Mm')
        # MmAmtoss is MN
        self.link_n_n_mapping('Mm', 'AmtossRef', 'MmAmtoss', 'MmId', 'AmtossId')
        # MmInhibit is MN - TODO
        # Ms
        self.link_1_n_mapping('AtaMajorSec', 'Ms')
        self.link_1_n_mapping('Lru', 'Ms')
        # MsCmdSignal is MN - TODO
        # MsCfgDef
        self.link_1_n_mapping('Ms', 'MsCfgDef')
        # MsCfgDirectSrc  is MN
        self.link_n_n_mapping('InParam', 'MsCfgDef', 'MsCfgDirectSrc', rel_table_dst_key='MsCfgId')
        self.link_n_n_mapping('InParam', 'Channel', 'MsCfgDirectSrc')
        # MsCfgSignal - Even this is MN, link it via 1:N
        self.link_1_n_mapping('Ms', 'MsCfgSignal')
        self.link_n_n_mapping('Channel', 'InParam', 'MsCfgSignal', rel_table_dst_key='HighAsciiInParamId',
                              src_table_src_key='HighAsciiInParams')
        self.link_n_n_mapping('Channel', 'InParam', 'MsCfgSignal', rel_table_dst_key='LowAsciiInParamId',
                              src_table_src_key='LowAsciiInParams')
        self.link_n_n_mapping('Channel', 'InParam', 'MsCfgSignal', rel_table_dst_key='SeqCountInParamId',
                              src_table_src_key='SeqCountInParams')
        self.link_1_n_mapping('Channel', 'MsCfgSignal')
        # MsNvm
        self.link_1_n_mapping('Ms', 'MsNvm')
        # NvmColl is leaf
        # NvmCollFile is MN
        self.link_n_n_mapping('NvmColl', 'NvmFile', 'NvmCollFile', rel_table_src_key='ColId',
                              rel_table_dst_key='PredefinedFileId')
        # NvmBdtSrc
        self.link_1_n_mapping('NvmFile', 'NvmBdtSrc', dst_key='NvmPredFileId')
        # NvmColl
        # NvmCollFile
        # self.link_n_n_mapping('NvmColl', 'NvmFile', 'NvmCollFile')
        # NvmDataLoaderSrc
        self.link_1_n_mapping('NvmFile', 'NvmDataLoaderSrc', dst_key='NvmPredFileId')
        # NvmFile
        self.link_1_n_mapping('Ms', 'NvmFile')
        # NvmWmsbrgSrc
        self.link_1_n_mapping('NvmFile', 'NvmWmsbrgSrc', dst_key='NvmPredFileId')
        # OutParam is leaf
        # Rc is leaf
        # RepDetail
        self.link_1_n_mapping('EqAnsRpt', 'RepDetail', dst_key='AnsReportId')
        # Version is leaf

    def make_relations_omi(self):
        # AdminFn
        self.link_1_n_mapping('OmsFn', 'AdminFn')
        self.link_1_n_mapping('Coll', 'AdminFn')
        # Coll is leaf
        # CallObject is MN
        self.link_n_n_mapping('RpTargetTemplate', 'Coll', 'CollObject')
        self.link_n_n_mapping('RpTargetTemplate', 'DeleteType', 'CollObject')
        # DeleteType
        self.link_1_n_mapping('OmsFn', 'DeleteType')
        # OmsFn is leaf
        # RpTargetTemplate
        self.link_1_n_mapping('RptType', 'RpTargetTemplate')
        self.link_1_n_mapping('Template', 'RpTargetTemplate')
        self.link_1_n_mapping('Target', 'RpTargetTemplate')
        # RptType
        self.link_1_n_mapping('OmsFn', 'RptType')
        # Target is leaf
        # TargetStorage
        # self.link_1_n_mapping('Target', 'TargetStorage') TODO: Setting relation of this tables not working, need to fix
        # TargetStorageError
        # self.link_1_n_mapping('Target', 'TargetStorageError') TODO: Setting relation of this tables not working, need to fix
        # Template is leaf
        # TemplateProperty
        self.link_1_n_mapping('Template', 'TemplateProperty')
        # Version is leaf

    def make_relations_tcrf(self):
        # App
        self.link_1_n_mapping('RecSpec', 'App')
        # Eq
        self.link_1_n_mapping('EqNode', 'Eq', dst_key='RootNodeId')
        # EqCaidIn
        self.link_1_n_mapping('EqNode', 'EqCaidIn')
        # EqDefault is leaf
        # EqEdge is MN - TODO
        # EqLiteral
        self.link_1_n_mapping('EqNode', 'EqLiteral')
        self.link_1_n_mapping('EqDefault', 'EqLiteral')
        # EqNode is leaf
        # EqOptLogicIn
        self.link_1_n_mapping('EqNode', 'EqOptLogicIn')
        self.link_1_n_mapping('OptLogic', 'EqOptLogicIn')
        # EqOptLogicOut
        self.link_1_n_mapping('EqNode', 'EqOptLogicOut')
        self.link_1_n_mapping('OptLogic', 'EqOptLogicOut')
        # EqParamIn
        self.link_1_n_mapping('EqNode', 'EqParamIn')
        self.link_1_n_mapping('SrcSelect', 'EqParamIn')
        # EqRptOut
        self.link_1_n_mapping('EqNode', 'EqRptOut')
        # EqVar
        self.link_1_n_mapping('EqNode', 'EqVar')
        self.link_1_n_mapping('EqDefault', 'EqVar')
        # Frame
        self.link_1_n_mapping('Rpt', 'Frame')
        # FrameOptLogic
        self.link_1_n_mapping('OptLogic', 'FrameOptLogic')
        self.link_1_n_mapping('Frame', 'FrameOptLogic')
        # InParam is leaf
        # OptLogic is leaf
        # RecNode
        self.link_1_n_mapping('TcrfProp', 'RecNode', dst_key='TcrfPropertyId')
        self.link_1_n_mapping('SrcSelect', 'RecNode')
        self.link_1_n_mapping('Frame', 'RecNode')
        # RecSpec is leaf
        # Rpt
        self.link_1_n_mapping('App', 'Rpt')
        self.link_1_n_mapping('EqRptOut', 'Rpt')
        # RptOutTarget
        self.link_1_n_mapping('Rpt', 'RptOutTarget')
        # SrcSelect is leaf
        # SrcSelectInParam
        self.link_1_n_mapping('InParam', 'SrcSelectInParam')
        self.link_1_n_mapping('SrcSelect', 'SrcSelectInParam')
        # TcrfProp is leaf
        if 'OutParam' not in self.maintenance_model:
            self.maintenance_model['OutParam'] = {}
        self.load_output_model('Partition_IO_MaintenanceTCRF')

    def link_1_1_mapping(self, src_table_name, dst_table_name, src_table_name_key=None,
                         src_table_dst_key=None):
        link_1_1_mapping(self.maintenance_model, src_table_name, dst_table_name, src_table_name_key, src_table_dst_key)

    def link_1_n_mapping(self, src_table_name, dst_table_name, src_table_src_key=None, dst_key=None):
        link_1_n_mapping(self.maintenance_model, self.table_connections, src_table_name, dst_table_name,
                         src_table_src_key, dst_key)

    def link_n_n_mapping(self, src_table_name, dst_table_name, rel_table_name,
                         rel_table_src_key=None, rel_table_dst_key=None, src_table_src_key=None,
                         dst_table_src_key=None):
        link_n_n_mapping(self.maintenance_model, src_table_name, dst_table_name,
                         rel_table_name, rel_table_src_key, rel_table_dst_key, src_table_src_key, dst_table_src_key)
