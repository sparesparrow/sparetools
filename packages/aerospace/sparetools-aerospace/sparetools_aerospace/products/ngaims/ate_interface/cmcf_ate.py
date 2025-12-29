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
// File Name: cmcf_ate.py
//
// Program:   TITAN
//
// Purpose:   CMCF ATE class.
//
// Notes:     None
//
//********************************************************************************************
//********************************************************************************************
"""
import json
import logging
import pprint
import queue
import threading
import time
from ctypes import *
from ctypes import c_char_p
from enum import Enum, IntEnum

import anyconfig
import deprecation
import munch

from ngapy.exceptions import ngapy_exceptions
from ngapy.exceptions.ngapy_exceptions import NgapyRuntimeError
from sparetools_aerospace.products.ngaims.common_functions import get_cmcf_log
from ngapy.util.miscellaneous_functions import get_tuple_from_dict
from ngapy.util.singleton import SingletonType

log = logging.getLogger('__main__.' + __name__)


class DbIds(IntEnum):
    ldiDisk = 0,
    ldiMem = 1,
    hdbDisk = 2,
    hdbMem = 3,
    omiDisk = 4,
    omiMem = 5


class NvmFile(Structure):
    def __init__(self, ms_id, src_path, src_file_name, dst_file_name, tx_settings_id):
        self.msId = ms_id
        self.srcPath = src_path
        self.srcFileName = src_file_name
        self.dstFileName = dst_file_name
        self.txSettingsId = tx_settings_id

    _fields_ = [('msId', c_int),
                ('srcPath', c_char_p),
                ('srcFileName', c_char_p),
                ('dstFileName', c_char_p),
                ('txSettingsId', c_int),
                ]


class sessionType(Enum):
    external = 0
    adn_ua = 1


class AteFactory(metaclass=SingletonType):
    def __init__(self):
        self.instantiated_ate_devices = {}

    @staticmethod
    def check_expected_attribute_config(config):
        return (hasattr(config, 'oms_repository_layout') and
                hasattr(config.oms_repository_layout, 'ate_dll') and
                hasattr(config, 'oms_runtime') and
                hasattr(config.oms_runtime, 'ate_ip') and
                hasattr(config.oms_runtime, 'ate_port'))

    def get_ate_device(self, config=None):
        from sparetools_aerospace.products.ngaims.setup_environment import get_oms_repository_config
        if not config:
            config = get_oms_repository_config()
        if not self.check_expected_attribute_config(config):
            raise ngapy_exceptions.NgapyConfigurationError(f'AteFactory: '
                                                           f'Config is missing expected attributes')

        key_dict = {'cmcf_ip_address': config.oms_runtime.ate_ip,
                    'cmcf_port': config.oms_runtime.ate_port,
                    'ate_cmcf_path': config.oms_repository_layout.ate_dll
                    }
        key = get_tuple_from_dict(key_dict)

        try:
            return self.instantiated_ate_devices[key]
        except KeyError:
            self.instantiated_ate_devices[key] = AteCmcfDevice(**key_dict)
            return self.instantiated_ate_devices[key]


class CmcfEnvInfo:
    def __init__(self):
        self.absolute_fl = None
        self.relative_fl = None

        self.flight_phase = None
        self.curr_time = None
        self.sel_cas_source = None

    def populate_from_munch(self, munch_data):
        if not munch_data:
            return None

        self.absolute_fl = munch_data.data.absoluteFlightLeg
        self.relative_fl = munch_data.data.relativeFlightLeg

        self.flight_phase = munch_data.data.flightPhase
        self.curr_time = munch_data.data.currentTime
        self.sel_cas_source = munch_data.data.selectedCasSource


class AteCmcfDevice:
    """
    Class responsible for ATE CMCF handling
    """

    def __init__(self, cmcf_ip_address, cmcf_port, ate_cmcf_path):
        self.cmcf_ip_address = cmcf_ip_address
        # the required value should be in bytes, here is test and conversion to bytes if required
        if self.cmcf_ip_address and not isinstance(self.cmcf_ip_address, bytes):
            self.cmcf_ip_address = str.encode(self.cmcf_ip_address)
        self.cmcf_port = cmcf_port
        self.sessionId = 0
        self.sessionType = sessionType.external
        self.all_member_systems_instances = []
        self.__get_all_data_executed = False
        self.__restart_executed = False
        self.ate_cmcf_dll = None
        self.method_failed = None
        self.ate_cmcf_path = ate_cmcf_path
        self.ate_repeats = 3
        self.hdb_report_id = 5
        self.hdb_rep_name = "ExportHDB"
        self.default_target_location = ".\\"

        try:
            self.ate_cmcf_dll = cdll.LoadLibrary(self.ate_cmcf_path)
            self.__setup = self.ate_cmcf_dll.setup
            self.__requestSession = self.ate_cmcf_dll.requestSession
            self.__closeSession = self.ate_cmcf_dll.closeSession
            self.__setJsonResponse = self.ate_cmcf_dll.setJsonResponse
            self.__getResponseTypeisJson = self.ate_cmcf_dll.getResponseTypeisJson
            self.__isConnected = self.ate_cmcf_dll.isConnected
            self.__setResponseWaitTime = self.ate_cmcf_dll.setResponseWaitTime
            self.__getAllAtaChap = self.ate_cmcf_dll.getAllAtaChap
            self.__getAllAtaSec = self.ate_cmcf_dll.getAllAtaSec
            self.__getAllMsDef = self.ate_cmcf_dll.getAllMsDef
            self.__getAllMsSts = self.ate_cmcf_dll.getAllMsSts
            self.__getSelectedMsSts = self.ate_cmcf_dll.getSelectedMsSts
            self.__getSelectedChannelSts = self.ate_cmcf_dll.getSelectedChannelSts
            self.__getActiveMMs = self.ate_cmcf_dll.getActiveMms
            self.__getMMDetail = self.ate_cmcf_dll.getMmDetail
            self.__getAllMMDefs = self.ate_cmcf_dll.getAllMmDefs
            self.__getActiveFdes = self.ate_cmcf_dll.getActiveFdes
            self.__getFdeState = self.ate_cmcf_dll.getFdeState
            self.__getMmState = self.ate_cmcf_dll.getMmState
            self.__getAllRcDefs = self.ate_cmcf_dll.getAllRcDefs
            self.__getAllSevDefs = self.ate_cmcf_dll.getAllSevDefs
            self.__getAllFdeDefs = self.ate_cmcf_dll.getAllFdeDefs
            self.__getCmcfSwVersion = self.ate_cmcf_dll.getCmcfSwVersion
            self.__getCmcfLdiVersion = self.ate_cmcf_dll.getCmcfLdiVersion
            self.__getCmcfFhVersion = self.ate_cmcf_dll.getCmcfFhVersion
            self.__getCmcfFdeDetail = self.ate_cmcf_dll.getCmcfFdeDetail
            self.__getEnvInfo = self.ate_cmcf_dll.getEnvInfo
            self.__getFlightPhasesDefs = self.ate_cmcf_dll.getFlightPhasesDefs
            self.__getAllLruDefs = self.ate_cmcf_dll.getAllLruDefs
            self.__getAllBusDefs = self.ate_cmcf_dll.getAllBusDefs
            self.__downloadReport = self.ate_cmcf_dll.downloadReport
            self.__getAdminList = self.ate_cmcf_dll.getAdminList
            self.__getAdminExecute = self.ate_cmcf_dll.getAdminExecute
            self.__sendAdminExecuteRequest = self.ate_cmcf_dll.sendAdminExecuteRequest
            self.__sendAdminExecuteStatusRequest = self.ate_cmcf_dll.sendAdminExecuteStatusRequest
            self.__sendAdminExecuteAbortRequest = self.ate_cmcf_dll.sendAdminExecuteAbortRequest
            self.__recvAdminExecuteResponse = self.ate_cmcf_dll.recvAdminExecuteResponse
            self.__getNvmMss = self.ate_cmcf_dll.getNvmMss
            self.__getNvmMs = self.ate_cmcf_dll.getNvmMs
            self.__getNvmFsItem = self.ate_cmcf_dll.getNvmFsItem
            self.__getNvmCollections = self.ate_cmcf_dll.getNvmCollections
            self.__getNvmCollectionFiles = self.ate_cmcf_dll.getNvmCollectionFiles
            self.__startNvmDownload = self.ate_cmcf_dll.startNvmDownload
            self.__startNvmDownloadCollection = self.ate_cmcf_dll.startNvmDownloadCollection
            self.__getNvmDownloadResponse = self.ate_cmcf_dll.getNvmDownloadResponse
            self.__getAllSysCfgDefs = self.ate_cmcf_dll.getAllSysCfgDefs
            self.__getAllLruCfgDefs = self.ate_cmcf_dll.getAllLruCfgDefs
            self.__statusNvmDownload = self.ate_cmcf_dll.statusNvmDownload
            self.__abortNvmDownload = self.ate_cmcf_dll.abortNvmDownload
            self.__getAllMsConfigValues = self.ate_cmcf_dll.getAllMsConfigValues
            self.__getReportDefs = self.ate_cmcf_dll.getReportDefs
            self.__enterDiagTest = self.ate_cmcf_dll.enterDiagTest
            self.__diagTestPreconditionComplete = self.ate_cmcf_dll.diagTestPreconditionComplete
            self.__statusDiagTest = self.ate_cmcf_dll.statusDiagTest
            self.__abortDiagTest = self.ate_cmcf_dll.abortDiagTest
            self.__getDiagTestResponse = self.ate_cmcf_dll.getDiagTestResponse
            self.__getTestFilters = self.ate_cmcf_dll.getTestFilters
            self.__getTestList = self.ate_cmcf_dll.getTestList
            self.__getTestInfo = self.ate_cmcf_dll.getTestInfo
            self.__startReportDownload = self.ate_cmcf_dll.startReportDownload
            self.__statusReportDownload = self.ate_cmcf_dll.statusReportDownload
            self.__abortReportDownload = self.ate_cmcf_dll.abortReportDownload
            self.__getFlightLegs = self.ate_cmcf_dll.getFlightLegs
            self.__getFlightPhases = self.ate_cmcf_dll.getFlightPhases
            self.__getAtaChapters = self.ate_cmcf_dll.getAtaChapters
            self.__getAtaSections = self.ate_cmcf_dll.getAtaSections
            self.__getFaulted = self.ate_cmcf_dll.getFaulted
            self.__getSpecificMmOccur = self.ate_cmcf_dll.getSpecificMmOccur
            self.__getDatabase = self.ate_cmcf_dll.getDatabase
            self.__unlatchAll = self.ate_cmcf_dll.unlatchAll
            self.__unlatchMm = self.ate_cmcf_dll.unlatchMm
            self.__getAllMmTypeDef = self.ate_cmcf_dll.getAllMmTypeDef
            self.__getAllFdeTypeDef = self.ate_cmcf_dll.getAllFdeTypeDef
            self.__getAllAmtossDef = self.ate_cmcf_dll.getAllAmtossDef
            self.__cmcfRestart = self.ate_cmcf_dll.cmcfRestart
            self.__monitorAdd = self.ate_cmcf_dll.monitorAdd
            self.__getMonitors = self.ate_cmcf_dll.getMonitors
            self.__getEqs = self.ate_cmcf_dll.getEqs
            self.__getEqNodeValues = self.ate_cmcf_dll.getEqNodeValues
            self.__getEqVariables = self.ate_cmcf_dll.getEqVariables
            self.__sendCmcActiveOverrideSetRequest = self.ate_cmcf_dll.sendCmcActiveOverrideSetRequest

            self.__requestSession.restype = c_int32
            self.__closeSession.restype = None
            self.__getResponseTypeisJson.restype = c_bool
            self.__isConnected.restype = c_bool
            self.__setResponseWaitTime.resType = None
            self.__getAllAtaChap.restype = c_char_p
            self.__getAllAtaSec.restype = c_char_p
            self.__getAllMsDef.restype = c_char_p
            self.__getAllMsSts.restype = c_char_p
            self.__getSelectedMsSts.restype = c_char_p
            self.__getSelectedChannelSts.restype = c_char_p
            self.__getActiveMMs.restype = c_char_p
            self.__getMMDetail.restype = c_char_p
            self.__getAllMMDefs.restype = c_char_p
            self.__getActiveFdes.restype = c_char_p
            self.__getFdeState.restype = c_char_p
            self.__getMmState.restype = c_char_p
            self.__getAllRcDefs.restype = c_char_p
            self.__getAllSevDefs.restype = c_char_p
            self.__getAllFdeDefs.restype = c_char_p
            self.__getCmcfSwVersion.restype = c_char_p
            self.__getCmcfLdiVersion.restype = c_char_p
            self.__getCmcfFhVersion.restype = c_char_p
            self.__getCmcfFdeDetail.restype = c_char_p
            self.__getEnvInfo.restype = c_char_p
            self.__getFlightPhasesDefs.restype = c_char_p
            self.__getAllLruDefs.restype = c_char_p
            self.__getAllBusDefs.restype = c_char_p
            self.__downloadReport.restype = c_char_p  # already deprecated in dll, need to remove usage within here
            self.__getAdminList.restype = c_char_p
            self.__getAdminExecute.restype = c_char_p
            self.__sendAdminExecuteRequest.restype = None
            self.__sendAdminExecuteStatusRequest.restype = None
            self.__sendAdminExecuteAbortRequest.restype = None
            self.__recvAdminExecuteResponse.restype = c_bool
            self.__getNvmMss.restype = c_char_p
            self.__getNvmMs.restype = c_char_p
            self.__getNvmFsItem.restype = c_char_p
            self.__getNvmCollections.restype = c_char_p
            self.__getNvmCollectionFiles.restype = c_char_p
            self.__startNvmDownload.restype = None
            self.__startNvmDownloadCollection.restype = None
            self.__getNvmDownloadResponse.restype = c_bool
            self.__getAllSysCfgDefs.restype = c_char_p
            self.__getAllLruCfgDefs.restype = c_char_p
            self.__statusNvmDownload.restype = None
            self.__abortNvmDownload.restype = None
            self.__getAllMsConfigValues.restype = c_char_p
            self.__getReportDefs.restype = c_char_p
            self.__enterDiagTest.restype = None
            self.__diagTestPreconditionComplete.restype = None
            self.__statusDiagTest.restype = None
            self.__abortDiagTest.restype = None
            self.__getDiagTestResponse.restype = c_bool
            self.__getTestFilters.restype = c_char_p
            self.__getTestList.restype = c_char_p
            self.__getTestInfo.restype = c_char_p
            self.__startReportDownload.restype = None
            self.__statusReportDownload.restype = None
            self.__abortReportDownload.restype = None
            self.__getFlightLegs.restype = c_char_p
            self.__getFlightPhases.restype = c_char_p
            self.__getAtaChapters.restype = c_char_p
            self.__getAtaSections.restype = c_char_p
            self.__getFaulted.restype = c_char_p
            self.__getSpecificMmOccur.restype = c_char_p
            self.__getDatabase.restype = c_char_p
            self.__unlatchMm.restype = c_char_p
            self.__unlatchAll.restype = c_char_p
            self.__getAllMmTypeDef.restype = c_char_p
            self.__getAllFdeTypeDef.restype = c_char_p
            self.__getAllAmtossDef.restype = c_char_p
            self.__cmcfRestart.restype = c_char_p
            self.__monitorAdd.restype = c_char_p
            self.__getMonitors.restype = None
            self.__getEqs.restype = c_char_p
            self.__getEqNodeValues.restype = c_char_p
            self.__getEqVariables.restype = c_char_p
            self.__sendCmcActiveOverrideSetRequest.restype = c_char_p

            self.setup_comm_connection(self.cmcf_ip_address, self.cmcf_port)

            self.q = queue.Queue()
        except:
            print(f"ATE CMCF DLL import failed. Path: {self.ate_cmcf_path}")
            self.ate_cmcf_dll = None
            raise

    def __del__(self):
        pass

    def set_response_wait_time(self, wait_time):
        self.__setResponseWaitTime(wait_time)

    def set_json_response(self, responseAsJson):
        self.__setJsonResponse(responseAsJson)

    def get_response_type_is_json(self):
        return self.__getResponseTypeisJson()

    def is_session_connected(self, resp=None):
        if resp is None:
            resp = c_char_p()
            return self._communicate_with_ate(self.__isConnected, byref(resp))
        return self._communicate_with_ate(self.__isConnected, resp)

    @staticmethod
    def _parse_json_result(json_data):
        try:
            parsed_data = anyconfig.loads(json_data, ac_parser="json")
        except json.decoder.JSONDecodeError as e:
            log.exception(e)
            parsed_data = None
        except Exception as e:
            log.exception(e)
            parsed_data = None
        log.debug(f'Json decode: {parsed_data}')
        return parsed_data

    def worker(self, function, args):
        result = function(*args)
        self.q.put(result)

    def _communicate_with_ate(self, function, *args):
        if self.ate_cmcf_dll:
            t = threading.Thread(target=lambda q1, arg1: q1.put(function(*arg1)), args=(self.q, args),
                                 daemon=True, name=function.__name__)
            t.start()
            t.join()  # wait for api response
            if self.q.qsize() > 0:
                data = self.q.get()
                return data

            # if no data recieved above, get connection information, therefor always sending a response from this function
            # cannot call this with _communicate_with_ate recursively because it may end up in infinite recursive loop
            response_data = c_char_p()
            t2 = threading.Thread(target=self.__isConnected, args=(byref(response_data)), daemon=True,
                                  name="checkConnection")
            t2.start()
            t2.join()
            return response_data.value
        else:
            NgapyRuntimeError('Missing ATE library')

    def _json_returning_function(self, function, *args):
        parsed_data = self._parse_json_result(self._communicate_with_ate(function, *args))
        return munch.munchify(parsed_data)

    def _get_common_response(self, function, queue, result_as_munch=False):
        response_data = c_char_p()
        return_value = self._communicate_with_ate(function, byref(queue), byref(response_data))
        response_data_decoded = response_data.value.decode('ascii')
        try:
            if result_as_munch:
                return return_value, munch.munchify(self._parse_json_result(response_data_decoded))
            else:
                return return_value, response_data_decoded
        except:
            return True, '0'  # true will end the call, false could cause infinite loop

    def send_connect_request(self, ses_type=sessionType.external):

        response_data = c_char_p()

        self.sessionId = self._communicate_with_ate(self.__requestSession, byref(response_data), ses_type.value)

        response_data_decoded = response_data.value.decode('ascii')
        print(response_data_decoded)
        return (response_data_decoded, self.sessionId)

    def setup_comm_connection(self, address, port):
        c_address = address
        self.__setup(c_address, port)

    def close_comm_session(self):
        response_data = c_char_p()
        self.__closeSession(byref(response_data))
        response_data_decoded = response_data.value.decode('ascii')
        return response_data_decoded

    def get_all_ata_chap(self):
        return self._json_returning_function(self.__getAllAtaChap)

    def get_all_ata_sec(self):
        return self._json_returning_function(self.__getAllAtaSec)

    def get_all_ms_def(self):
        return self._json_returning_function(self.__getAllMsDef)

    def get_all_ms_sts(self):
        return self._json_returning_function(self.__getAllMsSts)

    def get_selected_ms_sts(self, ms_id):
        return self._json_returning_function(self.__getSelectedMsSts, ms_id)

    def get_selected_channel_sts(self, channel_id):
        return self._json_returning_function(self.__getSelectedChannelSts, channel_id)

    def get_active_mms(self, tick: int = 0):
        return self._json_returning_function(self.__getActiveMMs, tick)

    def get_mm_detail(self, mm_id: int):
        return self._json_returning_function(self.__getMMDetail, mm_id)

    def get_all_mm_defs(self):
        return self._json_returning_function(self.__getAllMMDefs)

    def get_active_fdes(self, tick: int = 0):
        return self._json_returning_function(self.__getActiveFdes, tick)

    @deprecation.deprecated(details="Use the get_fde_state function instead")
    def get_fde_sts(self, fde_id: int):
        return self.get_fde_state(fde_id)

    def get_fde_state(self, fde_id: int):
        return self._json_returning_function(self.__getFdeState, fde_id)

    @deprecation.deprecated(details="Use the get_mm_state function instead")
    def get_cmcf_mm_state(self, mm_id: int):
        return self.get_mm_state(mm_id)

    def get_mm_state(self, mm_id: int):
        return self._json_returning_function(self.__getMmState, mm_id)

    def get_all_rc_defs(self):
        return self._json_returning_function(self.__getAllRcDefs)

    def get_all_sev_defs(self):
        return self._json_returning_function(self.__getAllSevDefs)

    def get_all_fde_defs(self):
        return self._json_returning_function(self.__getAllFdeDefs)

    def get_cmcf_sw_version(self):
        return self._json_returning_function(self.__getCmcfSwVersion)

    def get_cmcf_ldi_version(self):
        return self._json_returning_function(self.__getCmcfLdiVersion)

    def get_cmcf_fh_version(self):
        return self._json_returning_function(self.__getCmcfFhVersion)

    def get_cmcf_fde_detail(self, fde_id: int):
        return self._json_returning_function(self.__getCmcfFdeDetail, fde_id)

    def get_cmcf_env_info(self):
        return self._json_returning_function(self.__getEnvInfo, 0)

    def get_cmcf_all_flight_phases_defs(self):
        return self._json_returning_function(self.__getFlightPhasesDefs)

    def get_cmcf_all_lru_defs(self):
        return self._json_returning_function(self.__getAllLruDefs)

    def get_cmcf_all_bus_defs(self):
        return self._json_returning_function(self.__getAllBusDefs)

    def get_admin_list(self):
        return self._json_returning_function(self.__getAdminList)

    def get_admin_execute(self, admin_id, confirm_hash):
        return self._json_returning_function(self.__getAdminExecute, admin_id, confirm_hash.encode('ascii'))

    def send_admin_execute_request(self, admin_id, confirm_hash):
        queue = c_void_p()
        self._communicate_with_ate(self.__sendAdminExecuteRequest, admin_id, confirm_hash.encode('ascii'), byref(queue))
        return queue

    def send_admin_execute_status_request(self, queue):
        self._communicate_with_ate(self.__sendAdminExecuteStatusRequest, byref(queue))

    def send_admin_execute_abort_request(self, queue):
        self._communicate_with_ate(self.__sendAdminExecuteAbortRequest, byref(queue))

    def recv_admin_execute_response(self, queue, result_as_munch=False):
        return self._get_common_response(self.__recvAdminExecuteResponse, queue, result_as_munch)

    def get_nvm_mss(self):
        return self._json_returning_function(self.__getNvmMss)

    def get_nvm_ms(self, id: int):
        return self._json_returning_function(self.__getNvmMs, id)

    def get_nvm_fs_item(self, ms_id, path):
        return self._json_returning_function(self.__getNvmFsItem, ms_id, path.encode('ascii'))

    def get_nvm_collections(self):
        return self._json_returning_function(self.__getNvmCollections)

    def get_nvm_collection_files(self, collection_id: int):
        return self._json_returning_function(self.__getNvmCollectionFiles, collection_id)

    def start_nvm_download(self, download_struct, download_archive, target_id, length):
        queue = c_void_p()
        self._communicate_with_ate(self.__startNvmDownload, download_struct, download_archive, target_id, length, byref(queue))
        return queue

    def start_nvm_download_collection(self, coll_id, download_archive, target_id):
        queue = c_void_p()
        self._communicate_with_ate(self.__startNvmDownloadCollection, coll_id, download_archive, target_id, byref(queue))
        return queue

    def get_nvm_download_response(self, queue, result_as_munch=False):
        return self._get_common_response(self.__getNvmDownloadResponse, queue, result_as_munch)

    def get_all_sys_cfg_defs(self):
        return self._json_returning_function(self.__getAllSysCfgDefs)

    def get_all_lru_cfg_defs(self):
        return self._json_returning_function(self.__getAllLruCfgDefs)

    def status_nvm_download(self, queue):
        self._communicate_with_ate(self.__statusNvmDownload, byref(queue))

    def abort_nvm_download(self, queue):
        self._communicate_with_ate(self.__abortNvmDownload, byref(queue))

    def get_all_ms_config_values(self):
        return self._json_returning_function(self.__getAllMsConfigValues)

    def unlatch_all(self):
        return self._json_returning_function(self.__unlatchAll)

    def unlatch_mm(self, id: int):
        return self._json_returning_function(self.__unlatchMm, id)

    def get_all_mm_type_def(self):
        return self._json_returning_function(self.__getAllMmTypeDef)

    def get_all_fde_type_def(self):
        return self._json_returning_function(self.__getAllFdeTypeDef)

    def get_all_amtoss_def(self):
        return self._json_returning_function(self.__getAllAmtossDef)

    def cmcf_restart(self):
        return self._json_returning_function(self.__cmcfRestart)

    def monitor_add(self, monitor_id):
        queue = c_void_p()
        self._communicate_with_ate(self.__monitorAdd, monitor_id, byref(queue))
        return queue

    def get_monitors(self, queue):
        self._communicate_with_ate(self.__getMonitors, byref(queue))

    def get_eqs(self):
        return self._json_returning_function(self.__getEqs)

    def get_eq_node_values(self, eq_id):
        return self._json_returning_function(self.__getEqNodeValues, eq_id)

    def get_eq_variables(self):
        return self._json_returning_function(self.__getEqVariables)

    @staticmethod
    def __parse_rep_def(rep_defs):
        report_list = rep_defs.data
        rep_dict = dict()
        for rep in report_list.data:
            rep_list = rep_dict.get(rep.name, list())
            rep_list.append([rep.reportId, rep.storageId, rep.storageName])
            rep_dict[rep.name] = rep_list
        return rep_dict

    def get_report_defs(self, parse_result=True):
        munch_data = self._json_returning_function(self.__getReportDefs)
        if parse_result:
            return self.__parse_rep_def(munch_data)
        return munch_data

    def get_cmcf_hdb(self, target_directory=None):
        return self.get_database(DbIds.hdbDisk, target_directory)

    def get_cmcf_hdb_mem(self, target_directory=None):
        return self.get_database(DbIds.hdbMem, target_directory)

    def get_cmcf_ldi(self, target_directory=None):
        return self.get_database(DbIds.ldiDisk, target_directory)

    def get_cmcf_ldi_mem(self, target_directory=None):
        return self.get_database(DbIds.ldiMem, target_directory)

    def get_omi_sldb(self, target_directory=None):
        return self.get_database(DbIds.omiDisk, target_directory)

    def get_omi_sldb_mem(self, target_directory=None):
        return self.get_database(DbIds.omiMem, target_directory)

    def enter_diag_test(self, id: int):
        queue = c_void_p()
        self._communicate_with_ate(self.__enterDiagTest, id, byref(queue))
        return queue

    def diag_test_precondition_complete(self, queue):
        self._communicate_with_ate(self.__diagTestPreconditionComplete, byref(queue))

    def status_diag_test(self, queue):
        self._communicate_with_ate(self.__statusDiagTest, byref(queue))

    def abort_diag_test(self, queue):
        self._communicate_with_ate(self.__abortDiagTest, byref(queue))

    def get_diag_test_response(self, queue, result_as_munch=False):
        return self._get_common_response(self.__getDiagTestResponse, queue, result_as_munch)

    def get_test_filters(self):
        return self._json_returning_function(self.__getTestFilters)

    def get_test_list(self, id: int):
        return self._json_returning_function(self.__getTestList, id)

    def get_test_info(self, id: int):
        return self._json_returning_function(self.__getTestInfo, id)

    def start_report_download(self, report_id):
        queue = c_void_p()
        response_data = c_char_p()
        self._communicate_with_ate(self.__startReportDownload, report_id, byref(queue), byref(response_data))
        response_data_decoded = response_data.value.decode('ascii')
        resp = munch.munchify(self._parse_json_result(response_data_decoded))
        success = resp.data.ack == 'ok'
        return queue, success, resp

    def status_report_download(self, queue, result_as_munch=False):
        return self._get_common_response(self.__statusReportDownload, queue, result_as_munch)

    @deprecation.deprecated(details="Use the status_report_download function instead")
    def send_report_download_status(self, queue, result_as_munch=False):
        return self.status_report_download(queue, result_as_munch)

    def abort_report_download(self, queue):
        self._communicate_with_ate(self.__abortReportDownload, byref(queue))

    @deprecation.deprecated(details="Use the abort_report_download function instead")
    def send_report_download_abort_request(self, queue):
        self.abort_report_download(queue)

    def get_faults_by_flight_phases(self, year: int, month: int, day: int, end_year: int, end_month: int, end_day: int,
                                    rel_fl: int):
        return self._json_returning_function(self.__getFlightPhases, year, month, day, end_year, end_month, end_day,
                                             rel_fl)

    def get_faults_by_ata_chapters(self, year: int, month: int, day: int, n_of_days: int, rel_fl: int):
        return self._json_returning_function(self.__getAtaChapters, year, month, day, n_of_days, rel_fl)

    def get_faults_by_ata_sections(self, ata_chapter: int, year: int, month: int, day: int, n_of_days: int,
                                   rel_fl: int):
        return self._json_returning_function(self.__getAtaSections, ata_chapter, year, month, day, n_of_days,
                                             rel_fl)

    def get_faulted(self, type: int, from_last_fl: bool, flight_leg: int, time_ordered: bool, n_of_days: int, year: int,
                    month: int, day: int, ata_sec: int, ata_ch: int, flight_phase: int, limit: int, flight_leg_end: int,
                    abs_flight_leg: int, grouped_by_id: bool):
        return self._json_returning_function(self.__getAtaSections, type, from_last_fl, flight_leg, time_ordered,
                                             n_of_days, year, month, day, ata_sec, ata_ch, flight_phase, limit,
                                             flight_leg_end, abs_flight_leg, grouped_by_id)

    def get_specific_mm_occur(self, mm_id: int, abs_fl: int, limit: int):
        return self._json_returning_function(self.__getSpecificMmOccur, mm_id, abs_fl, limit)

    def get_database(self, database_type: DbIds, target_directory='0'):
        if target_directory:
            c_target_directory = c_char_p(str(target_directory).encode('ascii'))
        else:
            c_target_directory = c_char_p()
        json_data = self.__getDatabase(database_type, c_target_directory)
        json_data = json_data.replace(b"\\",
                                      b"\\\\")  # api returns file path with "\\", but json parser see this as an escape character \, convert \\ to \\\\ so json parser works corectly
        path_data = munch.munchify(self._parse_json_result(json_data))
        if path_data.status != 0:
            cmcf_log = get_cmcf_log()
            log.error(f'Error Response from ATE. Log: {pprint.pformat(cmcf_log)}')
        return path_data.data.data

    def get_hdb_storage_rep_id(self):
        return self.__get_report_id(self.hdb_rep_name, "STORAGE")

    @deprecation.deprecated(details="Use the get_report function instead")
    def get_coded_report(self, report_type):
        """
        deprecated function, use get_report instead
        """
        # TODO: remove this function after it is removed from all tests
        self.start_report_download(report_type)

    def __load_env_data(self) -> CmcfEnvInfo:
        env_data = CmcfEnvInfo()
        env_data.populate_from_munch(self.get_cmcf_env_info())
        return env_data

    def get_flight_legs(self) -> tuple[int, int]:
        """
        returns tuple with absolute flight leg and relative flight leg
        """
        env_data = self.__load_env_data()

        return env_data.absolute_fl, env_data.relative_fl

    def get_absolute_flight_leg(self):
        return self.get_flight_legs()[0]

    def get_relative_flight_leg(self):
        return self.get_flight_legs()[1]

    def get_flight_phase(self):
        return self.__load_env_data().flight_phase

    def get_current_time(self):
        return self.__load_env_data().curr_time

    def get_selected_cas_source(self):
        return self.__load_env_data().sel_cas_source

    def send_cmc_active_override_set_request(self, value: bool):
        return self._json_returning_function(self.__sendCmcActiveOverrideSetRequest, value)

    def __get_report_id(self, rep_name, storage_name):
        reports = self.get_report_defs()
        hdb_reports = reports.get(rep_name)
        for item in hdb_reports:
            # this can be changed from text to TargetId, but name is fixed, ID can be changed in DB
            if item[2] == storage_name:
                return item[0]

    def __download_hdb_export_report(self, rep_id, target_directory):
        rep_queue, success, resp = self.start_report_download(rep_id)
        rslt_1 = self.send_report_download_status(rep_queue, result_as_munch=True)
        try:
            while rslt_1.data.data.download.progress < 100:
                time.sleep(0.1)
                rslt_1 = self.send_report_download_status(rep_queue, result_as_munch=True)
                log.info(rslt_1.data.data.download.progress)

        except AttributeError:
            pass
        return rslt_1
