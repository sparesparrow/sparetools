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
import os
import shutil
import subprocess
import re

from datetime import datetime
from pathlib import Path

from ngapy.conan.conan_functions import download_python_interpreter
from ngapy.launcher.conan_launcher import top_level_path
from sparetools_aerospace.products.ngaims.test_execution.oms_repository_configuration import OmsRepositoryConfiguration
from ngapy.util.execute_command import execute_command
from ngapy.conan.conan_functions import get_default_conan, get_package_details

cfg = OmsRepositoryConfiguration()

dlls_to_remove = ["Qt6WebEngineCore.*", "Qt6ShaderTools.*", "Qt63D.*", "opengl32sw.dll", "libopenblas.*", "libcrypto.*",
                  ]


def get_resources(path):
    return path.parent / 'uiLayout.ui', \
           cfg.config.atedll, \
           path.parent / 'conanfile.py', \
           Path(cfg.config.atedll).parent / "libcurl.dll", \
           Path(cfg.config.atedll).parent.parent / "Bdtte" / 'BDTTE.dll', \
           Path(cfg.config.atedll).parent.parent / "Bdtte" / 'fileMap.csv'


def copy_resources():
    layout, atedll, conanfile, libcurl, bdttedll, filemap = get_resources(Path(os.environ["ENV_REPOSITORY_ROOT"]) /
                                                              cfg.config.oms_utility)
    shutil.copy(layout, os.path.join('oms_utility', 'uiLayout.ui'))
    shutil.copy(atedll, os.path.join('oms_utility', 'ATE.dll'))
    shutil.copy(libcurl, os.path.join('oms_utility', 'libcurl.dll'))
    shutil.copy(bdttedll, os.path.join('oms_utility', 'BDTTE.dll'))
    shutil.copy(filemap, os.path.join('oms_utility', 'fileMap.csv'))
    shutil.copy(conanfile, './')


def upload_package():
    path_to_conanfile = str(Path(__file__).parent)
    details = get_package_details(os.environ["ENV_REPOSITORY_ROOT"], "ngaims-icd-dev")
    icd_version = details['export_folder'].split('\\')[-4]
    date = datetime.today().strftime('%Y-%m-%d')
    rc, return_string = execute_command(f'{get_default_conan()} export-pkg {path_to_conanfile} -pf oms_utility '
                                        f'-o icd_version={icd_version} -o creation_date={date} --force')
    rc, return_string = execute_command(
        f'{get_default_conan()} search OmsUtility/*')
    latest = max(re.findall('OmsUtility/([^ ]+)', ' '.join(return_string)))
    rc, return_string = execute_command(f'{get_default_conan()} search OmsUtility/{latest}@ -q "icd_version={icd_version}"')
    reference = [line for line in return_string if "Package_ID" in line][0].strip().split(' ')[1]
    rc, return_string = execute_command(f'{get_default_conan()} upload OmsUtility/{latest}@:{reference} '
                                        f'-r nga-conan --force --all')


def create_oms_exe():
    full_conan, python_path = download_python_interpreter(os.environ["ENV_REPOSITORY_ROOT"])
    pyinstaller_path = Path(python_path).parent / "Scripts" / "pyinstaller"
    output_dir_change = '--distpath ' + str(Path(__file__).parent)
    os.environ['PATH'] = str(top_level_path(str(Path(__file__)))) + os.pathsep + os.environ['PATH']
    src_location = Path(os.environ["ENV_REPOSITORY_ROOT"]) / cfg.config.oms_utility
    include_dir = f"--paths={src_location.parent}"
    command = f"{str(pyinstaller_path)} --exclude-module cryptography" \
              f" --exclude-module numpy {output_dir_change} {include_dir} {src_location}"
    p = subprocess.Popen(command)
    p.wait()
    copy_resources()


def remove_dlls():
    all_files = os.listdir('oms_utility')
    for file_pattern in dlls_to_remove:
        r = re.compile(file_pattern)
        new_list = list(filter(r.match, all_files))
        for file_match in new_list:
            os.remove(os.path.join("oms_utility", file_match))


def remove_artifacts():
    try:
        os.remove("conanfile.py")
        os.remove("oms_utility.spec")
        shutil.rmtree("build")
        shutil.rmtree("oms_utility")
    except Exception as e:
        print(e)


if __name__ == '__main__':
    create_oms_exe()
    remove_dlls()
    upload_package()
    remove_artifacts()
