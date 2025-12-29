################################################################################
#
# caid_utils.py
#
# Description:
#
# CAID utilities library.
#
# The module defines interface and functionality for handling CAID values.
#
################################################################################

################################################################################
# Imports

import logging
import os
import pathlib
import time
import ctypes

from sparetools_aerospace.products.ngaims.test_execution.oms_repository_configuration import OmsRepositoryConfiguration

log = logging.getLogger('__main__.' + __name__)


################################################################################
# Public interface

# class CaidObject
# =============================================================================
# The class defines interface and functionality for handling CAID values.
class CaidObject:
    # Class attributes
    # -----------------------------------------------------------------------------

    _ACTUAL_DIR = os.getcwd()  # Name of actual working directory.
    _CAID_DIR = os.path.join(str(OmsRepositoryConfiguration().config.packages["caid-utils"][2]),
                             "x64")  # Name of CAID utilities core directory.
    _CAID_APP = os.path.join(_CAID_DIR, "CaidUtilsApp.exe")  # File name of CAID utilities core application.
    _caid_dll = ctypes.CDLL(os.path.join(_CAID_DIR, "CaidUtils.dll"))  # Object of CAID utilities core DLL.
    _is_initialized = False  # Indicator, which indicates that this module is initialized.

    DATA_STRING_MAX_SIZE = 256  # Maximal count of characters (bytes) allowed to be stored within

    # Data string representing CAID value.

    # Methods
    # -----------------------------------------------------------------------------

    # Class Constructor.
    def __init__(
            self,
            connection_config_path,
            # Configuration file, which represents configuration for connecting to Target module,
            # Target submodule, and Deos partition.
            # Note: The file is generated externally via PCT tool.
            ip_address="127.0.0.1",  # IP address to connect to.
            # Note: It can be found within Configuration file.
            context_id=2,  # Probably Deos partition ID (not confirmed by Platform India team) to connect to.
            # Note: It can be found within Configuration file.
            output_file_name=None
            # Temporary output file, which contains output data like CAID value received from CAID utilities application.
    ):
        # Initializing class attributes.

        if not CaidObject._is_initialized:
            try:
                CaidObject._caid_dll.caid_create.argtypes = [ctypes.c_char_p]
                CaidObject._caid_dll.caid_create.restype = ctypes.POINTER(ctypes.c_long)

                CaidObject._caid_dll.caid_dispose.argtypes = [ctypes.POINTER(ctypes.c_long)]
                CaidObject._caid_dll.caid_dispose.restype = ctypes.c_int

                CaidObject._caid_dll.caid_connect.argtypes = [ctypes.POINTER(ctypes.c_long), ctypes.c_int,
                                                              ctypes.c_char_p]
                CaidObject._caid_dll.caid_connect.restype = ctypes.c_int

                CaidObject._caid_dll.caid_get_data.argtypes = [ctypes.POINTER(ctypes.c_long), ctypes.c_int,
                                                               ctypes.c_int, ctypes.c_char_p]
                CaidObject._caid_dll.caid_get_data.restype = ctypes.c_int

                CaidObject._caid_dll.caid_set_data.argtypes = [ctypes.POINTER(ctypes.c_long), ctypes.c_int,
                                                               ctypes.c_int, ctypes.c_char_p]
                CaidObject._caid_dll.caid_set_data.restype = ctypes.c_int

                CaidObject._caid_dll.caid_get_data_ex.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int,
                                                                  ctypes.c_int, ctypes.c_char_p]
                CaidObject._caid_dll.caid_get_data_ex.restype = ctypes.c_int

                CaidObject._caid_dll.caid_set_data_ex.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int,
                                                                  ctypes.c_int, ctypes.c_char_p]
                CaidObject._caid_dll.caid_set_data_ex.restype = ctypes.c_int

                CaidObject._is_initialized = True

            except Exception as e:
                CaidObject._log_exception(e)
                CaidObject._is_initialized = False
                return

        # Initializing class object attributes.

        self._connection_config_path = connection_config_path
        self._ip_address = ip_address
        self._context_id = context_id
        self._output_file_name = output_file_name if (output_file_name != None) else os.path.join(
            pathlib.Path(__file__).parent, "out_tmp.txt")

        return

    # Supporting methods

    # The method logs exception passed in.
    @staticmethod
    def _log_exception(exception):
        time.sleep(2)
        log.exception(exception)
        time.sleep(2)

        return

    # The method gets Configuration file.
    @property
    def connection_config_path(self):
        return self._connection_config_path

    # The method gets IP address to connect to.
    @property
    def ip_address(self):
        return self._ip_address

    # The method gets Context ID to connect to.
    @property
    def context_id(self):
        return self._context_id

    # The method gets Temporary output file.
    @property
    def output_file_name(self):
        return self._output_file_name

    # CAID utilities DLL interface related methods

    # TODO: Using CAID utilities DLL interface causes "OS Access violation reading exception", which occurs within "caid_connect()" function
    #  during calling external application "FMLib_Comm_Layer.exe" (provided by Platform India team).
    #  This exception does not occur, when CAID utilities application interface is used. If CAID utilities DLL interface
    #  is decided to be used, then additional communication is needed with Platform India team to resolve the issue.
    #  .
    #  Possible exception occurrence:
    #    caid_utils.py.caid_connect()
    #      CaidUtils.dll.caid_connect()
    #        CaidLib.dll.CAIDINTERFACE.connect()  // External library provided by Platform India team.
    #          FMLib_Comm_Layer.exe               // External application provided by Platform India team.
    #  .
    #  Possible reason of exception:
    #  "FMLib_Comm_Layer.exe" itself might not be the reason of exception. The reason might be the way of integration
    #  external DDLs (which are using additional external executables) into Python. In this way, the memory is shared among several
    #  consumers (Python itself, external DLLs, external .exe(s)), which might lead to memory space conflicts and memory access violations.
    #  It is required to do additional discussions regarding the question, if using direct CAID utilities application interface instead of
    #  using CAID utilities DLL interface is not better solution.

    # The method creates and initializes CAIDs interface object.
    def caid_create(self):
        return_value = -1

        if CaidObject._is_initialized:
            try:
                os.chdir(CaidObject._CAID_DIR)

                return_value = CaidObject._caid_dll.caid_create(self._connection_config_path.encode())

                os.chdir(CaidObject._ACTUAL_DIR)

            except Exception as e:
                CaidObject._log_exception(e)

        return return_value

    # The method creates and initializes CAIDs interface object.
    @staticmethod
    def caid_dispose(
            caid_handle  # Handle of actual CAIDs interface object.
    ):
        return_value = -1

        if CaidObject._is_initialized:
            try:
                os.chdir(CaidObject._CAID_DIR)

                return_value = CaidObject._caid_dll.caid_dispose(caid_handle)

                os.chdir(CaidObject._ACTUAL_DIR)

            except Exception as e:
                CaidObject._log_exception(e)

        return return_value

    # The method connects CAIDs interface object with Target.
    def caid_connect(
            self,
            caid_handle,  # Handle of actual CAIDs interface object.
            context_id=None  # Probably Deos partition ID (not confirmed by Platform India team) to connect to.
            # Note 1: It can be found within Configuration file.
            # Note 2: If omitted, then default context ID from constructor is used.
    ):
        return_value = -1

        if CaidObject._is_initialized:
            try:
                os.chdir(CaidObject._CAID_DIR)

                return_value = CaidObject._caid_dll.caid_connect(
                    caid_handle,
                    self._context_id if (context_id == None) else context_id,
                    self._ip_address.encode()
                )

                os.chdir(CaidObject._ACTUAL_DIR)

            except Exception as e:
                CaidObject._log_exception(e)

        return return_value

    # The method gets CAID data.
    def caid_get_data(
            self,
            caid_handle,  # Handle of actual CAIDs interface object.
            caid_number,  # CAID number corresponding to CAID name.
            # Note: It can be found within CAID list file. For info, where to find this file, contact Platform India team.
            context_id=None  # Probably Deos partition ID (not confirmed by Platform India team) to connect to.
            # Note 1: It can be found within Configuration file.
            # Note 2: If omitted, then default context ID from constructor is used.
    ):
        return_value = -1
        data_string = ""  # Data string, where actual CAID value shall be stored.
        # Note: It is string representation of CAID value (e.g. value 88.88 is represented as "88.88").

        if CaidObject._is_initialized:
            try:
                os.chdir(CaidObject._CAID_DIR)

                data_string_obj = ctypes.create_string_buffer(CaidObject.DATA_STRING_MAX_SIZE)

                return_value = CaidObject._caid_dll.caid_get_data(
                    caid_handle,
                    caid_number,
                    self._context_id if (context_id == None) else context_id,
                    data_string_obj
                )

                data_string = data_string_obj.value.decode()

                os.chdir(CaidObject._ACTUAL_DIR)

            except Exception as e:
                CaidObject._log_exception(e)

        return return_value, data_string

    # The method sets CAID data.
    def caid_set_data(
            self,
            caid_handle,  # Handle of actual CAIDs interface object.
            caid_number,  # CAID number corresponding to CAID name.
            # Note: It can be found within CAID list file. For info, where to find this file, contact Platform India team.
            data_string,  # Data string, which shall be used to set CAID value.
            # Note: It is string representation of CAID value (e.g. value 88.88 is represented as "88.88").
            context_id=None  # Probably Deos partition ID (not confirmed by Platform India team) to connect to.
            # Note 1: It can be found within Configuration file.
            # Note 2: If omitted, then default context ID from constructor is used.
    ):
        return_value = -1

        if CaidObject._is_initialized:
            try:
                os.chdir(CaidObject._CAID_DIR)

                return_value = CaidObject._caid_dll.caid_set_data(
                    caid_handle,
                    caid_number,
                    self._context_id if (context_id == None) else context_id,
                    data_string.encode()
                )

                os.chdir(CaidObject._ACTUAL_DIR)

            except Exception as e:
                CaidObject._log_exception(e)

        return return_value

    # The method performs the following actions in the following order:
    # - It creates and initializes CAIDs interface object.
    # - It connects CAIDs interface object with Target.
    # - It gets CAID data.
    def caid_get_data_ex(
            self,
            caid_number,  # CAID number corresponding to CAID name.
            # Note: It can be found within CAID list file. For info, where to find this file, contact Platform India team.
            context_id=None  # Probably Deos partition ID (not confirmed by Platform India team) to connect to.
            # Note 1: It can be found within Configuration file.
            # Note 2: If omitted, then default context ID from constructor is used.
    ):
        return_value = -1
        data_string = ""  # Data string, where actual CAID value shall be stored.
        # Note: It is string representation of CAID value (e.g. value 88.88 is represented as "88.88").

        if CaidObject._is_initialized:
            try:
                os.chdir(CaidObject._CAID_DIR)

                data_string_obj = ctypes.create_string_buffer(CaidObject.DATA_STRING_MAX_SIZE)

                return_value = CaidObject._caid_dll.caid_get_data_ex(
                    self._connection_config_path.encode(),
                    self._ip_address.encode(),
                    caid_number,
                    self._context_id if (context_id == None) else context_id,
                    data_string_obj
                )

                data_string = data_string_obj.value.decode()

                os.chdir(CaidObject._ACTUAL_DIR)

            except Exception as e:
                CaidObject._log_exception(e)

        return return_value, data_string

    # The method performs the following actions in the following order:
    # - It creates and initializes CAIDs interface object.
    # - It connects CAIDs interface object with Target.
    # - It sets CAID data.
    def caid_set_data_ex(
            self,
            caid_number,  # CAID number corresponding to CAID name.
            # Note: It can be found within CAID list file. For info, where to find this file, contact Platform India team.
            data_string,  # Data string, which shall be used to set CAID value.
            # Note: It is string representation of CAID value (e.g. value 88.88 is represented as "88.88").
            context_id=None  # Probably Deos partition ID (not confirmed by Platform India team) to connect to.
            # Note 1: It can be found within Configuration file.
            # Note 2: If omitted, then default context ID from constructor is used.
    ):
        return_value = -1

        if CaidObject._is_initialized:
            try:
                os.chdir(CaidObject._CAID_DIR)

                return_value = CaidObject._caid_dll.caid_set_data_ex(
                    self._connection_config_path.encode(),
                    self._ip_address.encode(),
                    caid_number,
                    self._context_id if (context_id == None) else context_id,
                    data_string.encode()
                )

                os.chdir(CaidObject._ACTUAL_DIR)

            except Exception as e:
                CaidObject._log_exception(e)

        return return_value

    # CAID utilities application interface related methods
    # ------------------------------------------------------------------------------

    # The method performs the following actions in the following order:
    # - It creates and initializes CAIDs interface object.
    # - It connects CAIDs interface object with Target.
    # - It gets CAID data.
    def caid_app_get_data_ex(
            self,
            caid_number,  # CAID number corresponding to CAID name.
            # Note: It can be found within CAID list file. For info, where to find this file, contact Platform India team.
            context_id=None  # Probably Deos partition ID (not confirmed by Platform India team) to connect to.
            # Note 1: It can be found within Configuration file.
            # Note 2: If omitted, then default context ID from constructor is used.
    ):
        # This code is intentionally disable for now because it is causing issues during system test execution.
        return 0, ''
        return_value = -1
        data_string = ""  # Data string, where actual CAID value shall be stored.
        # Note: It is string representation of CAID value (e.g. value 88.88 is represented as "88.88").

        if CaidObject._is_initialized:
            try:
                output_file = open(self._output_file_name, "wb")
                output_file.close()

                os.chdir(CaidObject._CAID_DIR)

                command = f'{self._CAID_APP} -get "{self._connection_config_path}" "{self._ip_address}" {caid_number} ' \
                          f'{self._context_id if (context_id == None) else context_id} "{self._output_file_name}"'
                return_value = os.system(command)

                os.chdir(CaidObject._ACTUAL_DIR)

                with open(self._output_file_name, "rb") as output_file:
                    data_string = output_file.read().decode()

                os.remove(self._output_file_name)

            except Exception as e:
                CaidObject._log_exception(e)

        return return_value, data_string

    # The method performs the following actions in the following order:
    # - It creates and initializes CAIDs interface object.
    # - It connects CAIDs interface object with Target.
    # - It sets CAID data.
    def caid_app_set_data_ex(
            self,
            caid_number,  # CAID number corresponding to CAID name.
            # Note: It can be found within CAID list file. For info, where to find this file, contact Platform India team.
            data_string,  # Data string, which shall be used to set CAID value.
            # Note: It is string representation of CAID value (e.g. value 88.88 is represented as "88.88").
            context_id=None  # Probably Deos partition ID (not confirmed by Platform India team) to connect to.
            # Note 1: It can be found within Configuration file.
            # Note 2: If omitted, then default context ID from constructor is used.
    ):
        # This code is intentionally disable for now because it is causing issues during system test execution.
        return 0
        return_value = -1

        if CaidObject._is_initialized:
            try:
                os.chdir(CaidObject._CAID_DIR)

                command = f'{self._CAID_APP} -set "{self._connection_config_path}" "{self._ip_address}" {caid_number} ' \
                          f'{self._context_id if (context_id == None) else context_id} "{data_string}"'
                return_value = os.system(command)

                os.chdir(CaidObject._ACTUAL_DIR)

            except Exception as e:
                CaidObject._log_exception(e)

        return return_value

# end class CaidObject

# caid_utils.py
