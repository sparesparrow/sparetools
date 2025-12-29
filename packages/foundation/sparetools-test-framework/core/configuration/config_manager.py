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
// File Name: config_manager.py
//
// Program:   TITAN
//
// Purpose:   Config loader class.
//
// Notes:     None
//
//********************************************************************************************
//********************************************************************************************
"""

"""
Configuration management system for SpareTools test framework.

Provides centralized configuration loading from multiple sources including
YAML files, environment variables, and package configurations.
"""

import glob
import logging
import os
import pprint
import re
import hashlib
import os
from pathlib import Path
import anyconfig
import munch


# Utility functions for configuration management
def get_file_metadata(file_path):
    """Get file metadata including MD5 hash."""
    with open(file_path, 'rb') as f:
        content = f.read()
        return {'MD5': hashlib.md5(content).hexdigest()}


def make_list_from_variable(var):
    """Convert variable to list."""
    if var is None:
        return []
    if isinstance(var, list):
        return var
    return [var]


def get_tuple_from_dict(d):
    """Convert dict to sorted tuple of items."""
    return tuple(sorted(d.items()))


class ConfigurationBase:
    """Simple base class for configuration management."""
    pass


log = logging.getLogger('__main__.' + __name__)


class ConfigManagerManager(ConfigurationBase):
    def _compute_key(self, **kwargs):
        additional_arguments = kwargs['additional_arguments']
        ac_merge = kwargs['ac_merge']
        files = self.get_config_files(**kwargs)
        files_hash = list(map(lambda file: get_file_metadata(file)['MD5'], files))
        return get_tuple_from_dict({'config_files': tuple(files),
                                    'config_files_hash': tuple(files_hash),
                                    'additional_arguments': get_tuple_from_dict(additional_arguments),
                                    'ac_merge': ac_merge,
                                    'environ': get_tuple_from_dict(dict(os.environ))})

    @staticmethod
    def get_config_files(**kwargs):
        config_folders = kwargs['config_folders']
        config_pattern = kwargs['config_pattern']
        recursive_config_search = kwargs['recursive_config_search']
        if config_folders is None:
            config_folders = get_config_path()
        files = []
        for path in make_list_from_variable(config_folders):
            if path is not None:
                files.extend(glob.glob(os.path.join(path, config_pattern), recursive=recursive_config_search))
        return files

    def _create_new_configuration(self, **kwargs):
        return ConfigManagerInstance(self.get_config_files(**kwargs), kwargs['additional_arguments'], kwargs['ac_merge'])


def get_config_path():
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(Path(__file__))))
    config_folder = os.path.join(base_path, "Conf")
    log.debug(f'Opening configs in {config_folder}')
    return config_folder


class ConfigManagerInstance:
    def __init__(self, config_files, additional_arguments, ac_merge):
        self.munchified_config = None
        self.config = dict()
        self.data_changed = True
        self.variable_re_pattern = re.compile(r'(.*)\${(.*)}(.*)')
        self.config = None

        self.config = anyconfig.load(config_files, ac_merge=ac_merge)
        self.update_and_merge(additional_arguments)

    def update_and_merge(self, additional_arguments):
        anyconfig.merge(self.config, dict(os.environ))
        anyconfig.merge(self.config, additional_arguments)
        self.update_reference_variables()

    def recursive_traverse(self, node, parent, key, cannot_expand=None):
        if cannot_expand is None:
            cannot_expand = list()
        if isinstance(node, list):
            for i in range(len(node)):
                self.recursive_traverse(node[i], node, i, cannot_expand)
        elif isinstance(node, dict):
            for config_value in node.items():
                self.recursive_traverse(config_value[1], node, config_value[0], cannot_expand)
        else:
            match = self.variable_re_pattern.match(str(node))
            if match is not None:
                try:
                    tag_evaluate = eval('self.munchified_config.' + match.group(2))
                    parent[key] = match.group(1) + str(tag_evaluate) + match.group(3)
                    self.data_changed = True
                except AttributeError:
                    cannot_expand.append(match.group(2))

    def update_reference_variables(self):
        while self.data_changed:
            self.data_changed = False
            self.munchified_config = munch.munchify(self.config)
            self.recursive_traverse(self.config, None, None)
        cannot_expand = []
        self.recursive_traverse(self.config, None, None, cannot_expand)
        if cannot_expand:
            log.info(f'Could not expand variables: {list(dict.fromkeys(cannot_expand))}')


def get_config_manager(config_folders=None, additional_arguments=None, ac_merge=anyconfig.MS_DICTS,
                      config_pattern=r'**\*.*', recursive_config_search=True) -> munch.Munch:
    if additional_arguments is None:
        additional_arguments = dict()
    config = ConfigManagerManager().get_configuration(config_folders=config_folders,
                                                     additional_arguments=additional_arguments,
                                                     ac_merge=ac_merge,
                                                     config_pattern=config_pattern,
                                                     recursive_config_search=recursive_config_search)
    return config.munchified_config


def get_conan_merged_configuration(root_folder, additional_arguments=dict(),
                                   ac_merge=anyconfig.MS_DICTS,
                                   config_pattern=r'**\*.*', recursive_config_search=True) -> munch.Munch:
    """Load configuration with conan package integration if available."""
    try:
        from ngapy.conan.conan_functions import get_all_package_config_folders, get_configuration_safe
        config_folders = []
        config_folders.extend(get_all_package_config_folders(root_folder))
        if additional_arguments is None:
            additional_arguments = dict()
        conan_configurations = get_configuration_safe(root_folder)
        for conan_configuration in conan_configurations.values():
            additional_arguments[f'PACKAGE_ROOT_{conan_configuration[0]}'] = conan_configuration[2]
        config = ConfigManagerManager().get_configuration(config_folders=config_folders,
                                                         additional_arguments=additional_arguments,
                                                         ac_merge=ac_merge,
                                                         config_pattern=config_pattern,
                                                         recursive_config_search=recursive_config_search)
        config.config['conan_package_config'] = conan_configurations
        config.munchified_config = munch.munchify(config.config)
        return config.munchified_config
    except ImportError:
        # Fallback to basic configuration loading without conan integration
        log.warning("Conan integration not available, loading basic configuration")
        return get_config_manager(root_folder, additional_arguments, ac_merge, config_pattern, recursive_config_search)
