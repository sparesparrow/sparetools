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
################################################################################
#
# common_functions.py #
#
# Description:
#
# Test common functions.
#
################################################################################

import functools
################################################################################
# Imports
import inspect
import json
import logging
import os
import pathlib
import re
import shutil
import sqlite3
import time
from datetime import datetime
from enum import Enum

import deprecation

import sparetools_aerospace.products.ngaims.common_functions as common
import ngapy.tprocedure as tp
from ngapy.bench.bench_factory import BenchFactory
from ngapy.database.sqlite_exec import Accessor
from ngapy.io_platform.message_composition import get_complete_validity
from sparetools_aerospace.products.ngaims.constants import MsDispStatus
from sparetools_aerospace.products.ngaims.decoder.tcrf_decoder import TCRFDecoder
from sparetools_aerospace.products.ngaims.error_log.ngaims_log_parser import NgaimsLogParser
from sparetools_aerospace.products.ngaims.filter_samples import search_by_attribute, Functor, equality
from sparetools_aerospace.products.ngaims.io_parameters.parameters_manager import IoParameterManager
from sparetools_aerospace.products.ngaims.setup_environment import get_oms_repository_config

################################################################################
# Variables

# TODO: In the future, when Target paths are defined in final forms, the following variables need to be moved into
#  "conf/*.yaml" files appropriately to be consistent with NGAPy configuration mechanism.

TARGET_CMCF_DIR = "APU/CMCF_01"
TARGET_CMCF_DB = "APU/MP00/cmcf_ldi.db"
TARGET_CMCF_LOG = "APU/oms_cmcf.log"
TARGET_TCRF_DIR = "APU/TCRF_01"
TARGET_TCRF_DB = "APU/MP00/tcrf_oem.db"
TARGET_TCRF_LOG = "APU/oms_tcrf.log"
TARGET_DB_MODULE_DIR = "APU"

REP_SUM_NAME = "cmcf_hdb_info.txt"
HDB_NAME = "cmcf_hdb.db"
OMI_NAME = "oms_omi.db"
PDB_NAME = "cmcf_pdb.db"
LDI_NAME = "cmcf_ldi.db"
DLF_NAME = "cmcf_dl.db"

HOST_LOG_DIR = os.path.join(pathlib.Path(__file__).parent)
HOST_CMCF_LOG = os.path.join(HOST_LOG_DIR, "oms_cmcf.log")
HOST_TCRF_LOG = os.path.join(HOST_LOG_DIR, "oms_tcrf.log")

FL_FP_DELAY = 20  # When used on uBench set to 2, when used on slow PC (ASE) set to 20, in other cases set 3


################################################################################
# Test functions

# Common test functions related to Target/Bench
# ------------------------------------------------------------------------------


def start_bench():
    BenchFactory().start()


# The function stops Target.
def stop_bench():
    BenchFactory().stop()
    time.sleep(5)


def check_stop_bench(do_stop_bench):
    if do_stop_bench is None:
        do_stop_bench = BenchFactory().bench_stop_when_download_file()
    if do_stop_bench:
        stop_bench()


# The function gets list of files within Target.
def get_files_list(
        target_path,  # Directory path within Target, which file list is got from.
        do_stop_bench=None
        # Indicator, which indicates that Target shall be stopped firstly.
):
    check_stop_bench(do_stop_bench)
    return BenchFactory().get_files_list(target_path)


# The function downloads file from Source into Destination.
def download_file(
        source_path,  # File path within Source.
        host_path,  # File path within Destination.
        do_stop_bench=None
        # Indicator, which indicates that Target shall be stopped firstly.
):
    check_stop_bench(do_stop_bench)
    BenchFactory().download_file(source_path, host_path)

    return


# The function downloads files from Source into Destination.
def download_files(
        source_paths,  # File paths within Source.
        host_paths,  # File paths within Destination.
        do_stop_bench=None
        # Indicator, which indicates that Target shall be stopped firstly.
):
    check_stop_bench(do_stop_bench)
    for target_path, host_path in zip(source_paths, host_paths):
        download_file(target_path, host_path)
    return


def download_hdb(download_path):
    # local import prevents circular importing
    from sparetools_aerospace.products.ngaims.ate_interface.cmcf_ate import AteFactory
    ate = AteFactory().get_ate_device(get_oms_repository_config())
    return ate.get_cmcf_hdb(download_path)


def download_hdb_by_ftp(download_path):
    # download path without file name
    target_location = pathlib.Path(download_path, HDB_NAME)
    BenchFactory().download_file(rf"APU\MP00\{HDB_NAME}", target_location)
    return target_location


def download_omi(download_path):
    # local import prevents circular importing
    from sparetools_aerospace.products.ngaims.ate_interface.cmcf_ate import AteFactory
    ate = AteFactory().get_ate_device(get_oms_repository_config())
    return ate.get_omi_sldb(download_path)


def download_omi_by_ftp(download_path):
    # download path without file name
    target_location = pathlib.Path(download_path, OMI_NAME)
    BenchFactory().download_file(rf"APU\MP00\{OMI_NAME}", target_location)
    return target_location


def download_cmcf_ldi(download_path):
    # local import prevents circular importing
    from sparetools_aerospace.products.ngaims.ate_interface.cmcf_ate import AteFactory
    ate = AteFactory().get_ate_device(get_oms_repository_config())
    return ate.get_cmcf_ldi(download_path)


def download_cmcf_ldi_by_ftp(download_path):
    # download path without file name
    target_location = pathlib.Path(download_path, LDI_NAME)
    bnch = BenchFactory()
    bnch.download_file(rf"APU\MP00\{LDI_NAME}", target_location)
    return target_location


def download_pdb_by_ftp(download_path):
    # download path without file name
    target_location = pathlib.Path(download_path, PDB_NAME)
    BenchFactory().download_file(rf"APU\MP00\{PDB_NAME}", target_location)
    return target_location


def download_downlink_filter_by_ftp(download_path):
    # download path without file name
    target_location = pathlib.Path(download_path, DLF_NAME)
    BenchFactory().download_file(rf"APU\MP00\{DLF_NAME}", target_location)
    return target_location


# The function uploads file from Host into Target.
def upload_file(
        host_path,  # File path within Host.
        target_path,  # File path within Target.
        do_stop_bench=None
        # Indicator, which indicates that Target shall be stopped firstly.
):
    check_stop_bench(do_stop_bench)
    BenchFactory().upload_file(host_path, target_path)
    return


# The function uploads files from Host into Target.
def upload_files(
        host_paths,  # File paths within Host.
        target_paths,  # File paths within Target.
        do_stop_bench=None
        # Indicator, which indicates that Target shall be stopped firstly.
):
    check_stop_bench(do_stop_bench)
    for host_path, target_path in zip(host_paths, target_paths):
        BenchFactory().upload_file(host_path, target_path)
    return


# The function deletes file from Target.
def delete_file(
        target_path,  # File path within Target.
        do_stop_bench=None  # Indicator, which indicates that Target shall be stopped firstly.
):
    check_stop_bench(do_stop_bench)
    BenchFactory().delete_file(target_path)
    return


# The function downloads Log files from Target into Host.
def download_log_files(do_stop_bench=None):
    check_stop_bench(do_stop_bench)
    BenchFactory().download_file(TARGET_CMCF_LOG, HOST_CMCF_LOG)
    BenchFactory().download_file(TARGET_TCRF_LOG, HOST_TCRF_LOG)
    return HOST_CMCF_LOG, HOST_TCRF_LOG


# The function deletes Log files from Target.
def delete_log_files(do_stop_bench=None):
    check_stop_bench(do_stop_bench)
    BenchFactory().delete_file(TARGET_CMCF_LOG)
    BenchFactory().delete_file(TARGET_TCRF_LOG)
    return


# The function determines error within Log file.
def is_error_in_log_file(
        file_path,  # Log file path.
        error_name,  # Error string to be searched.
        err_desc_to_skip=None,  # Error description to be skipped.
        err_desc_to_find=None,  # Error description to be searched.
        do_stop_bench=None  # Indicator, which indicates that Target shall be stopped firstly.
):
    is_error = True
    file_paths = download_log_files(do_stop_bench)
    if file_path in file_paths:
        lg = NgaimsLogParser(file_path)
        error = lg.find_latest_error_in_file(error_name, err_desc_to_skip, err_desc_to_find)
        is_error = True if error else False

    return is_error


def get_log_parser_data(file_path, do_stop_bench=None):
    file_paths = download_log_files(do_stop_bench)
    if file_path in file_paths:
        return NgaimsLogParser(file_path).parse_ngaims_log()


def get_log_parser_data_for_error(file_path, error_name, do_stop_bench=None):
    file_paths = download_log_files(do_stop_bench)
    if file_path in file_paths:
        return NgaimsLogParser(file_path).find_errors_in_log_file(error_name)


# The function restores backed-up files.
def restore_backup_files(do_stop_bench=None):
    check_stop_bench(do_stop_bench)
    BenchFactory().restore()


@deprecation.deprecated(details="Use the is_error_in_log_file function instead")
def is_error_in_log(error_name, err_desc_to_skip=None, err_desc_to_find=None):
    return is_error_in_log_file(HOST_CMCF_LOG, error_name, err_desc_to_skip, err_desc_to_find, True)


def get_cmcf_log(do_stop_bench=None):
    file_paths = download_log_files(do_stop_bench)
    if HOST_CMCF_LOG in file_paths:
        return NgaimsLogParser(HOST_CMCF_LOG).parse_ngaims_log()
    return None


def get_tcrf_log(do_stop_bench=None):
    file_paths = download_log_files(do_stop_bench)
    if HOST_TCRF_LOG in file_paths:
        return NgaimsLogParser(HOST_TCRF_LOG).parse_ngaims_log()
    return None


# Common test functions related to TCRF component
# ------------------------------------------------------------------------------


# The function triggers TCRF EQ logic.
def tcrf_trigger(
        io_input_manager,  # IO input manager.
        parameter_identifier,  # Identifier (Name/ID) of EQ trigger parameter triggering EQ logic.
        start_value,  # Value of EQ trigger parameter, which starts triggering EQ logic.
        stop_value,  # Value of EQ trigger parameter, which stops triggering EQ logic.
        start_time,  # Wait time after triggering EQ logic was started.
        stop_time  # Wait time after triggering EQ logic was stopped.
):
    if type(parameter_identifier) == str:
        parameter_obj = io_input_manager.get_parameter_by_logical_name(parameter_identifier)
    else:
        parameter_obj = io_input_manager.get_parameter_by_id(parameter_identifier)

    # Setting trigger EQ parameter to stop triggering TCRF report.
    io_input_manager.set_values([parameter_obj], [(stop_value, get_complete_validity())])
    time.sleep(2)

    # Setting trigger EQ parameter to start triggering TCRF report.
    io_input_manager.set_values([parameter_obj], [(start_value, get_complete_validity())])
    time.sleep(start_time)

    # Setting trigger EQ parameter to stop triggering TCRF report.
    io_input_manager.set_values([parameter_obj], [(stop_value, get_complete_validity())])
    time.sleep(stop_time)

    return


# The function triggers TCRF EQ logic.
def tcrf_trigger_start(
        io_input_manager,  # IO input manager.
        parameter_identifier,  # Identifier (Name/ID) of EQ trigger parameter triggering EQ logic.
        start_value,  # Value of EQ trigger parameter, which starts triggering EQ logic.
        start_time  # Wait time after triggering EQ logic was started.
):
    if type(parameter_identifier) == str:
        parameter_obj = io_input_manager.get_parameter_by_logical_name(parameter_identifier)
    else:
        parameter_obj = io_input_manager.get_parameter_by_id(parameter_identifier)

    # Setting trigger EQ parameter to start triggering TCRF report.
    io_input_manager.set_values([parameter_obj], [(start_value, get_complete_validity())])
    time.sleep(start_time)

    return


# The function triggers TCRF EQ logic.
def tcrf_trigger_stop(
        io_input_manager,  # IO input manager.
        parameter_identifier,  # Identifier (Name/ID) of EQ trigger parameter triggering EQ logic.
        stop_value,  # Value of EQ trigger parameter, which stops triggering EQ logic.
        stop_time  # Wait time after triggering EQ logic was stopped.
):
    if type(parameter_identifier) == str:
        parameter_obj = io_input_manager.get_parameter_by_logical_name(parameter_identifier)
    else:
        parameter_obj = io_input_manager.get_parameter_by_id(parameter_identifier)

    # Setting trigger EQ parameter to stop triggering TCRF report.
    io_input_manager.set_values([parameter_obj], [(stop_value, get_complete_validity())])
    time.sleep(stop_time)

    return


# The function downloads TCRF report files from Target into Host.
def tcrf_download_reports(
        host_tcrf_dir=None  # Host directory, where TCRF report files are located.
):
    tcrf_report_file_names_target = get_files_list(f"{TARGET_TCRF_DIR}/*.tcrf")
    tcrf_report_file_names_host = \
        [os.path.join(os.path.dirname(
            (Accessor(get_oms_repository_config().oms_repository_layout.runtime_files.ase.tcrf_oem_path)).path),
            os.path.basename(file)) for file in tcrf_report_file_names_target] \
            if host_tcrf_dir is None else \
            [os.path.join(host_tcrf_dir, os.path.basename(file)) for file in tcrf_report_file_names_target]

    download_files(tcrf_report_file_names_target, tcrf_report_file_names_host)

    return tcrf_report_file_names_host


# The function verifies decoded TCRF report file.
def tcrf_verify_report(
        fred_file_name,  # Name of FRED file.
        tcrf_report_file_names,  # List of names of TCRF report files.
        parameters_expected  # Dictionary of expected TCRF report parameters.
):
    decoder = TCRFDecoder(None)

    parameters_actual = None
    result = False

    decoder.decode(fred_file_name, tcrf_report_file_names)
    decoder.parse()

    try:
        parameters_actual = decoder.reports[0].parameters
    except:
        return result

    result = tp.verify_local(
        parameters_actual,
        parameters_expected,
        "==", "TCRF report parameters"
    )

    return result


def get_record_date(path: str, begin=23):
    """
    Parse filename of a record and return datetime, used to find most recent record from TCRF
    """
    filename = os.path.basename(path)
    splits = (filename.split('.')[0]).split('_')
    timestamp = '19990101010101'
    for split in splits:
        if split.isnumeric() and len(split) == 14:
            timestamp = split
            break

    return datetime(year=int(timestamp[0:4]), month=int(timestamp[4:6]) + 1,
                    day=int(timestamp[6:8]), hour=int(timestamp[8:10]),
                    minute=int(timestamp[10:12]), second=int(timestamp[12:14]))


# Other Common test functions
# ------------------------------------------------------------------------------


def set_status_for_multiple_entities(input_io_manager: IoParameterManager, entity_list: list, value, validity,
                                     **kwargs) -> None:
    input_io_manager.start_queued_mode()
    for entity in entity_list:
        entity.set_status(value, validity, **kwargs)
    input_io_manager.stop_queued_mode()


def get_ldi_id_for_sequence_id(collection, sequence_id):
    return search_by_attribute(collection, Functor(equality, 'sequence_id', sequence_id)).id


def filter_empty_values(value_to_filter: list, attribute='Id', compared_value=0):
    return list(filter(lambda element: getattr(element, attribute) != compared_value, value_to_filter))


@deprecation.deprecated(details="Use the ate.get_flight_phase function instead")
def get_flight_phase(io_output_manager: IoParameterManager):
    return get_flight_phase_from_bus(io_output_manager)


def get_flight_phase_from_bus(io_output_manager: IoParameterManager):
    p_fp = io_output_manager.get_parameter_by_logical_name('oms_flight_phase.0')
    value = io_output_manager.get_values([p_fp, ])
    return value[0]


@deprecation.deprecated(details="Use the ate.get_flight_legs function instead")
def get_flight_legs(io_input_manager, io_output_manager):
    # absolute, relative
    return get_absolute_flight_leg(io_input_manager), get_relative_flight_leg(io_output_manager)


@deprecation.deprecated(details="Use the ate.get_absolute_flight_leg function instead")
def get_absolute_flight_leg(io_input_manager: IoParameterManager):
    # TODO: needs correct implementation when supported by code
    try:
        p_fl = io_input_manager.get_parameter_by_logical_name('oms_flight_leg.0')
        value = io_input_manager.get_values([p_fl, ])
        return value[0][0]
    except:
        return 0


@deprecation.deprecated(details="Use the ate.get_relative_flight_leg function instead")
def get_relative_flight_leg(io_output_manager: IoParameterManager):
    return get_relative_flight_leg_from_bus(io_output_manager)


def get_relative_flight_leg_from_bus(io_output_manager: IoParameterManager):
    try:
        p_fl = io_output_manager.get_parameter_by_logical_name('oms_flight_leg.0')
        value = io_output_manager.get_values([p_fl, ])
        return value[0][0]
    except:
        return 0


def get_record_count(db_location, table):
    connection = sqlite3.connect(db_location)
    r_s = connection.execute(f"SELECT COUNT(*) FROM {table};")
    return r_s.fetchone()[0]


def get_content(db_location, table):
    connection = sqlite3.connect(db_location)
    r_s = connection.execute(f"SELECT * FROM {table};")
    a = r_s.fetchall()
    return a


def get_table_column_names(db_location, table):
    connection = sqlite3.connect(db_location)
    r_s = connection.execute(f"SELECT name, type FROM pragma_table_info('{table}') ORDER BY cid;")
    a = r_s.fetchall()
    return a


def increase_flight_leg(io_input_manager):
    # TODO: after EQ is stored in official LDI, update setting logic - JIRA NGAIMS-1601
    p_11 = io_input_manager.get_parameter_by_logical_name('adp_avg_pressure_AZ200.1')
    p_5 = io_input_manager.get_parameter_by_logical_name('calibrated_airspeed_voted_ACSS_ada.1')

    param_set = [p_11, p_5]
    value_set = [(0, get_complete_validity()), (1, get_complete_validity())]
    io_input_manager.set_values(param_set, value_set)
    time.sleep(3)
    param_set = [p_11, p_5]
    value_set = [(1, get_complete_validity()), (1, get_complete_validity())]
    io_input_manager.set_values(param_set, value_set)


def set_flight_phase(io_input_manager, flight_phase_value):
    # TODO: after EQ is stored in official LDI, update setting logic - JIRA NGAIMS-1601
    p_6 = io_input_manager.get_parameter_by_logical_name('acss_air_data_source_ACSS_ada.1')

    param_set = [p_6, ]
    value_set = [(flight_phase_value, get_complete_validity()), ]
    io_input_manager.set_values(param_set, value_set)


def set_ms_for_mms(mms: list, ms_manager,
                   ms_state=MsDispStatus.NORM_OP):
    li_ms = []
    for mm in mms:
        for fr in mm.fault_reports:
            ms = ms_manager.get_ms_by_id(fr.ms_id)
            ms.set_status(ms_state)
            if ms not in li_ms:
                li_ms.append(ms)

    return li_ms


# Obsolete functions
# ------------------------------------------------------------------------------


def upload_ldi(source_file):
    upload_file(source_file, r"APU\MP00\cmcf_ldi.db")


def delete_hdb():
    BenchFactory().delete_file(rf"APU\MP00\{HDB_NAME}")


def delete_log_file():
    BenchFactory().delete_file(r"APU\oms_cmcf.log")


def delete_cmcf_log_file():
    BenchFactory().delete_file(r"APU\oms_cmcf.log")


def delete_tcrf_log_file():
    BenchFactory().delete_file(r"APU\oms_tcrf.log")


def delete_tcrf_services_db():
    BenchFactory().delete_file(r"APU\tcrf_services.db")


def upload_hdb(source_file):
    upload_file(source_file, rf"APU\MP00\{HDB_NAME}")


def upload_omi(source_file):
    upload_file(source_file, rf"APU\MP00\{OMI_NAME}")


def delete_omi():
    BenchFactory().delete_file(rf"APU\MP00\{OMI_NAME}")


def delete_omi():
    BenchFactory().delete_file(r"APU\MP00\oms_omi.db")


def upload_pdb(source_file):
    upload_file(source_file, rf"APU\MP00\{PDB_NAME}")


def delete_pdb():
    BenchFactory().delete_file(rf"APU\MP00\{PDB_NAME}")


def delete_hdb_journal_file():
    bnch = BenchFactory()
    bnch.delete_file(rf"APU\MP00\{HDB_NAME}-journal")


def upload_tcrf_db(source_file, is_oem=True):
    if is_oem:
        upload_file(source_file, r"APU\MP00\tcrf_oem.db")
    else:
        upload_file(source_file, r"APU\MP00\tcrf_services.db")


def upload_tcrf_oem(source_file):
    upload_file(source_file, r"APU\MP00\tcrf_oem.db")


def upload_tcrf_services(source_file):
    upload_file(source_file, r"APU\MP00\tcrf_services.db")


def set_parameters(param_list: tuple, io_input_manager, validity_list: list = None):
    """

    :param param_list: Parameters to be set - tuple(id, value)
    :type param_list: tuple
    :param io_input_manager:
    :type io_input_manager:
    :param validity_list:
    :type validity_list: list
    :return:
    :rtype:
    """
    param_set = list()
    value_set = list()
    if not validity_list:
        validity_list = [get_complete_validity()] * len(param_list)
    for param, validity in zip(param_list, validity_list):
        param_set.append(io_input_manager.get_parameter_by_id(param[0]))
        value_set.append((param[1], validity))

    io_input_manager.set_values(param_set, value_set)


def set_file_date_time(file_path, unix_time):
    os.utime(file_path, (unix_time, unix_time))


def update_unixtime_in_version(db_location, new_time: int):
    connection = sqlite3.connect(db_location)
    r_s = connection.execute(f"UPDATE Version SET UnixTime = {new_time};")
    return r_s


def is_ase_run():
    cfg_hndl = get_oms_repository_config()
    if cfg_hndl.configuration.platform.lower() == "ase":
        return True
    else:
        return False


def timeis(func):
    '''Decorator that reports the execution time.'''

    def wrap(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()

        print(func.__name__, end - start)
        return result

    return wrap


def LogCollectionAndTest(app, tp, use_whitelist=True, save_logs=True, delete_initial_logs=True,
                         white_list_extention_faults=[],
                         white_list_extention_full_faults=[], white_list_extention_regex_faults=[]):
    def _decorate(function):

        @functools.wraps(function)
        def wrapped_function(*args, **kwargs):
            save_dir = pathlib.Path(inspect.stack()[1].filename).parent
            test_name = function.__name__
            lc = LogCollect(app, save_dir, test_name, delete_initial_logs, use_whitelist, white_list_extention_faults,
                            white_list_extention_full_faults, white_list_extention_regex_faults)
            result = function(*args, **kwargs)
            logs = lc.get_logs()
            if save_logs:
                lc.save_logs()
            verifiy = tp.verify_local(len(logs), 0, "==", "Unexpected OMS logs")
            tp.message("LogCollect: Unexpected OMS Logs:")
            for log in logs:
                tp.message(json.dumps(log, sort_keys=False))
            return result and verifiy

        return wrapped_function

    return _decorate


class LogCollect:
    class App(Enum):
        CMCF = 0
        TCRF = 1

    def __init__(self, app: App, save_dir, test_name, delete_initial_logs=True, use_whitelist=True,
                 white_list_extention_faults: list = None, white_list_extention_full_faults: list = None,
                 white_list_extention_regex_faults: list = None):
        if white_list_extention_regex_faults is None:
            white_list_extention_regex_faults = list()
        if white_list_extention_full_faults is None:
            white_list_extention_full_faults = list()
        if white_list_extention_faults is None:
            white_list_extention_faults = list()
        if app == self.App.CMCF:
            app = "cmcf"
        elif app == self.App.TCRF:
            app = "tcrf"
        else:
            app = "app"
        self.use_whitelist = use_whitelist
        self.white_list_extention_faults = white_list_extention_faults
        self.white_list_extention_full_faults = white_list_extention_full_faults
        self.white_list_extention_regex_faults = white_list_extention_regex_faults
        self.time_str = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        self.test_name = test_name
        save_folder = os.path.join(save_dir, "logs", self.test_name, self.time_str)
        os.makedirs(save_folder, exist_ok=True)
        self.tmp_log_file = os.path.join(save_folder, 'oms_' + app + '_tmp.log')
        self.log_file_name = os.path.join(save_folder, 'collected_' + app + '_logs.json')
        self.tmp_reduced_log_filename = os.path.join(save_folder, 'tmp_reduced_log.log')
        self.initial_log_size = 0
        self.oms_log_file = "APU\oms_" + app + ".log"
        if delete_initial_logs:
            common.delete_log_files()
        else:
            download_file(self.oms_log_file, self.tmp_log_file)
            if os.path.exists(self.tmp_log_file):
                lg = NgaimsLogParser(self.tmp_log_file)
                parsed_log_list = lg.parse_ngaims_log()
                self.initial_log_size = len(parsed_log_list)
                os.remove(self.tmp_log_file)

    def get_logs(self):
        download_file(self.oms_log_file, self.tmp_log_file)
        if os.path.exists(self.tmp_log_file):
            lg = NgaimsLogParser(self.tmp_log_file)
            parsed_log_list = lg.parse_ngaims_log()
            parsed_log_list = parsed_log_list[self.initial_log_size:]
            filtered_json = self.parse_content(parsed_log_list)
            return filtered_json
        else:
            return []

    def save_logs(self):
        filtered_json = self.get_logs()
        date_time = datetime.now().strftime("%m/%d/%Y_%H:%M:%S")
        filtered_json = {f'{self.test_name}_{date_time}': filtered_json}
        if os.path.exists(self.log_file_name):
            try:
                with open(self.log_file_name) as f:
                    data = json.load(f)
                data.update(filtered_json)
            except:
                os.remove(self.log_file_name)
        else:
            data = filtered_json
        with open(self.log_file_name, 'w') as f:
            json.dump(data, f)

        try:
            os.remove(self.tmp_log_file)
        except FileNotFoundError:
            pass

    def parse_content(self, content):
        error_list = []
        whitelist = {"faults": get_oms_repository_config().log_whitelist.log_whitelist_faults,
                     "full_faults": get_oms_repository_config().log_whitelist.log_whitelist_full_faults,
                     "regex_faults": get_oms_repository_config().log_whitelist.log_whitelist_regex_faults}
        whitelist["faults"].extend(self.white_list_extention_faults)
        whitelist["full_faults"].extend(self.white_list_extention_full_faults)
        whitelist["regex_faults"].extend(self.white_list_extention_regex_faults)

        for record in content:
            dict_entry = {"full_log": record.full_log,
                          "timestamp": record.time_stamp,
                          "timestamp_sys": record.time_stamp_sys_time,
                          "fault": record.fault_name,
                          "seq_number": record.seq_number,
                          "user_seq_number": record.user_seq_number}
            matches_found = 1
            if self.use_whitelist:
                for regex_fault in whitelist["regex_faults"]:
                    matches = re.finditer(regex_fault, dict_entry["full_log"])
                    for _, _ in enumerate(matches, start=1):
                        matches_found += 1
                        break
                if matches_found > 1:
                    continue
                if dict_entry["fault"] in whitelist["faults"] or dict_entry["full_log"] in whitelist["full_faults"]:
                    continue
            error_list.append(dict_entry)
        return error_list


def clear_folder_local(folder, log=logging.getLogger()):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            log.exception(e)


def delete_file_local(path, log=logging.getLogger()):
    try:
        os.remove(path)
    except PermissionError as pe:
        try:
            shutil.rmtree(path)
        except Exception as e:
            log.exception(e)
    except FileNotFoundError as fnf:
        # exception is caught here, but it is still propagated outside
        log.exception(fnf)
    except Exception as e:
        log.exception(e)


def create_stub_file_local(path):
    f = open(path, "a")
    f.write("Stub content")
    f.close()


def create_dir_local(dir_name, log=logging.getLogger()):
    if not os.path.exists(dir_name):
        try:
            os.makedirs(dir_name)
        except Exception as e:
            log.exception(e)


def delete_dir_local(dir_name):
    if os.path.exists(dir_name):
        delete_file_local(dir_name)


