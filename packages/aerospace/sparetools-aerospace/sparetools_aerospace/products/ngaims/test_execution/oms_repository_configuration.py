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
from pathlib import Path

import munch

from ngapy.conan.conan_functions import get_ngapy_root
from ngapy.exceptions.ngapy_exceptions import NgapyConfigurationError
from sparetools_aerospace.products.ngaims.setup_environment import get_oms_repository_config, get_oms_repository_root

log = logging.getLogger('__main__.' + __name__)


def test_path(path_to_test):
    if not Path(path_to_test).exists():
        log.warning(f'Path invalid: {path_to_test}')
    return path_to_test


class OmsRepositoryConfiguration:
    def __init__(self):
        self.__config_dict = {}

    @property
    def config(self):
        try:
            loaded_config = get_oms_repository_config()
        except NgapyConfigurationError as ex:
            print(f'Exception {ex}, DevBar component will not work as expected!')
            return None
        ngapy_path = get_ngapy_root(get_oms_repository_root())
        self.__config_dict = {
            'packages': loaded_config.conan_package_config,
            'ngapy': test_path(ngapy_path),
            'python_interpreter': test_path(
                loaded_config.conan_package_config['titan-python-environment'][2] / 'python.exe'),
            'pexp': test_path(ngapy_path /
                              r'ngapy\product_specific\ngaims\gui\devbar\_ProcessHacker\x64'
                              r'\ProcessHacker.exe'),
            'apu': test_path(loaded_config.oms_repository_layout.ase_apu_root),
            'pmu': test_path(loaded_config.oms_repository_layout.ase_pmu_root),
            'tars_root': test_path(loaded_config.oms_repository_layout.tars_root),
            'ase_root': test_path(loaded_config.oms_repository_layout.ase_root),
            'product_root': test_path(loaded_config.oms_repository_layout.product_root),
            'ldi': test_path(loaded_config.oms_repository_layout.runtime_files.ase.ldi_path),
            'tcrf_oem': test_path(loaded_config.oms_repository_layout.runtime_files.ase.tcrf_oem_path),
            'sln': test_path(loaded_config.oms_repository_layout.vs17_sln_path),
            'atetest': test_path(loaded_config.oms_repository_layout.ate_app_test_dll),
            'oms_utility': test_path(loaded_config.oms_repository_layout.oms_utility),
            'atedll': test_path(loaded_config.oms_repository_layout.ate_dll),
            'ateip': loaded_config.oms_runtime.ate_ip,
            'ateport': loaded_config.oms_runtime.ate_port,
            'ossl': test_path(loaded_config.oms_repository_layout.ossl_exec),
            'pssl': test_path(loaded_config.oms_repository_layout.ossl_exec),
            'platforms': test_path(loaded_config.oms_repository_layout.build_root),
            'dtf': test_path(loaded_config.oms_repository_layout.dtfspy_tool),
            'cmc_partition_id': loaded_config.oms_runtime.oms_cmcf_partition_id,
            'tcrf_partition_id': loaded_config.oms_runtime.oms_tcrf_partition_id,
            'module_name': loaded_config.oms_runtime.oms_module_name,
        }
        return munch.munchify(self.__config_dict)
