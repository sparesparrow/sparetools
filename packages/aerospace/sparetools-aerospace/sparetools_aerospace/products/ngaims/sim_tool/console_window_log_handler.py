from PySide6 import QtCore
from numpy import unicode

from sparetools_aerospace.products.ngaims.setup_environment import get_oms_repository_config
from ngapy.util.custom_logging import setup_logging_from_config

class ConsoleWindowLogHandler(QtCore.QObject):
    buffer_message = QtCore.Signal(str)

    def __init__(self, *args, **kwargs):
        QtCore.QObject.__init__(self)
        self.mLog = setup_logging_from_config(get_oms_repository_config())

    def write(self, message):

        if message and message.strip() != "":
            self.buffer_message.emit(unicode(message.strip().strip("\n").strip("\r").strip()))
    
    def info(self, message):
        self.mLog.info(message)
        self.write(message)

    def exception(self, message):
        self.mLog.exception(message)
        self.write(message)