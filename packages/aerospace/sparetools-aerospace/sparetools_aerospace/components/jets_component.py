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
// File Name: jets_module.py
//
// Program:   TITAN
//
// Purpose:   JETS module class.
//
// Notes:     This module defines Module object representing JETS module.
//
//  .. _Google Python Style Guide: http://google.github.io/styleguide/pyguide.html
//
//********************************************************************************************
//********************************************************************************************
"""
# Standard

# External

# Internal
import logging

from sparetools.core.components.deos_ftp_client import DeosFtpClient
from sparetools.core.components.ftp_module import FtpModule
from ngapy.util.miscellaneous_functions import try_ping_with_timeout


log = logging.getLogger('__main__.' + __name__)


class JetsModule(FtpModule):
    """
    Class implementing JETS version of MAU module (e.g. CMC module).
    """

    def __init__(self, config_loader):
        super().__init__()
        self.backupDir = None
        self.loader = config_loader
        self.ftp_client = None

    def __exit__(self, exc_type, exc_value, traceback):
        if self.ftp_client:
            self.ftp_client.disconnect_ftp()

    def init(self, module_config):
        """
        Initializes FTP connection to the DEOS module.
        """

        self.ftp_client = DeosFtpClient(module_config.jets_ip,
                                        module_config.jets_user_name,
                                        module_config.jets_password)

    def start(self, delay=-1):
        log.info("Starting DEOS module... ")
        return self.ftp_client.set_deos_mode_device(0)

    def stop(self):
        log.info("Stopping DEOS module... ")
        return self.ftp_client.set_deos_mode_device(3)

    def restart(self):
        self.stop()
        self.start()

    def delete_file(self, module_path, backup_enabled=True):
        """
        Deletes single file from the module.

        Args:
            module_path: file path on the module, e.g. "/CFA/OMS/OMS_OMI.DB"
            backup_enabled: optional flag specifying if backup should apply for these files, True by default

        Returns:
            True if file was succesfuly deleted, False otherwise
        """
        raise NotImplementedError("Method not implemented.")

    def file_exists(self, module_path):
        """
        Checks if file exists on the module. Supports "*" wildcard at the end of the path.

        Args:
            module_path: Path to the file

        Returns:
            True if file exists, False otherwise
        """
        raise NotImplementedError("Method not implemented.")

    def delete_multiple_files(self, file_paths, backup_enabled=True):
        """
        Deletes given list of files from the module.

        Args:
            file_paths: list of module file paths, e.g. ["/CFA/OMS/OMS_OMI.DB","/CFA/OMS/OMS_LDI.DB"]
            backup_enabled: optional flag specifying if backup should apply for these files, True by default

        Returns:
            True if all files were succesfuly deleted, False otherwise
        """
        raise NotImplementedError("Method not implemented.")

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
        raise NotImplementedError("Method not implemented.")

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
        raise NotImplementedError("Method not implemented.")

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
        raise NotImplementedError("Method not implemented.")

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
        raise NotImplementedError("Method not implemented.")

    def load_image(self, image):
        """
        Loads given image to the module

        Args:
            image: TBD - needs to be defined

        Returns:
            True if files were succesfuly uploaded, False otherwise
        """
        raise NotImplementedError("Method not implemented.")

    def get_files_list(self, path='*'):
        """
        Loads files in given module path

        Args:
            path (str): module path

        Returns:
            List of filename paths in lower case.
        """
        raise NotImplementedError("Method not implemented.")

    def verify_operational_by_ping(self, timeout=120):
        """
        Verifies if module is operational by using ping to its address
        :return: True if host respond, False if not, None if error
        """
        return try_ping_with_timeout(self.loader.bench["jets_ip"], timeout=timeout)

    def __module_path_to_abs_path(self, path):
        raise NotImplementedError("Method not implemented.")

    def __abs_path_to_module_path(self, path):
        raise NotImplementedError("Method not implemented.")


if __name__ == '__main__':
    print("Main of module: " + __file__ + "entered")
