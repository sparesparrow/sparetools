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
// File Name: titan_developer_buddy_oms.py
//
// Program:   TITAN
//
// Purpose:   TITAN developer buddy - OMS.
//
// Notes:     None
//
//********************************************************************************************
//********************************************************************************************
"""
import logging
import os
from tkinter import *
from tkinter.ttk import *


from ngapy.gui import titan_developer_buddy
from ngapy.gui.titan_developer_buddy import TitanDeveloperBuddy
from sparetools_aerospace.products.ngaafcs.gui.devbar import devbar_window

log = logging.getLogger('__main__.' + __name__)


class TitanDeveloperBuddyFcs(TitanDeveloperBuddy):
    def __init__(self):
        super().__init__()
        self.devbar = LabelFrame(self.top_frame)
        self.devbar.config(height='10', width='254', text='DevBar')
        self.devbar.pack(side='left', fill=BOTH)
        devbar_window.create_buttons(self.devbar)
        devbar_window.log_target = self.log_dev_bar
        devbar_window.log_target_popen = self.log_dev_bar_popen
        devbar_window.buddy_kill_callback = self.kill_process
        self.product = None
        self.first_product_selection = True
        self.product_mode = None
        self.product_radio = []

    def open_repository_activity(self):
        os.environ['ENV_REPOSITORY_ROOT'] = self.file_path
        super().open_repository_activity()

    def log_dev_bar(self, command):
        log.debug(f'Opening DevBar command: {command}')
        try:
            os.startfile(command)
        except Exception as inst:
            log.error(f'Opening DevBar Exception: {inst}')

    def log_dev_bar_popen(self, command, **kwargs):
        log.debug(f'Opening DevBar command: {command}, params: {kwargs}')
        try:
            self.log_window.run_process_in_thread(command, **kwargs)
        except Exception as inst:
            log.error(f'Opening DevBar Exception: {inst}')

    def kill_process(self, called_from_devbar=False):
        if not called_from_devbar:
            from sparetools_aerospace.products.ngaims.gui.devbar import devbar_window
            devbar_window.kill_all()
        else:
            super().kill_process()

    @staticmethod
    def create_main_window():
        return TitanDeveloperBuddyFcs()


if __name__ == '__main__':
    titan_developer_buddy.run_buddy(TitanDeveloperBuddyFcs)
