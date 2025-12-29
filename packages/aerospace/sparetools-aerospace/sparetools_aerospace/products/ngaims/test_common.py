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
import logging
import os
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock
import sqlite3
import munch

from ngapy.bench.bench_factory import TestBenchContainer
from ngapy.conan.conan_functions import download_python_interpreter, get_package_details, remove_conan_lock_files
from ngapy.io_platform import IoOperationStatus
from sparetools_aerospace.products.ngaims.ate_interface.cmcf_ate import AteFactory
from sparetools_aerospace.products.ngaims.io_parameters.parameters_manager import InputParameterManager, OutputParameterManager
from sparetools_aerospace.products.ngaims.maintenance_model.maintenance_model_composition import MaintenanceModelComposition
from sparetools_aerospace.products.ngaims.maintenance_model.maintenance_model_loader import MaintenanceModelLoader
from sparetools_aerospace.products.ngaims.setup_environment import get_oms_repository_config
from sparetools_aerospace.products.ngaims.test_execution.run_test_functions import prepare_cmcf_bench, wait_for_cmcf_init
from ngapy.util.copy_tools import copy_file
from ngapy.util.custom_logging import setup_logging_from_config
from ngapy.util.execute_command import execute_command
from sparetools_aerospace.products.ngaims.common_functions import is_ase_run, clear_folder_local
from ngapy.miscellaneous.http_client import HttpClient

mock_set_state = {}


def store_state(array):
    for item in array:
        mock_set_state[item.name] = item
        item.operation_status = IoOperationStatus.SUCCESS


def get_state(array):
    for index in range(len(array)):
        try:
            array[index] = mock_set_state[array[index].name]
            array[index].operation_status = IoOperationStatus.SUCCESS
        except:
            pass
    return array


io_manager_mock = MagicMock()
io_manager_mock.set_values.side_effect = store_state
io_manager_mock.get_values.side_effect = get_state


def get_mocked_input_io_manager(maintenance_model_loader):
    return InputParameterManager(maintenance_model_loader, get_oms_repository_config(), io_manager_mock)


def get_mocked_output_io_manager(maintenance_model_loader):
    return OutputParameterManager(maintenance_model_loader, get_oms_repository_config(), io_manager_mock)


def get_real_input_io_manager(maintenance_model_loader):
    return InputParameterManager(maintenance_model_loader, get_oms_repository_config())


def get_real_output_io_manager(maintenance_model_loader):
    return OutputParameterManager(maintenance_model_loader, get_oms_repository_config())


def create_ldi_model_loader():
    maintenance_model_loader = MaintenanceModelLoader()
    maintenance_model_loader.load_ldi()
    return maintenance_model_loader


def create_omi_model_loader():
    maintenance_model_loader = MaintenanceModelLoader()
    maintenance_model_loader.load_omi()
    return maintenance_model_loader


def create_tcrf_model_loader():
    maintenance_model_loader = MaintenanceModelLoader()
    maintenance_model_loader.load_tcrf()
    return maintenance_model_loader


def prepare_full_external_dependencies_for_cmcf_unit_test():
    conanfile_path = Path(__file__).parent / '_unit_tests_support'
    remove_conan_lock_files()

    conan_path, python_path = download_python_interpreter(conanfile_path)
    os.environ['TITAN_BUILD_SET_OVERRIDE'] = 'Desktop - Full OMS;ASE-dev-rls'
    os.environ['CONAN_NO_PACKAGE_CONTENT'] = 'X'
    os.environ['ENV_SKIP_PMU_CONTROLLER'] = 'X'
    ngaims_info = get_package_details(conanfile_path, 'ngaims', options='-o ngaims:product_type=GaTitan_Custom_Product')
    bf = Path(ngaims_info['build_folder'])
    os.environ['ENV_REPOSITORY_ROOT'] = str(bf)
    if not bf.exists():
        result, _ = execute_command(
            f'{conan_path} install . -o ngaims:product_type=GaTitan_Custom_Product -r nga-conan '
            f'--build=ngaims',
            cwd=str(conanfile_path))
    copy_file(Path(ngaims_info['export_folder']) / 'conanfile.py', bf / 'conanfile.py')
    prepare_cmcf_bench()


def prepare_external_dependencies():
    ate = AteFactory().get_ate_device()
    wait_for_cmcf_init(ate)
    model_loader = create_ldi_model_loader()
    input_io_manager = get_real_input_io_manager(model_loader)
    output_io_manager = get_real_output_io_manager(model_loader)
    return model_loader, munch.munchify({'input_io_manager': input_io_manager, 'output_io_manager': output_io_manager,
                                         'ate': ate})


class TestPrepareCmcfDeps(TestCase):
    def setUp(self) -> None:
        setup_logging_from_config()
        prepare_full_external_dependencies_for_cmcf_unit_test()
        self.bench_object = TestBenchContainer().get_instance()
        self.bench_object.stop()
        self.bench_object.start()
        self.model, self.external_dependencies = prepare_external_dependencies()
        self.maintenance_model_composition = MaintenanceModelComposition(self.model, self.external_dependencies)
        self.maintenance_model_loader = self.model

    def tearDown(self) -> None:
        self.bench_object.stop()


class CommonNgaimsAppManager:

    ASE_TARGET = os.path.join('Build', 'Bdtte')
    SITS_MODULE = "INSU1"

    class Target:
        def __init__(self, id_st, name, storage_name, folder):
            self.id = id_st
            self.tgt_name = name
            self.storage_name = storage_name
            self.folder = folder

    def __init__(self):
        self.cfg_hndl = get_oms_repository_config()
        self.log = logging.getLogger('__main__.' + __name__)
        self.targets = []
        self.http_client = None
        if not is_ase_run():
            self.connection_info = None
            self.set_up_module_connection()

    def set_up_module_connection(self):
        self.connection_info = {}
        try:
            for module in self.cfg_hndl.bench.modules:
                if module.name == CommonNgaimsAppManager.SITS_MODULE:
                    self.connection_info["ip"] = module.ip_address
                    self.connection_info["username"] = module.user_name
                    self.connection_info["password"] = module.password
                    self.connection_info["http_client"] = HttpClient(self.connection_info["username"],
                                                                     self.connection_info["password"])
                    self.connection_info["area"] = "cffs"
        except:
            self.log.info("Unable to initialize connection to SITS module")

    def get_targets(self):
        return self.targets

    def reload_targets(self, omi_path):
        connection = sqlite3.connect(omi_path)
        r_s = connection.execute("SELECT TargetStorage.Id, Target.Name, TargetStorage.Name, "
                                 "SystemName, StorageName FROM TargetStorage "
                                 "LEFT JOIN Target ON TargetStorage.TargetId==Target.Id "
                                 "ORDER BY TargetStorage.Id;")
        for item in r_s.fetchall():
            system_name = item[3] if item[3] != ' ' else ''
            storage_name = item[4] if item[4] != ' ' else ''
            self.targets.append(self.Target(item[0], item[1], item[2], os.path.join(system_name, storage_name)))

    def get_target_content(self, target_storage_id=1):
        if target_storage_id not in [tgt.id for tgt in self.targets]:
            self.targets.append(self.Target(target_storage_id, "UNKNOWN", "UNKNOWN", './'))

        path = [tgt.folder for tgt in self.targets if tgt.id == target_storage_id][0]

        if is_ase_run():
            dest_path = os.path.join(os.environ['ENV_REPOSITORY_ROOT'], CommonNgaimsAppManager.ASE_TARGET,
                                     path)
            return os.listdir(dest_path) if os.path.isdir(dest_path) else []
        else:
            src_path = f"https://{self.connection_info['ip']}/{self.connection_info['area']}/dir"
            response = self.connection_info["http_client"].get_file_list(f"{src_path}")
            if not isinstance(response, dict):
                self.log.info(response)
                return []

            dir_list = []
            for file in response:
                if file["path"] != path:
                    continue
                else:
                    dir_list.append((file["name"], file["isDir"]))
            return dir_list

    def get_files_from_target(self, target_storage_id=1):
        if target_storage_id not in [tgt.id for tgt in self.targets]:
            self.targets.append(self.Target(target_storage_id, "UNKNOWN", "UNKNOWN", './'))

        path = [tgt.folder for tgt in self.targets if tgt.id == target_storage_id][0]

        if is_ase_run():
            return os.path.join(os.environ['ENV_REPOSITORY_ROOT'], CommonNgaimsAppManager.ASE_TARGET,
                                path)
        else:
            src_path = f"https://{self.connection_info['ip']}/{self.connection_info['area']}/" \
                       f"{path}"
            response = self.connection_info["http_client"].get_file_list(f"{src_path}")
            if not isinstance(response, dict):
                self.log.info(response)
                return []

            dir_list = []
            for file in response:
                if file["path"] == '' or file["isDir"]:
                    continue

                if self.get_file_from_target(f"{file['filename']}", target_storage_id):
                    dir_list.append(file["name"])

            return dir_list

    def get_file_from_target(self, filename, target_storage_id=1):
        if target_storage_id not in [tgt.id for tgt in self.targets]:
            self.targets.append(self.Target(target_storage_id, "UNKNOWN", "UNKNOWN", './'))

        path = [tgt.folder for tgt in self.targets if tgt.id == target_storage_id][0]

        if is_ase_run():
            return os.path.join(os.environ['ENV_REPOSITORY_ROOT'], CommonNgaimsAppManager.ASE_TARGET,
                                path, filename)
        else:
            src_path = f"https://{self.connection_info['ip']}/{self.connection_info['area']}/" \
                       f"{path}/{filename}"
            response = self.connection_info["http_client"].get_file(f"{src_path}/get?filename={filename}", filename)
            if not response:
                self.log.info("Unable to download specified file.")
                return None

            return filename

    def clear_target(self, target_storage_id=1):
        if target_storage_id not in [tgt.id for tgt in self.targets]:
            self.targets.append(self.Target(target_storage_id, "UNKNOWN", "UNKNOWN", './'))

        path = [tgt.folder for tgt in self.targets if tgt.id == target_storage_id][0]

        if is_ase_run():
            clear_folder_local(os.path.join(os.environ['ENV_REPOSITORY_ROOT'], CommonNgaimsAppManager.ASE_TARGET,
                                            path))
        else:
            src_path = f"https://{self.connection_info['ip']}/{self.connection_info['area']}/dir"
            response = self.connection_info["http_client"].get_file_list(f"{src_path}")
            for file in response:
                if file["path"] != path:
                    continue
                if file["isDir"]:
                    src_path = f"https://{self.connection_info['ip']}/{self.connection_info['area']}/" \
                               f"rmdir?directory={path}/{file['filename']}"
                    response = self.connection_info["http_client"].get_file_list(f"{src_path}")
                else:
                    src_path = f"https://{self.connection_info['ip']}/{self.connection_info['area']}/" \
                               f"del?filename={path}/{file['filename']}"
                    response = self.connection_info["http_client"].get_file_list(f"{src_path}")

            if not response:
                self.log.info("Unable to clear target")
                return False

            return True
