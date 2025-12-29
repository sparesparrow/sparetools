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

"""
Environment-based configuration provider for SpareTools.

Provides utilities for loading configuration from environment variables
and repository paths.
"""

import os

from sparetools.core.configuration.config_manager import get_conan_merged_configuration


def get_path_by_os_variable(variable_name):
    if variable_name not in os.environ:
        raise ValueError(f'{variable_name} is not set. Please add it to your environment variables!')
    if not os.path.exists(os.environ[variable_name]):
        raise ValueError(f'{variable_name} is pointing to incorrect path')
    return os.environ[variable_name]


def get_config_by_os_variable(variable_name):
    config_path = get_path_by_os_variable(variable_name)
    config_loader = get_conan_merged_configuration(config_path)
    return config_loader


def get_repository_root():
    return get_path_by_os_variable('ENV_REPOSITORY_ROOT')


def get_config_from_env():
    return get_config_by_os_variable('ENV_REPOSITORY_ROOT')
