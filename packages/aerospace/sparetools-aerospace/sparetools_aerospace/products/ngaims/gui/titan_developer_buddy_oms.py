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
import re
from pathlib import Path
from tkinter import *
from tkinter.ttk import *

from ngapy.gui import titan_developer_buddy
from ngapy.gui.titan_developer_buddy import TitanDeveloperBuddy
from sparetools_aerospace.products.ngaims.gui.devbar import devbar_window
from sparetools_aerospace.products.ngaims.test_execution.oms_repository_configuration import OmsRepositoryConfiguration

log = logging.getLogger('__main__.' + __name__)


class TitanDeveloperBuddyOms(TitanDeveloperBuddy):
    def __init__(self):
        super().__init__()
        self.devbar = LabelFrame(self.top_frame)
        self.devbar.config(height='10', width='454', text='DevBar by PaUr')
        self.devbar.pack(side='left', fill=BOTH)
        devbar_window.create_buttons(self.devbar)
        devbar_window.log_target = self.log_dev_bar
        devbar_window.log_target_popen = self.log_dev_bar_popen
        devbar_window.buddy_kill_callback = self.kill_process
        self.product = None
        self.first_product_selection = True
        self.product_mode = None
        self.crash_observer.add_register_file_callback(self.get_additional_crash_files)
        self.product_radio = []

    @staticmethod
    def get_additional_crash_files():
        cfg = OmsRepositoryConfiguration()
        return set(Path(cfg.config.apu).glob('*.pdb'))

    def open_repository_activity(self):
        os.environ['ENV_REPOSITORY_ROOT'] = self.file_path
        super().open_repository_activity()

        with open(os.path.join(self.file_path, 'conanfile.py'), 'r') as conanfile:
            conanfile_content = conanfile.read()
            product_sets = []
            for product_set in re.finditer('\'product_name\'[ ]*:[ ]*\'(.*)\'', conanfile_content):
                if product_set.group(1) not in product_sets:
                    product_sets.append(product_set.group(1))
        if self.product:
            self.product.destroy()
        if product_sets:
            self.product = LabelFrame(self.top_frame)
            self.product.config(height='10', width='354', text='Product Selection')
            self.product.pack(side='left', fill=BOTH)

            self.product_mode = StringVar()
            self.product_radio = []
            for index, text in enumerate(product_sets):
                if index % 5 == 0:
                    column_frame = Frame(self.product)
                    column_frame.pack(side=LEFT, anchor=NW, expand=YES)
                self.product_radio.append(Radiobutton(column_frame, text=text,
                                                      variable=self.product_mode, value=text,
                                                      command=self.product_selected))
                self.product_radio[index].pack(side=TOP, anchor=NW)
            self.first_product_selection = True
            self.product_radio[0].invoke()

    def get_install_options(self):
        if self.product_mode:
            selected_product = self.product_mode.get()
            return f'-o ngaims:product_type={selected_product}'
        else:
            return super(TitanDeveloperBuddyOms, self).get_install_options()

    def product_selected(self):
        if self.first_product_selection:
            self.first_product_selection = False
        else:
            os.environ['TITAN_REBUILD_METHOD'] = '3'
            self.install_and_build()

    def build_activity(self):
        super().build_activity()

    @staticmethod
    def log_dev_bar(command):
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
        return TitanDeveloperBuddyOms()


if __name__ == '__main__':
    titan_developer_buddy.run_buddy(TitanDeveloperBuddyOms)
