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
import glob
import logging
import os
import re
import subprocess
import threading
from datetime import datetime
from functools import cache
from pathlib import Path
from tkinter import *
from tkinter.ttk import *

from mdutils import MdUtils

from ngapy.bench.bench_debugging.debugging_gui import VisualStudioDebugDialog
from sparetools_aerospace.products.ngaims.common_functions import get_cmcf_log, get_tcrf_log
from sparetools_aerospace.products.ngaims.decoder.tcrf_decoder import TCRFDecoder
from sparetools_aerospace.products.ngaims.downloader.tcrf_ftp_downloader import TcrfFtpDownloader
from sparetools_aerospace.products.ngaims.gui.system_test_launcher import get_ngaims_test_files, run_test, get_ngaims_test_root
from sparetools_aerospace.products.ngaims.hdb_decoder.hdb_decoder import HDBDecoder
from sparetools_aerospace.products.ngaims.setup_environment import get_oms_repository_config
from sparetools_aerospace.products.ngaims.test_execution.oms_repository_configuration import OmsRepositoryConfiguration
from ngapy.simulations.clock import ClockSimulation
from ngapy.util.process import kill_proc_tree

log = logging.getLogger('__main__.' + __name__)

log_target = None
log_target_popen = None
buddy_kill_callback = None
cfg = OmsRepositoryConfiguration()
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
    start_file(cfg.config.pexp)


def atetest():
    try:
        os.system(
            f'start cmd /k "cd {os.path.dirname(cfg.config.atetest)} & {cfg.config.atetest} {cfg.config.ateip} '
            f'{cfg.config.ateport}  & exit"')

    except Exception as ex:
        log.exception(ex)


def start_oms_utility():
    try:
        test_path = cfg.config.oms_utility
        subprocess.Popen([str(cfg.config.python_interpreter), test_path])

    except Exception as ex:
        log.exception(ex)


def start_oms_sim_tool():
    try:
        import sparetools_aerospace.products.ngaims.sim_tool.SimToolGui as simtoolgui
        subprocess.Popen([str(cfg.config.python_interpreter), simtoolgui.__file__])

    except Exception as ex:
        log.exception(ex)


def ldi():
    start_file(cfg.config.ldi)


def apu():
    start_file(cfg.config.apu)


def pmu():
    start_file(cfg.config.pmu)


def pct():
    start_file(cfg.config.pct)


def sln():
    start_file(cfg.config.sln)


def start_ngtbox_thread():
    subprocess.run(
        [cfg.config.python_interpreter,
         os.path.abspath(os.path.join(cfg.config.ngapy, r'ngapy\io_platform\next_gen_something_like_tbox.py'))],
        cwd=os.path.abspath(cfg.config.ngapy))


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
    os.environ['PATH'] = f'{os.path.dirname(cfg.config.python_interpreter)};{os.environ["PATH"]}'
    os.environ['PYTHONPATH'] = os.path.abspath(cfg.config.ngapy)
    os.system(f'start cmd /K cd {os.path.abspath(cfg.config.ngapy)}')


def start_pmu_thread():
    from ngapy.bench.ase_bench import main
    main()


def start_pmu():
    t = threading.Thread(target=start_pmu_thread, daemon=True)
    t.start()


def start_cmcf_thread():
    try:
        os.system(f'start cmd /k "cd {cfg.config.apu} & {cfg.config.ossl} {cfg.config.cmc_partition_id} & exit"')
    except Exception as ex:
        log.exception(ex)


def start_cmcf():
    t = threading.Thread(target=start_cmcf_thread, daemon=True)
    t.start()


def start_tcrf_thread():
    try:
        os.system(f'start cmd /k "cd {cfg.config.apu} & {cfg.config.ossl} {cfg.config.tcrf_partition_id} & exit "')
    except Exception as ex:
        log.exception(ex)


def start_tcrf():
    t = threading.Thread(target=start_tcrf_thread, daemon=True)
    t.start()


@cache
def create_severity_dict(source_path: Path, source_pattern: str):
    return_dict = {}
    pattern = re.compile('[^\(]+.*::([^\)]+).*CriticalityLevel::([^\),]+)', flags=0)
    for file_path in glob.glob(str(Path(source_path) / source_pattern), recursive=True):
        log.debug(f'Processing: {file_path} fmea file')
        with open(file_path, 'r') as file:
            for line in file.readlines():
                if 'CriticalityLevel' not in line:
                    continue
                matches = re.findall(pattern, line)
                for match in matches:
                    if match[0] in return_dict:
                        if return_dict[match[0]] != match[1]:
                            log.warning(
                                f'Fault {match[0]} already in dict with value: {return_dict[match[0]]}. New value: {match[1]}')
                        else:
                            log.info(
                                f'Fault {match[0]} already in dict with value: {return_dict[match[0]]}. Value is same')
                    return_dict[match[0]] = match[1]
    return return_dict


def start_cmcf_log_thread():
    log_file = get_cmcf_log()
    file_name = create_md_file_from_log(log_file, 'CMCF')
    os.startfile(file_name)


def create_md_file_from_log(log_file, application):
    oms_repository_config = get_oms_repository_config()
    severity_dict = create_severity_dict(oms_repository_config.oms_repository_layout.aero_sps_source_root,
                                         '**/*fmea*.h')
    md_file_path = Path(oms_repository_config.oms_repository_layout.ase_apu_root) / f'{application}_log.md'
    md_file = MdUtils(file_name=str(md_file_path), title=f'{application} Decoded Log file')
    execution = 1
    for log_entry in log_file:
        if log_entry.seq_number == 1:
            md_file.new_header(level=1, title=f'Execution cycle {str(execution)}')
            execution += 1
        md_file.new_header(level=2, title=f'{str(log_entry.seq_number)}: {log_entry.fault_name}')
        md_file.new_header(level=3, title='Description')
        md_file.new_paragraph(log_entry.full_log)
        md_file.new_header(level=3, title='Date Time')
        md_file.new_paragraph(f'UTC: {datetime.utcfromtimestamp(log_entry.time_stamp).strftime("%Y-%m-%d %H:%M:%S")}')
        md_file.new_paragraph(f'Local: {datetime.fromtimestamp(log_entry.time_stamp).strftime("%Y-%m-%d %H:%M:%S")}')
        md_file.new_header(level=3, title='Severity')

        severity_color = 'black'
        if log_entry.fault_name in severity_dict:
            severity = severity_dict[log_entry.fault_name]
            if severity == 'critical':
                severity_color = 'red'
        else:
            severity = 'Unknown'
            severity_color = 'orange'
        md_file.new_paragraph(severity, color=severity_color)

        md_file.new_header(level=3, title='Corrective action')
        md_file.new_paragraph('...')
    md_file.new_table_of_contents(table_title='Contents', depth=2)
    md_file.create_md_file()
    return md_file_path


def cmcf_log():
    t = threading.Thread(target=start_cmcf_log_thread, daemon=True)
    t.start()


def start_tcrf_log_thread():
    log_file = get_tcrf_log()
    file_name = create_md_file_from_log(log_file, 'TCRF')
    os.startfile(file_name)


def tcrf_log():
    t = threading.Thread(target=start_tcrf_log_thread, daemon=True)
    t.start()


def clock_sim():
    clock_sim = ClockSimulation()
    clock_sim.start(datetime.now())


eq_visualizer = None


def start_eq_debugging_thread():
    global eq_visualizer
    if eq_visualizer:
        eq_visualizer.kill()
    eq_visualizer = subprocess.Popen(
        [cfg.config.python_interpreter,
         (Path(
             cfg.config.ngapy) / r'ngapy/product_specific/ngaims/gui/equation_visualizer/visualizer_gui.py').absolute()],
        cwd=Path(cfg.config.ngapy).absolute())


def eq_debugging():
    t = threading.Thread(target=start_eq_debugging_thread, daemon=True)
    t.start()


def start_decoder():
    t = threading.Thread(target=start_decoder_thread, daemon=True)
    t.start()
    return


def start_decoder_thread():
    try:
        decoder = TCRFDecoder(gui_root)

        log.info("Flight data decoding ...")
        decoder.decode(fred_initial_dir_name=os.getcwd(), tcrf_initial_dir_name=os.getcwd())
        log.info(f"Output decoded TCRF report files: {decoder.out_file_names[0]}")
        log.info("Flight data decoding finished.")

    except Exception as ex:
        log.exception(ex)

    return


def start_hdb_decoder():
    t = threading.Thread(target=start_hdb_decoder_thread, daemon=True)
    t.start()
    return


def start_hdb_decoder_thread():
    try:
        decoder = HDBDecoder(gui_root)

        log.info("HDB decoding ...")
        decoder.decode(cmcf_ldi_initial_dir_name=os.getcwd(), cmcf_hdb_initial_dir_name=os.getcwd())
        log.info(f"Output decoded HDB file: {decoder.decoded_hdb_file_name}")
        log.info("HDB decoding finished.")

    except Exception as ex:
        log.exception(ex)

    return


def start_downloader():
    t = threading.Thread(target=start_downloader_thread, daemon=True)
    t.start()
    return


def start_downloader_thread():
    try:
        downloader = TcrfFtpDownloader(gui_root)

        log.info("start Ftp download ...")
        downloader.download(initial_local_dir=os.getcwd())
        # log.info(f"Output decoded TCRF report files: {decoder.out_file_names[0]}")
        log.info("Ftp download finished.")

    except Exception as ex:
        log.exception(ex)

    return


def start_test_thread():
    global test_combo
    test_file_names = [str(x) for x in get_ngaims_test_files()]
    run_test(get_ngaims_test_root() / test_file_names[test_combo.current()])


def run_test_using_combo():
    t = threading.Thread(target=start_test_thread, daemon=True)
    t.start()


def bench_debug():
    global gui_root
    dialog = VisualStudioDebugDialog(gui_root)


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
    bl.add_button(r"LDI", ldi, bwidth)
    bl.add_button(r"\APU", apu, bwidth)
    bl.add_button(r"\PMU", pmu, bwidth)
    bl.add_button(r"Decode", start_decoder, bwidth)
    bl.add_button(r"P-Hck", pexp, bwidth)
    bl.add_button(r"NG_IO", start_ngtbox, bwidth)

    test_file_names = [str(x) for x in get_ngaims_test_files()]
    test_combo = Combobox(parent, width=100,
                          values=test_file_names)
    bl.add_separator(1)
    bl.add_item(test_combo, 98, y=1, h=23)

    bl2 = BtnLine(parent, 25)
    bl2.add_button(r"Pmu", start_pmu, bwidth)
    bl2.add_button(r"Cmcf", start_cmcf, bwidth)
    bl2.add_button(r"Tcrf", start_tcrf, bwidth)
    bl2.add_button(r"CmcLog", cmcf_log, bwidth)
    bl2.add_button(r"TcrfLog", tcrf_log, bwidth)
    bl2.add_button(r"KillAll", kill_all, bwidth)
    bl2.add_button(r"Python", python_console, bwidth)

    bl2.add_button(r"RunTest", run_test_using_combo, 100)

    bl3 = BtnLine(parent, 50)
    bl3.add_button(r"AteTest", atetest, bwidth)
    bl3.add_button(r"OMS SimTool", start_oms_sim_tool, 90)
    bl3.add_button(r"OMS Utility", start_oms_utility, 90)
    bl3.add_button(r"ClkSim", clock_sim, bwidth)
    bl3.add_button(r"HwDbg", bench_debug, bwidth)
    bl3.add_button(r"Get TCRF files", start_downloader, 110)

    bl4 = BtnLine(parent, 75)
    bl4.add_button(r"Decode HDB", start_hdb_decoder, 110)
    bl4.add_button(r"EqDbg", eq_debugging, bwidth)

    # main_frame.pack(side='right')
    # main_window = TestSelectionWindow.create_main_window(main_frame)

    # Commented because it is not working on Bench
    # if running_on_bench():
    #    from ngapy.config_loader import get_config_loader
    #    bench = SITSBench(get_config_loader())
    #    bwidth = 100
    #    bl3 = BtnLine(parent, 50)
    #    bl3.add_button(r"Start DPM", bench.hw_start, bwidth)
    #    bl3.add_button(r"Stop DPM", bench.hw_stop, bwidth)
    #    bl3.add_button(r"Restart DPM", bench.hw_restart, bwidth)
    #
    #    bl4 = BtnLine(parent, 75)
    #    bl4.add_button(r"Flight mode", bench.start, bwidth)
    #    bl4.add_button(r"Download mode", bench.stop, bwidth)
    #    bl4.add_button(r"Restart mode", bench.restart, bwidth)
