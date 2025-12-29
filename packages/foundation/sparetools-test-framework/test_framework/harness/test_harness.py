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
import numbers
import time
import traceback
import inspect
import os
import logging

try:
    from .test_logging import ThLogger
except ImportError:
    #     from test_logging import ThLogger
    from sparetools.test_framework.harness import ThLogger


class NgapyTestHarnes(object):

    def __init__(self):
        """initializes the testharness utility."""
        self.__output_format__ = "dec"
        self.__callback_function__ = None
        self.th_logger = ThLogger()

    # -----------------------------------------------------------------------------
    # Verify - Verify equality
    # -----------------------------------------------------------------------------
    # @[Verify_1_DCODE]
    # @{Verify_1}
    def verify(self, actual, expected, msg="", test_num=0, on_fail=None):
        """verifies the test condition for equality."""
        # Perform the Verify
        # Comparison may be done for list, tuples, strings or float with integer data types
        value = (actual == expected)
        text = ["Verify " + {False: msg + " ", True: ""}[msg == ""] + ":"]
        if self.__output_format__ == "hex" and \
                ((type(expected) == int) or (type(expected) == int)) and (
                (type(actual) == int) or (type(actual) == int)):
            text.append("\t  " + "Expected : " + "0x%x" % expected)
            text.append("\t  " + "Actual   : " + "0x%x" % actual)
        else:
            text.append("\t  " + "Expected : " + str(expected))
            text.append("\t  " + "Actual   : " + str(actual))
        self.th_logger.log_result(value, text, test_num)
        self.th_logger.log_junit_result(value, text, description=msg, testnum=test_num, timestamp=time.ctime())

        if not value:
            self.handle_on_fail(on_fail)

        return value

    # -----------------------------------------------------------------------------
    # VerifyNE - Verify not equal
    # -----------------------------------------------------------------------------
    # @[VerifyNE_1_DCODE]
    # @{VerifyNE_1}
    def verify_ne(self, actual, expected, msg="", test_num=0, on_fail=None):
        """verifies the test condition for non-equality."""
        # Perform the VerifyNE
        value = (actual != expected)
        text = []
        text.append("Verify " + {False: msg + " ", True: ""}[msg == ""] + ":")
        if self.__output_format__ == "hex" and \
                ((type(expected) == int) or (type(expected) == int)) and (
                (type(actual) == int) or (type(actual) == int)):
            text.append("\t  " + "Expected : <> " + "0x%x" % expected)
            text.append("\t  " + "Actual   : " + "0x%x" % actual)
        else:
            text.append("\t  " + "Expected : <> " + str(expected))
            text.append("\t  " + "Actual   : " + str(actual))
        self.th_logger.log_result(value, text, test_num)
        self.th_logger.log_junit_result(value, text, description=msg, testnum=test_num, timestamp=time.ctime())

        if not value:
            self.handle_on_fail(on_fail)

        return value

    # -----------------------------------------------------------------------------
    # VerifyTol - Verify with tolerance
    # -----------------------------------------------------------------------------
    # @[VerifyTol_1_DCODE]
    # @{VerifyTol_1}
    def verify_tol(self, actual, expected, tolerance, msg="", test_num=0, on_fail=None):
        """verifies the test condition for equality with given tolerance value."""

        if not isinstance(tolerance, numbers.Number):
            raise ValueError("the argument tolerance must be a numeric value.")

        # Perform the VerifyTol (float data type comparison with integer should also be allowed)
        value = False
        if isinstance(actual, numbers.Number) and isinstance(expected, numbers.Number):
            value = ((expected + tolerance) >= actual) & ((expected - tolerance) <= actual)
        else:
            raise ValueError('invalid data types specified for verification.')

        text = []
        text.append("Verify " + {False: msg + " ", True: ""}[msg == ""] + ":")
        text.append("\t  " + "Expected : " + str(expected) + " +/- " + \
                    str(tolerance))
        text.append("\t  " + "Actual   : " + str(actual))
        self.th_logger.log_result(value, text, test_num)
        self.th_logger.log_junit_result(value, text, description=msg, testnum=test_num, timestamp=time.ctime())

        if not value:
            self.handle_on_fail(on_fail)

        return value

    # -----------------------------------------------------------------------------
    # VerifyLE - Verify that actual <= max_value
    # -----------------------------------------------------------------------------
    # @[VerifyLE_1_DCODE]
    # @{VerifyLE_1}

    def verify_le(self, actual, max_value, msg="", test_num=0, on_fail=None):
        """verifies the test condition for actual <= max_value"""
        # Perform the VerifyLE
        value = False
        if isinstance(actual, numbers.Number) and isinstance(max_value, numbers.Number):
            value = (actual <= max_value)
        else:
            raise ValueError('invalid data types specified for verification.')

        text = []
        text.append("Verify " + {False: msg + " ", True: ""}[msg == ""] + ":")
        text.append("\t  " + "Expected : <= " + str(max_value))
        text.append("\t  " + "Actual   : " + str(actual))
        self.th_logger.log_result(value, text, test_num)
        self.th_logger.log_junit_result(value, text, description=msg, testnum=test_num, timestamp=time.ctime())

        if not value:
            self.handle_on_fail(on_fail)

        return value

    # -----------------------------------------------------------------------------
    # VerifyGE - Verify that actual >= min_value
    # -----------------------------------------------------------------------------
    # @[VerifyGE_1_DCODE]
    # @{VerifyGE_1}
    def verify_ge(self, actual, min_value, msg="", test_num=0, on_fail=None):
        """verifies the test condition for actual >= min_value"""
        # Perform the VerifyGE
        value = False
        if isinstance(actual, numbers.Number) and isinstance(min_value, numbers.Number):
            value = (actual >= min_value)
        else:
            raise ValueError('invalid data type specified for verification.')

        text = []
        text.append("Verify " + {False: msg + " ", True: ""}[msg == ""] + ":")
        text.append("\t  " + "Expected : >= " + str(min_value))
        text.append("\t  " + "Actual   : " + str(actual))
        self.th_logger.log_result(value, text, test_num)
        self.th_logger.log_junit_result(value, text, description=msg, testnum=test_num, timestamp=time.ctime())

        if not value:
            self.handle_on_fail(on_fail)

        return value

    # -----------------------------------------------------------------------------
    # VerifyLT - Verify that actual < max_value
    # -----------------------------------------------------------------------------
    # @[VerifyLT_1_DCODE]
    # @{VerifyLT_1}
    def verify_lt(self, actual, max_value, msg="", test_num=0, on_fail=None,
                  error=ValueError('invalid data type specified for verification.')):
        """verifies the test condition for actual < max_value"""
        # Perform the VerifyLT
        value = False
        if isinstance(actual, numbers.Number) and isinstance(max_value, numbers.Number):
            value = (actual < max_value)
        else:
            raise error

        text = []
        text.append("Verify " + {False: msg + " ", True: ""}[msg == ""] + ":")
        text.append("\t  " + "Expected : < " + str(max_value))
        text.append("\t  " + "Actual   : " + str(actual))
        self.th_logger.log_result(value, text, test_num)
        self.th_logger.log_junit_result(value, text, description=msg, testnum=test_num, timestamp=time.ctime())

        if not value:
            self.handle_on_fail(on_fail)

        return value

    # -----------------------------------------------------------------------------
    # verify_gt - Verify that actual > min_value
    # -----------------------------------------------------------------------------
    # @[VerifyGT_1_DCODE]
    # @{VerifyGT_1}
    def verify_gt(self, actual, min_value, msg="", test_num=0, on_fail=None):
        """verifies the test condition for actual > min_value"""
        # Perform the verify_gt
        value = False
        if isinstance(actual, numbers.Number) and isinstance(min_value, numbers.Number):
            value = (actual > min_value)
        else:
            raise ValueError('invalid data type specified for verification.')

        text = []
        text.append("Verify " + {False: msg + " ", True: ""}[msg == ""] + ":")
        text.append("\t  " + "Expected : > " + str(min_value))
        text.append("\t  " + "Actual   : " + str(actual))
        self.th_logger.log_result(value, text, test_num)
        self.th_logger.log_junit_result(value, text, description=msg, testnum=test_num, timestamp=time.ctime())

        if not value:
            self.handle_on_fail(on_fail)

        return value

    # -----------------------------------------------------------------------------
    # verify_range - Verify that min_value <= actual <= max_value
    # -----------------------------------------------------------------------------
    # @[VerifyRange_1_DCODE]
    # @{VerifyRange_1}
    def verify_range(self, actual, min_value, max_value, msg="", test_num=0, on_fail=None):
        """verifies the test condition for the value in the specified range."""
        # Perform the verify_range
        value = False
        if isinstance(actual, numbers.Number) and isinstance(min_value, numbers.Number) and isinstance(max_value,
                                                                                                       numbers.Number):
            value = ((actual >= min_value) and (actual <= max_value))
        else:
            raise ValueError('invalid data type specified for verification.')

        text = []
        text.append("Verify " + {False: msg + " ", True: ""}[msg == ""] + ":")
        text.append("\t  " + "Expected : " + str(min_value) + " <= Actual <= " + \
                    str(max_value))
        text.append("\t  " + "Actual   : " + str(actual))
        self.th_logger.log_result(value, text, test_num)
        self.th_logger.log_junit_result(value, text, description=msg, testnum=test_num, timestamp=time.ctime())

        if not value:
            self.handle_on_fail(on_fail)

        return value

    # -----------------------------------------------------------------------------
    # verify_not_in_range - Verify that actual < min_value and > max_value
    # -----------------------------------------------------------------------------
    # @[VerifyNotInRange_1_DCODE]
    # @{VerifyNotInRange_1}
    def verify_not_in_range(self, actual, min_value, max_value, msg="", test_num=0, on_fail=None):
        """verifies the test condition for the value not in the specified range."""
        # Perform the verify_not_in_range
        value = False
        if isinstance(actual, numbers.Number) and isinstance(min_value, numbers.Number) and isinstance(max_value,
                                                                                                       numbers.Number):
            value = ((actual < min_value) or (actual > max_value))
        else:
            raise ValueError('invalid data type specified for verification.')

        text = []
        text.append("Verify " + {False: msg + " ", True: ""}[msg == ""] + ":")
        text.append("\t  " + "Expected : < " + str(min_value) + " OR " + \
                    " > " + str(max_value))
        text.append("\t  " + "Actual   : " + str(actual))
        self.th_logger.log_result(value, text, test_num)
        self.th_logger.log_junit_result(value, text, description=msg, testnum=test_num, timestamp=time.ctime())

        if not value:
            self.handle_on_fail(on_fail)

        return value

    # -----------------------------------------------------------------------------
    # verify_percent - Verify that actual = expected
    # within the given percent tolerance of the expected value
    # -----------------------------------------------------------------------------
    # @[VerifyPercent_1_DCODE]
    # @{VerifyPercent_1}
    def verify_percent(self, actual, expected, percent, msg="", test_num=0, on_fail=None):
        """verifies the test condition with specified percentage tolerance band."""

        if not isinstance(percent, numbers.Number):
            raise ValueError("the argument percent must be a numeric value.")

        value = False
        if isinstance(actual, numbers.Number) and isinstance(expected, numbers.Number):
            # Perform the verify_percent
            tolerance = abs(expected * percent / 100.0)
            min_value = expected - tolerance
            max_value = expected + tolerance
            value = (actual >= min_value) and (actual <= max_value)
        else:
            raise ValueError('invalid data type specified for verification.')

        text = []
        text.append("Verify " + {False: msg + " ", True: ""}[msg == ""] + ":")
        text.append("\t  " + "Expected : " + str(expected) + " +/- " + \
                    str(percent) + "% (+/- " + str(tolerance) + ")")
        text.append("\t  " + "Actual   : " + str(actual))
        self.th_logger.log_result(value, text, test_num)
        self.th_logger.log_junit_result(value, text, description=msg, testnum=test_num, timestamp=time.ctime())

        if not value:
            self.handle_on_fail(on_fail)

        return value

    # -----------------------------------------------------------------------------
    # verify_string - Verify that actual = expected
    # -----------------------------------------------------------------------------
    # @[VerifyString_1_DCODE]
    # @{VerifyString_1}
    def verify_string(self, actual, expected, case_sensitive=True, msg="", test_num=0, on_fail=None):
        """verifies the string values for equality with/without case."""

        if not type(actual) in (str,):
            raise ValueError("the argument type of 'actual' is not correct, string expected.")
        if not type(expected) in (str,):
            raise ValueError("the argument type of 'expected' is not correct, string expected.")

        # Perform the verify_string
        if case_sensitive:
            value = (actual == expected)
        else:
            value = (actual.upper() == expected.upper())
        text = []
        text.append("Verify " + {False: msg + " ", True: ""}[msg == ""] + ":")
        text.append("\t  " + "Expected : " + expected)
        text.append("\t  " + "Actual   : " + actual)
        self.th_logger.log_result(value, text, test_num)
        self.th_logger.log_junit_result(value, text, description=msg, testnum=test_num, timestamp=time.ctime())

        if not value:
            self.handle_on_fail(on_fail)

        return value

    @staticmethod
    def handle_on_fail(on_fail):
        try:
            if hasattr(on_fail, '__iter__'):
                # multiple on fail actions
                for obj in on_fail:
                    obj.run()
            else:
                if callable(on_fail):
                    on_fail()

                # 1 on fail action
                on_fail.run()
        except:
            pass


# -----------------------------------------------------------------------------
# RunTest - Run a test procedure
# -----------------------------------------------------------------------------
# @[RunTest_1_DCODE]
# @{RunTest_1}
def run_test(function_to_run, results_dir_path, header_message):
    """
    This function is responsible for executing test procedure function. A result
    log is created in provided result directory. Log starts with the header message,
    followed by start test timestamp, individual verification results, end test
    timestamp and results summary.
    :param function_to_run: Function to be executed, should contain verifications
    :param results_dir_path: Target directory to store log files
    :param header_message: String type, formatted, can be as simple as test name
    :return: One of three options ("abort", "pass", "fail") based on the actual result.
    """
    th_logger = ThLogger()
    time_stamp = time.strftime("%m_%d_%Y_%H%M%S", time.localtime())
    test_name = os.path.basename(inspect.getfile(function_to_run)).removesuffix('.py')
    log_file_basename = test_name + "_" + time_stamp + ".txt"
    junit_xml_log_file_basename = test_name + "_" + time_stamp + ".xml"

    abs_results_dir_path = os.path.realpath(results_dir_path)
    abs_path_log_filename = os.path.join(results_dir_path, log_file_basename)
    abs_path_junit_xml_log_filename = os.path.join(abs_results_dir_path, junit_xml_log_file_basename)

    """executes the specified test function and logs the test result."""
    if log_file_basename is not None:
        th_logger.__test_log__.open_test_log_file(abs_path_log_filename, header_message)

    # Try to extract information, if possible, about test description
    for line in header_message.split('\n'):
        if 'description' in line.lower():
            test_descr = line.split(':  ')[1]
            break
    else:
        test_descr = header_message

    if junit_xml_log_file_basename is not None:
        header_info_dict = {"TestProcedureName": os.path.basename(test_name + '.py'),
                            "Description": test_descr}
        # XML infor data for JUNIT
        th_logger.__junit_xml_log__.set_header_info_dict(header_info_dict)

    # Run test
    try:
        result = "fail"
        function_to_run()
        if not th_logger.__test_log__.get_test_failures():
            if th_logger.__test_log__.get_test_passes():
                result = "pass"
            else:
                th_logger.log_result(0, "No verifications performed:", 0)
    except:
        th_logger.__test_log__.write_test_log(traceback.format_exc())  # store to test results log
        th_logger.__junit_xml_log__.write_test_result(False, traceback.format_exc(),
                                                      description="Test exception occurred",
                                                      testnum=-1, timestamp=time.ctime())
        logging.getLogger().warning(traceback.format_exc())  # store to standard log

        th_logger.log_result(0, "Exception occurred:", 0)
        result = "abort"
    th_logger.__test_log__.close_test_log_file()
    th_logger.__junit_xml_log__.create_test_log_file(abs_path_junit_xml_log_filename)
    # Call verification callback because logging counters changed
    try:
        if th_logger.__callback_function__ is not None:
            th_logger.__callback_function__(th_logger.__test_log__.get_test_passes(),
                                            th_logger.__test_log__.get_test_failures(),
                                            th_logger.__test_log__.get_total_test_passes(),
                                            th_logger.__test_log__.get_total_test_failures())
    except:
        pass

    return result
