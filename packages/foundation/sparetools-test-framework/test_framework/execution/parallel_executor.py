import argparse
import datetime
import logging
import os
import pprint
import sys
import threading
import time
from multiprocessing import Pool, Manager

import psutil
import tqdm

from sparetools.core.configuration.providers.env_provider import get_config_from_env

log = logging.getLogger('__main__.sparetools.test_framework.execution.parallel_executor')
gb = 1024 * 1024 * 1024


class Options:
    pool_size = ''
    job_file = ''
    job_string = ''
    pool_delay = 0
    performance_stats = False


def prepare_arguments(args):
    parser = argparse.ArgumentParser(
        description='Script allowing multi-process execution')
    parser.add_argument(
        '-p',
        '--PoolSize',
        dest='pool_size',
        help='Pool Size - How many Processes should run in parallel',
        required=False,
        default=-1
    )
    parser.add_argument(
        '-j',
        '--JobFile',
        dest='job_file',
        help=r'Path to file where cmd jobs are listed',
        required=False,
    )
    parser.add_argument(
        '-s',
        '--JobString',
        dest='job_string',
        help=r'";" separated string with commands',
        required=False,
    )

    parser.add_argument(
        '-d',
        '--poolDelay',
        dest='pool_delay',
        help=r'Delay between each process start in seconds',
        required=False,
        default=0
    )

    parser.add_argument(
        '-f',
        '--PerformanceStats',
        dest='performance_stats',
        action='store_true',
        help=r'Delay between each process start in seconds',
        required=False,
        default=False
    )

    options = parser.parse_args(args)
    return options


def run_process(process):
    argument, delay, sequence, tracking_dict = process
    if tracking_dict['RunWithDelay']:
        time.sleep(delay)
    start_execution = datetime.datetime.now()
    tracking_dict[sequence] = (argument, sequence, 'Started', os.getpid())
    result = execute_command(argument) + (argument,)
    tracking_dict[sequence] = (
        argument, sequence, 'Finished', result[0], datetime.datetime.now() - start_execution, os.getpid())
    return result


def measure_cpu():
    gb = 1024 * 1024 * 1024
    while True:
        most_consuming = sorted([p.info for p in psutil.process_iter(['pid', 'name', 'cpu_percent'])],
                                key=lambda x: x['cpu_percent'], reverse=True)[0:10]
        log.debug(f'{psutil.cpu_count()}, {psutil.cpu_percent()}%, {round(psutil.virtual_memory().used / gb, 2)}GB/'
                  f'{round(psutil.virtual_memory().total / gb, 2)}GB, {most_consuming}')
        time.sleep(1)


def run(args: list, external_options: Options = None):
    if external_options is None:
        options = prepare_arguments(args)
    else:
        options = external_options

    commands = []
    if options.job_file:
        with open(options.job_file, 'r') as command_file:
            commands = command_file.read().splitlines()
    if options.job_string:
        commands = options.job_string.split(';')

    if options.performance_stats:
        cpu_thread = threading.Thread(target=measure_cpu, daemon=True)
        cpu_thread.start()

    manager = Manager()
    tracking_dict = manager.dict()
    tracking_dict['RunWithDelay'] = True

    delays = [i * int(options.pool_delay) for i in range(0, len(commands))]
    enumerated_commands = list(zip(commands, delays, [i for i in range(0, len(commands))],
                                   [tracking_dict for _ in range(0, len(commands))]))
    commands_print = pprint.pformat(enumerated_commands, width=1000)
    log.info(f'Commands to be executed (Command, delay, sequence, tracking_dict):\n{commands_print}')
    try:
        pool_size = int(options.pool_size)
    except ValueError:
        pool_size = int(eval(options.pool_size))

    overall_result = 0
    with Pool(processes=pool_size) as pool:
        for rc, text, command in tqdm.tqdm(pool.imap_unordered(run_process, enumerated_commands),
                                           total=len(enumerated_commands)):
            time.sleep(1)
            tracking_dict['RunWithDelay'] = False
            log.info(f'Pool execution rc: {rc}, command: {command}')
            tracking_dict_print = ''
            for entry in tracking_dict.values():
                tracking_dict_print += pprint.pformat(entry, width=500) + '\n'
            log.info(f'Pool state:\n{tracking_dict_print}')
            if rc != 0:
                overall_result = rc
            # log.debug(f'Pool execution rc: {rc}, command: {command}, text: {text},')
    return overall_result


if __name__ == '__main__':
    log = setup_logging_from_config(get_repository_config())
    run(sys.argv[1:])
