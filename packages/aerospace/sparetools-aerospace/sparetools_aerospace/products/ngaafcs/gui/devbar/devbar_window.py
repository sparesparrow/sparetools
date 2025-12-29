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
import logging
import os
import subprocess
import threading
import sys
from pathlib import Path
from tkinter import *
from tkinter.ttk import *

from ngapy.conan.conan_functions import get_ngapy_root
from sparetools_aerospace.products.ngaims.setup_environment import get_oms_repository_root, get_oms_repository_config
from ngapy.util.process import kill_proc_tree

log = logging.getLogger('__main__.' + __name__)


log_target = None
log_target_popen = None
buddy_kill_callback = None
gui_root = None
test_combo = None


def start_file(command):
    if log_target is None:
        os.startfile(command)
    else:
        log_target(command)


def popen_log(command, callback=None, **kwargs):
    if log_target_popen is None:
        subprocess.Popen(command, **kwargs)
    else:
        log_target_popen(command, **kwargs)


def pexp():
    start_file(get_ngapy_root(get_oms_repository_root()) /
               r'ngapy\product_specific\ngaims\gui\devbar\_ProcessHacker\x64'
               r'\ProcessHacker.exe')


def apu():
    start_file(get_oms_repository_config().fcs_repository_layout.ase_apu_root)


def pmu():
    start_file(get_oms_repository_config().fcs_repository_layout.ase_pmu_root)


def start_ngtbox_thread():
    ngapy_root = Path(get_ngapy_root(get_oms_repository_root()))
    python_exe = get_oms_repository_config().conan_package_config['titan-python-environment'][2] / 'python.exe'
    subprocess.run(
        [python_exe,
         (ngapy_root / r'ngapy\product_specific\ngaafcs\vgp_interface\vgp_interface.py').absolute()],
        cwd=os.path.abspath(ngapy_root))


def start_ngtbox():
    t = threading.Thread(target=start_ngtbox_thread, daemon=True)
    t.start()


def kill_all():
    from ngapy.util.process import kill_processes_by_name
    kill_processes_by_name([r'TIU.exe', r'PMU.exe', r'RPU_PB.exe', r'RPU_PT.exe', r'TiuServer.exe', r'Boot.exe',
                            r'PmuControllerII.exe', r'OSSL_Exec_Context.exe', 'PSSL_Exec_Windows.exe',
                            'ATEAppTest.exe', 'RPU0.exe', 'RPU1.exe'])
    kill_proc_tree(exceptions=['devenv.exe'])
    if buddy_kill_callback:
        buddy_kill_callback(True)


def python_console():
    ngapy_root = Path(get_ngapy_root(get_oms_repository_root())).absolute()
    os.environ[
        'PATH'] = f'{get_oms_repository_config().conan_package_config["titan-python-environment"][2]};{os.environ["PATH"]}'
    os.environ['PYTHONPATH'] = ngapy_root
    os.system(f'start cmd /K cd {ngapy_root}')

def generate_dfts():
    path = os.path.abspath(get_oms_repository_config().fcs_repository_layout.repository_root)
    sys.path.insert(0, path)
    from conanfile import NgaFcsFgsConan
    NgaFcsFgsConan.generate_smm_file(NgaFcsFgsConan)

def start_pmu_thread():
    from ngapy.bench.ase_bench import main
    main()


def start_pmu():
    t = threading.Thread(target=start_pmu_thread)
    t.start()


def start_fgs_thread():
    try:
        apu_root = get_oms_repository_config().fcs_repository_layout.ase_apu_root
        ossl_exec = get_oms_repository_config().fcs_repository_layout.ossl_exec
        fcs_fgs_partition_id = get_oms_repository_config().fcs_runtime.fcs_fgs_partition_id
        os.system(f'start cmd /k "cd {apu_root} & {ossl_exec} {fcs_fgs_partition_id} & exit "')
    except Exception as ex:
        log.exception(ex)


def start_fgs():
    t = threading.Thread(target=start_fgs_thread)
    t.start()


def sln():
    start_file(get_oms_repository_config().fcs_repository_layout.vs17_sln_path)


class BtnLine:
    x = 0
    h = 25
    sep = 5

    def __init__(self, wnd, y):
        self.wnd = wnd
        self.y = y

    def add_button(self, label, cmd, w):
        b = Button(self.wnd, text=label, command=cmd)
        b.place(x=self.x, y=self.y, width=w, height=self.h)
        self.x = self.x + w

    def add_item(self, item, w, x=None, y=None, h=None):
        if not x:
            x = self.x
        if not y:
            y = self.y
        if not h:
            h = self.h
        item.place(x=x, y=y, width=w, height=h)
        self.x = self.x + w

    def add_separator(self, w):
        self.x = self.x + w


def create_buttons(parent):
    global gui_root, test_combo
    gui_root = parent
    bwidth = 50
    bl = BtnLine(parent, 0)
    bl.add_button(r"Sln", sln, bwidth)
    bl.add_button(r"\APU", apu, bwidth)
    bl.add_button(r"\PMU", pmu, bwidth)
    bl.add_button(r"P-Hck", pexp, bwidth)
    bl.add_button(r"NG_IO", start_ngtbox, bwidth)

    bl.add_separator(1)

    bl2 = BtnLine(parent, 25)
    bl2.add_button(r"Pmu", start_pmu, bwidth)
    bl2.add_button(r"FGS", start_fgs_thread, bwidth)
    bl2.add_button(r"KillAll", kill_all, bwidth)
    bl2.add_button(r"Python", python_console, bwidth)
    bl2.add_button(r"DFTS Gen", generate_dfts, bwidth)