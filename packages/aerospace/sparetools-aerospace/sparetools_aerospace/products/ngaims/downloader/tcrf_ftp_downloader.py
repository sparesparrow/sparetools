#
# DATA_RIGHTS:  HONEYWELL CONFIDENTIAL & PROPRIETARY
#              THIS WORK CONTAINS VALUABLE CONFIDENTIAL AND PROPRIETARY
#              INFORMATION. DISCLOSURE, USE OR REPRODUCTION OUTSIDE OF
#              HONEYWELL INTERNATIONAL, INC. IS PROHIBITED EXCEPT AS
#              AUTHORIZED IN WRITING. THIS UNPUBLISHED WORK IS PROTECTED BY
#              THE LAWS OF THE UNITED STATES AND OTHER COUNTRIES. IN THE
#              EVENT OF PUBLICATION, THE FOLLOWING NOTICE SHALL APPLY:
#              COPR. 2020-2022 HONEYWELL INTERNATIONAL, INC. ALL RIGHTS RESERVED.
#
################################################################################
#
# downloader.py
#
# Description:
#
# Download recorded files from DPM2 to folder on bench using ftp.
#
################################################################################

################################################################################
# Imports
import fnmatch
import logging
import os
from time import sleep
from tkinter import filedialog

from ngapy.bench.bench_factory import BenchFactory
from ngapy.bench.sits_bench import SITSBench

log = logging.getLogger('__main__.' + __name__)


################################################################################
# Public variables

# Public interface

# class TcrfFtpDownloader
class TcrfFtpDownloader:

    # Attributes
    # -----------------------------------------------------------------------------

    # Methods
    # -----------------------------------------------------------------------------

    # Class Constructor.
    def __init__(
            self,
            gui_root
    ):
        self._gui_root = gui_root  # Root GUI window.
        self._local_dir = ""  # local folder to download tcrf files.
        self._tb = BenchFactory()

    # The method get name of local folder.
    @property
    def local_dir(self):
        return self._local_dir

    # The method select local folder.
    def _determine_local_dir(
            self,
            initial_local_dir=None  # Name of initial directory.
    ):
        if initial_local_dir:
            self._local_dir = filedialog.askdirectory(
                parent=self._gui_root,
                initialdir=initial_local_dir,
                title="Select folder to download recorded files:",
                mustexist=True
            )

        return
    # The method check DPM2 is online.
    def checkBench(
            self
    ):
        if isinstance(self._tb, SITSBench):
                if self._tb.selected_module_name() in 'DPM2':
                    self._tb.select_module("DPM2")

                ping_result = self._tb.get_selected_module().verify_operational_by_ping()
                if not ping_result:
                    log.info("Module is not online ... try start.")
                    self._tb.start()
                    print("Wait some time")
                    sleep(200)
                    ping_result2 = self._tb.get_selected_module().verify_operational_by_ping()
                    if not ping_result2:
                        raise Exception("Module is not online. Terminating")

                return True
        else :
            raise Exception("Function is implemented only for SITSBench. Terminating")


    # The method download TCRF files from DPM2.
    def download(
            self,
            initial_local_dir=None  # Name of initial directory.
    ):
        file_list = None
        try:
            self._determine_local_dir(initial_local_dir)
            if self.checkBench():
                file_list = self._tb.get_files_list('/cffs/MP00')

                for file in file_list:
                    if fnmatch.fnmatch(file, 'tcrf*.tcrf'):
                        self._tb.download_file(file, self._local_dir)
                        self._tb.delete_file(file)

        except Exception as e:
            log.exception(e)

        return
# end class TcrfFtpDownloader
################################################################################
# Public interface functions
# downloader.py