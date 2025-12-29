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
from ctypes import c_char_p

import logging
import munch
import pprint
import time

from ngapy.bench.bench_factory import BenchStarter
from sparetools_aerospace.products.ngaims.ate_interface.cmcf_ate import NvmFile, DbIds
from sparetools_aerospace.products.ngaims.test_common import prepare_external_dependencies
from sparetools_aerospace.products.ngaims.test_execution.run_test_functions import prepare_cmcf_bench
from ngapy.util.custom_logging import setup_logging_from_config

log = logging.getLogger('__main__.' + __name__)


def traverse_nvm_tree(nodes, ate, level=1):
    for details in nodes:
        if details.detail_type == 'FsItemInfo':
            internal_nodes = ate.get_nvm_fs_item(details.detail.ms.id,
                                                 details.detail.path + details.name)
            print('    ' * level + str(internal_nodes))
            traverse_nvm_tree(internal_nodes.data.nodes, ate, level + 1)
        if details.detail_type == 'FileInfo':
            print('    ' * level + str(details))


def log_return_object(print_object):
    if isinstance(print_object, munch.Munch):
        log.info(pprint.pformat(print_object.toDict(), indent=1, width=1000))
    elif isinstance(print_object, str):
        log.info(print_object)
    else:
        pass
    return


def log_it(string):
    log.info(string)


def execute_all_ate_apis(ate_interface):
    log_return_object(ate_interface.get_all_ata_chap())
    log_return_object(ate_interface.get_all_ata_sec())
    log_return_object(ate_interface.get_all_ms_def())
    log_return_object(ate_interface.get_all_ms_sts())
    log_return_object(ate_interface.get_selected_ms_sts(1))
    log_return_object(ate_interface.get_selected_channel_sts(1))
    log_return_object(ate_interface.get_active_mms(0))
    #log_return_object(ate_interface.get_mm_detail(1))
    log_return_object(ate_interface.get_all_mm_defs())
    log_return_object(ate_interface.get_active_fdes(0))
    log_return_object(ate_interface.get_fde_sts(1))
    log_return_object(ate_interface.get_fde_state(1))
    #log_return_object(ate_interface.get_cmcf_mm_state(1))
    #log_return_object(ate_interface.get_mm_state(1))
    log_return_object(ate_interface.get_all_rc_defs())
    log_return_object(ate_interface.get_all_sev_defs())
    log_return_object(ate_interface.get_all_fde_defs())
    log_return_object(ate_interface.get_cmcf_sw_version())
    log_return_object(ate_interface.get_cmcf_ldi_version())
    log_return_object(ate_interface.get_cmcf_fh_version())
    log_return_object(ate_interface.get_cmcf_fde_detail(1))
    log_return_object(ate_interface.get_cmcf_env_info())
    log_return_object(ate_interface.get_cmcf_all_flight_phases_defs())
    log_return_object(ate_interface.get_cmcf_all_lru_defs())
    log_return_object(ate_interface.get_cmcf_all_bus_defs())
    log_return_object(ate_interface.get_all_mm_type_def())
    log_return_object(ate_interface.get_all_fde_type_def())

    report_defs = ate_interface.get_report_defs(False)
    log_return_object(report_defs)
    for report_def in report_defs.data.data:
        log_return_object(ate_interface.start_report_download(report_def.reportId))

    admin_list = ate_interface.get_admin_list()
    log_return_object(admin_list)
    for admin_action in admin_list.data.fns:
        # TODO: currently CMCF restart needs ID as input - CMCF execution is blocked/stopped
        if "Clear" in admin_action.caption:
            continue
        log_return_object(ate_interface.get_admin_execute(admin_action.id, ''))
        log_it(f'Execution of {admin_action.id} - {admin_action.caption}')
        queue = ate_interface.send_admin_execute_request(admin_action.id, '')
        admin_action_completed = False
        while not admin_action_completed:
            ate_interface.send_admin_execute_status_request(queue)
            time.sleep(0.1)
            admin_action_completed, admin_result_status = \
                ate_interface.recv_admin_execute_response(queue)
            log_it(f'Admin action: {admin_action_completed}, {admin_result_status}')

    nvm_mss = ate_interface.get_nvm_mss()
    log_return_object(nvm_mss)
    for nvm_node in nvm_mss.data.nodes:
        log_it(f'NvmNode: {nvm_node.detail.id} - {nvm_node.name}, detail type: {nvm_node.detail_type}')
        internal_detail = ate_interface.get_nvm_ms(nvm_node.detail.id)
        log_return_object(internal_detail)
        traverse_nvm_tree(internal_detail.data.nodes, ate_interface)
    log_return_object(ate_interface.get_nvm_collections())
    log_return_object(ate_interface.get_nvm_collection_files(1))
    tx_settings_id = 1
    target_id = 1
    # 64 is contId of CMCF1 ms
    ms_id = 64
    array = (NvmFile * 3)(NvmFile(ms_id, '/SATA/MP00'.encode('ascii'),
                                           'test_file_1.txt'.encode('ascii'),
                                           'CMCF1_test_file_1_<DateTimeStamp>.txt'.encode('ascii'),
                                           tx_settings_id),
                                  NvmFile(ms_id, '/SATA/MP00'.encode('ascii'),
                                           'test_file_2.txt'.encode('ascii'),
                                           'CMCF1_test_file_2_<DateTimeStamp>.txt'.encode('ascii'),
                                           tx_settings_id),
                                  NvmFile(ms_id, '/SATA/MP00'.encode('ascii'),
                                           'test_file_3.txt'.encode('ascii'),
                                           'test_file_3_DestNameModifiedByUser.txt'.encode('ascii'),
                                           tx_settings_id)
                          )

    irrelevant_int = -1
    irrelevant_str = ''.encode('ascii')
    download_archive = None
    queue = ate_interface.start_nvm_download(array, download_archive, target_id, len(array))
    nvm_action_completed = False
    while not nvm_action_completed:
        ate_interface.status_nvm_download(queue)
        nvm_action_completed, nvm_result_status = \
            ate_interface.get_nvm_download_response(queue)  #
        log_it(f'NVM action: {nvm_action_completed}, {nvm_result_status}')

    log_return_object(ate_interface.get_all_sys_cfg_defs())
    log_return_object(ate_interface.get_all_lru_cfg_defs())
    log_return_object(ate_interface.get_all_ms_config_values())
    log_return_object(ate_interface.get_report_defs(False))
    log_return_object(ate_interface.get_cmcf_hdb())
    # Those APIs are currently crashing in CMCF side
    # queue = ate_interface.enter_diag_test(3)
    # log_return_object(ate_interface.diag_test_precondition_complete(queue))
    # log_return_object(ate_interface.status_diag_test(queue))
    # log_return_object(ate_interface.get_diag_test_response(queue))
    test_filters = ate_interface.get_test_filters()
    log_return_object(test_filters)
    for test_filter in test_filters.data.filters:
        test_list = ate_interface.get_test_list(test_filter.filterId)
        log_return_object(test_list)
        for test in test_list.data.tests:
            log_return_object(ate_interface.get_test_info(test.id))
    log_return_object(ate_interface.get_faults_by_flight_phases(2020, 1, 1, 2025, 1, 1, 1))
    log_return_object(ate_interface.get_faults_by_ata_chapters(2020, 1, 1, 1000, 1))
    log_return_object(ate_interface.get_faults_by_ata_sections(92, 2020, 1, 1, 1000, 1))
    # log_return_object(ate_interface.get_faulted(...))
    # log_return_object(ate_interface.get_specific_mm_occur(...))
    for db_id in DbIds:
        log_return_object(ate_interface.get_database(db_id))

    log_return_object(ate_interface.get_all_amtoss_def())
    #log_return_object(ate_interface.cmcf_restart())
    #queue = ate_interface.monitor_add(0)
    #log_return_object(ate_interface.get_monitors(queue))
    log_return_object(ate_interface.get_eqs())
    log_return_object(ate_interface.get_eq_node_values(0))
    log_return_object(ate_interface.get_eq_variables())


if __name__ == "__main__":
    setup_logging_from_config()
    prepare_cmcf_bench()
    with BenchStarter():
        model, external_dependencies = prepare_external_dependencies()
        admin_result_status = c_char_p()
        execute_all_ate_apis(external_dependencies.ate)
