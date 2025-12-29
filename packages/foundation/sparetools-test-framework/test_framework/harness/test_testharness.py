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
# ********************************************************************************************
#

#
# Program:   BBITS
#
# Purpose:   Verification of RTAR Test Harness verification methods
#
# Notes: None
# ********************************************************************************************
# ********************************************************************************************

try:
    from .test_harness import NgapyTestHarnes
except ImportError:
    from sparetools.test_framework.harness import NgapyTestHarnes

import unittest
import os
import re
import logging
import argparse

# Definition of Globally used variables/constants
PASSED = 'PASSED'
FAILED = 'FAILED'
RESULTS_DIR = 'results'
on_fail_msg = 'On Fail method called.\n'
temp_results = r'temp_results.log'


def on_fail_function():
    logging.getLogger().info(on_fail_msg)


def th_verify_log(log_msg, expected_result, actual, expected, tolerance=None, prcnt=None, rng=None, msg='', test_num=0, on_fail=None):
    # This function verifies result written to a file by test_harness verification methods, by
    # recreating the result using  regular expression and comparing it. The pre-requisite for
    # using this function is that the file contains only unique records, so only one record
    # can match to a regular expression search (can be accomplished by combining extra message
    # and the record itself)
    re_log_msg = r''
    re_test_num_msg_result = r''
    re_expected_val = r''
    re_actual_val = r''
    re_on_fail_val = r''

    if type(expected) == list:
        expected = '\\' + str(expected)
        actual = '\\' + str(actual)

    re_log_msg = log_msg.replace('(', '\(').replace(')', '\)') + '\n'

    if test_num is None or test_num == 0:
        re_test_num_msg_result = 'Verify *{msg} *: *{res} *\n?'.format(msg=msg, res=expected_result)
    else:
        re_test_num_msg_result = 'Test number *: *{num} *{res}\n? *Verify *{msg} *: *\n?'.format(num=test_num, msg=msg, res=expected_result)

    if tolerance is None and rng is None and prcnt is None:
        re_expected_val = '\t? *Expected *: [<>=+/%-]* *{exp} *\n?'.format(exp=expected)
    elif tolerance is not None:
        re_expected_val = '\t? *Expected *: *{exp} *[<>+/%-]* *{tol} *\n?'.format(exp=expected, tol=tolerance)
    elif rng is not None:
        re_expected_val = '\t? *Expected *: *<* *{min} *(?:OR *>|<= *Actual *<=) *{max}\n?'.format(min=rng[0], max=rng[1])
    elif prcnt is not None:
        re_expected_val = '\t? *Expected *: *{exp} *[+/-]* *{prcnt}% *\([+/-]* *{tol}\) *\n?'.format(exp=expected, prcnt=prcnt, tol=abs(expected * prcnt / 100.0))

    re_actual_val = '\t *Actual *: *{act} *\n?'.format(act=actual)
    re_on_fail_val = on_fail_msg if (expected_result == FAILED and on_fail is not None) else '\n'

    re_string = re.compile(re_log_msg + re_test_num_msg_result + re_expected_val + re_actual_val + re_on_fail_val)
    with open(temp_results, 'r') as log:
        match_count = len(re.findall(re_string, log.read()))
        if match_count == 1:
            return True
        else:
            return False


class TestTestHarness(unittest.TestCase):
    def setUp(self):
        self.th = NgapyTestHarnes()

    def log_results(self):
        logging.info('\n\n')
        logging.info('RESULTS')

    # @[Verify_1_TCASE_1]
    # @{Verify_1}
    def test_verify_1_TCASE_1(self):
        logging.info('\n\nTesting Verify_1 anchor - floating point parameters\n')
        actual_value = 50.4567
        expected_value = 50.4567
        tolerance = 0.0001

        test_cases_table = [
            # Test that the verify() function indicates Passed
            # when the actual value is equal to expected value.
            [PASSED, 'Test Verify_1 (Passed expected)', '\nThe Actual value is equal to the Expected value.',     actual_value, expected_value,               1],

            # Test that the verify() function indicates Failed
            # when the actual value is less than the expected value.
            [FAILED, 'Test Verify_1 (Failed expected)', '\nThe Actual value is less than the Expected value.',    actual_value, (expected_value + tolerance), 2],

            # Test that the verify() function indicates Failed
            # when the actual value is greater then the expected value.
            [FAILED, 'Test Verify_1 (Failed expected)', '\nThe Actual value is greater than the Expected value.', actual_value, (expected_value - tolerance), 3]
        ]

        for exp_result, log_msg, msg, act_val, exp_val, test_num in test_cases_table:
            logging.info(log_msg)
            assert_method = self.assertTrue if exp_result == PASSED else self.assertFalse
            assert_method(self.th.verify(act_val, exp_val, msg, test_num), f'{exp_result} expected')
            self.assertTrue(th_verify_log(log_msg, exp_result, act_val, exp_val, msg=msg, test_num=test_num), f'Exactly one record match expected')

    # @[Verify_1_TCASE_2]
    # @{Verify_1}
    def test_verify_1_TCASE_2(self):
        logging.info('\n\nTesting Verify_1 anchor - integer/boolean parameters\n')
        actual_value = 50
        expected_value = 50
        tolerance = 1

        test_cases_table = [
            # Test that the verify() function indicates Passed
            # when the actual value is equal to expected value.
            [PASSED, 'Test Verify_1 (Passed expected)', '\nThe Actual value is equal to the Expected value.',     actual_value, expected_value,               1],

            # Test that the verify() function indicates Failed
            # when the actual value is less than the expected value.
            [FAILED, 'Test Verify_1 (Failed expected)', '\nThe Actual value is less than the Expected value.',    actual_value, (expected_value + tolerance), 2],

            # Test that the verify() function indicates Failed
            # when the actual value is greater then the expected value.
            [FAILED, 'Test Verify_1 (Failed expected)', '\nThe Actual value is greater than the Expected value.', actual_value, (expected_value - tolerance), 3]
        ]

        for exp_result, log_msg, msg, act_val, exp_val, test_num in test_cases_table:
            logging.info(log_msg)
            assert_method = self.assertTrue if exp_result == PASSED else self.assertFalse
            assert_method(self.th.verify(act_val, exp_val, msg, test_num), f'{exp_result} expected')
            self.assertTrue(th_verify_log(log_msg, exp_result, act_val, exp_val, msg=msg, test_num=test_num), f'Exactly one record match expected')

    # @[Verify_1_TCASE_3]
    # @{Verify_1}
    def test_verify_1_TCASE_3(self):
        logging.info('\n\nTesting Verify_1 anchor - string parameters\n')
        actual_string = 'Test String'
        expected_string = 'Test String'

        test_cases_table = [
            # Test that the verify() function indicates Passed
            # when the actual string is equal to expected string.
            [PASSED, 'Test Verify_1 (Passed expected)', '\nThe Actual string is equal to the Expected string.',   actual_string, expected_string, 1],

            # Test that the verify() function indicates Failed
            # when the actual string and the expected strings are same,
            # but differ in case.
            [FAILED, 'Test Verify_1 (Failed expected)', '\nThe Actual string and the Expected string are same,\n'
                                                        'but differ in case.',                                    actual_string, 'test string',   2],

            # Test that the verify() function indicates Failed
            # when the actual string and the expected string are different.
            [FAILED, 'Test Verify_1 (Failed expected)', '\nThe Actual string and Expected string are different.', actual_string, 'abcdf',         3]
        ]

        for exp_result, log_msg, msg, act_val, exp_val, test_num in test_cases_table:
            logging.info(log_msg)
            assert_method = self.assertTrue if exp_result == PASSED else self.assertFalse
            assert_method(self.th.verify(act_val, exp_val, msg, test_num), f'{exp_result} expected')
            self.assertTrue(th_verify_log(log_msg, exp_result, act_val, exp_val, msg=msg, test_num=test_num), f'Exactly one record match expected')

    # @[Verify_1_TCASE_4]
    # @{Verify_1}
    def test_verify_1_TCASE_4(self):
        logging.info('\n\nTesting Verify_1 anchor - list parameters\n')
        actual_list = list(['abc', 3, 1.0, True])
        expected_list = list(['abc', 3, 1.0, True])

        test_cases_table = [
            # Test that the verify() function indicates Passed
            # when the actual list is equal to the expected list.
            [PASSED, 'Test Verify_1 (Passed expected)', '\nThe Actual list is equal to the Expected list.',    actual_list,                 expected_list, 1],

            # Test that the verify() function indicates Failed
            # when the actual list has different order of the items.
            [FAILED, 'Test Verify_1 (Failed expected)', '\nThe Actual list has different order of the items.', list([3, 'abc', True, 1.0]), expected_list, 2],

            # Test that the verify() function indicates Failed
            # when the actual list has different value of one item.
            [FAILED, 'Test Verify_1 (Failed expected)', '\nThe Actual list has different value of one item.',  list(['abc', 3, 1.1, True]), expected_list, 3],

            # Test that the verify() function indicates Failed
            # when the actual list is subset of the expected list.
            [FAILED, 'Test Verify_1 (Failed expected)', '\nThe Actual list is subset of the Expected list.',   actual_list[:-1],            expected_list, 4],

            # Test that the verify() function indicates Failed
            # when the actual list and expected list are different.
            [FAILED, 'Test Verify_1 (Failed expected)', '\nThe Actual list and Expected list are different.',  list(['True', 'False']),     expected_list, 5]
        ]

        for exp_result, log_msg, msg, act_val, exp_val, test_num in test_cases_table:
            logging.info(log_msg)
            assert_method = self.assertTrue if exp_result == PASSED else self.assertFalse
            assert_method(self.th.verify(act_val, exp_val, msg, test_num), f'{exp_result} expected')
            self.assertTrue(th_verify_log(log_msg, exp_result, act_val, exp_val, msg=msg, test_num=test_num), f'Exactly one record match expected')

    # @[Verify_1_TCASE_5]
    # @{Verify_1}
    def test_verify_1_TCASE_5(self):
        logging.info('\n\nTesting Verify_1 anchor - on_fail/test_num parameters\n')

        actual_value = 1
        expected_value = 1
        # on_fail_msg = 'Verify_1 On Fail method called.'

        test_cases_table = [
            # Test that the verify() function indicates Passed and omits
            # the test number, when the test number is not set (or equals to 0)
            # and the actual value is equal to the expected value.
            [PASSED, 'Test Verify_1 (Passed expected)', '\nThe test_num parameter is not set and the Actual\n'
                                                        'value is equal to the Expected value.',              actual_value,       expected_value, 0, None],

            # Test that the verify() function indicates Failed and omits
            # the test number, when the test number is not set (or equals to 0)
            # and the actual value does not equal to the expected value.
            [FAILED, 'Test Verify_1 (Failed expected)', '\nThe test_num parameter is not set and the Actual\n'
                                                        'value does not equal to the expected value.',        (actual_value + 1), expected_value, 0, None],

            # Test that the verify() function indicates Passed and does not
            # trigger on_fail() method, when on_fail method is set
            # and the actual value is equal to the expected value.
            [PASSED, 'Test Verify_1 (Passed expected)', '\nThe on_fail parameter is set and the Actual\n'
                                                        'value is equal to the Expected value.',              actual_value,       expected_value, 3, on_fail_function],

            # Test that the verify() function indicates Failed and does
            # trigger on_fail() method, when on_fail method is set
            # and the actual value is different than the expected value.
            [FAILED, 'Test Verify_1 (Failed expected)', '\nThe on_fail parameter is set and the Actual\n'
                                                        'value is different than the Expected value.',        (actual_value + 1), expected_value, 4, on_fail_function]
        ]

        for exp_result, log_msg, msg, act_val, exp_val, test_num, on_fail in test_cases_table:
            logging.info(log_msg)
            assert_method = self.assertTrue if exp_result == PASSED else self.assertFalse
            assert_method(self.th.verify(act_val, exp_val, msg, test_num, on_fail=on_fail), f'{exp_result} expected')
            self.assertTrue(th_verify_log(log_msg, exp_result, act_val, exp_val, msg=msg, test_num=test_num, on_fail=on_fail), f'Exactly one record match expected')

    # @[VerifyNE_1_TCASE_1]
    # @{VerifyNE_1}
    def test_verify_ne_1_TCASE_1(self):
        logging.info('\n\nTesting VerifyNE_1 anchor - floating point parameters\n')
        actual_value = 50.4567
        expected_value = 50.4567
        tolerance = 0.0001

        test_cases_table = [
            # Test that the verify_ne() function indicates Failed
            # when the actual value is equal to expected value.
            [FAILED, 'Test VerifyNE_1 (Failed expected)', '\nThe Actual value is equal to Expected value.',         actual_value, expected_value,               1],

            # Test that the verify_ne() function indicates Passed
            # when the actual value is less than the expected value.
            [PASSED, 'Test VerifyNE_1 (Passed expected)', '\nThe Actual value is less than the Expected value.',    actual_value, (expected_value + tolerance), 2],

            # Test that the verify_ne() function indicates Passed
            # when the actual value is greater then the expected value.
            [PASSED, 'Test VerifyNE_1 (Passed expected)', '\nThe Actual value is greater than the Expected value.', actual_value, (expected_value - tolerance), 3]
        ]

        for exp_result, log_msg, msg, act_val, exp_val, test_num in test_cases_table:
            logging.info(log_msg)
            assert_method = self.assertTrue if exp_result == PASSED else self.assertFalse
            assert_method(self.th.verify_ne(act_val, exp_val, msg, test_num), f'{exp_result} expected')
            self.assertTrue(th_verify_log(log_msg, exp_result, act_val, exp_val, msg=msg, test_num=test_num), f'Exactly one record match expected')

    # @[VerifyNE_1_TCASE_2]
    # @{VerifyNE_1}
    def test_verify_ne_1_TCASE_2(self):
        logging.info('\n\nTesting VerifyNE_1 anchor - integer/boolean parameters\n')
        actual_value = 50
        expected_value = 50
        tolerance = 1

        test_cases_table = [
            # Test that the verify_ne() function indicates Failed
            # when the actual value is equal to expected value.
            [FAILED, 'Test VerifyNE_1 (Failed expected)', '\nThe Actual value is equal to Expected value.',         actual_value, expected_value,               1],

            # Test that the verify_ne() function indicates Passed
            # when the actual value is less than the expected value.
            [PASSED, 'Test VerifyNE_1 (Passed expected)', '\nThe Actual value is less than the Expected value.',    actual_value, (expected_value + tolerance), 2],

            # Test that the verify_ne() function indicates Passed
            # when the actual value is greater then the expected value.
            [PASSED, 'Test VerifyNE_1 (Passed expected)', '\nThe Actual value is greater than the Expected value.', actual_value, (expected_value - tolerance), 3]
        ]

        for exp_result, log_msg, msg, act_val, exp_val, test_num in test_cases_table:
            logging.info(log_msg)
            assert_method = self.assertTrue if exp_result == PASSED else self.assertFalse
            assert_method(self.th.verify_ne(act_val, exp_val, msg, test_num), f'{exp_result} expected')
            self.assertTrue(th_verify_log(log_msg, exp_result, act_val, exp_val, msg=msg, test_num=test_num), f'Exactly one record match expected')

    # @[VerifyNE_1_TCASE_3]
    # @{VerifyNE_1}
    def test_verify_ne_1_TCASE_3(self):
        logging.info('\n\nTesting VerifyNE_1 anchor - string parameters\n')
        actual_string = 'Test String'
        expected_string = 'Test String'

        test_cases_table = [
            # Test that the verify_ne() function indicates Failed
            # when the actual string is equal to expected string.
            [FAILED, 'Test VerifyNE_1 (Failed expected)', '\nThe Actual string is equal to Expected string.',        actual_string, expected_string,         1],

            # Test that the verify_ne() function indicates Passed
            # when the actual string and the expected strings are same,
            # but differ in case.
            [PASSED, 'Test VerifyNE_1 (Passed expected)', '\nThe Actual string and the Expected strings are same,\n'
                                                          'but differ in case.',                                     actual_string, expected_string.lower(), 2],

            # Test that the verify_ne() function indicates Passed
            # when the actual string and the expected string are different.
            [PASSED, 'Test VerifyNE_1 (Passed expected)', '\nThe Actual string and Expected string are different.',  actual_string, 'abcd',                  3]
        ]

        for exp_result, log_msg, msg, act_val, exp_val, test_num in test_cases_table:
            logging.info(log_msg)
            assert_method = self.assertTrue if exp_result == PASSED else self.assertFalse
            assert_method(self.th.verify_ne(act_val, exp_val, msg, test_num), f'{exp_result} expected')
            self.assertTrue(th_verify_log(log_msg, exp_result, act_val, exp_val, msg=msg, test_num=test_num), f'Exactly one record match expected')

    # @[VerifyNE_1_TCASE_4]
    # @{VerifyNE_1}
    def test_verify_ne_1_TCASE_4(self):
        logging.info('\n\nTesting VerifyNE_1 anchor - list parameters\n')
        actual_list = list(['abc', 3, 1.0, True])
        expected_list = list(['abc', 3, 1.0, True])

        test_cases_table = [
            # Test that the verify_ne() function indicates Failed
            # when the actual list is equal to the expected list.
            [FAILED, 'Test VerifyNE_1 (Failed expected)', '\nThe Actual list is equal to Expected list.',        actual_list,                 expected_list,      1],

            # Test that the verify_ne() function indicates Passed
            # when the actual list has different order of the items.
            [PASSED, 'Test VerifyNE_1 (Passed expected)', '\nThe Actual list has different order of the items',  list([3, 'abc', True, 1.0]), expected_list,      2],

            # Test that the verify_ne() function indicates Passed
            # when the actual list has different value of one item.
            [PASSED, 'Test VerifyNE_1 (Passed expected)', '\nThe Actual list has different value of one item\n'
                                                         'compared to Expected list.',                           list(['abc', 3, 1.1, True]), expected_list,      3],

            # Test that the verify_ne() function indicates Passed
            # when the actual list is subset of the expected list.
            [PASSED, 'Test VerifyNE_1 (Passed expected)', '\nThe Actual list has different length compared to\n'
                                                          'Expected list.',                                      actual_list[:-1],            expected_list,      4],

            # Test that the verify_ne() function indicates Passed
            # when the actual list and expected list are different.
            [PASSED, 'Test VerifyNE_1 (Passed expected)', '\nThe Actual list and Expected list are different.',  list(['True', 'False']),     expected_list,      5]
        ]

        for exp_result, log_msg, msg, act_val, exp_val, test_num in test_cases_table:
            logging.info(log_msg)
            assert_method = self.assertTrue if exp_result == PASSED else self.assertFalse
            assert_method(self.th.verify_ne(act_val, exp_val, msg, test_num), f'{exp_result} expected')
            self.assertTrue(th_verify_log(log_msg, exp_result, act_val, exp_val, msg=msg, test_num=test_num), f'Exactly one record match expected')

    # @[VerifyNE_1_TCASE_5]
    # @{VerifyNE_1}
    def test_verify_ne_1_TCASE_5(self):
        logging.info('\n\nTesting VerifyNE_1 anchor - on_fail/test_num parameters\n')
        actual_value = 1
        expected_value = 1

        test_cases_table = [
            # Test that the verify_ne() function indicates Failed and omits
            # the test number, when the test number is not set (or equals to 0)
            # and the actual value is equal to the expected value.
            [FAILED, 'Test VerifyNE_1 (Failed expected)', '\nThe test_num parameter is not set and the Actual\n'
                                                          'value is equal to the Expected value.',              actual_value,       expected_value, 0, None],

            # Test that the verify_ne() function indicates Passed and omits
            # the test number, when the test number is not set (or equals to 0)
            # and the actual value does not equal to the expected value.
            [PASSED, 'Test VerifyNE_1 (Passed expected)', '\nThe test_num parameter is not set and the Actual\n'
                                                          'value does not equal to the expected value.',        (actual_value - 1), expected_value, 0, None],

            # Test that the verify_ne() function indicates Failed and does
            # trigger on_fail() method, when on_fail method is set
            # and the actual value is equal to the expected value.
            [FAILED, 'Test VerifyNE_1 (Failed expected)', '\nThe on_fail parameter is set and the Actual\n'
                                                          'value is equal to the Expected value.',              actual_value,       expected_value, 3, on_fail_function],

            # Test that the verify_ne() function indicates Passed and does not
            # trigger on_fail() method, when on_fail method is set
            # and the actual value is different than the expected value.
            [PASSED, 'Test VerifyNE_1 (Passed expected)', '\nThe on_fail parameter is set and the Actual\n'
                                                          'value is different than the Expected value.',        (actual_value - 1), expected_value, 4, on_fail_function]
        ]

        for exp_result, log_msg, msg, act_val, exp_val, test_num, on_fail in test_cases_table:
            logging.info(log_msg)
            assert_method = self.assertTrue if exp_result == PASSED else self.assertFalse
            assert_method(self.th.verify_ne(act_val, exp_val, msg, test_num, on_fail=on_fail), f'{exp_result} expected')
            self.assertTrue(th_verify_log(log_msg, exp_result, act_val, exp_val, msg=msg, test_num=test_num, on_fail=on_fail), f'Exactly one record match expected')

    # @[VerifyTol_1_TCASE_1]
    # @{VerifyTol_1}
    def test_verify_tol_1_TCASE_1(self):
        logging.info('\n\nTesting VerifyTol_1 anchor - floating point parameters\n')
        actual_value = 50.4567
        expected_value = 50.4567
        tol = 0.0001

        test_cases_table = [
            # Test that the verify_tol() function indicates Passed
            # when the actual value is just within tolerance above the expected value.
            [PASSED, 'Test VerifyTol_1 (Passed expected)', '\nThe Actual value is just within tolerance above the Expected value.',
             (actual_value + tol - 0.5 * tol), expected_value, tol, 1],

            # Test that the verify_tol() function indicates Passed
            # when the actual value is just within tolerance below the expected value.
            [PASSED, 'Test VerifyTol_1 (Passed expected)', '\nThe Actual value is just within tolerance below the Expected value.',
             (actual_value - tol + 0.5 * tol), expected_value, tol, 2],

            # Test that the verify_tol() function indicates Passed
            # when the actual value is outside the tolerance above the expected value.
            [FAILED, 'Test VerifyTol_1 (Failed expected)', '\nThe Actual value is outside tolerance above the Expected value.',
             (actual_value + tol + 0.5 * tol), expected_value, tol, 3],

            # Test that the verify_tol() function indicates Passed
            # when the actual value is outside the tolerance below the expected value.
            [FAILED, 'Test VerifyTol_1 (Failed expected)', '\nThe Actual value is outside tolerance below the Expected value.',
             (actual_value - tol - 0.5 * tol), expected_value, tol, 4]
        ]

        for exp_result, log_msg, msg, act_val, exp_val, tol, test_num in test_cases_table:
            logging.info(log_msg)
            assert_method = self.assertTrue if exp_result == PASSED else self.assertFalse
            assert_method(self.th.verify_tol(act_val, exp_val, tol, msg, test_num), f'{exp_result} expected')
            self.assertTrue(th_verify_log(log_msg, exp_result, act_val, exp_val, tolerance=tol, msg=msg, test_num=test_num),
                            f'Exactly one record match expected')

    # @[VerifyTol_1_TCASE_2]
    # @{VerifyTol_1}
    def test_verify_tol_1_TCASE_2(self):
        logging.info('\n\nTesting VerifyTol_1 anchor - integer/boolean parameters\n')
        actual_value = 50
        expected_value = 50
        tol = 2

        test_cases_table = [
            # Test that the verify_tol() function indicates Passed
            # when the actual value is just within tolerance above the expected value.
            [PASSED, 'Test VerifyTol_1 (Passed expected)', '\nThe Actual value is just within tolerance above the Expected value.',
             (actual_value + tol - 1), expected_value, tol, 1],

            # Test that the verify_tol() function indicates Passed
            # when the actual value is just within tolerance below the expected value.
            [PASSED, 'Test VerifyTol_1 (Passed expected)', '\nThe Actual value is just within tolerance below the Expected value.',
             (actual_value - tol + 1), expected_value, tol, 2],

            # Test that the verify_tol() function indicates Failed
            # when the actual value is outside the tolerance above the expected value.
            [FAILED, 'Test VerifyTol_1 (Failed expected)', '\nThe Actual value is outside tolerance above the Expected value.',
             (actual_value + tol + 1), expected_value, tol, 3],

            # Test that the verify_tol() function indicates Failed
            # when the actual value is outside the tolerance below the expected value.
            [FAILED, 'Test VerifyTol_1 (Failed expected)', '\nThe Actual value is outside tolerance below the Expected value.',
             (actual_value - tol - 1), expected_value, tol, 4]
        ]

        for exp_result, log_msg, msg, act_val, exp_val, tol, test_num in test_cases_table:
            logging.info(log_msg)
            assert_method = self.assertTrue if exp_result == PASSED else self.assertFalse
            assert_method(self.th.verify_tol(act_val, exp_val, tol, msg, test_num), f'{exp_result} expected')
            self.assertTrue(th_verify_log(log_msg, exp_result, act_val, exp_val, tolerance=tol, msg=msg, test_num=test_num),
                            f'Exactly one record match expected')

    # @[VerifyTol_1_TCASE_3]
    # @{VerifyTol_1}
    def test_verify_tol_1_TCASE_3(self):
        logging.info('\n\nTesting VerifyTol_1 anchor - test_num/on_fail parameters\n')
        actual_value = 1
        expected_value = 1
        tol = 1

        test_cases_table = [
            # Test that the verify_tol() function indicates Failed and omits
            # the test number, when the test number is not set (or equals to 0)
            # and the actual value is outside the tolerance below the expected value.
            [FAILED, 'Test VerifyTol_1 (Failed expected)', '\nThe test_num parameter is not set and the Actual\n'
                                                           'value is outside the tolerance below the Expected value.', (actual_value - 2), expected_value, tol, 0, None],

            # Test that the verify_tol() function indicates Passed and omits
            # the test number, when the test number is not set (or equals to 0)
            # and the actual value is within the tolerance below the expected value.
            [PASSED, 'Test VerifyTol_1 (Passed expected)', '\nThe test_num parameter is not set and the Actual\n'
                                                           'value is within the tolerance below the expected value.',  (actual_value - 1), expected_value, tol, 0, None],

            # Test that the verify_tol() function indicates Failed and does
            # trigger on_fail() method, when on_fail method is set
            # and the actual value is outside the tolerance below the expected value.
            [FAILED, 'Test VerifyTol_1 (Failed expected)', '\nThe on_fail parameter is set and the Actual\n'
                                                           'value is outside the tolerance below the Expected value.', (actual_value - 2), expected_value, tol, 3, on_fail_function],

            # Test that the verify_tol() function indicates Passed and does not
            # trigger on_fail() method, when on_fail method is set
            # and the actual value is within the tolerance below the expected value.
            [PASSED, 'Test VerifyTol_1 (Passed expected)', '\nThe on_fail parameter is set and the Actual\n'
                                                           'value is within the tolerance below the Expected value.',  (actual_value - 1), expected_value, tol, 4, on_fail_function]
        ]

        for exp_result, log_msg, msg, act_val, exp_val, tol, test_num, on_fail in test_cases_table:
            logging.info(log_msg)
            assert_method = self.assertTrue if exp_result == PASSED else self.assertFalse
            assert_method(self.th.verify_tol(act_val, exp_val, tol, msg, test_num, on_fail=on_fail), f'{exp_result} expected')
            self.assertTrue(th_verify_log(log_msg, exp_result, act_val, exp_val, tolerance=tol, msg=msg, test_num=test_num, on_fail=on_fail),
                            f'Exactly one record match expected')

    # @[VerifyLE_1_TCASE_1]
    # @{VerifyLE_1}
    def test_verify_le_1_TCASE_1(self):
        logging.info('\n\nTesting VerifyLE_1 anchor - floating point parameters\n')
        actual_value = 50.4567
        expected_value = 50.4567
        tolerance = 0.0001

        test_cases_table = [
            # Test that the verify_le() function indicates Passed
            # when the actual value is less than the maximum value.
            [PASSED, 'Test VerifyLE_1 (Passed expected)', '\nThe Actual value is less than the maximum value.',    actual_value, (expected_value + tolerance), 1],

            # Test that the verify_le() function indicates Passed
            # when the actual value is equal to the maximum value.
            [PASSED, 'Test VerifyLE_1 (Passed expected)', '\nThe Actual value is equal to the maximum value.',     actual_value, expected_value,               2],

            # Test that the verify_le() function indicates Failed
            # when the actual value is greater than the maximum value.
            [FAILED, 'Test VerifyLE_1 (Failed expected)', '\nThe Actual value is greater than the maximum value.', actual_value, (expected_value - tolerance), 3]
        ]

        for exp_result, log_msg, msg, act_val, exp_val, test_num in test_cases_table:
            logging.info(log_msg)
            assert_method = self.assertTrue if exp_result == PASSED else self.assertFalse
            assert_method(self.th.verify_le(act_val, exp_val, msg, test_num), f'{exp_result} expected')
            self.assertTrue(th_verify_log(log_msg, exp_result, act_val, exp_val, msg=msg, test_num=test_num),
                            f'Exactly one record match expected')

    # @[VerifyLE_1_TCASE_2]
    # @{VerifyLE_1}
    def test_verify_le_1_TCASE_2(self):
        logging.info('\n\nTesting VerifyLE_1 anchor - integer parameters\n')
        actual_value = 50
        expected_value = 50
        tolerance = 1

        test_cases_table = [
            # Test that the verify_le() function indicates Passed
            # when the actual value is less than the maximum value.
            [PASSED, 'Test VerifyLE_1 (Passed expected)', '\nThe Actual value is less than the maximum value.',    actual_value, (expected_value + tolerance), 1],

            # Test that the verify_le() function indicates Passed
            # when the actual value is equal to the maximum value.
            [PASSED, 'Test VerifyLE_1 (Passed expected)', '\nThe Actual value is equal to the maximum value.',     actual_value, expected_value,               2],

            # Test that the verify_le() function indicates Failed
            # when the actual value is greater than the maximum value.
            [FAILED, 'Test VerifyLE_1 (Failed expected)', '\nThe Actual value is greater than the maximum value.', actual_value, (expected_value - tolerance), 3]
        ]

        for exp_result, log_msg, msg, act_val, exp_val, test_num in test_cases_table:
            logging.info(log_msg)
            assert_method = self.assertTrue if exp_result == PASSED else self.assertFalse
            assert_method(self.th.verify_le(act_val, exp_val, msg, test_num), f'{exp_result} expected')
            self.assertTrue(th_verify_log(log_msg, exp_result, act_val, exp_val, msg=msg, test_num=test_num),
                            f'Exactly one record match expected')

    # @[VerifyLE_1_TCASE_3]
    # @{VerifyLE_1}
    def test_verify_le_1_TCASE_3(self):
        logging.info('\n\nTesting VerifyLE_1 anchor - test_num/on_fail parameters\n')
        actual_value = 2
        expected_value = 2

        test_cases_table = [
            # Test that the verify_le() function indicates Failed and omits
            # the test number, when the test number is not set (or equals to 0)
            # and the actual value is greater than the maximum value.
            [FAILED, 'Test VerifyLE_1 (Failed expected)', '\nThe test_num parameter is not set and the Actual\n'
                                                          'value is greater than the maximum value.',            (actual_value + 1), expected_value, 0, None],

            # Test that the verify_le() function indicates Passed and omits
            # the test number, when the test number is not set (or equals to 0)
            # and the actual value is less than the maximum value.
            [PASSED, 'Test VerifyLE_1 (Passed expected)', '\nThe test_num parameter is not set and the Actual\n'
                                                          'value is less than the maximum value.',               (actual_value - 1), expected_value, 0, None],

            # Test that the verify_le() function indicates Failed and does
            # trigger on_fail() method, when on_fail method is set
            # and the actual value is greater than the maximum value.
            [FAILED, 'Test VerifyLE_1 (Failed expected)', '\nThe on_fail parameter is set and the Actual\n'
                                                          'value is greater than the maximum value.',            (actual_value + 1), expected_value, 3, on_fail_function],

            # Test that the verify_le() function indicates Passed and does not
            # trigger on_fail() method, when on_fail method is set
            # and the actual value is less than the maximum value.
            [PASSED, 'Test VerifyLE_1 (Passed expected)', '\nThe on_fail parameter is set and the Actual\n'
                                                          'value is less than the maximum value.',               (actual_value - 1), expected_value, 4, on_fail_function]
        ]

        for exp_result, log_msg, msg, act_val, exp_val, test_num, on_fail in test_cases_table:
            logging.info(log_msg)
            assert_method = self.assertTrue if exp_result == PASSED else self.assertFalse
            assert_method(self.th.verify_le(act_val, exp_val, msg, test_num, on_fail=on_fail), f'{exp_result} expected')
            self.assertTrue(th_verify_log(log_msg, exp_result, act_val, exp_val, msg=msg, test_num=test_num, on_fail=on_fail),
                            f'Exactly one record match expected')

    # @[VerifyGE_1_TCASE_1]
    # @{VerifyGE_1}
    def test_verify_ge_1_TCASE_1(self):
        logging.info('\n\nTesting VerifyGE_1 anchor - floating point parameters\n')
        actual_value = 50.4567
        expected_value = 50.4567
        tolerance = 0.0001

        test_cases_table = [
            # Test that the verify_ge() function indicates Failed
            # when the actual value is less than the maximum value.
            [FAILED, 'Test VerifyGE_1 (Failed expected)', '\nThe Actual value is less than the maximum value.',    actual_value, (expected_value + tolerance), 1],

            # Test that the verify_ge() function indicates Passed
            # when the actual value is equal to the maximum value.
            [PASSED, 'Test VerifyGE_1 (Passed expected)', '\nThe Actual value is equal to the maximum value.',     actual_value, expected_value,               2],

            # Test that the verify_ge() function indicates Passed
            # when the actual value is greater than the maximum value.
            [PASSED, 'Test VerifyGE_1 (Passed expected)', '\nThe Actual value is greater than the maximum value.', actual_value, (expected_value - tolerance), 3]
        ]

        for exp_result, log_msg, msg, act_val, exp_val, test_num in test_cases_table:
            logging.info(log_msg)
            assert_method = self.assertTrue if exp_result == PASSED else self.assertFalse
            assert_method(self.th.verify_ge(act_val, exp_val, msg, test_num), f'{exp_result} expected')
            self.assertTrue(th_verify_log(log_msg, exp_result, act_val, exp_val, msg=msg, test_num=test_num),
                            f'Exactly one record match expected')

    # @[VerifyGE_1_TCASE_2]
    # @{VerifyGE_1}
    def test_verify_ge_1_TCASE_2(self):
        logging.info('\n\nTesting VerifyGE_1 anchor - integer parameters\n')
        actual_value = 50
        expected_value = 50
        tolerance = 1

        test_cases_table = [
            # Test that the verify_ge() function indicates Failed
            # when the actual value is less than the maximum value.
            [FAILED, 'Test VerifyGE_1 (Failed expected)', '\nThe Actual value is less than the maximum value.',    actual_value, (expected_value + tolerance), 1],

            # Test that the verify_ge() function indicates Passed
            # when the actual value is equal to the maximum value.
            [PASSED, 'Test VerifyGE_1 (Passed expected)', '\nThe Actual value is equal to the maximum value.',     actual_value, expected_value,               2],

            # Test that the verify_ge() function indicates Passed
            # when the actual value is greater than the maximum value.
            [PASSED, 'Test VerifyGE_1 (Passed expected)', '\nThe Actual value is greater than the maximum value.', actual_value, (expected_value - tolerance), 3]
        ]

        for exp_result, log_msg, msg, act_val, exp_val, test_num in test_cases_table:
            logging.info(log_msg)
            assert_method = self.assertTrue if exp_result == PASSED else self.assertFalse
            assert_method(self.th.verify_ge(act_val, exp_val, msg, test_num), f'{exp_result} expected')
            self.assertTrue(th_verify_log(log_msg, exp_result, act_val, exp_val, msg=msg, test_num=test_num),
                            f'Exactly one record match expected')

    # @[VerifyGE_1_TCASE_3]
    # @{VerifyGE_1}
    def test_verify_ge_1_TCASE_3(self):
        logging.info('\n\nTesting VerifyGE_1 anchor - test_num/on_fail parameters\n')
        actual_value = 2
        expected_value = 2

        test_cases_table = [
            # Test that the verify_ge() function indicates Failed and omits
            # the test number, when the test number is not set (or equals to 0)
            # and the actual value is less than the maximum value.
            [FAILED, 'Test VerifyGE_1 (Failed expected)', '\nThe test_num parameter is not set and the Actual\n'
                                                          'value is less than the maximum value.',              (actual_value - 1), expected_value, 0, None],

            # Test that the verify_ge() function indicates Passed and omits
            # the test number, when the test number is not set (or equals to 0)
            # and the actual value is greater than the maximum value.
            [PASSED, 'Test VerifyGE_1 (Passed expected)', '\nThe test_num parameter is not set and the Actual\n'
                                                          'value is greater than the maximum value.',           (actual_value + 1), expected_value, 0, None],

            # Test that the verify_ge() function indicates Failed and does
            # trigger on_fail() method, when on_fail method is set
            # and the actual value is less than the maximum value.
            [FAILED, 'Test VerifyGE_1 (Failed expected)', '\nThe on_fail parameter is set and the Actual\n'
                                                          'value is less than the maximum value.',              (actual_value - 1), expected_value, 3, on_fail_function],

            # Test that the verify_ge() function indicates Passed and does not
            # trigger on_fail() method, when on_fail method is set
            # and the actual value is greater than the maximum value.
            [PASSED, 'Test VerifyGE_1 (Passed expected)', '\nThe on_fail parameter is set and the Actual\n'
                                                          'value is greater than the maximum value.',           (actual_value + 1), expected_value, 4, on_fail_function]
        ]

        for exp_result, log_msg, msg, act_val, exp_val, test_num, on_fail in test_cases_table:
            logging.info(log_msg)
            assert_method = self.assertTrue if exp_result == PASSED else self.assertFalse
            assert_method(self.th.verify_ge(act_val, exp_val, msg, test_num, on_fail=on_fail), f'{exp_result} expected')
            self.assertTrue(th_verify_log(log_msg, exp_result, act_val, exp_val, msg=msg, test_num=test_num, on_fail=on_fail),
                            f'Exactly one record match expected')

    # @[VerifyLT_1_TCASE_1]
    # @{VerifyLT_1}
    def test_verify_lt_1_TCASE_1(self):
        logging.info('\n\nTesting VerifyLT_1 anchor - floating point parameters\n')
        actual_value = 50.4567
        expected_value = 50.4567
        tolerance = 0.0001

        test_cases_table = [
            # Test that the verify_lt() function indicates Passed
            # when the actual value is less than the maximum value.
            [PASSED, 'Test VerifyLT_1 (Passed expected)', '\nThe Actual value is less than the maximum value.',    actual_value, (expected_value + tolerance), 1],

            # Test that the verify_lt() function indicates Failed
            # when the actual value is equal to the maximum value.
            [FAILED, 'Test VerifyLT_1 (Failed expected)', '\nThe Actual value is equal to the maximum value.',     actual_value, expected_value,               2],

            # Test that the verify_lt() function indicates Failed
            # when the actual value is greater than the maximum value.
            [FAILED, 'Test VerifyLT_1 (Failed expected)', '\nThe Actual value is greater than the maximum value.', actual_value, (expected_value - tolerance), 3]
        ]

        for exp_result, log_msg, msg, act_val, exp_val, test_num in test_cases_table:
            logging.info(log_msg)
            assert_method = self.assertTrue if exp_result == PASSED else self.assertFalse
            assert_method(self.th.verify_lt(act_val, exp_val, msg, test_num), f'{exp_result} expected')
            self.assertTrue(th_verify_log(log_msg, exp_result, act_val, exp_val, msg=msg, test_num=test_num),
                            f'Exactly one record match expected')

    # @[VerifyLT_1_TCASE_2]
    # @{VerifyLT_1}
    def test_verify_lt_1_TCASE_2(self):
        logging.info('\n\nTesting VerifyLT_1 anchor - integer parameters\n')
        actual_value = 50
        expected_value = 50
        tolerance = 1

        test_cases_table = [
            # Test that the verify_lt() function indicates Passed
            # when the actual value is less than the maximum value.
            [PASSED, 'Test VerifyLT_1 (Passed expected)', '\nThe Actual value is less than the maximum value.',    actual_value, (expected_value + tolerance), 1],

            # Test that the verify_lt() function indicates Failed
            # when the actual value is equal to the maximum value.
            [FAILED, 'Test VerifyLT_1 (Failed expected)', '\nThe Actual value is equal to the maximum value.',     actual_value, expected_value,               2],

            # Test that the verify_lt() function indicates Failed
            # when the actual value is greater than the maximum value.
            [FAILED, 'Test VerifyLT_1 (Failed expected)', '\nThe Actual value is greater than the maximum value.', actual_value, (expected_value - tolerance), 3]
        ]

        for exp_result, log_msg, msg, act_val, exp_val, test_num in test_cases_table:
            logging.info(log_msg)
            assert_method = self.assertTrue if exp_result == PASSED else self.assertFalse
            assert_method(self.th.verify_lt(act_val, exp_val, msg, test_num), f'{exp_result} expected')
            self.assertTrue(th_verify_log(log_msg, exp_result, act_val, exp_val, msg=msg, test_num=test_num),
                            f'Exactly one record match expected')

    # @[VerifyLT_1_TCASE_3]
    # @{VerifyLT_1}
    def test_verify_lt_1_TCASE_3(self):
        logging.info('\n\nTesting VerifyLT_1 anchor - test_num/on_fail parameters\n')
        actual_value = 1
        expected_value = 2

        test_cases_table = [
            # Test that the verify_lt() function indicates Failed and omits
            # the test number, when the test number is not set (or equals to 0)
            # and the actual value is greater than the maximum value.
            [FAILED, 'Test VerifyLT_1 (Failed expected)', '\nThe test_num parameter is not set and the Actual\n'
                                                          'value is greater than the maximum value.',           (actual_value + 1), expected_value, 0, None],

            # Test that the verify_lt() function indicates Passed and omits
            # the test number, when the test number is not set (or equals to 0)
            # and the actual value is less than the maximum value.
            [PASSED, 'Test VerifyLT_1 (Passed expected)', '\nThe test_num parameter is not set and the Actual\n'
                                                          'value is less than the maximum value.',              (actual_value - 1), expected_value, 0, None],

            # Test that the verify_lt() function indicates Failed and does
            # trigger on_fail() method, when on_fail method is set
            # and the actual value is greater than the maximum value.
            [FAILED, 'Test VerifyLT_1 (Failed expected)', '\nThe on_fail parameter is set and the Actual\n'
                                                          'value is greater than the maximum value.',           (actual_value + 1), expected_value, 3, on_fail_function],

            # Test that the verify_lt() function indicates Passed and does not
            # trigger on_fail() method, when on_fail method is set
            # and the actual value is less than the maximum value.
            [PASSED, 'Test VerifyLT_1 (Passed expected)', '\nThe on_fail parameter is set and the Actual\n'
                                                          'value is less than the maximum value.',              (actual_value - 1), expected_value, 4, on_fail_function]
        ]

        for exp_result, log_msg, msg, act_val, exp_val, test_num, on_fail in test_cases_table:
            logging.info(log_msg)
            assert_method = self.assertTrue if exp_result == PASSED else self.assertFalse
            assert_method(self.th.verify_lt(act_val, exp_val, msg, test_num, on_fail=on_fail), f'{exp_result} expected')
            self.assertTrue(th_verify_log(log_msg, exp_result, act_val, exp_val, msg=msg, test_num=test_num, on_fail=on_fail),
                            f'Exactly one record match expected')

    # @[VerifyGT_1_TCASE_1]
    # @{VerifyGT_1}
    def test_verify_gt_1_TCASE_1(self):
        logging.info('\n\nTesting VerifyGT_1 anchor - floating point parameters\n')
        actual_value = 50.4567
        expected_value = 50.4567
        tolerance = 0.0001

        test_cases_table = [
            # Test that the verify_gt() function indicates Failed
            # when the actual value is less than the maximum value.
            [FAILED, 'Test VerifyGT_1 (Failed expected)', '\nThe Actual value is less than the maximum value.',    actual_value, (expected_value + tolerance), 1],

            # Test that the verify_gt() function indicates Failed
            # when the actual value is equal to the maximum value.
            [FAILED, 'Test VerifyGT_1 (Failed expected)', '\nThe Actual value is equal to the maximum value.',     actual_value, expected_value,               2],

            # Test that the verify_gt() function indicates Passed
            # when the actual value is greater than the maximum value.
            [PASSED, 'Test VerifyGT_1 (Passed expected)', '\nThe Actual value is greater than the maximum value.', actual_value, (expected_value - tolerance), 3]
        ]

        for exp_result, log_msg, msg, act_val, exp_val, test_num in test_cases_table:
            logging.info(log_msg)
            assert_method = self.assertTrue if exp_result == PASSED else self.assertFalse
            assert_method(self.th.verify_gt(act_val, exp_val, msg, test_num), f'{exp_result} expected')
            self.assertTrue(th_verify_log(log_msg, exp_result, act_val, exp_val, msg=msg, test_num=test_num),
                            f'Exactly one record match expected')

    # @[VerifyGT_1_TCASE_2]
    # @{VerifyGT_1}
    def test_verify_gt_1_TCASE_2(self):
        logging.info('\n\nTesting VerifyGT_1 anchor - integer parameters\n')
        actual_value = 50
        expected_value = 50
        tolerance = 1

        test_cases_table = [
            # Test that the verify_gt() function indicates Failed
            # when the actual value is less than the maximum value.
            [FAILED, 'Test VerifyGT_1 (Failed expected)', '\nThe Actual value is less than the maximum value.',    actual_value, (expected_value + tolerance), 1],

            # Test that the verify_gt() function indicates Failed
            # when the actual value is equal to the maximum value.
            [FAILED, 'Test VerifyGT_1 (Failed expected)', '\nThe Actual value is equal to the maximum value.',     actual_value, expected_value,               2],

            # Test that the verify_gt() function indicates Passed
            # when the actual value is greater than the maximum value.
            [PASSED, 'Test VerifyGT_1 (Passed expected)', '\nThe Actual value is greater than the maximum value.', actual_value, (expected_value - tolerance), 3]
        ]

        for exp_result, log_msg, msg, act_val, exp_val, test_num in test_cases_table:
            logging.info(log_msg)
            assert_method = self.assertTrue if exp_result == PASSED else self.assertFalse
            assert_method(self.th.verify_gt(act_val, exp_val, msg, test_num), f'{exp_result} expected')
            self.assertTrue(th_verify_log(log_msg, exp_result, act_val, exp_val, msg=msg, test_num=test_num),
                            f'Exactly one record match expected')

    # @[VerifyGT_1_TCASE_3]
    # @{VerifyGT_1}
    def test_verify_gt_1_TCASE_3(self):
        logging.info('\n\nTesting VerifyGT_1 anchor - test_num/on_fail parameters\n')
        actual_value = 2
        expected_value = 1

        test_cases_table = [
            # Test that the verify_gt() function indicates Failed and omits
            # the test number, when the test number is not set (or equals to 0)
            # and the actual value is less than the maximum value.
            [FAILED, 'Test VerifyGT_1 (Failed expected)', '\nThe test_num parameter is not set and the Actual\n'
                                                          'value is less than the maximum value.',              (actual_value - 1), expected_value, 0, None],

            # Test that the verify_gt() function indicates Passed and omits
            # the test number, when the test number is not set (or equals to 0)
            # and the actual value is greater than the maximum value.
            [PASSED, 'Test VerifyGT_1 (Passed expected)', '\nThe test_num parameter is not set and the Actual\n'
                                                          'value is greater than the maximum value.',           (actual_value + 1), expected_value, 0, None],

            # Test that the verify_gt() function indicates Failed and does
            # trigger on_fail() method, when on_fail method is set
            # and the actual value is less than the maximum value.
            [FAILED, 'Test VerifyGT_1 (Failed expected)', '\nThe on_fail parameter is set and the Actual\n'
                                                          'value is less than the maximum value.',              (actual_value - 1), expected_value, 3, on_fail_function],

            # Test that the verify_gt() function indicates Passed and does not
            # trigger on_fail() method, when on_fail method is set
            # and the actual value is greater than the maximum value.
            [PASSED, 'Test VerifyGT_1 (Passed expected)', '\nThe on_fail parameter is set and the Actual\n'
                                                          'value is greater than the maximum value.',           (actual_value + 1), expected_value, 4, on_fail_function]
        ]

        for exp_result, log_msg, msg, act_val, exp_val, test_num, on_fail in test_cases_table:
            logging.info(log_msg)
            assert_method = self.assertTrue if exp_result == PASSED else self.assertFalse
            assert_method(self.th.verify_gt(act_val, exp_val, msg, test_num, on_fail=on_fail), f'{exp_result} expected')
            self.assertTrue(th_verify_log(log_msg, exp_result, act_val, exp_val, msg=msg, test_num=test_num, on_fail=on_fail),
                            f'Exactly one record match expected')

    # @[VerifyRange_1_TCASE_1]
    # @{VerifyRange_1}
    def test_verify_range_1_TCASE_1(self):
        logging.info('\n\nTesting VerifyRange_1 anchor - floating point parameters\n')
        actual_value = 50.4567
        expected_value = 50.4567
        tol = 0.0001

        test_cases_table = [
            # Test that the verify_range() function indicates Passed
            # when the actual value is greater than the min value and
            # is less than the max value.
            [PASSED, 'Test VerifyRange_1 (Passed expected)', '\nThe Actual value is greater than the min value \nand is less than the max value.',
             actual_value, (expected_value - tol),     (expected_value + tol),     1],

            # Test that the verify_range() function indicates Passed
            # when the actual value is equal to the min value and
            # is less than the max value.
            [PASSED, 'Test VerifyRange_1 (Passed expected)', '\nThe Actual value is equal to min value \nand is less than the max value.',
             actual_value, expected_value,             (expected_value + tol),     2],

            # Test that the verify_range() function indicates Passed
            # when the actual value is greater than the min value and
            # is equal to the max value.
            [PASSED, 'Test VerifyRange_1 (Passed expected)', '\nThe Actual value is greater than the min value \nand is equal to max value.',
             actual_value, (expected_value - tol),     expected_value,             3],

            # Test that the verify_range() function indicates Failed
            # when the actual value is less than the min value and
            # is also less than the max value.
            [FAILED, 'Test VerifyRange_1 (Failed expected)', '\nThe Actual value is less than the max_value and is \nalso less than the min_value',
             actual_value, (expected_value + tol),     (expected_value + 2 * tol), 4],

            # Test that the verify_range() function indicates Failed
            # when the actual value is greater than the min value and
            # is also greater than the max value.
            [FAILED, 'Test VerifyRange_1 (Failed expected)', '\nThe Actual value is greater than the min value \nand is also greater than the max value.',
             actual_value, (expected_value - 2 * tol), (expected_value - tol),     5]
        ]

        for exp_result, log_msg, msg, act_val, min_val, max_val, test_num in test_cases_table:
            logging.info(log_msg)
            assert_method = self.assertTrue if exp_result == PASSED else self.assertFalse
            assert_method(self.th.verify_range(act_val, min_val, max_val, msg, test_num), f'{exp_result} expected')
            self.assertTrue(th_verify_log(log_msg, exp_result, act_val, 0, rng=(min_val, max_val), msg=msg, test_num=test_num),
                            f'Exactly one record match expected')

    # @[VerifyRange_1_TCASE_2]
    # @{VerifyRange_1}
    def test_verify_range_1_TCASE_2(self):
        logging.info('\n\nTesting VerifyRange_1 anchor - integer parameters\n')
        actual_value = 50
        expected_value = 50
        tol = 5

        test_cases_table = [
            # Test that the verify_range() function indicates Passed
            # when the actual value is greater than the min value and
            # is less than the max value.
            [PASSED, 'Test VerifyRange_1 (Passed expected)', '\nThe Actual value is greater than the min value \nand is less than the max value.',
             actual_value, (expected_value - tol),     (expected_value + tol),     1],

            # Test that the verify_range() function indicates Passed
            # when the actual value is equal to the min value and
            # is less than the max value.
            [PASSED, 'Test VerifyRange_1 (Passed expected)', '\nThe Actual value is equal to min value \nand is less than the max value.',
             actual_value, expected_value,             (expected_value + tol),     2],

            # Test that the verify_range() function indicates Passed
            # when the actual value is greater than the min value and
            # is equal to the max value.
            [PASSED, 'Test VerifyRange_1 (Passed expected)', '\nThe Actual value is greater than the min value \nand is equal to max value.',
             actual_value, (expected_value - tol),     expected_value,             3],

            # Test that the verify_range() function indicates Failed
            # when the actual value is less than the min value and
            # is also less than the max value.
            [FAILED, 'Test VerifyRange_1 (Failed expected)', '\nThe Actual value is less than the max_value and is \nalso less than the min_value',
             actual_value, (expected_value + tol),     (expected_value + 2 * tol), 4],

            # Test that the verify_range() function indicates Failed
            # when the actual value is greater than the min value and
            # is also greater than the max value.
            [FAILED, 'Test VerifyRange_1 (Failed expected)', '\nThe Actual value is greater than the min value \nand is equal to max value.',
             actual_value, (expected_value - 2 * tol), (expected_value - tol),     5]
        ]

        for exp_result, log_msg, msg, act_val, min_val, max_val, test_num in test_cases_table:
            logging.info(log_msg)
            assert_method = self.assertTrue if exp_result == PASSED else self.assertFalse
            assert_method(self.th.verify_range(act_val, min_val, max_val, msg, test_num), f'{exp_result} expected')
            self.assertTrue(th_verify_log(log_msg, exp_result, act_val, 0, rng=(min_val, max_val), msg=msg, test_num=test_num),
                            f'Exactly one record match expected')

    # @[VerifyRange_1_TCASE_3]
    # @{VerifyRange_1}
    def test_verify_range_1_TCASE_3(self):
        logging.info('\n\nTesting VerifyRange_1 anchor - test_num/on_fail parameters\n')
        actual_value = 1
        expected_value = 1
        tol = 1

        test_cases_table = [
            # Test that the verify_range() function indicates Failed and omits
            # the test number, when the test number is not set (or equals to 0)
            # and the actual value is less than the min value and is also less
            # than the max value.
            [FAILED, 'Test VerifyRange_1 (Failed expected)', '\nThe test_num parameter is not set and the Actual\n'
                                                             'value is less than the min value and is also less\n'
                                                             'than the max value.',                                actual_value, (expected_value + tol), (expected_value + tol), 0, None],

            # Test that the verify_range() function indicates Passed and omits
            # the test number, when the test number is not set (or equals to 0)
            # and the actual value is greater than the min value and is less
            # than the max value.
            [PASSED, 'Test VerifyRange_1 (Passed expected)', '\nThe test_num parameter is not set and the Actual\n'
                                                             'value is greater than the min value and is less\n'
                                                             'than the max value.',                                actual_value, (expected_value - tol), (expected_value + tol), 0, None],

            # Test that the verify_range() function indicates Failed and does
            # trigger on_fail() method, when on_fail method is set and the
            # actual value is less than the min value and is also less than
            # the max value.
            [FAILED, 'Test VerifyRange_1 (Failed expected)', '\nThe on_fail parameter is set and the Actual\n'
                                                             'value is less than the min value and is also less\n'
                                                             'than the max value.',                                actual_value, (expected_value + tol), (expected_value + tol), 3, on_fail_function],

            # Test that the verify_range() function indicates Passed and does not
            # trigger on_fail() method, when on_fail method is set and the
            # actual value is greater than the min value and is less than
            # the max value.
            [PASSED, 'Test VerifyRange_1 (Passed expected)', '\nThe on_fail parameter is set and the Actual\n'
                                                             'value is greater than the min value and is less\n'
                                                             'than the max value.',                                actual_value, (expected_value - tol), (expected_value + tol), 4, on_fail_function]
        ]

        for exp_result, log_msg, msg, act_val, min_val, max_val, test_num, on_fail in test_cases_table:
            logging.info(log_msg)
            assert_method = self.assertTrue if exp_result == PASSED else self.assertFalse
            assert_method(self.th.verify_range(act_val, min_val, max_val, msg, test_num, on_fail=on_fail), f'{exp_result} expected')
            self.assertTrue(th_verify_log(log_msg, exp_result, act_val, 0, rng=(min_val, max_val), msg=msg, test_num=test_num, on_fail=on_fail),
                            f'Exactly one record match expected')

    # @[VerifyNotInRange_1_TCASE_1]
    # @{VerifyNotInRange_1}
    def test_verify_not_in_range_1_TCASE_1(self):
        logging.info('\n\nTesting VerifyNotInRange_1 anchor - floating point parameters\n')
        actual_value = 50.4567
        expected_value = 50.4567
        tol = 0.0001

        test_cases_table = [
            # Test that the verify_not_in_range() function indicates Failed
            # when the actual value is greater than the min value and
            # is less than the max value.
            [FAILED, 'Test VerifyNotInRange_1 (Failed expected)', '\nThe Actual value is greater than the min value \nand is less than the max value.',
             actual_value, (expected_value - tol),     (expected_value + tol),     1],

            # Test that the verify_not_in_range() function indicates Failed
            # when the actual value is equal to the min value and
            # is less than the max value.
            [FAILED, 'Test VerifyNotInRange_1 (Failed expected)', '\nThe Actual value is equal to min value \nand is less than the max value.',
             actual_value, expected_value,             (expected_value + tol),     2],

            # Test that the verify_not_in_range() function indicates Failed
            # when the actual value is greater than the min value and
            # is equal to the max value.
            [FAILED, 'Test VerifyNotInRange_1 (Failed expected)', '\nThe Actual value is greater than the min value \nand is equal to max value.',
             actual_value, (expected_value - tol),     expected_value,             3],

            # Test that the verify_not_in_range() function indicates Passed
            # when the actual value is less than the min value and
            # is also less than the max value.
            [PASSED, 'Test VerifyNotInRange_1 (Passed expected)', '\nThe Actual value is less than the max_value and is \nalso less than the min_value',
             actual_value, (expected_value + tol),     (expected_value + 2 * tol), 4],

            # Test that the verify_not_in_range() function indicates Passed
            # when the actual value is greater than the min value and
            # is also greater than the max value.
            [PASSED, 'Test VerifyNotInRange_1 (Passed expected)', '\nThe Actual value is greater than the min value \nand is equal to max value.',
             actual_value, (expected_value - 2 * tol), (expected_value - tol),     5]
        ]

        for exp_result, log_msg, msg, act_val, min_val, max_val, test_num in test_cases_table:
            logging.info(log_msg)
            assert_method = self.assertTrue if exp_result == PASSED else self.assertFalse
            assert_method(self.th.verify_not_in_range(act_val, min_val, max_val, msg, test_num), f'{exp_result} expected')
            self.assertTrue(th_verify_log(log_msg, exp_result, act_val, 0, rng=(min_val, max_val), msg=msg, test_num=test_num),
                            f'Exactly one record match expected')

    # @[VerifyNotInRange_1_TCASE_2]
    # @{VerifyNotInRange_1}
    def test_verify_not_in_range_1_TCASE_2(self):
        logging.info('\n\nTesting VerifyNotInRange_1 anchor - integer parameters\n')
        actual_value = 50
        expected_value = 50
        tol = 5

        test_cases_table = [
            # Test that the verify_not_in_range() function indicates Failed
            # when the actual value is greater than the min value and
            # is less than the max value.
            [FAILED, 'Test VerifyNotInRange_1 (Failed expected)', '\nThe Actual value is greater than the min value \nand is less than the max value.',
             actual_value, (expected_value - tol),     (expected_value + tol),     1],

            # Test that the verify_not_in_range() function indicates Failed
            # when the actual value is equal to the min value and
            # is less than the max value.
            [FAILED, 'Test VerifyNotInRange_1 (Failed expected)', '\nThe Actual value is equal to min value \nand is less than the max value.',
             actual_value, expected_value,             (expected_value + tol),     2],

            # Test that the verify_not_in_range() function indicates Failed
            # when the actual value is greater than the min value and
            # is equal to the max value.
            [FAILED, 'Test VerifyNotInRange_1 (Failed expected)', '\nThe Actual value is greater than the min value \nand is equal to max value.',
             actual_value, (expected_value - tol),     expected_value,             3],

            # Test that the verify_not_in_range() function indicates Passed
            # when the actual value is less than the min value and
            # is also less than the max value.
            [PASSED, 'Test VerifyNotInRange_1 (Passed expected)', '\nThe Actual value is less than the max_value and is \nalso less than the min_value',
             actual_value, (expected_value + tol),     (expected_value + 2 * tol), 4],

            # Test that the verify_not_in_range() function indicates Passed
            # when the actual value is greater than the min value and
            # is also greater than the max value.
            [PASSED, 'Test VerifyNotInRange_1 (Passed expected)', '\nThe Actual value is greater than the min value \nand is equal to max value.',
             actual_value, (expected_value - 2 * tol), (expected_value - tol),     5]
        ]

        for exp_result, log_msg, msg, act_val, min_val, max_val, test_num in test_cases_table:
            logging.info(log_msg)
            assert_method = self.assertTrue if exp_result == PASSED else self.assertFalse
            assert_method(self.th.verify_not_in_range(act_val, min_val, max_val, msg, test_num), f'{exp_result} expected')
            self.assertTrue(th_verify_log(log_msg, exp_result, act_val, 0, rng=(min_val, max_val), msg=msg, test_num=test_num),
                            f'Exactly one record match expected')

    # @[VerifyNotInRange_1_TCASE_3]
    # @{VerifyNotInRange_1}
    def test_verify_not_in_range_1_TCASE_3(self):
        logging.info('\n\nTesting VerifyNotInRange_1 anchor - test_num/on_fail parameters\n')
        actual_value = 1
        expected_value = 1
        tol = 1

        test_cases_table = [
            # Test that the verify_not_in_range() function indicates Failed and omits
            # the test number, when the test number is not set (or equals to 0)
            # and the actual value is greater than the min value and is less
            # than the max value.
            [FAILED, 'Test VerifyNotInRange_1 (Failed expected)', '\nThe test_num parameter is not set and the Actual\n'
                                                                  'value is greater than the min value and is less\n'
                                                                  'than the max value.',
             actual_value, (expected_value - tol), (expected_value + tol), 0, None],

            # Test that the verify_not_in_range() function indicates Passed and omits
            # the test number, when the test number is not set (or equals to 0)
            # and the actual value is less than the min value and is also less
            # than the max value.
            [PASSED, 'Test VerifyNotInRange_1 (Passed expected)', '\nThe test_num parameter is not set and the Actual\n'
                                                                  'value is less than the min value and is also less\n'
                                                                  'than the max value.',
             actual_value, (expected_value + tol), (expected_value + tol), 0, None],

            # Test that the verify_not_in_range() function indicates Failed and does
            # trigger on_fail() method, when on_fail method is set and the
            # actual value is greater than the min value and is less than
            # the max value.
            [FAILED, 'Test VerifyNotInRange_1 (Failed expected)', '\nThe on_fail parameter is set and the Actual\n'
                                                                  'value is greater than the min value and is less\n'
                                                                  'than the max value.',
             actual_value, (expected_value - tol), (expected_value + tol), 3, on_fail_function],

            # Test that the verify_not_in_range() function indicates Passed and does not
            # trigger on_fail() method, when on_fail method is set and the
            # actual value is less than the min value and is also less than
            # the max value.
            [PASSED, 'Test VerifyNotInRange_1 (Passed expected)', '\nThe on_fail parameter is set and the Actual\n'
                                                                  'value is less than the min value and is also less\n'
                                                                  'than the max value.',
             actual_value, (expected_value + tol), (expected_value + tol), 4, on_fail_function]
        ]

        for exp_result, log_msg, msg, act_val, min_val, max_val, test_num, on_fail in test_cases_table:
            logging.info(log_msg)
            assert_method = self.assertTrue if exp_result == PASSED else self.assertFalse
            assert_method(self.th.verify_not_in_range(act_val, min_val, max_val, msg, test_num, on_fail=on_fail), f'{exp_result} expected')
            self.assertTrue(th_verify_log(log_msg, exp_result, act_val, 0, rng=(min_val, max_val), msg=msg, test_num=test_num, on_fail=on_fail),
                            f'Exactly one record match expected')

    # @[VerifyPercent_1_TCASE_1]
    # @{VerifyPercent_1}
    def test_verify_percent_1_TCASE_1(self):
        logging.info('\n\nTesting VerifyPercent_1 anchor - floating point parameters\n')
        actual_value = 50.4567
        expected_value = 50.4567
        percent = 0.0001 * 100

        test_cases_table = [
            # Test that the verify_percent() function indicates Passed
            # when the actual value is just below the upper percent boundary.
            [PASSED, 'Test VerifyPercent_1 (Passed expected)', '\nThe Actual value is just below the upper percent boundary.',
             actual_value,                                            expected_value, percent, 1],

            # Test that the verify_percent() function indicates Passed
            # when the actual value is at the upper percent boundary.
            [PASSED, 'Test VerifyPercent_1 (Passed expected)', '\nThe Actual value is at the upper percent boundary.',
             (actual_value + (expected_value * percent / 100.0)),     expected_value, percent, 2],

            # Test that the verify_percent() function indicates Failed
            # when the actual value is just above the upper percent boundary.
            [FAILED, 'Test VerifyPercent_1 (Failed expected)', '\nThe Actual value is above the upper percent boundary.',
             (actual_value + 2 * (expected_value * percent / 100.0)), expected_value, percent, 3],

            # Test that the verify_percent() function indicates Passed
            # when the actual value is just above the lower percent boundary.
            [PASSED, 'Test VerifyPercent_1 (Passed expected)', '\nThe Actual value is just above the lower percent boundary.',
             actual_value,                                            expected_value, percent, 4],

            # Test that the verify_percent() function indicates Passed
            # when the actual value is at the lower percent boundary.
            [PASSED, 'Test VerifyPercent_1 (Passed expected)', '\nThe Actual value is at the lower percent boundary.',
             (actual_value - (expected_value * percent / 100.0)),     expected_value, percent, 5],

            # Test that the verify_percent() function indicates Failed
            # when the actual value is just below the lower percent boundary.
            [FAILED, 'Test VerifyPercent_1 (Failed expected)', '\nThe Actual value is below the lower percent boundary.',
             (actual_value - 2 * (expected_value * percent / 100.0)), expected_value, percent, 6]
        ]

        for exp_result, log_msg, msg, act_val, exp_val, percent, test_num in test_cases_table:
            logging.info(log_msg)
            assert_method = self.assertTrue if exp_result == PASSED else self.assertFalse
            assert_method(self.th.verify_percent(act_val, exp_val, percent, msg, test_num), f'{exp_result} expected')
            self.assertTrue(th_verify_log(log_msg, exp_result, act_val, exp_val, prcnt=percent, msg=msg, test_num=test_num),
                            f'Exactly one record match expected')

    # @[VerifyPercent_1_TCASE_2]
    # @{VerifyPercent_1}
    def test_verify_percent_1_TCASE_2(self):
        logging.info('\n\nTesting VerifyPercent_1 anchor - integer parameters\n')
        actual_value = 100
        expected_value = 100
        percent = 5

        test_cases_table = [
            # Test that the verify_percent() function indicates Passed
            # when the actual value is just below the upper percent boundary.
            [PASSED, 'Test VerifyPercent_1 (Passed expected)', '\nThe Actual value is just below the upper percent boundary.',
             actual_value,                                          expected_value, percent, 1],

            # Test that the verify_percent() function indicates Passed
            # when the actual value is at the upper percent boundary.
            [PASSED, 'Test VerifyPercent_1 (Passed expected)', '\nThe Actual value is at the upper percent boundary.',
             (actual_value + (expected_value * percent / 100)),     expected_value, percent, 2],

            # Test that the verify_percent() function indicates Failed
            # when the actual value is just above the upper percent boundary.
            [FAILED, 'Test VerifyPercent_1 (Failed expected)', '\nThe Actual value is above the upper percent boundary.',
             (actual_value + 2 * (expected_value * percent / 100)), expected_value, percent, 3],

            # Test that the verify_percent() function indicates Passed
            # when the actual value is just above the lower percent boundary.
            [PASSED, 'Test VerifyPercent_1 (Passed expected)', '\nThe Actual value is just above the lower percent boundary.',
             actual_value,                                          expected_value, percent, 4],

            # Test that the verify_percent() function indicates Passed
            # when the actual value is at the lower percent boundary.
            [PASSED, 'Test VerifyPercent_1 (Passed expected)', '\nThe Actual value is at the lower percent boundary.',
             (actual_value - (expected_value * percent / 100)),     expected_value, percent, 5],

            # Test that the verify_percent() function indicates Failed
            # when the actual value is just below the lower percent boundary.
            [FAILED, 'Test VerifyPercent_1 (Failed expected)', '\nThe Actual value is below the lower percent boundary.',
             (actual_value - 2 * (expected_value * percent / 100)), expected_value, percent, 6]
        ]

        for exp_result, log_msg, msg, act_val, exp_val, percent, test_num in test_cases_table:
            logging.info(log_msg)
            assert_method = self.assertTrue if exp_result == PASSED else self.assertFalse
            assert_method(self.th.verify_percent(act_val, exp_val, percent, msg, test_num), f'{exp_result} expected')
            self.assertTrue(th_verify_log(log_msg, exp_result, act_val, exp_val, prcnt=percent, msg=msg, test_num=test_num),
                            f'Exactly one record match expected')

    # @[VerifyPercent_1_TCASE_3]
    # @{VerifyPercent_1}
    def test_verify_percent_1_TCASE_3(self):
        logging.info('\n\nTesting VerifyPercent_1 anchor - test_num/on_fail parameters\n')
        actual_value = 1
        expected_value = 1
        percent = 10

        test_cases_table = [
            # Test that the verify_percent() function indicates Failed and omits
            # the test number, when the test number is not set (or equals to 0)
            # and the actual value is just above the upper percent boundary.
            [FAILED, 'Test VerifyPercent_1 (Failed expected)', '\nThe test_num parameter is not set and the Actual\n'
                                                               'value is just above the upper percent boundary.',
             (actual_value + 1), expected_value, percent, 0, None],

            # Test that the verify_percent() function indicates Passed and omits
            # the test number, when the test number is not set (or equals to 0)
            # and the actual value is just below the upper percent boundary.
            [PASSED, 'Test VerifyPercent_1 (Passed expected)', '\nThe test_num parameter is not set and the Actual\n'
                                                               'value is just below the upper percent boundary.',
             actual_value,       expected_value, percent, 0, None],

            # Test that the verify_percent() function indicates Failed and does
            # trigger on_fail() method, when on_fail method is set and the
            # actual value is just above the upper percent boundary.
            [FAILED, 'Test VerifyPercent_1 (Failed expected)', '\nThe on_fail parameter is set and the Actual\n'
                                                               'value is just above the upper percent boundary.',
             (actual_value + 1), expected_value, percent, 3, on_fail_function],

            # Test that the verify_percent() function indicates Passed and does not
            # trigger on_fail() method, when on_fail method is set and the
            # actual value is just below the upper percent boundary.
            [PASSED, 'Test VerifyPercent_1 (Passed expected)', '\nThe on_fail parameter is set and the Actual\n'
                                                               'value is just below the upper percent boundary.',
             actual_value,       expected_value, percent, 4, on_fail_function]
        ]

        for exp_result, log_msg, msg, act_val, exp_val, percent, test_num, on_fail in test_cases_table:
            logging.info(log_msg)
            assert_method = self.assertTrue if exp_result == PASSED else self.assertFalse
            assert_method(self.th.verify_percent(act_val, exp_val, percent, msg, test_num, on_fail=on_fail), f'{exp_result} expected')
            self.assertTrue(th_verify_log(log_msg, exp_result, act_val, exp_val, prcnt=percent, msg=msg, test_num=test_num, on_fail=on_fail),
                            f'Exactly one record match expected')

    # @[VerifyString_1_TCASE_1]
    # @{VerifyString_1}
    def test_verify_string_1_TCASE_1(self):
        logging.info('\n\nTesting VerifyString_1 anchor - string parameters\n')
        actual_string = 'String'
        expected_string = 'String'

        test_cases_table = [
            # Test that the verify_string() function indicates Passed
            # when the actual string is equal to the expected string
            # and the caseSensitive flag is set to TRUE.
            [PASSED, 'Test VerifyString_1 (Passed expected)', '\nThe Actual string is equal to the Expected string, \n'
                                                              'and the caseSensitive flag is set to TRUE.',
             actual_string, expected_string, True,  1],

            # Test that the verify_string() function indicates Failed
            # when the actual string and the expected string are same,
            # but differ in case. The caseSensitive flag is set to TRUE.
            [FAILED, 'Test VerifyString_1 (Failed expected)', '\nThe Actual string and the expected strings are same,\n'
                                                              'but differ in case. The caseSensitive flag is set to TRUE.',
             actual_string, 'stRing',        True,  2],

            # Test that the verify_string() function indicates Failed
            # when the actual string and the expected string are different
            # and the caseSensitive flag is set to TRUE.
            [FAILED, 'Test VerifyString_1 (Failed expected)', '\nThe Expected string is different, the caseSensitive\n'
                                                              'flag is set to TRUE.',
             actual_string, 'verify',        True,  3],

            # Test that the verify_string() function indicates Passed
            # when the actual string is equal to the expected string
            # and the caseSensitive flag is set to FALSE.
            [PASSED, 'Test VerifyString_1 (Passed expected)', '\nThe Actual string is equal to the Expected string, \n'
                                                              'and the caseSensitive flag is set to FALSE.',
             actual_string, expected_string, False, 4],

            # Test that the verify_string() function indicates Failed
            # when the actual string and the expected string are same,
            # but differ in case. The caseSensitive flag is set to FALSE.
            [PASSED, 'Test VerifyString_1 (Passed expected)', '\nThe Actual string and the Expected string are same,\n'
                                                              'but differ in case. The caseSensitive flag is set to FALSE.',
             actual_string, 'stRing',        False, 5],

            # Test that the verify_string() function indicates Failed
            # when the actual string and the expected string are different
            # and the caseSensitive flag is set to FALSE.
            [FAILED, 'Test VerifyString_1 (Failed expected)', '\nThe Expected string are different, the caseSensitive\n'
                                                              'flag is set to FALSE.',
             actual_string, 'verify',        False, 6]
        ]

        for exp_result, log_msg, msg, act_val, exp_val, case, test_num in test_cases_table:
            logging.info(log_msg)
            assert_method = self.assertTrue if exp_result == PASSED else self.assertFalse
            assert_method(self.th.verify_string(act_val, exp_val, case, msg, test_num), f'{exp_result} expected')
            self.assertTrue(th_verify_log(log_msg, exp_result, act_val, exp_val, msg=msg, test_num=test_num),
                            f'Exactly one record match expected')

    # @[VerifyString_1_TCASE_2]
    # @{VerifyString_1}
    def test_verify_string_1_TCASE_2(self):
        logging.info('\n\nTesting VerifyString_1 anchor - test_num/on_fail parameters\n')
        actual_string = 'test_num/on_fail'
        expected_string = 'test_num/on_fail'

        test_cases_table = [
            # Test that the verify_string() function indicates Failed and omits
            # the test number, when the test number is not set (or equals to 0)
            # and the actual string is not equal to the expected string.
            [FAILED, 'Test VerifyString_1 (Failed expected)', '\nThe test_num parameter is not set and the Actual\n'
                                                              'string is not equal to the Expected string.',
             'actual_stri', expected_string, True, 0, None],

            # Test that the verify_string() function indicates Passed and omits
            # the test number, when the test number is not set (or equals to 0)
            # and the actual string is equal to the expected string.
            [PASSED, 'Test VerifyString_1 (Passed expected)', '\nThe test_num parameter is not set and the Actual\n'
                                                              'string is equal to the Expected string.',
             actual_string, expected_string, True, 0, None],

            # Test that the verify_percent() function indicates Failed and does
            # trigger on_fail() method, when on_fail method is set and the
            # actual string is not equal to the expected string.
            [FAILED, 'Test VerifyPercent_1 (Failed expected)', '\nThe on_fail parameter is set and the Actual\n'
                                                               'string is not equal to the Expected string.',
             'actual_stri', expected_string, True, 3, on_fail_function],

            # Test that the verify_percent() function indicates Passed and does not
            # trigger on_fail() method, when on_fail method is set and the
            # actual value is just below the upper percent boundary.
            [PASSED, 'Test VerifyPercent_1 (Passed expected)', '\nThe on_fail parameter is set and the Actual\n'
                                                               'string is equal to the Expected string.',
             actual_string, expected_string, True, 4, on_fail_function]
        ]

        for exp_result, log_msg, msg, act_val, exp_val, case, test_num, on_fail in test_cases_table:
            logging.info(log_msg)
            assert_method = self.assertTrue if exp_result == PASSED else self.assertFalse
            assert_method(self.th.verify_string(act_val, exp_val, case, msg, test_num, on_fail=on_fail), f'{exp_result} expected')
            self.assertTrue(th_verify_log(log_msg, exp_result, act_val, exp_val, msg=msg, test_num=test_num, on_fail=on_fail),
                            f'Exactly one record match expected')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Define results dir path.')
    parser.add_argument('--path', dest='result_path', type=str)
    args = parser.parse_args()

    # Check if result path was passed as an argument
    if args.result_path is not None:
        RESULTS_DIR = os.path.join(args.result_path, RESULTS_DIR)
    else:
        RESULTS_DIR = os.path.join(os.getcwd(), RESULTS_DIR)

    # Create directory if it does not exist
    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)

    # Store results into temporary file
    temp_results = os.path.join(RESULTS_DIR, temp_results)
    if os.path.exists(temp_results):
        os.remove(temp_results)
    log_file_handler = logging.FileHandler(temp_results)
    logging.getLogger().addHandler(log_file_handler)

    # Unit tests results stored into temporary file
    temp_summary = os.path.join(RESULTS_DIR, 'temp_summary.log')
    with open(temp_summary, 'w') as output_file:
        unittest.TextTestRunner(output_file).run(unittest.TestLoader().loadTestsFromTestCase(TestTestHarness))

    # Merge result log with summary
    complete_log = os.path.join(RESULTS_DIR, 'test_testharness.log')
    with open(complete_log, 'w') as l:
        for file in [temp_results, temp_summary]:
            with open(file, 'r') as f:
                l.write(f.read())

    # Cleanup temp files
    logging.getLogger().handlers = []
    log_file_handler = None
    os.remove(temp_results)
    os.remove(temp_summary)
