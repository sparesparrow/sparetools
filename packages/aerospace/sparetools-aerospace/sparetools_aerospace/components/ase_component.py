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
// File Name: ase_module.py
//
// Program:   TITAN
//
// Purpose:   ASE module class.
//
// Notes:     None
//
//********************************************************************************************
//********************************************************************************************
"""

# This module defines Module object representing MAU modules, such as CMC (AGM), or NIC. These have different
# implementation for EASE and different for DEOS (minibench).
#
# .. _Google Python Style Guide:
#    http://google.github.io/styleguide/pyguide.html

import time
import glob
import logging
import os
# Standard
import shutil
import stat
from os.path import join

# Internal
from .module import Module

# External
log = logging.getLogger('__main__.' + __name__)


class AseModule(Module):
    """
    Class implementing EASE verion of MAU module (e.g. CMC module). It utilizes FTP client to communicate with the
    actual module. Should be used on mini-benchce/SITS.
    """

    def __init__(self, config_loader):
        super().__init__()
        self.backupDir = None
        self.loader = config_loader
        # TODO: remove after CMCF/plafroms can create cmcf log file
        self._init_files()

    def init(self):
        print("Method not implemented.")

    def start(self, delay=-1):
        print("Method not implemented.")

    def stop(self):
        print("Method not implemented.")

    def restart(self):
        print("Method not implemented.")

    def delete_file(self, module_path, backup_enabled=True):
        """
        Deletes single file from the module.

        Args:
            module_path: file path on the module, e.g. "/CFA/OMS/OMS_OMI.DB"
            backup_enabled: optional flag specifying if backup should apply for these files, True by default

        Returns:
            True if file was succesfuly deleted, False otherwise
        """
        if '*' in module_path:
            filelist = glob.glob(self.__module_path_to_abs_path(module_path))
            module_path_list = []
            for filename in filelist:
                module_path_list.append(self.__abs_path_to_module_path(filename))
            return self.delete_multiple_files(module_path_list, backup_enabled)
        return self.delete_multiple_files([module_path], backup_enabled)

    def file_exists(self, module_path):
        """
        Checks if file exists on the module. Supports "*" wildcard at the end of the path.

        Args:
            module_path: Path to the file

        Returns:
            True if file exists, False otherwise
        """
        if module_path.endswith("*"):
            module_path = module_path[:len(module_path) - 1]
            files = os.listdir(os.path.dirname(module_path))
            for file in files:
                if file.startswith(module_path):
                    return True
            return False
        return os.path.exists(self.__module_path_to_abs_path(module_path))

    def delete_multiple_files(self, file_paths, backup_enabled=True):
        """
        Deletes given list of files from the module.

        Args:
            file_paths: list of module file paths, e.g. ["/CFA/OMS/OMS_OMI.DB","/CFA/OMS/OMS_LDI.DB"]
            backup_enabled: optional flag specifying if backup should apply for these files, True by default

        Returns:
            True if all files were succesfuly deleted, False otherwise
        """
        status = True

        if backup_enabled:
            self.backup(self.loader.bench.local_backup_dir)
            self.backup_files(file_paths)

        for modulePath in file_paths:
            abs_path = self.__module_path_to_abs_path(modulePath)
            if os.path.isfile(abs_path):
                try:
                    log.info("Deleting " + modulePath)
                    try:
                        os.remove(abs_path)
                    except IOError:
                        # possibly issue with file permissions (read only flag), try lift them
                        os.chmod(abs_path, stat.S_IWRITE)
                        os.unlink(abs_path)
                        os.remove(abs_path)
                except IOError:
                    status = False
            else:
                status = False
        return status

    def download_file(self, module_path, local_path, echo=True):
        """
        Downloads single file from the module.

        Args:
            module_path: module file path (source), e.g. "/CFA/OMS/OMS_OMI.DB"
            local_path: local file path (destination), e.g. "OMS_OMI.DB"
            echo: optional flag defining if downloaded files names should be printed, True by default

        Returns:
            True if file was succesfuly downloaded, False otherwise
        """
        if echo:
            log.info("Downloading " + module_path)
        dest_dir = os.path.dirname(local_path)
        if dest_dir != '' and not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        if os.path.isfile(self.__module_path_to_abs_path(module_path)):
            for retry in range(10):
                try:
                    shutil.copyfile(self.__module_path_to_abs_path(module_path), local_path)
                    break
                except PermissionError as e:
                    log.exception(e)
                    # Retry after some time.
                    time.sleep(1)
        return True

    def download_multiple_files(self, paths_list, echo=True):
        """
        Downloads given list of files from the module.

        Args:
            paths_list: list of (modulePath, localPath) pairs of local file path
                and module file path  e.g. [("/CFA/OMS/OMS_OMI.DB","OMS_OMI.DB"), ("/CFA/OMS/OMS_LDI.DB","OMS_LDI.DB")]
            echo: optional flag defining if downloaded files names should be printed, True by default

        Returns:
            True if files were succesfuly downloaded, False otherwise
        """
        status = True
        for (module_path, local_path) in paths_list:
            if not self.download_file(module_path, local_path, echo):
                status = False
        return status

    def upload_file(self, local_path, module_path, backup_enabled=True):
        """
        Uploads single file from the module.

        Args:
            local_path: local file path (source), e.g. "OMS_OMI.DB"
            module_path: module file path (destination), e.g. "/CFA/OMS/OMS_OMI.DB"
            backup_enabled: optional flag specifying if backup should apply for these files, True by default

        Returns:
            True if file was succesfuly uploaded, False otherwise
        """
        return self.upload_multiple_files([(local_path, module_path)], backup_enabled)

    def upload_multiple_files(self, paths_list, backup_enabled=True):
        """
        Uploads given list of files to the module.

        Args:
            paths_list: list of (localPath, moduleFilePath) pairs of local file path
                         and module file path  e.g. [(".","OMS_OMI.DB"), (".","OMS_LDI.DB")]
            backup_enabled: optional flag specifying if backup should apply for these files, True by default

        Returns:
            True if files were succesfuly uploaded, False otherwise
        """
        status = True

        if backup_enabled:
            list_to_backup = []
            for (source, destination) in paths_list:
                list_to_backup.append(destination)
            self.backup_files(list_to_backup)

        for (source, destination) in paths_list:
            abs_path = self.__module_path_to_abs_path(destination)
            if os.path.isfile(source):
                try:
                    log.info("Uploading " + destination)
                    try:
                        shutil.copyfile(source, abs_path)
                    except IOError:
                        # possibly issue with file permissions (read only flag), try lift them
                        os.chmod(abs_path, stat.S_IWRITE)
                        os.unlink(abs_path)
                        shutil.copyfile(source, abs_path)
                except IOError as e:
                    log.error("Failed to upload %s (%s) ", destination, str(e))
                    status = False
            else:
                status = False
        return status

    def load_image(self, image):
        """
        Loads given image to the module

        Args:
            image: TBD - needs to be defined

        Returns:
            True if files were succesfuly uploaded, False otherwise
        """
        return

    def get_files_list(self, path='*'):
        """
        Loads files in given module path

        Args:
            path (str): module path

        Returns:
            List of filename paths in lower case.
        """
        files = glob.glob(self.__module_path_to_abs_path(path), recursive=True)
        module_paths_list = []
        for filename in files:
            module_paths_list.append(self.__abs_path_to_module_path(filename).lower())
        return module_paths_list

    def __module_path_to_abs_path(self, path):
        path = os.path.normpath(path.strip('/').strip('\\'))
        parts = path.split(os.sep)

        if parts[0].upper() == 'CFA':
            fullpath = join(self.configuration['EASEPath'], 'platforms', self.configuration['Platform'], path)
        elif parts[0].upper() == 'EEPROM':
            fullpath = path
        else:  # ROOT, assume the DEOS folder on EASE...

            fullpath = join(self.loader.bench['ase_root'],
                            path)
            # fullpath = join(self.configuration['EASEPath'], 'platforms', self.configuration['Platform'], 'DEOS', path)
        return fullpath

    def __abs_path_to_module_path(self, path):
        # relative = os.path.relpath(path, join(self.configuration['EASEPath'],
        #                                      'platforms',
        #                                      self.configuration['Platform']))
        relative = os.path.relpath(path, self.loader.bench['ase_root'])
        parts = relative.split(os.sep)
        if parts[0].upper() == 'CFA':
            return '/' + relative.replace('\\', '/')
        elif parts[0].upper() == 'APU':
            return '/' + relative.replace('\\', '/')
        elif parts[0].upper() == 'PMU':
            return '/' + relative.replace('\\', '/')
        elif parts[0] == 'FFS':
            return path
        elif parts[0].upper() == 'DEOS':  # ROOT
            return parts[1]
        else:
            raise ValueError('Unknown EASE directory!')

    def _init_files(self):
        file_path = self.__module_path_to_abs_path(r"APU\oms_cmcf.log")
        if not os.path.exists(file_path):
            open(file_path, 'w').close()


if __name__ == '__main__':
    print("Main of module: " + __file__ + "entered")
