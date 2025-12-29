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
import inspect
import logging
import os
import time
from pathlib import Path

from junit_xml import TestSuite, TestCase


class Logging:
    # Initialize class constants
    __SPACING__ = 78

    # -------------------------------------------------------------------------
    # Write to log file
    # -------------------------------------------------------------------------
    def __write_log__(self, msg, stream):
        if stream != None:
            try:
                stream.write(msg + "\n")
                stream.flush()
            except:
                logging.getLogger().info("Failed to write string, dumping:")
                dump = ':'.join(hex(ord(x))[2:] for x in msg)
                logging.getLogger().info("Dump: %s" % dump)
                raise
        for line in msg.splitlines():
            logging.getLogger().info(line)

    # -------------------------------------------------------------------------
    # Write verification result to log file
    # -------------------------------------------------------------------------
    def __write_result__(self, value, text, stream, testnum=0):
        # Determine spacing of text
        spacing = self.__SPACING__ - len("      FAILED")

        # Put text in a list
        if type(text) != list:
            temp = []
            temp.append(text)
            text = temp
        if testnum != 0:
            text.insert(0, f"Test number: %s" % testnum)

            # Determine spacing if test number is used
            msg = text[0]
            msg = msg + " " * (spacing - len(msg))
        else:
            # Determine spacing if test number is not used
            msg = text[0]
            lines = msg.split('\n')
            if len(lines) == 1:
                while len(msg) >= spacing:
                    self.__write_log__(msg[0:(spacing - 1)], stream)
                    msg = msg[(spacing - 1):len(msg)]
                else:
                    if len(msg) < self.__SPACING__:
                        msg = msg + " " * (spacing - len(msg))
            else:
                for line in lines[:-1]:
                    self.__write_log__(line, stream)
                msg = lines[-1] + " " * (spacing - len(lines[-1]))

        # Display text
        if value:
            msg = msg + "PASSED"
        else:
            msg = msg + "      FAILED"
        self.__write_log__(msg, stream)
        for i in range(1, len(text)):
            self.__write_log__(text[i], stream)


class TestLogging(Logging):
    # Initialize class variables
    __logFile__ = None
    __testPasses__ = 0
    __testFailures__ = 0
    __totalTestPasses__ = 0
    __totalTestFailures__ = 0

    # -------------------------------------------------------------------------
    # Close test log file
    # -------------------------------------------------------------------------
    def close_test_log_file(self):
        if self.__logFile__ is not None:
            self.___write_test_footer__()
            self.__logFile__.close()
            self.__logFile__ = None
        self.__testPasses__ = 0
        self.__testFailures__ = 0

    # -------------------------------------------------------------------------
    # Retrieve number of tests failed
    # -------------------------------------------------------------------------
    def get_test_failures(self):
        return self.__testFailures__

    def get_total_test_failures(self):
        return self.__totalTestFailures__

    # -------------------------------------------------------------------------
    # Retrieve number of tests passed
    # -------------------------------------------------------------------------
    def get_test_passes(self):
        return self.__testPasses__

    def get_total_test_passes(self):
        return self.__totalTestPasses__

    # -------------------------------------------------------------------------
    # Open test log file
    # -------------------------------------------------------------------------
    def open_test_log_file(self, log_file_name, test_name, overwrite=False):
        try:
            if (overwrite is False) and os.path.exists(log_file_name):
                for ext in range(1, 1000):
                    index = log_file_name.rfind(".")
                    if (index == -1) or (log_file_name.rfind("/") > index):
                        backup_name = log_file_name + "." + str(ext)
                    else:
                        backup_name = log_file_name[0:index] + "." + str(ext)
                    if os.path.exists(backup_name) == 0:
                        break
                else:
                    backup_name = log_file_name + ".log"
                    if os.path.exists(backup_name):
                        os.remove(backup_name)
                os.rename(log_file_name, backup_name)
            self.close_test_log_file()
            if not os.path.exists(Path(log_file_name).parent):
                Path.mkdir(Path(log_file_name).parent)
            self.__logFile__ = open(log_file_name, "w")
            self.__WriteTestHeader__(test_name)
        except:
            print("ERROR: Cannot open log file")
            raise

    # -------------------------------------------------------------------------
    # Write to test log file
    # -------------------------------------------------------------------------
    def write_test_log(self, msg):
        self.__write_log__(msg, self.__logFile__)

    # -------------------------------------------------------------------------
    # Write verification result to test log file
    # -------------------------------------------------------------------------
    def write_test_result(self, value, text, testnum=0):
        if value:
            self.__totalTestPasses__ = self.__totalTestPasses__ + 1
            self.__testPasses__ = self.__testPasses__ + 1
        else:
            self.__totalTestFailures__ = self.__totalTestFailures__ + 1
            self.__testFailures__ = self.__testFailures__ + 1
        self.__write_result__(value, text, self.__logFile__, testnum)

    # -------------------------------------------------------------------------
    # Write footer to test log file
    # -------------------------------------------------------------------------
    def ___write_test_footer__(self):
        self.write_test_log("")
        self.write_test_log("Test end time = " + time.ctime(time.time()))
        self.write_test_log('=' * self.__SPACING__)
        self.write_test_log("Total number of passes   : " +
                            str(self.__testPasses__))
        self.write_test_log("Total number of failures : " +
                            str(self.__testFailures__))
        self.write_test_log('=' * self.__SPACING__)

    # -------------------------------------------------------------------------
    # Write header to test log file
    # -------------------------------------------------------------------------
    def __WriteTestHeader__(self, test_name):
        self.write_test_log("")
        self.write_test_log('=' * self.__SPACING__)
        self.write_test_log("TEST : " + test_name)
        self.write_test_log('=' * self.__SPACING__)
        self.write_test_log("Test start time = " + time.ctime(time.time()))
        self.write_test_log("")

    # Init function
    def init(self):
        self.close_test_log_file()
        self.__totalTestPasses__ = 0
        self.__totalTestFailures__ = 0


class JunitTestLogging(Logging):
    __test_suite__ = None
    __test_results__ = []
    __test_name__ = ""
    __testnum__ = 0
    __test_case_start__ = 0
    __test_case_elapsed_time__ = 0
    __error_count__ = 0

    def reset_internal_state(self):
        self.__logFile__ = None
        self.__test_suite__ = None
        self.__test_results__ = []
        self.__test_name__ = ""
        self.__testnum__ = 0
        self.__test_case_start__ = 0
        self.__test_case_elapsed_time__ = 0
        self.__error_count__ = 0

    # -------------------------------------------------------------------------
    # Create xml test log file - flush all data
    # -------------------------------------------------------------------------
    def create_test_log_file(self, log_file_name, overwrite=False):
        self.populate_test_suite_info()
        try:
            if (overwrite is False) and os.path.exists(log_file_name):
                for ext in range(1, 1000):
                    index = log_file_name.rfind(".")
                    if (index == -1) or (log_file_name.rfind("/") > index):
                        backup_name = log_file_name + "." + str(ext)
                    else:
                        backup_name = log_file_name[0:index] + "." + str(ext)
                    if os.path.exists(backup_name) == 0:
                        break
                else:
                    backup_name = log_file_name + ".log"
                    if os.path.exists(backup_name):
                        os.remove(backup_name)
                os.rename(log_file_name, backup_name)

            file = open(log_file_name, 'w+')
            rc = TestSuite.to_file(file, [self.__test_suite__], prettyprint=True)
            file.close()
            self.reset_internal_state()
        except:
            print("ERROR: Cannot create xml file")
            raise

    # -------------------------------------------------------------------------
    # Write to test log file
    # -------------------------------------------------------------------------
    def write_test_log(self, msg):
        self.__write_log__(msg, self.__logFile__)

    # -------------------------------------------------------------------------
    # Write verification result to test log file
    # -------------------------------------------------------------------------
    def write_test_result(self, value, text, description="", testnum=0, timestamp=0, duration_sec=0):
        # Preproces text:
        processed_text = (''.join(text)).replace('\t', '')
        # Self increment of test verification item
        if testnum == 0:
            stack_list = inspect.stack()
            for item in stack_list:
                # https://docs.python.org/3/library/inspect.html
                # filename = 1 and linenum = 2
                # Get line number from calling script
                if self.__test_name__ == os.path.basename(item.filename):
                    self.__testnum__ = item.lineno
                    break
        else:
            self.__testnum__ = testnum

        # Generate internal elapsed time
        if duration_sec == 0:
            new_start_frozen = time.time()
            self.__test_case_elapsed_time__ = new_start_frozen - self.__test_case_start__
            # reset timer
            self.__test_case_start__ = new_start_frozen
        else:
            self.__test_case_elapsed_time__ = duration_sec

        test_name = "Id: " + str(self.__testnum__) + " " + description
        # remove .py since JUni parser removes data before .py
        class_name_junit = self.__test_name__.replace(".py", "")
        ts = TestCase(name=test_name, classname=class_name_junit,
                      elapsed_sec=self.__test_case_elapsed_time__, timestamp=timestamp,
                      stdout=processed_text)
        if not value:
            ts.add_failure_info(message=processed_text, failure_type="FAIL")
            if 'Traceback (most recent call last)' in processed_text:
                ts.add_error_info(message=processed_text, error_type="error")
        self.__test_results__.append(ts)

    # -------------------------------------------------------------------------
    # set test name used in test suite info
    # -------------------------------------------------------------------------
    def set_header_info_dict(self, dict_info):
        # this is at the beginning of the test.Set initial timer"
        self.__test_case_start__ = time.time()
        self.__header_dict__ = dict_info
        if "TestProcedureName" in dict_info:
            self.__test_name__ = dict_info["TestProcedureName"]

        else:
            self.__test_name__ = "Not Identified Test Procedure"

    # -------------------------------------------------------------------------
    # Create overall test suite info including attributes
    # -------------------------------------------------------------------------
    def populate_test_suite_info(self):
        self.__test_suite__ = TestSuite(name=self.__test_name__, test_cases=self.__test_results__,
                                        properties=self.__header_dict__, hostname=os.getenv('COMPUTERNAME'))


class ThLogger(object):
    __instance = None

    def __new__(cls):
        if ThLogger.__instance is None:
            ThLogger.__instance = object.__new__(cls)
            ThLogger.__instance.__callback_function__ = None
            ThLogger.__instance.__test_log__ = TestLogging()
            ThLogger.__instance.__junit_xml_log__ = JunitTestLogging()
            ThLogger.__instance.__init_logging()
        return ThLogger.__instance

    @staticmethod
    def __init_logging(test_logging_level=logging.INFO):

        # basic logging level, this is lowest level that will be logged across all registered handlers
        logging.getLogger().setLevel(level=logging.DEBUG)

        # command console output, standard output when running from command line
        from logging import StreamHandler
        console_handler = StreamHandler()
        console_handler.setLevel(level=test_logging_level)
        formatter = logging.Formatter('%(message)s')
        console_handler.setFormatter(formatter)
        logging.getLogger().addHandler(console_handler)

        # log beginning header
        logging.info(' ' * 80)
        logging.info('*' * 80)
        logging.info('Log file opened at %s', time.strftime("%m/%d/%Y %H:%M:%S", time.localtime()))
        logging.info('*' * 80)

    def log_result(self, value, text, test_num):
        self.__test_log__.write_test_result(value, text, test_num)
        if self.__callback_function__ is not None:
            self.__callback_function__(self.__test_log__.get_test_passes(),
                                       self.__test_log__.get_test_failures(), self.__test_log__.get_total_test_passes(),
                                       self.__test_log__.get_total_test_failures())

    def log_junit_result(self, value, text, description="", testnum=0, timestamp=0, duration_sec=0):
        self.__junit_xml_log__.write_test_result(value, text, description, testnum, timestamp, duration_sec)


class GlobalLogging(Logging):
    # Initialize class variables
    __globalLogFile__ = None
    __globalPasses__ = 0
    __globalFailures__ = 0

    # -------------------------------------------------------------------------
    # Constructor
    # -------------------------------------------------------------------------
    def __init__(self, global_log_file_name):

        # Try to open global log file
        try:
            if global_log_file_name is not None:
                self.__globalLogFile__ = open(global_log_file_name, "wt")
            self.__write_global_header__()
        except:
            print("ERROR: Cannot open global log file")
            raise

    # -------------------------------------------------------------------------
    # Close global log file
    # -------------------------------------------------------------------------
    def close_global_log_file(self, expectedTestsRun):
        self.__write_global_footer__(expectedTestsRun)
        if self.__globalLogFile__ is not None:
            self.__globalLogFile__.close()
            self.__globalLogFile__ = None

    # -------------------------------------------------------------------------
    # Retrieve number of tests failed
    # -------------------------------------------------------------------------
    def get_global_failures(self):
        return self.__globalFailures__

    # -------------------------------------------------------------------------
    # Retrieve number of tests passed
    # -------------------------------------------------------------------------
    def get_global_passes(self):
        return self.__globalPasses__

    # -------------------------------------------------------------------------
    # Write to global log file
    # -------------------------------------------------------------------------
    def write_global_log(self, msg):
        self.__write_log__(msg, self.__globalLogFile__)

    # -------------------------------------------------------------------------
    # Write verification result to global log file
    # -------------------------------------------------------------------------
    def write_global_result(self, value, text):
        if value:
            self.__globalPasses__ = self.__globalPasses__ + 1
        else:
            self.__globalFailures__ = self.__globalFailures__ + 1
        self.__write_result__(value, text, self.__globalLogFile__)

    # -------------------------------------------------------------------------
    # Write footer to global log file
    # -------------------------------------------------------------------------
    def __write_global_footer__(self, expectedTestsRun):
        self.write_global_log("")
        self.write_global_log("Global end time = " + time.ctime(time.time()))
        self.write_global_log('=' * self.__SPACING__)
        self.write_global_log("Expected Procedures Executed : " +
                              str(expectedTestsRun))
        self.write_global_log("Total Procedures Executed    : " +
                              str(self.__globalFailures__ + self.__globalPasses__))
        self.write_global_log("Procedures Passed            : " +
                              str(self.__globalPasses__))
        self.write_global_log("Procedures Failed            : " +
                              str(self.__globalFailures__))
        self.write_global_log('=' * self.__SPACING__)
        self.write_global_log("")
        if self.__globalFailures__ or (expectedTestsRun !=
                                       self.__globalFailures__ + self.__globalPasses__):
            self.write_global_log("Overall Test Results : FAILED")
        else:
            self.write_global_log("Overall Test Results : PASSED")

    # -------------------------------------------------------------------------
    # Write header to global log file
    # -------------------------------------------------------------------------
    def __write_global_header__(self):
        self.write_global_log("")
        self.write_global_log('=' * self.__SPACING__)
        self.write_global_log((self.__SPACING__ - 28) // 2 * '=' + \
                              "  T E S T    S U M M A R Y  " + (self.__SPACING__ - 28) // 2 * '=')
        self.write_global_log('=' * self.__SPACING__)
        self.write_global_log("Global start time = " + time.ctime(time.time()))
        self.write_global_log("")
