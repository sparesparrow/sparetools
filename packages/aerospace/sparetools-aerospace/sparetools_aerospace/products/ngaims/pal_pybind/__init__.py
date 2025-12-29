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
import importlib.util
import os
from pathlib import Path
import sys
from sparetools_aerospace.products.ngaims.test_execution.oms_repository_configuration import OmsRepositoryConfiguration
from ngapy.exceptions.ngapy_exceptions import NgapyConfigurationError


_CONFIGURATION_FOLDER = "Configuration"
_CONFIGURATION_IN_PYTHON_FOLDER = os.path.join(Path(sys.executable).parent, _CONFIGURATION_FOLDER)

_TOOLS_CONFIGURATION_FOLDER = "Tools_Configuration"
_TOOLS_CONFIGURATION_IN_PYTHON_FOLDER = os.path.join(Path(sys.executable).parent, _TOOLS_CONFIGURATION_FOLDER)

_FMLIB_EXE = "FMLib_Comm_Layer.exe"
_FMLIB_EXE_IN_PYTHON_FOLDER = os.path.join(Path(sys.executable).parent, _FMLIB_EXE)

_DEFAULT_CONFIG = ".\\Tools_Configuration\\Connection_config\\DTF_Connection_Config.csv"
_DEFAULT_BUFFER_STRUCTURE = ".\\buffer_structure.csv"

try:
    _PALPYBIND_PACKAGE_DIR = OmsRepositoryConfiguration().config.packages["pal-pybind"][2]

    _spec = importlib.util.spec_from_file_location("SmPortGsmInterfacePyBind", os.path.join(_PALPYBIND_PACKAGE_DIR, "SmPortGsmInterfacePyBind.pyd"))
    _foo = importlib.util.module_from_spec(_spec)
    _SmPortGsmInterface = _foo.SmPortGsmInterface

    _spec = importlib.util.spec_from_file_location("CAIDInterfacePyBind", os.path.join(_PALPYBIND_PACKAGE_DIR, "CAIDInterfacePyBind.pyd"))
    _foo = importlib.util.module_from_spec(_spec)
    _CAIDInterface = _foo.CAIDInterface

    _spec = importlib.util.spec_from_file_location("IoGsmInterfacePyBind", os.path.join(_PALPYBIND_PACKAGE_DIR, "IoGsmInterfacePyBind.pyd"))
    _foo = importlib.util.module_from_spec(_spec)
    _IoGsmInterface = _foo.IoGsmInterface

    _spec = importlib.util.spec_from_file_location("MemoryGsmInterfacePyBind", os.path.join(_PALPYBIND_PACKAGE_DIR, "MemoryGsmInterfacePyBind.pyd"))
    _foo = importlib.util.module_from_spec(_spec)
    _MemoryGsmInterface = _foo.MemoryGsmInterface

except AttributeError:
    class PalDummyClass(object):
        def __init__(self, *args, **kwargs):
            raise NgapyConfigurationError("configuration was not loaded and .pyd modules were not loaded")

    _SmPortGsmInterface = PalDummyClass
    _CAIDInterface = PalDummyClass
    _IoGsmInterface = PalDummyClass
    _MemoryGsmInterface = PalDummyClass
    _PALPYBIND_PACKAGE_DIR = os.getcwd()


def symlink_pal_dll_dependencies(func):
    def wrap(*args, **kwargs):
        if os.path.exists(_CONFIGURATION_IN_PYTHON_FOLDER) is False:
            os.symlink(os.path.join(_PALPYBIND_PACKAGE_DIR, _CONFIGURATION_FOLDER), _CONFIGURATION_IN_PYTHON_FOLDER)

        if os.path.exists(_FMLIB_EXE_IN_PYTHON_FOLDER) is False:
            os.symlink(os.path.join(_PALPYBIND_PACKAGE_DIR, _FMLIB_EXE), _FMLIB_EXE_IN_PYTHON_FOLDER)

        if os.path.exists(_TOOLS_CONFIGURATION_IN_PYTHON_FOLDER) is False:
            os.symlink(os.path.join(_PALPYBIND_PACKAGE_DIR, _TOOLS_CONFIGURATION_FOLDER), _TOOLS_CONFIGURATION_IN_PYTHON_FOLDER)

        result = func(*args, **kwargs)

        if os.path.exists(_CONFIGURATION_IN_PYTHON_FOLDER):
            os.unlink(_CONFIGURATION_IN_PYTHON_FOLDER)

        if os.path.exists(_FMLIB_EXE_IN_PYTHON_FOLDER):
            os.unlink(_FMLIB_EXE_IN_PYTHON_FOLDER)

        if os.path.exists(_TOOLS_CONFIGURATION_IN_PYTHON_FOLDER):
            os.unlink(_TOOLS_CONFIGURATION_IN_PYTHON_FOLDER)
        return result
    return wrap


class SmPortGsmInterface(_SmPortGsmInterface):
    def __init__(self, config=_DEFAULT_CONFIG):
        current_dir = os.getcwd()
        os.chdir(_PALPYBIND_PACKAGE_DIR)
        super().__init__(config)
        os.chdir(current_dir)

    @symlink_pal_dll_dependencies
    def connect(self, *args, **kwargs):
        return super().connect(*args, **kwargs)


class CAIDInterface(_CAIDInterface):
    def __init__(self, config=_DEFAULT_CONFIG):
        current_dir = os.getcwd()
        os.chdir(_PALPYBIND_PACKAGE_DIR)
        super().__init__(config)
        os.chdir(current_dir)

    @symlink_pal_dll_dependencies
    def connect(self, *args, **kwargs):
        return super().connect(*args, **kwargs)


class IoGsmInterface(_IoGsmInterface):
    def __init__(self, buffer_structure=_DEFAULT_BUFFER_STRUCTURE, config=_DEFAULT_CONFIG):
        current_dir = os.getcwd()
        os.chdir(_PALPYBIND_PACKAGE_DIR)
        super().__init__(buffer_structure, config)
        os.chdir(current_dir)

    @symlink_pal_dll_dependencies
    def connect(self, *args, **kwargs):
        return super().connect(*args, **kwargs)


class MemoryGsmInterface(_MemoryGsmInterface):
    def __init__(self, config=_DEFAULT_CONFIG):
        current_dir = os.getcwd()
        os.chdir(_PALPYBIND_PACKAGE_DIR)
        super().__init__(config)
        os.chdir(current_dir)

    @symlink_pal_dll_dependencies
    def connect(self, *args, **kwargs):
        return super().connect(*args, **kwargs)