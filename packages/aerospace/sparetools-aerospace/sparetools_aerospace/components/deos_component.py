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
// File Name: deos_module.py
//
// Program:   TITAN
//
// Purpose:   DEOS module class.
//
// Notes:   This module defines Module object representing MAU modules, such as CMC (AGM), or NIC. These have different
// implementation for EASE and different for DEOS (minibench).
//
// .. _Google Python Style Guide: http://google.github.io/styleguide/pyguide.html
//
//********************************************************************************************
//********************************************************************************************
"""

# Standard
import logging
# Internal
from time import sleep

from ngapy.util.ssh_msg import send_start_stop_ssh_msg
from .deos_ftp_client import DeosFtpClient
from .ftp_module import FtpModule


# External
log = logging.getLogger('__main__.' + __name__)


class DeosModule(FtpModule):
    """
    Implements DEOS module which can be manipulated through FTP (supports also for example  Start/Stop)
    """

    def __init__(self, config_loader):
        super().__init__()
        self.local_backup_dir = None
        self.loader = config_loader
        self.ftp_client = None

    def __exit__(self, exc_type, exc_value, traceback):
        if self.ftp_client:
            self.ftp_client.disconnect_ftp()

    def init(self, module_config):
        """
        Initializes FTP connection to the DEOS module.
        """

        self.ftp_client = DeosFtpClient(module_config.ip_address,
                                        module_config.user_name,
                                        module_config.password)

    def start(self, delay=-1):
        """
        Starts the DEOS module using the FTP client.
        """
        log.info("Starting DEOS module... ")
        return self.ftp_client.set_deos_mode_device(0)

    def stop(self):
        """
        Stop the DEOS module using the FTP client.
        """
        log.info("Stopping DEOS module... ")
        return self.ftp_client.set_deos_mode_device(3)

    def restart(self):
        """
        Restarts the DEOS module using the FTP client. This is effectively same
        as Stop(), Start().
        """
        self.stop()
        self.start()

    def verify_operational_by_ping(self):
        """
        Verifies if module is operational by using ping to its address
        :return: True if host respond, False if not, None if error
        """
        if self.ftp_client:
            return self.ftp_client.verify_by_ping()
        return None

    @staticmethod
    def hw_stop():
        """
        HW stop of DPM
        :return: None
        """
        send_start_stop_ssh_msg(False)

    @staticmethod
    def hw_start():
        """
        HW start of DPM
        :return: None
        """
        send_start_stop_ssh_msg(True)

    def hw_restart(self):
        """
        HW restart of DPM
        :return: None
        """
        self.hw_start()
        sleep(1)
        self.hw_stop()


if __name__ == '__main__':
    print("Main of module: " + __file__ + "entered")
