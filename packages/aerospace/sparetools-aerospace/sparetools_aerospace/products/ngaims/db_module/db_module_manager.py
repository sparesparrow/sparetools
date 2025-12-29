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

import abc
import logging
# We use os.path instead of pathlib because functions called in this module expect string
import os

from ngapy.bench.bench_factory import BenchFactory
from ngapy.exceptions.ngapy_exceptions import NgapyConfigurationError
from sparetools_aerospace.products.ngaims.common_functions import stop_bench, HDB_NAME, REP_SUM_NAME
from sparetools_aerospace.products.ngaims.setup_environment import get_oms_repository_config
from ngapy.util.singleton import SingletonType

# If UPLOADING HDB, source file will be uploaded as 1_cmcf_hdb.db. If no source is specified, cmcf_hdb.db path will be
# taken. If DOWNLOADING HDB, target will be specified as 1_cmcf_hdb.db and downloaded as cmcf_hdb.db. Same with info
# files. This is to simulate Backup funcs as in CMCF. If you want custom hdb upload or download - use generic funcs.


log = logging.getLogger('__main__.' + __name__)

# Backuped files "should be" named with 1_* before actual filename - same as cmcf.
REMOTE_HDB_NAME = "1_cmcf_hdb.db"
REMOTE_HDB_INFO_NAME = "1_cmcf_hdb_info.txt"

DEOS_MODES = {'flight_mode': 0, 'download_mode': 3}


class DbModuleManagerContainer(metaclass=SingletonType):
    def __init__(self):
        super().__init__()
        self.cfg_hndl = get_oms_repository_config()
        self.platform = self.cfg_hndl.configuration.platform
        if self.platform.lower() == "ase":
            # call ASE bench
            self.hndl = DbModuleManagerASE()
        elif self.platform.lower() == "sits":
            # call SITS bench
            self.hndl = DbModuleManagerSITS()

    def get_instance(self):
        return self.hndl


def DbModuleManagerFactory():
    return DbModuleManagerContainer().get_instance()


class DbModuleManagerInterface(metaclass=abc.ABCMeta):
    def __init__(self):
        self.cmcf_hdb_name = HDB_NAME
        self.cmcf_hdb_info_name = REP_SUM_NAME
        self.remote_hdb_name = REMOTE_HDB_NAME
        self.remote_hdb_info_name = REMOTE_HDB_INFO_NAME
        self.remote_hdb_location = ''

    @abc.abstractmethod
    def download_file_from_db_module(self, remote_path, local_path, do_stop_bench=True):
        raise NotImplementedError("Method not implemented.")

    @abc.abstractmethod
    def upload_file_to_db_module(self, remote_path, local_path, do_stop_bench=True):
        raise NotImplementedError("Method not implemented.")

    @abc.abstractmethod
    def delete_file_on_db_module(self, remote_path, do_stop_bench=True):
        raise NotImplementedError("Method not implemented.")

    @abc.abstractmethod
    def get_file_list_from_db_module(self):
        raise NotImplementedError("Method not implemented.")

    def download_hdb_from_db_module(self, target_path=None, do_stop_bench=True):
        if target_path is None:
            target_path = self.cmcf_hdb_name
        res = self.download_file_from_db_module(self.remote_hdb_name,
                                                target_path, do_stop_bench)
        return res

    def upload_hdb_to_db_module(self, source_path=None, do_stop_bench=True):
        if source_path is None:
            source_path = self.cmcf_hdb_name
        res = self.upload_file_to_db_module(self.remote_hdb_name,
                                            source_path, do_stop_bench)
        return res

    def delete_hdb_on_db_module(self, path=None, do_stop_bench=True):
        if path is None:
            path = self.remote_hdb_name
        res = self.delete_file_on_db_module(path, do_stop_bench)
        return res

    def upload_hdb_info_to_db_module(self, source_path=None, do_stop_bench=True):
        if source_path is None:
            source_path = self.cmcf_hdb_info_name
        res = self.upload_file_to_db_module(self.remote_hdb_info_name,
                                            source_path, do_stop_bench)
        return res

    def delete_hdb_info_on_db_module(self, target_path=None, do_stop_bench=True):
        if target_path is None:
            target_path = self.remote_hdb_info_name
        res = self.delete_file_on_db_module(target_path, do_stop_bench)
        return res

    def download_hdb_info_from_db_module(self, target_path=None, do_stop_bench=True):
        if target_path is None:
            target_path = self.cmcf_hdb_info_name
        res = self.download_file_from_db_module(self.remote_hdb_info_name,
                                                target_path, do_stop_bench)
        return res


class DbModuleManagerASE(DbModuleManagerInterface):
    def __init__(self):
        super(DbModuleManagerASE, self).__init__()
        self.cfg_hndl = get_oms_repository_config()
        self.remote_hdb_location = self.cfg_hndl.oms_repository_layout.ase_main_partition
        pass

    def download_file_from_db_module(self, remote_path, local_path, do_stop_bench=True):
        remote_path = os.path.join(self.remote_hdb_location, remote_path)
        if do_stop_bench:
            stop_bench()
        try:
            BenchFactory().download_file(remote_path, local_path, False)
        except Exception as e:
            log.exception(e)
            return False
        return

    def upload_file_to_db_module(self, remote_path, local_path, do_stop_bench=True):
        remote_path = os.path.join(self.remote_hdb_location, remote_path)
        if do_stop_bench:
            stop_bench()
        try:
            BenchFactory().upload_file(local_path, remote_path, False)
        except Exception as e:
            log.exception(e)
            return False
        return True

    def delete_file_on_db_module(self, remote_path, do_stop_bench=True):
        remote_path = os.path.join(self.remote_hdb_location, remote_path)
        if do_stop_bench:
            stop_bench()
        try:
            BenchFactory().delete_file_on_db_module(remote_path)
        except Exception as e:
            log.exception(e)
            return False
        return True

    def get_file_list_from_db_module(self, path=None, do_stop_bench=False):
        file_list = None
        if do_stop_bench:
            stop_bench()
        try:
            if path is None:
                path = self.remote_hdb_location
            file_list = BenchFactory().get_files_list(path)
        except Exception as e:
            log.exception(e)
        return file_list


class DbModuleManagerSITS(DbModuleManagerInterface):
    def __init__(self):
        super(DbModuleManagerSITS, self).__init__()
        self.cfg_hndl = get_oms_repository_config()
        found = False
        for module in BenchFactory().deos_module.keys():
            # DB Module should be on DPM1
            if module == "DPM1":
                self.db_module = BenchFactory().deos_module[module]
                found = True
                break
        if not found:
            raise NgapyConfigurationError(f'DbModuleManagerSITS: Config is missing expected attributes')

        self.remote_hdb_location = self.cfg_hndl.hw_main_partition
        pass

    def download_file_from_db_module(self, remote_path, local_path, do_stop_bench=True):
        remote_path = os.path.join(self.remote_hdb_location, remote_path)
        ret = False
        if do_stop_bench:
            stop_bench()
        try:
            self.db_module.download_file(remote_path, local_path)
            ret = True
        except Exception as e:
            log.exception(e)

        return ret

    def upload_file_to_db_module(self, remote_path, local_path, do_stop_bench=True):
        remote_path = os.path.join(self.remote_hdb_location, remote_path)
        ret = False
        if do_stop_bench:
            stop_bench()
        try:
            ret = self.db_module.upload_file(local_path, remote_path, False)
        except Exception as e:
            log.exception(e)

        return ret

    def delete_file_on_db_module(self, remote_path, do_stop_bench=True):
        remote_path = os.path.join(self.remote_hdb_location, remote_path)
        ret = False
        if do_stop_bench:
            stop_bench()
        try:
            ret = self.db_module.delete_file(remote_path, False)
        except Exception as e:
            log.exception(e)

        return ret

    def get_file_list_from_db_module(self, path=None, do_stop_bench=False):
        file_list = None
        if do_stop_bench:
            stop_bench()
        try:
            if path is None:
                path = self.remote_hdb_location
            else:
                path = os.path.join(self.remote_hdb_location, path)
            file_list = self.db_module.get_files_list(path)
        except Exception as e:
            log.exception(e)

        return file_list
