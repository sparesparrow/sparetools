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
import subprocess
from pathlib import Path
from subprocess import Popen

from ngapy.conan.conan_functions import download_python_interpreter
from ngapy.launcher.conan_launcher import prepare_package_script_arguments
from sparetools_aerospace.products.ngaims.setup_environment import get_oms_repository_root, get_oms_repository_config


def get_ngaims_test_root():
    config = get_oms_repository_config()
    return config.conan_package_config['ngaims-tests'][2]


def get_ngaims_test_files():
    ngaims_test_package_path = get_ngaims_test_root()
    ngaims_test_files = list(ngaims_test_package_path.glob('**/*.py'))
    ngaims_test_files_relative = [x.relative_to(ngaims_test_package_path) for x in ngaims_test_files]
    return ngaims_test_files_relative


def run_test(test_file):
    test_file = Path(test_file)
    prepare_package_script_arguments(get_oms_repository_root(), '')
    full_conan, python_path = download_python_interpreter(get_oms_repository_root())
    process = Popen(f'{python_path} {test_file}', creationflags=subprocess.CREATE_NEW_CONSOLE)
    process.communicate()
