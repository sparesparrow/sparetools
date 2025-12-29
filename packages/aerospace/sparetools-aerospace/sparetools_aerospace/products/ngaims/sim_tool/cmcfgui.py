import datetime
import os
import shlex
import sys
from configparser import InterpolationMissingOptionError
from subprocess import Popen, PIPE
import pathlib
from enum import Enum, IntEnum
import time
import threading

from PySide6 import QtCore, QtUiTools
from PySide6.QtCore import QThreadPool, Qt
from PySide6.QtWidgets import QMainWindow, QMessageBox, QFileDialog, QApplication
from PySide6.QtQuick import QQuickWindow, QSGRendererInterface

from ngapy.bench.bench_manager import BenchManager
from sparetools_aerospace.products.ngaims.sim_tool.thread_pool_worker import Worker
from sparetools_aerospace.products.ngaims.test_execution.run_test_functions import prepare_cmcf_bench
from sparetools_aerospace.products.ngaims.sim_tool.console_window_log_handler import ConsoleWindowLogHandler
from sparetools_aerospace.products.ngaims.common_functions import set_flight_phase
from sparetools_aerospace.products.ngaims.cmcf_bench_manager.cmcf_manager import CmcfManager

ACTIVE = True
INACTIVE = False


class FlightPhases(Enum):
    FP_MAINTENANCE = 0
    FP_UNCERTAIN = 1
    FP_PREFLIGHT = 2
    FP_TAXI = 3
    FP_TAKE_OFF = 4
    FP_CLIMB = 5
    FP_CRUISE = 6
    FP_DECENT = 7
    FP_APPPROACH = 8


class MsDispStatus(IntEnum):
    NORM_OP = 0
    FN_TEST = 1
    INVALID = 2
    ADN_NO_COMM = 3
    LRU_NO_COMM = 4
    IO_FAILURE = 5
    DATA_FAILURE = 6
    NO_STATUS = 7


class RunScriptButtonText(Enum):
    run_script_text = "Run Script"
    stop_script_text = "Stop Script"


class Commands(IntEnum):
    set_all_ms_status = 0
    set_sel_ms_status = 1
    set_all_mm_active = 2
    set_all_mm_inactive = 3
    set_sel_mm_active = 4
    set_sel_mm_inactive = 5
    set_all_fde_active = 6
    set_all_fde_inactive = 7
    set_sel_fde_active = 8
    set_sel_fde_inactive = 9


"""
This module define CMCF GUI functionality.
"""


class CmcfGui(QMainWindow):
    def __init__(self, do_version_check=True, parent=None):

        QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)  # added for Pyside6
        QQuickWindow.setGraphicsApi(QSGRendererInterface.OpenGLRhi)  # added for Pyside6

        global app
        app = QApplication(sys.argv)
        self.thread_funcs = {
            0: self.set_all_ms_status,
            1: self.set_sel_ms_status,
            2: lambda: self.set_all_mm(ACTIVE),
            3: lambda: self.set_all_mm(INACTIVE),
            4: lambda: self.set_sel_mm(ACTIVE),
            5: lambda: self.set_sel_mm(INACTIVE),
            6: lambda: self.set_all_fde(ACTIVE),
            7: lambda: self.set_all_fde(INACTIVE),
            8: lambda: self.set_sel_fde(ACTIVE),
            9: lambda: self.set_sel_fde(INACTIVE)
        }
        super(CmcfGui, self).__init__(parent)
        self.threadpool = QThreadPool()
        self.mws_priority_value = None
        self.handle_ms_change = True
        self.handle_mm_tree_change = True
        # used for allowing only first init change of auto clock
        self.first_clock_change_done = False
        self.first_auto_tiu_change_done = False
        self.test_env_is_running = False
        self.local_path = os.getcwd()
        self.auto_update_checker_worker = None
        self.auto_updater_worker = None
        self.stop_script = False
        self.child_process = None
        self.script_file = ""
        self.ms_status_loading = False
        self.loadStatuses = False
        self.installed_ease_versions = []

        self.runningPath = pathlib.Path(__file__).parent.__str__()

        try:
            if ((getattr(sys, 'frozen', False)) and (hasattr(sys, '_MEIPASS'))):
                self.runningPath = os.path.dirname(sys.executable)

            self.ui_layout = os.path.join(self.runningPath, 'MainWindow.ui')

            my_file = self.ui_layout
            ui_file = QtCore.QFile(my_file)
            ui_file.open(QtCore.QFile.ReadOnly)
            loader = QtUiTools.QUiLoader()
            self.main_gui = loader.load(ui_file)

            self.logger = ConsoleWindowLogHandler()

            self.connect_buttons()
            self.connect_callbacks()

            self.__set_start_stop_enable(False)
            # show gui after button connections
            self.main_gui.show()
            # move window to the front, so user can see it.
            self.setWindowState(self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
            self.activateWindow()

            # Exit Handler is a callable
            app.aboutToQuit.connect(lambda: sys.exit(CmcfGui))
            sys.exit(app.exec())

        except ValueError as v_err:
            if v_err and "invalid interpolation" in str(v_err).lower():
                text = "<b>Error in parsing Windows Environment Variables.</b><br>" \
                       "SimTool functionality is <b>disabled</b>.<br>" \
                       "Fix Environment Variables or report this error to developers."
                self.msg_box(text, v_err)
            else:
                self.msg_box("Initialization error.<br>SimTool functionality is <b>disabled</b>.")

            time.sleep(5)

        except InterpolationMissingOptionError as ioe:
            self.configs_path_error_msg(ioe)

        except Exception as e:
            self.msg_box("Initialization error.<br>SimTool functionality is <b>disabled</b>.")

    def msg_box(self, text, v_err=0):
        """
        Default critical error message box. Do not enable SimTool GUI
        :param text: Main error text to be shown
        :param v_err: Additional error text to be shown
        :return: None
        """
        self.setDisabled(True)
        self.msg = QMessageBox()
        self.msg.setIcon(QMessageBox.Critical)
        self.msg.setText(text)
        self.msg.setInformativeText(str(v_err))
        self.msg.setWindowTitle("SimTool initialization error")
        self.msg.setModal(True)
        self.msg.show()

    def connect_buttons(self):
        self.main_gui.pushButton_startBenchSim.clicked.connect(lambda: self.start_bench_clicked())
        self.main_gui.pushButton_stopBenchSim.clicked.connect(lambda: self.stop_bench_clicked())
        self.main_gui.open_script_btn.clicked.connect(lambda: self.load_script_file())
        self.main_gui.run_script_btn.clicked.connect(lambda: self.execute_script_file_start_stop())

        self.main_gui.set_all_ms_btn.clicked.connect(lambda: self.start_thread(Commands.set_all_ms_status))
        self.main_gui.set_sel_ms_btn.clicked.connect(lambda: self.start_thread(Commands.set_sel_ms_status))
        self.main_gui.set_all_mm_active_btn.clicked.connect(lambda: self.start_thread(Commands.set_all_mm_active))
        self.main_gui.set_all_mm_inactive_btn.clicked.connect(lambda: self.start_thread(Commands.set_all_mm_inactive))
        self.main_gui.set_sel_mm_active_btn.clicked.connect(lambda: self.start_thread(Commands.set_sel_mm_active))
        self.main_gui.set_sel_mm_inactive_btn.clicked.connect(lambda: self.start_thread(Commands.set_sel_mm_inactive))

        self.main_gui.set_all_fde_active_btn.clicked.connect(lambda: self.start_thread(Commands.set_all_fde_active))
        self.main_gui.set_all_fde_inactive_btn.clicked.connect(lambda: self.start_thread(Commands.set_all_fde_inactive))
        self.main_gui.set_sel_fde_active_btn.clicked.connect(lambda: self.start_thread(Commands.set_sel_fde_active))
        self.main_gui.set_sel_fde_inactive_btn.clicked.connect(lambda: self.start_thread(Commands.set_sel_fde_inactive))

        self.main_gui.actionMaintenance.triggered.connect(lambda: self.set_flt_phase(FlightPhases.FP_MAINTENANCE.value))
        self.main_gui.actionPreflight.triggered.connect(lambda: self.set_flt_phase(FlightPhases.FP_PREFLIGHT.value))
        self.main_gui.actionTaxi.triggered.connect(lambda: self.set_flt_phase(FlightPhases.FP_TAXI.value))
        self.main_gui.actionTakeoff.triggered.connect(lambda: self.set_flt_phase(FlightPhases.FP_TAKE_OFF.value))
        self.main_gui.actionClimb.triggered.connect(lambda: self.set_flt_phase(FlightPhases.FP_CLIMB.value))
        self.main_gui.actionCruise.triggered.connect(lambda: self.set_flt_phase(FlightPhases.FP_CRUISE.value))
        self.main_gui.actionDescent.triggered.connect(lambda: self.set_flt_phase(FlightPhases.FP_DECENT.value))
        self.main_gui.actionApproach.triggered.connect(lambda: self.set_flt_phase(FlightPhases.FP_APPPROACH.value))

        self.main_gui.clear_ex_output_btn.clicked.connect(lambda: self.clear_execution_output())

    def connect_callbacks(self):
        self.logger.buffer_message.connect(self.update_output_info)

    def stop_bench_clicked(self, closing=False, count=0):
        """
        Stops testing environment

        Args:
            closing: Flag if SimTool is closing (GUI is closed)
            count: number of end attempts
        """

        try:
            if self.child_process:
                self.stop_running_script()

            self.bench.stop_bench()
            self.test_env_is_running = False
            self.logger.info("Testing environment stopped")

            # THREADs part - cleanup
            self.threadpool.releaseThread()
            self.threadpool.waitForDone()
        except BaseException as e:
            count += 1
            if count < 4:
                self.stop_bench_clicked(closing, count)
            else:
                self.logger.exception("Could not close all parts of SimTool. Please, close it manually.")

        if not closing and count == 0:
            self.__set_start_stop_enable(self.test_env_is_running)

    def __set_start_stop_enable(self, start_enabled=False):
        self.main_gui.msGroupBox.setEnabled(start_enabled)
        self.main_gui.fdeGroupBox.setEnabled(start_enabled)
        self.main_gui.pushButton_stopBenchSim.setEnabled(start_enabled)
        self.main_gui.menuSet_flt_phase.setEnabled(start_enabled)
        self.main_gui.msStatusGroupBox.setEnabled(start_enabled)

    def start_cmcf_manager(self):
        self.bench = BenchManager({'CMCF': CmcfManager(reset_dbs=False), })
        self.bench.set_up()
        self.cmcf = self.bench.get_modules()['CMCF']

    def start_bench_clicked(self):
        """
        Action done after start bench is clicked
        :return:
        """
        from ngapy.util.process import kill_processes_by_name
        kill_processes_by_name([r'TIU.exe', r'PMU.exe', r'RPU_PB.exe', r'RPU_PT.exe', r'TiuServer.exe', r'Boot.exe',
                                r'PmuControllerII.exe', r'OSSL_Exec_Context.exe', 'PSSL_Exec_Windows.exe',
                                'RPU0.exe', 'RPU1.exe'])
        self.logger.info("Starting Environment. Please Wait...")
        prepare_cmcf_bench()
        # prepare configuration
        if not self.threadpool:
            self.threadpool = QThreadPool()

        # Pass the function to execute
        worker = Worker(self.start_cmcf_manager,
                        use_progress=False)  # Any other args, kwargs are passed to the run function
        self.test_env_is_running = True
        worker.signals.finished.connect(self.thread_complete)
        worker.setAutoDelete(True)

        # Execute
        self.threadpool.start(worker)

    def thread_complete(self):
        # as it is not possible (safe) to write to GUI from other threads, it is required here or create PySlots
        # self.post_bench_init()
        self.__set_start_stop_enable(self.test_env_is_running)
        self.logger.info("Getting required data")
        self.populate_data()
        self.logger.info("Environment Start completed")

    def populate_data(self):
        self.mm_manager = self.cmcf.active_model.model_manager.maintenance_messages_manager
        self.fde_manager = self.cmcf.active_model.model_manager.flight_deck_effects_manager
        self.ms_manager = self.cmcf.active_model.model_manager.member_systems_manager
        self.lru_manager = self.cmcf.active_model.model_manager.lru_manager
        self.bus_manager = self.cmcf.active_model.model_manager.bus_manager
        self.correlation_manager = self.cmcf.active_model.model_manager.fde_mm_correlation_manager
        self.io_input_manager = self.cmcf.active_model.io_input_manager
        self.mms_for_ms = []

        self.ms_list = self.ms_manager.get_all_mss()
        self.fde_manager.set_active_cas_master_instance(self.fde_manager.cas_master_instances[0])
        for ms in self.ms_list.values():
            self.main_gui.combox_mss.addItem(str(ms.sequence_id) + "::" + ms.name)

        self.mm_list = self.mm_manager.get_all_mms()

        for mm in self.mm_list.values():
            self.main_gui.combox_mms.addItem(str(mm.sequence_id) + "::" + mm.name)

        self.fde_list = self.fde_manager.get_all_fdes()

        for fde in self.fde_list.values():
            self.main_gui.combox_fdes.addItem(str(fde.sequence_id) + "::" + fde.name)

        for status in MsDispStatus:
            if status != MsDispStatus.DATA_FAILURE and status != MsDispStatus.NO_STATUS:
                self.main_gui.combox_status.addItem(str(status).split('.')[1])

        self.main_gui.combox_mss.currentIndexChanged.connect(self.on_ms_changed)
        self.on_ms_changed()

    def on_ms_changed(self):
        ms_id = int(self.main_gui.combox_mss.currentText().split('::')[0])
        self.mms_for_ms = []
        added = []
        self.main_gui.combox_mms.clear()
        for mm in self.mm_list.values():
            for fr in mm.fault_reports:
                if self.ms_manager.get_ldi_id_for_sequence_id(ms_id) == fr.ms_id and mm.sequence_id not in added:
                    self.main_gui.combox_mms.addItem(str(mm.sequence_id) + "::" + mm.name)
                    self.mms_for_ms.append(mm)
                    added.append(mm.sequence_id)

    def set_all_ms_status(self):
        self.logger.info("Setting status")
        set_to_status = MsDispStatus[self.main_gui.combox_status.currentText()]
        self.ms_manager.set_all_ms_status(set_to_status)
        self.logger.info("Status was set")

    def set_sel_ms_status(self):
        self.logger.info("Setting status")
        set_to_status = MsDispStatus[self.main_gui.combox_status.currentText()]
        ms_id = int(self.main_gui.combox_mss.currentText().split('::')[0])
        self.ms_manager.set_all_ms_status(set_to_status, [self.ms_manager.get_ms_by_id(
            self.ms_manager.get_ldi_id_for_sequence_id(ms_id))])
        self.logger.info("Status was set")

    def set_all_mm(self, set_to_status=INACTIVE):
        self.logger.info(f"Setting all Mms to {set_to_status}")
        # Set the corresponding Member Systems to provided status
        self.set_ms_for_mms(self.mms_for_ms)
        self.mm_manager.set_all_mms(set_to_status, self.mms_for_ms)
        self.logger.info(f"Mms were set to {set_to_status}")

    def set_sel_mm(self, set_to_status=INACTIVE):
        self.logger.info(f"Setting selected Mm to {set_to_status}")
        mms_to_mod = list()
        mm_name = self.main_gui.combox_mms.currentText().split('::')[1]
        mms_to_mod.append(self.mm_manager.get_mm_by_name(mm_name))

        # Set the corresponding Member Systems to provided status
        self.set_ms_for_mms(mms_to_mod)
        self.mm_manager.set_all_mms(set_to_status, mms_to_mod)
        self.logger.info(f"Mm was set to status {set_to_status}")

    def set_ms_for_mms(self, mms):
        li_ms = []
        for mm in mms:
            for fr in mm.fault_reports:
                ms = self.ms_manager.get_ms_by_id(fr.ms_id)
                ms.set_status(MsDispStatus.NORM_OP)
                if ms not in li_ms:
                    li_ms.append(ms)

        return li_ms

    def set_all_fde(self, set_to_status=INACTIVE):
        self.logger.info(f"Setting all Fdes to status {set_to_status}")
        fdes_to_mod = list(self.fde_manager.model_dict.values())
        self.fde_manager.set_all_fdes(set_to_status, fdes_to_mod)
        self.logger.info(f"Fdes were set to status {set_to_status}")

    def set_sel_fde(self, set_to_status=INACTIVE):
        self.logger.info("Setting selected Fde")
        fde_id = int(self.main_gui.combox_fdes.currentText().split('::')[0])
        self.fde_manager.set_all_fdes(set_to_status, [self.fde_manager.get_fde_by_id(
            self.fde_manager.get_ldi_id_for_sequence_id(fde_id))])
        self.logger.info("Fde was set")

    def set_flt_phase(self, phase):
        set_flight_phase(self.io_input_manager, phase)

    def start_thread(self, command):
        tgt = self.thread_funcs[command]
        x = threading.Thread(target=tgt, args=())
        x.start()

    def get_run_button_status(self):
        return self.main_gui.actionRun.isEnabled()

    def load_script_file(self):
        """
        Opens file select dialog for script file
        :return: None
        """
        self.main_gui.run_script_btn.setEnabled(False)
        path = self.main_gui.script_file_path_lbl.text()
        self.main_gui.script_file_path_lbl.clear()
        if not path or not os.path.exists(path):
            path = pathlib.Path(__file__).__str__()

        file_name = self.open_file_name_dialog(path)
        if file_name:
            self.main_gui.script_file_path_lbl.setText(file_name)
            self.main_gui.run_script_btn.setEnabled(True)
        self.script_file = file_name

    def execute_script_file_start_stop(self):
        """
        Handles user mouse click on Run/Stop script
        :return: None
        """
        if self.child_process:
            self.stop_running_script()
            return
        if self.script_file is not None and os.path.isfile(self.script_file):
            self.stop_script = False
            self.set_script_gui_items(False)
            self.local_path = os.getcwd()
            # Pass the function to execute
            self.script_worker = Worker(self.run_script, True,
                                        self.script_file)  # Any other args, kwargs are passed to the run function
            # only finished signal is currently used for scripts
            # worker.signals.result.connect(self.thread_result)
            self.script_worker.signals.finished.connect(self.script_finished)
            # worker.signals.progress.connect(self.progress_fn)
            self.script_worker.setAutoDelete(True)

            # Execute
            if not self.threadpool:
                self.threadpool = QThreadPool()
            self.threadpool.start(self.script_worker)
        else:
            self.set_start_script(False)

    def run_script(self, script_file, progress_callback=None):
        """
        Runs user defined script in new thread. No gui actions should be here.
        :param script_file: Script file to be executed
        :param progress_callback: Not used now - can report execution status bas to main thread
        :return: None
        """
        try:
            self.logger.info(f"Launching {script_file} Test Script")
            file = script_file
            file = file[:len(file) - 3]
            script_path = os.path.dirname(file)
            os.chdir(script_path)

            cmd = "python " + script_file

            self.child_process = Popen(shlex.split(cmd), stderr=PIPE)
            while True:
                output = self.child_process.stderr.readline().decode()
                if output == '' and self.child_process.poll() is not None:
                    break
                if output:
                    self.logger.info(output.strip())

                if self.stop_script:
                    # terminate child thread
                    self.child_process.terminate()
            # check terminate return code if required
            rc = self.child_process.poll()

        except Exception as e:
            self.logger.exception(e)

    def stop_running_script(self):
        self.logger.info("Terminating test script.")
        self.child_process.terminate()
        # check result if required
        res = self.child_process.poll()
        self.child_process = None

    def script_finished(self):
        """
        Run rutines after executing of script is finished. All gui updates should be here not in the script thread.
        :return: None
        """
        self.set_script_gui_items(True)
        self.logger.info("\n Script executing finished. \n")
        os.chdir(self.local_path)

    def set_script_gui_items(self, enabled=True):
        """
        Sets GUI items related to running scripts to "script running" or "script not running" status.
        It changes status icon and disabled/enabled script buttons
        :param enabled: True - items are enabled - script is not running
        :return: None
        """
        if not self.main_gui.open_script_btn.isEnabled():
            self.stop_script = True

        self.main_gui.open_script_btn.setEnabled(enabled)

        if enabled:
            self.main_gui.run_script_btn.setText(RunScriptButtonText.run_script_text.value)
        else:
            self.main_gui.run_script_btn.setText(RunScriptButtonText.stop_script_text.value)

    @staticmethod
    def get_script_run(file_path):
        file = open(file_path, "r")
        init = False
        batch_line = None
        for line in file:
            if "if __name__ == '__main__':" in line:
                init = True
            if init and "tp.exec(" in line.lower():
                batch_line = line
                break

        if batch_line:
            batch_line = batch_line.strip()
            batch_line = batch_line[batch_line.find("(") + 1:]
            batch_line = batch_line[:batch_line.find(",")]

        return batch_line

    def set_start_script(self, status):
        self.main_gui.run_script_btn.setEnabled(status)

    def clear_execution_output(self):
        self.main_gui.scriptText.clear()

    def update_output_info(self, message):
        self.main_gui.scriptText.appendPlainText(message)

    def open_file_name_dialog(self, default_path=""):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(self, "Open test script file", default_path,
                                                   "Python Files (*.py);;IO Files (*.IO);;All Files (*)",
                                                   options=options)
        return file_name


def run_cmcf_gui():
    """
    Starting point for SimTool GUI
    """
    cmcf_app = CmcfGui()


if __name__ == '__main__':
    run_cmcf_gui()
