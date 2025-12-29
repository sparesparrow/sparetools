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
// File Name: ftp_client.py
//
// Program:   TITAN
//
// Purpose:   FTP client class.
//
// Notes:  This module defines Module object representing MAU modules, such as CMC (AGM), or NIC. These have different
// implementation for EASE and different for DEOS (minibench).
//
// .. _Google Python Style Guide: http://google.github.io/styleguide/pyguide.html
//********************************************************************************************
//********************************************************************************************
"""

import ftplib
# Standard
import logging
import os


# External

# Internal

log = logging.getLogger('__main__.' + __name__)


class FtpClient:
    """
    Class representing a DEOS FTP Client.

    Args:
        ftpAddress (str): FTP server IP address
        targetPath (str): FTP server folder, "." by default
        blacklist (list): TBD
    """

    def __init__(self, ftp_address, user='', passwd='', target_path=".", blacklist=None, ftp_dir=''):
        """
        Constructor.
        """
        self.targetPath = target_path
        self.blackList = blacklist if blacklist else []
        self.ftpAddress = ftp_address
        self.ftpActive = False
        self.username = user
        self.password = passwd
        self.ftpDir = ftp_dir
        self.ftp = None

        if not os.path.exists(self.targetPath):
            os.makedirs(self.targetPath)

    def connect_to_ftp(self):
        """
        Connects to the FTP server defined in constructor.
        """
        if not self.ftpActive:
            log.debug("ConnectToFTP: opening ftp connection")
            try:
                self.ftp = ftplib.FTP(self.ftpAddress)
            except ftplib.error_reply as ex:
                log.error("ConnectToFTP:Following error occured for the module with " \
                                          + self.ftpAddress + " on attempt to connect to its FTP server:\n" + str(ex) + \
                                          "\nPlease make sure that module is up and the ftp connection to the module is closed and execute the program again if needed.\n")
                return False
            except ConnectionRefusedError as cre:
                log.error(cre)
                return False
            self.ftp.login(self.username, self.password)
            result = self.ftp.sendcmd(r'site cffs mount CFFS_RAM_RO cffsftp /cffs/')
            if self.ftpDir != '':
                self.ftp.cwd(self.ftpDir)
            self.ftpActive = True

            # safety sleep, sometimes when manipulating too short
            # after connection, error 530 appeared
            from time import sleep
            sleep(0.1)
            log.debug("ConnectToFTP: successful")
            return True
        return False

    def disconnect_ftp(self):
        """
        Disconnects from the FTP server defined in constructor.
        """
        if self.ftpActive:
            self.ftp.close()
            self.ftpActive = False
            log.debug("DisconnectFTP: FTP disconnected")
            return True
        return False

    def set_and_create_target_dir(self, target_dir):
        """
        Sets target dir for transfer and ensures it is created.
        """
        self.targetPath = target_dir
        if not os.path.exists(self.targetPath):
            os.makedirs(self.targetPath)

    def download_file(self, file_name, target_path):
        """
        Downloads file from the FTP server to local.

        Args:
            file_name: distant (FTP server) file name
            target_path: local file name/path

        Returns:
            True if succesfully downloaded
        """
        log.debug("DownloadFile: going to download file " + file_name)
        command = "RETR " + file_name
        if self.ftpActive:
            ftp = self.ftp
        else:
            ftp = ftplib.FTP(self.ftpAddress)
            ftp.login(self.username, self.password)
            result = self.ftp.sendcmd(r'site cffs mount CFFS_RAM_RO cffsftp /cffs/')
        f = open(str(target_path), 'wb')
        try:
            ftp.retrbinary(command, f.write)
            log.debug("DownloadFile: command executed")
        except ftplib.error_reply as ex:
            log.error("DownloadFile: command NOT executed due to following ERROR:")
            log.error(ex)
            return False
        except ftplib.error_perm as ex:
            log.error("DownloadFile: command NOT executed due to following ERROR:")
            log.error(ex)
            return False
        finally:
            log.debug("DownloadFile: closing file transfer connection")
            if not self.ftpActive:
                ftp.close()
            f.close()
        log.debug("DownloadFile: successful")
        return True

    def upload_file(self, file_name, target_path):
        """
        Uploads file from from local to the FTP server.

        Args:
            file_name: local file name/path
            target_path: distant (FTP server) file name

        Returns:
            True if succesfully uploaded
        """

        log.debug("UploadFile: going to upload file " + target_path)
        command = "STOR " + target_path
        if self.ftpActive:
            ftp = self.ftp
        else:
            ftp = ftplib.FTP(self.ftpAddress)
            ftp.login(self.username, self.password)
            result = self.ftp.sendcmd(r'site cffs mount CFFS_RAM_RO cffsftp /cffs/')
        f = open(str(file_name), 'rb')
        try:
            ftp.storbinary(command, f)
            log.debug("UploadFile: command executed")
        except ftplib.error_reply as ex:
            log.error("UploadFile: command NOT executed due to following ERROR:")
            log.error(ex)
            return False
        finally:
            log.debug("UploadFile: closing file transfer connection")
            if not self.ftpActive:
                ftp.close()
            f.close()
        log.debug("UploadFile: successful")
        return True

    def delete_file(self, file_name):
        """
        Deletes file from from the FTP server.

        Args:
            file_name: distant (FTP server) file name

        Returns:
            True if succesfully deleted
        """
        log.debug("DeleteFile: going to delete file " + file_name)
        if self.ftpActive:
            ftp = self.ftp
        else:
            ftp = ftplib.FTP(self.ftpAddress)
            ftp.login(self.username, self.password)
            result = self.ftp.sendcmd(r'site cffs mount CFFS_RAM_RO cffsftp /cffs/')
        try:
            #ftp.delete(file_name)
            dummy_file = open('dummy.txt', 'w')
            dummy_file.close()
            self.upload_file(os.path.join(os.getcwd(), 'dummy.txt'), file_name)
            log.debug("DeleteFile: command executed")
        except (ftplib.error_reply, ftplib.error_perm) as ex:
            log.error("DeleteFile: command NOT executed due to following ERROR:")
            log.error(str(ex))
            return False
        finally:
            log.debug("DeleteFile: closing file transfer connection")
            if not self.ftpActive:
                ftp.close()
        log.debug("DeleteFile: successful")
        return True

    def read_dir(self, fldr):
        """
        Gets list of the FTP Server files/folders.

        Args:
            fldr: destination FTP server folder

        Returns:
            list of files/folders
        """

        if self.ftpActive:
            ftp_con = self.ftp
        else:
            ftp_con = ftplib.FTP()
            ftp_con.connect(self.ftpAddress)
            ftp_con.login(self.username, self.password)

        rf = self.__walk(fldr, ftp_con)

        if not self.ftpActive:
            ftp_con.close()
        return rf

    def download_from_folder(self, folder_name):
        """
        Download all files from given folder.

        Args:
            folder_name: destination FTP server folder

        Returns:
            list of local paths
        """

        files = self.read_dir(folder_name)
        return_paths = []
        for f in files:
            flist = f.rpartition('/')
            return_paths.append(self.download_file(flist[2], flist[0]))
        return return_paths

    def __walk(self, dir, ftp_con):
        files = ftp_con.nlst(dir)
        rf = []

        for file in files:
            try:
                ftp_con.cwd(dir + "/" + file)
                rf.extend(self.__walk(dir + "/" + file, ftp_con))
            except ftplib.error_reply:
                pass
            except ftplib.error_perm:
                # this is not a directory, it is a file then
                rf.append(dir + "/" + file)
                pass

        return rf


class FTPProtocol:
    """
    Thin wrapper around existing FTPClient class.
    Provides protocol interface while preserving 100% of existing FTP logic.
    """

    def __init__(self, address, **kwargs):
        self._impl = FtpClient(address, **kwargs)

    def connect(self, address, **kwargs):
        return self._impl.connect_to_ftp()

    def disconnect(self):
        return self._impl.disconnect_ftp()

    def send_data(self, data):
        # FTP doesn't have a direct send_data method, delegate to upload
        raise NotImplementedError("FTP protocol doesn't support send_data")

    def receive_data(self):
        # FTP doesn't have a direct receive_data method, delegate to download
        raise NotImplementedError("FTP protocol doesn't support receive_data")

    def upload_file(self, local_path, remote_path):
        return self._impl.upload_file(local_path, remote_path)

    def download_file(self, remote_path, local_path):
        return self._impl.download_file(remote_path, local_path)

    def delete_file(self, remote_path):
        return self._impl.delete_file(remote_path)

    def list_directory(self, remote_path):
        return self._impl.read_dir(remote_path)


if __name__ == '__main__':
    print("Main of module: " + __file__ + "entered")
