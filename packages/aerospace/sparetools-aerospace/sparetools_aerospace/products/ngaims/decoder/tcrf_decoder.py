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
################################################################################
#
# tcrf_decoder.py
#
# Description:
#
# TCRF decoder utilities.
#
# The module defines interface and functionality for decoding TCRF reports.
#
################################################################################

################################################################################
# Imports

import logging
import os
from tkinter import filedialog

from sparetools_aerospace.products.ngaims.decoder.tcrf_report import TCRFReport
from sparetools_aerospace.products.ngaims.test_execution.oms_repository_configuration import OmsRepositoryConfiguration

log = logging.getLogger('__main__.' + __name__)


################################################################################
# Public variables

# Flight data decoder tools.

def get_decoder_app():
    # OMS repository configuration.
    cfg = OmsRepositoryConfiguration()
    decoder_path = str(cfg.config.packages["flight-data-decoder"][2]) + "/bin"
    decoder_app = [f'java -jar "{os.path.join(decoder_path, file)}"' for file in os.listdir(decoder_path) \
                   if (file.startswith("decoder-manager") and file.endswith(".jar"))][0]
    return decoder_app


################################################################################
# Public interface

# class TCRFDecoder
# =============================================================================
# The class defines interface and functionality for decoding TCRF reports.
class TCRFDecoder:

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

        self._fred_file_name = ""  # Name of FRED file.
        self._tcrf_file_names = []  # List of input TCRF report files names.
        self._tcrf_file_names_str = ""  # String of input TCRF report files names.
        self._out_file_names = []  # List of output decoded TCRF report files names.
        self._out_file_names_str = ""  # String of output decoded TCRF report files names.

        self._reports = []  # List of decoded TCRF report dictionaries.

        return

    # The method gets name of FRED file.
    @property
    def fred_file_name(self):
        return self._fred_file_name

    # The method gets list of input TCRF report files names.
    @property
    def tcrf_file_names(self):
        return self._tcrf_file_names

    # The method gets list of output decoded TCRF report files names.
    @property
    def out_file_names(self):
        return self._out_file_names

    # The method gets list of decoded TCRF report dictionaries.
    @property
    def reports(self):
        return self._reports

    # The method determines files used by TCRF decoder application.
    def _determine_files(
            self,
            fred_file_name,  # Name of FRED file.
            tcrf_file_names  # List of names of TCRF report files.
    ):
        if fred_file_name:
            self._fred_file_name = fred_file_name

        if tcrf_file_names:
            for tcrf_file_name in tcrf_file_names:
                index = tcrf_file_name.rfind(".")
                out_file_name = (tcrf_file_name + ".csv") if (index < 0) else (tcrf_file_name[: index] + ".csv")

                self._tcrf_file_names.append(tcrf_file_name)
                self._out_file_names.append(out_file_name)
                self._tcrf_file_names_str += " \"" + tcrf_file_name + "\""
                self._out_file_names_str += " \"" + out_file_name + "\""

        return

    # The method determines files used by TCRF decoder application.
    def _determine_files_gui(
            self,
            fred_initial_dir_name,  # Name of initial directory, where to search FRED files.
            tcrf_initial_dir_name  # Name of initial directory, where to search TCRF files.
    ):
        if fred_initial_dir_name:
            self._fred_file_name = filedialog.askopenfilename(
                parent=self._gui_root,
                initialdir=fred_initial_dir_name,
                title="Select FRED decoding file:",
                filetypes=[("FRED files (.xml)", ".xml"), ("All files", ".*")]
            )

        if tcrf_initial_dir_name:
            self._tcrf_file_names = filedialog.askopenfilenames(
                parent=self._gui_root,
                initialdir=tcrf_initial_dir_name,
                title="Select TCRF record file(s):",
                filetypes=[("TCRF files (.tcrf)", ".tcrf"), ("All files", ".*")]
            )

            for tcrf_file_name in self._tcrf_file_names:
                index = tcrf_file_name.rfind(".")
                out_file_name = (tcrf_file_name + ".csv") if (index < 0) else (tcrf_file_name[: index] + ".csv")

                self._out_file_names.append(out_file_name)
                self._tcrf_file_names_str += " \"" + tcrf_file_name + "\""
                self._out_file_names_str += " \"" + out_file_name + "\""

        return

    # The method decodes TCRF report(s).
    def decode(
            self,
            fred_file_name=None,  # Name of FRED file.
            tcrf_file_names=None,  # List of names of TCRF report files.
            fred_initial_dir_name=None,  # Name of initial directory, where to search FRED files.
            tcrf_initial_dir_name=None  # Name of initial directory, where to search TCRF files.
    ):
        try:
            self._determine_files(fred_file_name, tcrf_file_names)
            self._determine_files_gui(fred_initial_dir_name, tcrf_initial_dir_name)

            os.system(
                f'{get_decoder_app()} -f \"{self._fred_file_name}\" -i {self._tcrf_file_names_str} -o {self._out_file_names_str} -csv 1')

        except Exception as ex:
            log.exception(ex)

        return

    # The method parses decoded TCRF report files, and produces TCRF report dictionaries.
    def parse(
            self,
            out_file_name=None,
            # Decoded output TCRF report file name. If None specified, then the last decoded files are taken.
            do_full=False  # Indicator, which indicates that full TCRF report shall be parsed.
    ):
        try:
            if out_file_name:
                report = TCRFReport()
                report.create(out_file_name, do_full)
                self._reports.append(report)

            else:
                for file_name in self._out_file_names:
                    report = TCRFReport()
                    report.create(file_name, do_full)
                    self._reports.append(report)

        except Exception as ex:
            log.exception(ex)

        return

# end class TCRFDecoder

################################################################################
# Public interface functions

# tcrf_decoder.py
