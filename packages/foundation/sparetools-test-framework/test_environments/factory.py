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
// File Name: bench_factory.py
//
// Program:   TITAN
//
// Purpose:   Bench factory
//
// Notes:     None
//
//********************************************************************************************
//********************************************************************************************
"""
import logging
import threading

import psutil
import time

from sparetools.test_environments.ase_bench import ASEBench
from sparetools.test_environments.jets_bench import JETSBench
from sparetools.test_environments.sits_bench import SITSBench
from ngapy.util.setup_environment import get_repository_config
from ngapy.util.singleton import SingletonType

log = logging.getLogger('__main__.' + __name__)


def measure_cpu():
    gb = 1024 * 1024 * 1024
    while True:
        log.debug(f'{psutil.cpu_count()}, {psutil.cpu_percent()}%, {round(psutil.virtual_memory().used / gb, 2)}GB/'
                  f'{round(psutil.virtual_memory().total / gb, 2)}GB')
        time.sleep(1)


# TODO consider update to class container
#  https://stackoverflow.com/questions/13460889/how-to-redirect-all-methods-of-a-contained-class-in-python/41040380
def TestEnvironmentFactory():
    return TestBenchContainer().get_instance()


class TestEnvironmentStarter:
    def __init__(self):
        self.t1 = threading.Thread(target=measure_cpu, daemon=True)
        self.t1.start()
        self.bench_object = TestBenchContainer().get_instance()
        self.bench_object.stop()

    def __enter__(self):
        self.bench_object.start()
        return self.bench_object

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.bench_object.stop()
        self.bench_object.restore()
        self.bench_object.delete_backup_files()


class TestBenchContainer(metaclass=SingletonType):
    # TODO: This needs to be called as the first step in the test
    def __init__(self):
        super().__init__()
        self.cfg_hndl = get_repository_config()
        self.platform = self.cfg_hndl.configuration.platform
        if self.platform.lower() == "ase":
            # call ASE bench
            self.hndl = ASEBench(config_loader=self.cfg_hndl)
        elif self.platform.lower() == "jets":
            # call JETS bench
            self.hndl = JETSBench(config_loader=self.cfg_hndl)
        elif self.platform.lower() == "sits":
            # call SITS bench
            self.hndl = SITSBench(config_loader=self.cfg_hndl)
        else:
            raise NotImplementedError("Platform support not implemented.")

    def get_instance(self):
        return self.hndl
