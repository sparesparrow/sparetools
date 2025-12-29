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
// File Name: setup_environment.py
//
// Program:   TITAN
//
// Purpose:   Setup environment for NGAPy.
//
// Notes:     None
//
//********************************************************************************************
//********************************************************************************************
"""
import os
from pathlib import Path

from ngapy.exceptions.ngapy_exceptions import NgapyConfigurationError
from ngapy.util.copy_tools import copy_folder
from ngapy.util.file_operations import remove_files
from ngapy.util.setup_environment import get_repository_root, get_repository_config


def get_oms_repository_root():
    oms_repository_root = get_repository_root()
    return oms_repository_root


def get_oms_repository_config():
    if 'ENV_RUNTIME_MODULE_NAME' in os.environ:
        runtime_module_name = os.environ['ENV_RUNTIME_MODULE_NAME']
        # Temporary solution until I bring something better
        if runtime_module_name == 'INSU_1':
            copy_folder(Path(get_oms_repository_root()) / 'ConfHw', Path(get_oms_repository_root()) / 'Conf')
        else:
            remove_files([file_name.name for file_name in (Path(get_oms_repository_root()) / 'ConfHw').glob('*.*')],
                         Path(get_oms_repository_root()) / 'Conf')

    oms_repository_config = get_repository_config()
    # Quick check this is really OMS repository
    if hasattr(oms_repository_config, 'oms_repository_layout'):
        if hasattr(oms_repository_config.oms_repository_layout, 'vs17_sln_path'):
            return oms_repository_config
    else:
        raise NgapyConfigurationError(f'ENV_REPOSITORY_ROOT is not pointing to OMS repository')
