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
from datetime import datetime
from time import sleep

from ngapy.bench.bench_factory import BenchFactory
from ngapy.bench.pmu_program_cfg_configurator import PmuProgramConfiguration
from ngapy.exceptions.ngapy_exceptions import NgapyRuntimeError
from sparetools_aerospace.products.ngaims.common_functions import delete_log_files
from ngapy.util.setup_environment import get_repository_config


def set_partition_to(partition_id, set_function):
    config = get_repository_config()
    bench = BenchFactory()
    bench.stop()
    delete_log_files()
    program_config = PmuProgramConfiguration(config.oms_repository_layout.ase_pmu_root)
    set_function(program_config, partition_id)
    program_config.write_config()


def partition_to_run(partition_id):
    set_function = lambda program_config, partition_id: program_config.set_partition_to_run(partition_id)
    set_partition_to(partition_id, set_function)


def partition_to_not_equipped(partition_id):
    set_function = lambda program_config, partition_id: program_config.set_partition_to_not_equipped(partition_id)
    set_partition_to(partition_id, set_function)


def setup_cmcf_to_run():
    config = get_repository_config()
    partition_to_run(config.oms_runtime.oms_cmcf_partition_id)


def setup_cmcf_to_not_equipped():
    config = get_repository_config()
    partition_to_not_equipped(config.oms_runtime.oms_cmcf_partition_id)


def setup_tcrf_to_run():
    config = get_repository_config()
    partition_to_run(config.oms_runtime.oms_tcrf_partition_id)


def setup_tcrf_to_not_equipped():
    config = get_repository_config()
    partition_to_not_equipped(config.oms_runtime.oms_tcrf_partition_id)


def prepare_cmcf_bench():
    setup_cmcf_to_run()


def wait_for_cmcf_init(ate_cmcf, timeout=60):
    sleep(5)  # some delay before request to allow CMCF to run
    ate_cmcf.set_response_wait_time(20)  # set a wait time for test startups
    start_time = dt = datetime.now()
    while True:
        ate_cmcf.send_connect_request()
        if ate_cmcf.is_session_connected():
            break
        sleep(1)
        if (datetime.now() - start_time).seconds > timeout:
            raise NgapyRuntimeError('Request session took more than ' + str(timeout) + ' seconds')
    ate_cmcf.set_response_wait_time(40)  # reset wait time


def wait_for_ate_init(ate, timeout=60):
    sleep(5)  # some delay before request to allow CMCF to run
    ate.set_response_wait_time(20)  # set a wait time for test startups
    start_time = dt = datetime.now()
    while True:
        ate.send_connect_request()
        if ate.is_session_connected():
            break
        sleep(1)
        if (datetime.now() - start_time).seconds > timeout:
            raise NgapyRuntimeError('Request session took more than ' + str(timeout) + ' seconds')
    ate.set_response_wait_time(40)  # reset wait time



def prepare_tcrf_bench():
    setup_tcrf_to_run()
