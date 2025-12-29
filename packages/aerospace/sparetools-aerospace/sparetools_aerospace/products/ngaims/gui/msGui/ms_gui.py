
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
import os.path
import sys
import pathlib

from ngapy.bench.bench_factory import BenchStarter
from sparetools_aerospace.products.ngaims.gui.ateTool.ategui import resource_path
from sparetools_aerospace.products.ngaims.maintenance_model.maintenance_model_composition import MaintenanceModelComposition
from sparetools_aerospace.products.ngaims.setup_environment import get_oms_repository_config
from sparetools_aerospace.products.ngaims.test_common import prepare_external_dependencies
from ngapy.util.custom_logging import setup_logging_from_config
from sparetools_aerospace.products.ngaims.constants import MsDispStatus

from PySide6 import QtCore, QtUiTools, QtWidgets
from PySide6.QtWidgets import QMainWindow

from sparetools_aerospace.products.ngaims.test_execution.run_test_functions import prepare_cmcf_bench

ACTIVE = True
INACTIVE = False

FR_STATE = {
    0: "Unknown",
    1: "Active",
    2: "Inactive"
}
FR_BOOL = {
    "Active": True,
    "Inactive": False
}


# TODO: implement threading - JIRA[NGAIMS-3110](Observation ticket)
class MainWindow(QMainWindow):
    main_gui = None
    ms_manager = None
    mm_manager = None
    fde_manager = None
    fr_manager = None

    def __init__(self, ms_manager, mm_manager, fde_manager, fr_manager):
        app = QtWidgets.QApplication(sys.argv)

        QMainWindow.__init__(self)
        super(MainWindow).__init__()

        MainWindow.ms_manager = ms_manager
        MainWindow.mm_manager = mm_manager
        MainWindow.fde_manager = fde_manager
        MainWindow.fr_manager = fr_manager

        MainWindow.start_gui()
        app.exec()

    @staticmethod
    def start_gui():
        layout_file = resource_path(os.path.join(pathlib.Path(__file__).parent, 'ms_gui.ui'))
        ui_file = QtCore.QFile(layout_file)
        ui_file.open(QtCore.QFile.ReadOnly)
        loader = QtUiTools.QUiLoader()
        MainWindow.main_gui = loader.load(ui_file)

        MainWindow.main_gui.setWindowTitle("Member System control GUI")
        MainWindow.setup_connections()
        MainWindow.main_gui.show()

    @staticmethod
    def load_selections():
        MainWindow.ms_selections()
        MainWindow.ms_status_selection()
        MainWindow.mm_selections_init()
        MainWindow.fde_selections()
        MainWindow.mm_fde_state_selections()

    @staticmethod
    def setup_connections():
        MainWindow.main_gui.pushButton_populate.clicked.connect(MainWindow.load_selections)
        MainWindow.main_gui.comboBox_ms_selector.currentIndexChanged.connect(MainWindow.update_ms_channel)
        MainWindow.main_gui.comboBox_ms_selector.currentIndexChanged.connect(MainWindow.show_ms_status)
        MainWindow.main_gui.comboBox_ms_selector.currentIndexChanged.connect(MainWindow.mm_selections)
        MainWindow.main_gui.comboBox_mm_selector.currentIndexChanged.connect(MainWindow.show_mm_state)
        MainWindow.main_gui.comboBox_fde_selector.currentIndexChanged.connect(MainWindow.show_fde_state)

        MainWindow.main_gui.pushButton_ms_status.clicked.connect(MainWindow.update_ms_status)
        MainWindow.main_gui.pushButton_mm_state.clicked.connect(MainWindow.update_mm_state)
        MainWindow.main_gui.pushButton_fde_state.clicked.connect(MainWindow.update_fde_state)

    @staticmethod
    def ms_selections():
        mss = MainWindow.ms_manager.get_all_mss()
        for ms in mss:
            ms_detail = MainWindow.ms_manager.get_ms_by_id(ms)
            MainWindow.main_gui.comboBox_ms_selector.addItem(str(ms) + ": " + ms_detail.name)

    @staticmethod
    def update_ms_channel():
        MainWindow.main_gui.comboBox_ms_channel.clear()
        ms_id = MainWindow.get_ms_id()
        ms_detail = MainWindow.ms_manager.get_ms_by_id(ms_id)
        for channel in ms_detail.channels:
            MainWindow.main_gui.comboBox_ms_channel.addItem("MS channel: " + str(channel))

    @staticmethod
    def ms_status_selection():
        for status in MsDispStatus:
            MainWindow.main_gui.comboBox_ms_status.addItem(str(status))

    @staticmethod
    def update_ms_status():
        ms_id = MainWindow.get_ms_id()
        li_ms = [MainWindow.ms_manager.get_ms_by_id(ms_id), ]
        status_enum = MainWindow.main_gui.comboBox_ms_status.currentIndex()
        status_to_set = MsDispStatus(status_enum)
        MainWindow.ms_manager.set_all_ms_status(status_to_set, li_ms)
        MainWindow.ms_manager.get_all_ms_status()

        MainWindow.show_ms_status()

    @staticmethod
    def show_ms_status():
        ms_id = MainWindow.get_ms_id()
        ms_detail = MainWindow.ms_manager.get_ms_by_id(ms_id)
        status = str(ms_detail.ate_status).partition(".")[-1]
        MainWindow.main_gui.label_ms_status.setText("Current MS status: " + status)

    @staticmethod
    def get_ms_id():
        ms = MainWindow.main_gui.comboBox_ms_selector.currentText()
        ms_id = int(ms.partition(":")[0])
        return ms_id

    @staticmethod
    def mm_selections_init():
        mms_all = MainWindow.mm_manager.get_all_mms()
        for mm in mms_all:
            mm_detail = MainWindow.mm_manager.get_mm_by_id(mm)
            MainWindow.main_gui.comboBox_mm_selector.addItem(str(mm) + ": " + mm_detail.name)

    @staticmethod
    def mm_selections():
        MainWindow.main_gui.comboBox_mm_selector.clear()
        ms_id = MainWindow.get_ms_id()
        mms_for_selected_ms = MainWindow.fr_manager.get_mms_for_selected_ms(ms_id)

        if mms_for_selected_ms:
            for mm_id in mms_for_selected_ms:
                mm_detail = MainWindow.mm_manager.get_mm_by_id(mm_id)
                MainWindow.main_gui.comboBox_mm_selector.addItem(str(mm_id) + ": " + mm_detail.name)
        else:
            MainWindow.main_gui.comboBox_mm_selector.addItem("0: No corresponding MM present")

    @staticmethod
    def update_mm_state():
        mm_id = MainWindow.get_mm_id()
        if mm_id:
            state = MainWindow.main_gui.comboBox_mm_state.currentText()
            li_mm = [MainWindow.mm_manager.get_mm_by_id(mm_id), ]
            ms_id = MainWindow.get_ms_id()
            li_ms = [MainWindow.ms_manager.get_ms_by_id(ms_id), ]

            MainWindow.ms_manager.set_all_ms_status(MsDispStatus.NORM_OP, li_ms)
            MainWindow.mm_manager.set_all_mms(state, li_mm)
        else:
            state = FR_STATE[0]

        MainWindow.main_gui.label_mm_state.setText("Current MM state: " + state)

    @staticmethod
    def show_mm_state():
        mm_id = MainWindow.get_mm_id()
        if mm_id:
            mm = MainWindow.mm_manager.get_mm_by_id(mm_id)
            is_active = mm.get_status_by_ate()
            if is_active:
                state = FR_STATE[1]
            else:
                state = FR_STATE[2]
        else:
            state = FR_STATE[0]

        MainWindow.main_gui.label_mm_state.setText("Current MM state: " + state)

    @staticmethod
    def get_mm_id():
        mm = MainWindow.main_gui.comboBox_mm_selector.currentText()
        if len(mm) == 0:
            return 0
        mm_id = int(mm.partition(":")[0])
        return mm_id

    @staticmethod
    def fde_selections():
        fdes = MainWindow.fde_manager.get_all_fdes()
        for fde in fdes:
            fde_detail = MainWindow.fde_manager.get_fde_by_id(fde)
            MainWindow.main_gui.comboBox_fde_selector.addItem(str(fde) + ": " + fde_detail.name)

    @staticmethod
    def update_fde_state():
        state = MainWindow.main_gui.comboBox_fde_state.currentText()
        fde_id = MainWindow.get_fde_id()
        li_fde = [MainWindow.fde_manager.get_fde_by_id(fde_id), ]

        MainWindow.fde_manager.set_all_fdes(FR_BOOL[state], li_fde)
        MainWindow.main_gui.label_fde_state.setText("Current FDE state: " + state)

    @staticmethod
    def show_fde_state():
        fde_id = MainWindow.get_fde_id()
        fde = MainWindow.fde_manager.get_fde_by_id(fde_id)
        state = fde.get_status_by_ate().data.active

        MainWindow.main_gui.label_fde_state.setText("Current FDE state: " + state)

    @staticmethod
    def get_fde_id():
        fde = MainWindow.main_gui.comboBox_fde_selector.currentText()
        fde_id = int(fde.partition(":")[0])
        return fde_id

    @staticmethod
    def mm_fde_state_selections():
        MainWindow.main_gui.comboBox_mm_state.addItem("Inactive")
        MainWindow.main_gui.comboBox_mm_state.addItem("Active")
        MainWindow.main_gui.comboBox_fde_state.addItem("Inactive")
        MainWindow.main_gui.comboBox_fde_state.addItem("Active")


def main():
    try:
        prepare_cmcf_bench()
        with BenchStarter():
            model, external_dependencies = prepare_external_dependencies()
            model_manager = MaintenanceModelComposition(model, external_dependencies)
            ms_manager = model_manager.member_systems_manager
            mm_manager = model_manager.maintenance_messages_manager
            fde_manager = model_manager.flight_deck_effects_manager
            fr_manager = model_manager.fault_report_manager
            fde_manager.set_active_cas_master_instance(fde_manager.cas_master_instances[0])

            MainWindow(ms_manager, mm_manager, fde_manager, fr_manager)

    except Exception as e:
        log.exception(e)


if __name__ == '__main__':
    log = setup_logging_from_config(get_oms_repository_config())
    main()
