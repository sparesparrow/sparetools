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
import copy
import os
import time
from pathlib import Path
from tkinter import *
from tkinter import ttk  # @Reimport

from ngapy.conan.conan_functions import get_ngapy_root
from ngapy.io_platform import io_interface
from ngapy.io_platform.next_gen_something_like_tbox import TreeDemo
from ngapy.util.setup_environment import get_repository_root


class VGPInterface(TreeDemo):

    # Inherit tk window generated in next_gen_something_like_tbox.py and extend
    # the VGP interface to it

    def __init__(self, name='titan-io-vgp'):
        super().__init__()

        self.add_vgp_panel()

    def add_vgp_panel(self):

        self.vgp_frame = ttk.LabelFrame(self, text='VGP Interface')
        self.vgp_frame.pack(side='bottom', fill=BOTH)

        # Create frame to contain settings widgets
        self.settings_frame = ttk.Frame(self.vgp_frame)
        self.settings_frame.pack(side='top', fill=BOTH)

        dpm_label = ttk.Label(self.settings_frame, text='Select DPM: ')
        dpm_label.grid(row=0, column=0, sticky='e', pady=10)

        self.dpm_combo = ttk.Combobox(self.settings_frame, width=10,
                                      values=[
                                          'DPM_1',
                                          'DPM_2',
                                          'DPM_3',
                                          'DPM_4']
                                      )
        self.dpm_combo.current(2)  # Set default: NORMAL_OPERATION_e (0x03)
        self.dpm_combo.grid(row=0, column=1, pady=10, sticky='w')

        vgp_config_button = ttk.Button(self.settings_frame, text='Configuration', command=self.open_vgp_config)
        vgp_config_button.grid(row=0, column=2, padx=4, sticky='e')

        reload_config_button = ttk.Button(self.settings_frame, text='Reload', command=self.populate_vgp_pb)
        reload_config_button.grid(row=0, column=3, sticky='w')

        # Create frame containing VGP push buttons widgets
        self.pb_frame = ttk.Frame(self.vgp_frame)
        self.pb_frame.pack(side='top', fill=BOTH)

        self.populate_vgp_pb()

    def open_vgp_config(self):

        """ Configuration filed used to add/remove VPG widgets on the fly """
        ngapy_root = Path(get_ngapy_root(get_repository_root()))
        os.startfile((ngapy_root / r'ngapy\product_specific\\ngaafcs\vgp_interface\vgp_config.txt').absolute())

    def populate_vgp_pb(self):

        """ Read contents from vgp_config.txt and create widgets """
        ngapy_root = Path(get_ngapy_root(get_repository_root()))
        for widgets in self.pb_frame.winfo_children():
            widgets.destroy()

        self.vgp_buttons = {}

        with open((ngapy_root / r'ngapy\product_specific\\ngaafcs\vgp_interface\vgp_config.txt').absolute()) as file:
            for read_line in file:
                line = read_line.strip('\n')
                # Ignore lines with '#' or empty lines
                if '#' not in line:
                    if '=' in line:
                        if 'button' in line:
                            button_name = line.split('=')[0].strip(' ')
                            samioc_name = line.split('=')[1].strip(' ')
                            self.vgp_buttons[button_name] = samioc_name

                            # Create buttons as two rows
        row_idx = 0
        col_idx = 0
        for key, value in self.vgp_buttons.items():
            if col_idx == int(0.5 * len(self.vgp_buttons)):
                row_idx += 1
                col_idx = 0
            pb = ttk.Button(self.pb_frame, text=f'{key}', width=15)
            pb.config(command=lambda v="{}".format(value): self.toggle_item(v))
            pb.grid(row=row_idx, column=col_idx)
            col_idx += 1

    def toggle_item(self, item):

        """ Buttons are implemented as toggled switches, simulating push and release """
        print(f'Toggle PB: {item}')
        self.simulate_pb(item, 1)
        time.sleep(1)
        self.simulate_pb(item, 0)

    def simulate_pb(self, item, value_to_write):
        validity = self.validity_var.get()
        validity_template = io_interface.IoDataValue('', 0)
        validity_template.validity = self.validity_var.get()
        validity_template.raw_status = self.raw_combo.current()
        validity_template.extended_status = self.ext_combo.current()

        dpm_number = self.dpm_combo.get()

        logical_name = f'{item}.1 ({dpm_number})'
        io_value = copy.copy(validity_template)
        io_value.name = logical_name

        io_value.value = bool(float(value_to_write))
        self.io_interface.set_values(io_value)


if __name__ == '__main__':
    # setup_logging_from_config()
    VGPInterface().mainloop()
