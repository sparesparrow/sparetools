import tkinter as tk
from pathlib import Path
from tkinter import filedialog as fd, messagebox
from tkinter import ttk

from sparetools.test_environments.bench_debugging.statmon import StatmonReader
from sparetools.test_environments.bench_debugging.vistual_studio_debugging import prepare_vs_debugging, run_visual_studio
from ngapy.conan.conan_functions import get_conan_home
from ngapy.miscellaneous.configuration_store_yaml import ConfigurationStoreYaml
from ngapy.util.setup_environment import get_repository_config


class ConfigurationDebugGui(ConfigurationStoreYaml):
    latest_version = '1.0'
    _data = {
        'version': latest_version,
        'visual_studio_path': '',
        'project_path': '',
        'last_selected_module': -1,
        'last_applications': list(),
        'last_selected_application': -1,
        'with_reset': False
    }
    config_file_path = Path(get_conan_home()[0]) / 'debugging_gui.yaml'


class VisualStudioDebugDialog:
    def __init__(self, parent):
        self.root = tk.Toplevel(parent)
        self.development_mode = False
        self.repo_config = get_repository_config()
        self.config = ConfigurationDebugGui()
        # root window
        self.root.title('Visual Studio Debugging')
        self.root.geometry('700x158')
        self.root.resizable(0, 0)
        # windows only (remove the minimize/maximize button)
        self.root.attributes('-toolwindow', True)

        # layout on the root window
        self.root.columnconfigure(0, weight=1)

        input_frame = self.create_input_frame(self.root)
        input_frame.grid(column=0, row=0)

        button_frame = self.create_button_frame(self.root)
        button_frame.grid(column=1, row=0)

        self.vs_location_text.set(self.config.data['visual_studio_path'])

    def create_input_frame(self, container):
        frame = ttk.Frame(container)
        frame.grid(sticky="sewn", padx=5)

        # grid layout for the input frame
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=5)

        ttk.Label(frame, text='Locate Visual Studio (Devenv.exe):').grid(column=0, row=0, sticky="sewn")
        self.vs_location_text = tk.StringVar()
        self.vs_location = ttk.Entry(frame, textvariable=self.vs_location_text)
        self.vs_location.focus()
        self.vs_location.grid(column=1, row=0, sticky=tk.W + tk.E, padx=5, pady=5)
        if self.config.data['visual_studio_path']:
            self.vs_location_text.set(self.config.data['visual_studio_path'])

        ttk.Label(frame, text='Locate project build folder').grid(column=0, row=1, sticky="sewn")
        self.project_location_text = tk.StringVar()
        self.project_location = ttk.Entry(frame, textvariable=self.project_location_text)
        self.project_location.focus()
        self.project_location.grid(column=1, row=1, sticky=tk.W + tk.E, padx=5, pady=5)
        if self.config.data['project_path']:
            self.project_location_text.set(self.config.data['project_path'])

        ttk.Label(frame, text='Select Module:').grid(column=0, row=2, sticky=tk.W)
        self.selected_module = ttk.Combobox(frame, state='readonly')
        all_products = [product for product in self.repo_config.product.products]
        self.all_products_hw = list(filter(lambda product: product.product_type == 'HW', all_products))
        self.selected_module['values'] = [f'{product.product_name} - IP: {product.ftp_connection_ip}' for product in
                                          self.all_products_hw]
        self.selected_module.grid(column=1, row=2, sticky=tk.W + tk.E, padx=5, pady=5)
        if self.config.data['last_selected_module'] != -1:
            self.selected_module.current(self.config.data['last_selected_module'])

        ttk.Label(frame, text='Select Application:').grid(column=0, row=3, sticky=tk.W)
        self.selected_app = ttk.Combobox(frame, state='readonly')
        self.selected_app.grid(column=1, row=3, sticky=tk.W + tk.E, padx=5, pady=5)
        self.selected_app['values'] = self.config.data['last_applications']

        self.selected_app.bind('<<ComboboxSelected>>', self.application_selected)
        if self.config.data['last_selected_application'] != -1:
            try:
                self.selected_app.current(self.config.data['last_selected_application'])
            except tk.TclError:
                pass

        # Wrap Around checkbox
        self.with_reset_text = tk.StringVar()
        self.with_reset = ttk.Checkbutton(
            frame,
            variable=self.with_reset_text,
            text='With Module Reset',
            command=self.with_reset)
        self.with_reset_text.set(self.config.data['with_reset'])
        self.with_reset.grid(column=0, row=4, sticky=tk.W, pady=5)

        return frame

    def get_selected_module_ip(self):
        selected_module = self.selected_module.current()
        if selected_module != -1:
            return self.all_products_hw[selected_module].ftp_connection_ip
        return None

    def select_file(self):
        filetypes = (
            ('Visual Studio', 'devenv.exe'),
            ('All files', '*.*')
        )

        vs_location = fd.askopenfilename(
            title='Locate Visual Studio - devenv.exe',
            filetypes=filetypes)

        self.vs_location_text.set(vs_location)
        self.config.data = ('visual_studio_path', vs_location)

    def select_project(self):
        project_path = fd.askdirectory(title='Locate project. Folder containing SOURCE and BUILD_ folders')
        self.project_location_text.set(project_path)
        self.config.data = ('project_path', project_path)

    def connect_to_module(self):
        ip = self.get_selected_module_ip()
        if not ip:
            messagebox.showerror('Module not selected', 'Module not selected - You need to select module!')
            return
        self.config.data = ('last_selected_module', self.selected_module.current())
        try:
            self.process_list = StatmonReader(ip, 1026).read_process_list()
        except TimeoutError:
            if self.development_mode:
                self.process_list = {'deosidle': ['0x70000', 'deosidle', 'deosidle.exe', ''],
                                     'MaintenanceCMCF': ['0x14070000', 'MaintenanceCMCF', 'PSSL_Exec_Deos653.exe', '']}
            else:
                messagebox.showerror('Communication with module failed',
                                     f'Could not connect to {ip}, check module is in normal mode')
                return
        apps = [f'{count}: {process[0]} {process[1]} {process[2]}' for
                count, process in
                enumerate(self.process_list.values())]
        self.config.data = ('last_applications', apps)
        self.selected_app['values'] = apps
        self.selected_app.current(0)
        self.config.data = ('last_selected_application', self.selected_app.current())

    def application_selected(self, eventObject):
        self.config.data = ('last_selected_application', self.selected_app.current())

    def debug_application(self):
        self.config.data = ('last_selected_application', self.selected_app.current())
        if not self.config.data['project_path'] \
                or not self.config.data['last_applications'] \
                or not self.config.data['visual_studio_path'] \
                or self.config.data['last_selected_application'] < 0 \
                or self.config.data['last_selected_module'] < 0:
            messagebox.showerror('Missing information', 'Information missing. Please check!')
            return
        try:
            prepare_vs_debugging(Path(self.config.data['project_path']),
                                 ip=self.get_selected_module_ip(),
                                 application_name=self.config.data['last_applications'][
                                     self.config.data['last_selected_application']].split()[2],
                                 with_module_reset=self.config.data['with_reset'])
        except:
            messagebox.showerror('Cannot connect using debugger', 'Check connection to module')
            return
        run_visual_studio(self.config.data['visual_studio_path'], self.config.data['project_path'])

    def cancel_application(self):
        self.root.destroy()

    def with_reset(self):
        self.config.data = ('with_reset', self.with_reset_text.get() == '1')

    def create_button_frame(self, container):
        frame = ttk.Frame(container)
        frame.grid(sticky="sewn", padx=5)
        ttk.Button(frame, text='...', command=self.select_file).grid(column=0, row=0)
        ttk.Button(frame, text='...', command=self.select_project).grid(column=0, row=1)
        ttk.Button(frame, text='Load Apps', command=self.connect_to_module).grid(column=0, row=2)
        ttk.Button(frame, text='Debug', command=self.debug_application).grid(column=0, row=3)
        ttk.Button(frame, text='Cancel', command=self.cancel_application).grid(column=0, row=4)
        for widget in frame.winfo_children():
            widget.grid(padx=0, pady=3)
        return frame


if __name__ == "__main__":
    root = tk.Tk()
    dialog = VisualStudioDebugDialog(root)
    root.mainloop()
