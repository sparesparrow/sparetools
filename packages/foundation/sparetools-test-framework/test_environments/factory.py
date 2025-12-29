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


class SingletonType(type):
    """Simple singleton metaclass to replace ngapy.util.singleton.SingletonType"""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

from sparetools.core.configuration.providers.env_provider import get_config_from_env

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
        self.cfg_hndl = get_config_from_env()
        self.platform = self.cfg_hndl.configuration.platform
        if self.platform.lower() in ["ase", "jets", "sits"]:
            # Aerospace platforms require sparetools-aerospace package
            raise ImportError(f"Aerospace platform '{self.platform}' requires sparetools-aerospace package. "
                            "Install with: pip install sparetools-aerospace or conan install sparetools-aerospace")
        else:
            raise NotImplementedError(f"Platform '{self.platform}' support not implemented. "
                                    "Available: embedded platforms (ESP32, etc.)")

    def get_instance(self):
        return self.hndl
