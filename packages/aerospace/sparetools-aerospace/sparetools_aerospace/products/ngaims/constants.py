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
// File Name: constants.py
//
// Program:   TITAN
//
// Purpose:   Constants holder
//
// Notes:     None
//
//********************************************************************************************
//********************************************************************************************
"""
from enum import IntEnum

from ngapy.exceptions.ngapy_exceptions import NgapyRuntimeError
from ngapy.io_platform.message_composition import IoExtendedStatus, get_complete_validity, IoRawStatus


class MsDispStatus(IntEnum):
    NORM_OP = 0
    FN_TEST = 1
    INVALID = 2
    ADN_NO_COMM = 3
    LRU_NO_COMM = 4
    IO_FAILURE = 5
    DATA_FAILURE = 6
    NO_STATUS = 7

    # Status value to value is 1:N, therefore we had to select one choice. Second is commented out
    @staticmethod
    def validity(status_value):
        if status_value == MsDispStatus.NORM_OP:
            return get_complete_validity(raw_status=IoRawStatus.NORMAL_OPERATION_e,
                                         extended_status=IoExtendedStatus.NO_EXTENDED_STATUS)
            # return get_complete_validity(raw_status=IoRawStatus.NO_COMPUTED_DATA_e,
            #                              extended_status=IoExtendedStatus.NO_EXTENDED_STATUS)
        if status_value == MsDispStatus.FN_TEST:
            return get_complete_validity(raw_status=IoRawStatus.FUNCTIONAL_TEST_e,
                                         extended_status=IoExtendedStatus.NO_EXTENDED_STATUS)
        if status_value == MsDispStatus.INVALID:
            return get_complete_validity(raw_status=IoRawStatus.NODATA_FAILUREWARNING_e,
                                         extended_status=IoExtendedStatus.NO_EXTENDED_STATUS)
        if status_value == MsDispStatus.ADN_NO_COMM:
            return get_complete_validity(raw_status=IoRawStatus.NORMAL_OPERATION_e,
                                         extended_status=IoExtendedStatus.ADN_NO_COMM)
        if status_value == MsDispStatus.LRU_NO_COMM:
            return get_complete_validity(raw_status=IoRawStatus.NORMAL_OPERATION_e,
                                         extended_status=IoExtendedStatus.EXT_SYSTEM_NO_COMM)
        if status_value == MsDispStatus.IO_FAILURE:
            return get_complete_validity(raw_status=IoRawStatus.NORMAL_OPERATION_e,
                                         extended_status=IoExtendedStatus.PROD_BIT_FAULT)
            # return get_complete_validity(raw_status=IoRawStatus.NORMAL_OPERATION_e,
            #                              extended_status=IoExtendedStatus.SUB_BIT_FAULT)
        if status_value == MsDispStatus.DATA_FAILURE:
            return get_complete_validity(raw_status=IoRawStatus.NORMAL_OPERATION_e,
                                         extended_status=IoExtendedStatus.DATA_CHECK_FAULT)
        if status_value == MsDispStatus.NO_STATUS:
            raise NgapyRuntimeError('There is no mapping of NO_STATUS to validity')


separator = 78 * "="


class ConnectionTypes(IntEnum):
    NO_TYPE = 0
    A429_DIRECT = 1
    A429_INDIRECT = 2
    ASCB = 3
    A825_DICRECT = 4
    A825_INDIRECT = 5
    A664_DIRECT = 6
    A664_INDIRECT = 7
    FUTURE = 8


class ControlTypes(IntEnum):
    cNone = 0
    cText = 1
    cLine = 2
    cShape = 3
    cTechPub = 4
    cArincDiscrete = 5
    cArincBnr = 6
    cArincBcd = 7
    cArincCoded = 8
    cASCBInt = 9
    cASCBUInt = 10
    cASCBFloat = 11
    cASCBEnum = 12
    cASCBText = 13
    cMsStatus = 14
    cGauge = 15
    cButton = 16
    cAdj_Control = 17
    cAdjustment = 17
    cFault_State = 18
    cMaintMsg = 18
    cMmState = 18
    cBezel = 20  # Essentially the same as a button but  managed differently.
    cTree = 21
    cAfTree = 22
    cMsTree = 23
    cAfDetail = 24
    cDynamicText = 26  # Essentially the same as cText but can be modified dynamically by CMC runtime.
    cSfTree = 27
    cDateLegTree = 28
    cDetailTree = 29
    cTimer = 30
    cXferTree = 31
    cDownloadTree = 32
    cTestTree = 33
    cTestCmplTree = 34  # interactive/non-interactive test results
    cTestStatus = 35  # all tests / test stopped for reason
    cConfigTree = 36
    cFdeTree = 37
    cFdeDetailTree = 38
    cAFdeTree = 39
    cReportTree = 40
    cFsaButton = 41
    cFileTextTree = 42
    cFdeMmelTree = 43
    cDlsButton = 44
    cManagerFDEMM = 45
    cFpVariable = 47
    cPrintMgrTree = 48
    cLatchButton = 49
    cPassCode = 50  # DLS control
    cProgFdeList = 51  # Programmable FDE Detail list
    cATOrderedTree = 52  # Active Time Ordered
    cSTOrderedTree = 53  # Stored Time Ordered
    cOptionsTree = 54  # Configurable Options
    cModuleRestart = 55  # Module Restart
    cNVMTgtTree = 56  # storage targets the nvm files can transfer
    cACMFConfigTree = 57
    cWirelessStatusTree = 58
    cWAPButton = 59
    cWirelessDisconnectAllButton = 60
    cPSFConfigTree = 61


run_script_text = "Run Script"
stop_script_text = "Stop Script"

EXIT_CODE_REBOOT = -12345678
