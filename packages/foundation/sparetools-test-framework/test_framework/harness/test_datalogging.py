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
# Purpose:   Verification of RTAR Test Harness data logging
#
# Notes: None
# ********************************************************************************************
# ********************************************************************************************

try:
    from .test_harness import run_test
    from .test_testprocedures.runtest_1_tp_1 import runtest_1_test_procedure_1
    from .test_testprocedures.runtest_1_tp_2 import runtest_1_test_procedure_2
    from .test_testprocedures.runtest_2_tp_1 import runtest_2_test_procedure_1
    from .test_testprocedures.runtest_2_tp_2 import runtest_2_test_procedure_2
    from .test_testprocedures.runtest_2_tp_3 import runtest_2_test_procedure_3
    from .test_testprocedures.runtest_2_tp_4 import runtest_2_test_procedure_4
    from .test_testprocedures.runtest_2_tp_5 import runtest_2_test_procedure_5
except ImportError:
    from sparetools.test_framework.harness import run_test
    from test_testprocedures.runtest_1_tp_1 import runtest_1_test_procedure_1
    from test_testprocedures.runtest_1_tp_2 import runtest_1_test_procedure_2
    from test_testprocedures.runtest_2_tp_1 import runtest_2_test_procedure_1
    from test_testprocedures.runtest_2_tp_2 import runtest_2_test_procedure_2
    from test_testprocedures.runtest_2_tp_3 import runtest_2_test_procedure_3
    from test_testprocedures.runtest_2_tp_4 import runtest_2_test_procedure_4
    from test_testprocedures.runtest_2_tp_5 import runtest_2_test_procedure_5

import unittest
import os
import re
import time
import glob
import argparse

# Definition of Globally used variables/constants
RESULTS_DIR = 'results'


def check_log_if_exists(dir, filename):
    file_list = glob.glob(os.path.join(dir, filename))
    if len(file_list) > 0:
        return True
    else:
        return False


def get_log_timestamp(dir, filename):
    file_list = glob.glob(os.path.join(dir, filename))
    if len(file_list) == 1:
        return re.search(r'.*_(\d{2}_\d{2}_\d{4}_\d+)\.txt', file_list[0])[1]
    else:
        return 'ERROR'


def remove_log_if_exists(dir, filename):
    file_list = glob.glob(os.path.join(dir, filename))
    for file in file_list:
        if os.path.exists(file):
            os.remove(file)

    # Remove complementary XML files as well
    file_list_xml = glob.glob(os.path.join(dir, filename.replace('.txt', '.xml')))
    for file in file_list_xml:
        if os.path.exists(file):
            os.remove(file)

    return check_log_if_exists(dir, filename)


class TestDatalogging(unittest.TestCase):
    # @[RunTest_1_TCASE_1]
    # @{RunTest_1}
    def test_runtest_1_TCASE_1(self):
        test_data = [
            # Verify that executing run_test() with parameters function_to_run
            # equal to Test Procedure runtest_1_tp_1, results_dir_path equal to
            # '\results\tp1' and header_message equal to 'RunTest_1 TP 1 Header
            # Message', produces a .txt file with a name combining Test Procedure
            # name and file creation time stamp, within folder '\results\tp1'.
            # The .txt file contains header 'RunTest_1 TP 1 Header Message'.
            [runtest_1_test_procedure_1, r'runtest_1_tp_1*.txt', RESULTS_DIR + r'\tp1', 'RunTest_1 TP 1 Header Message'],

            # Verify that executing run_test() with parameters function_to_run
            # equal to Test Procedure runtest_1_tp_2, results_dir_path equal to
            # '\results\tp2' and header_message equal to 'RunTest_1 TP 2 Header
            # Message', produces a .txt file with a name combining Test Procedure
            # name and file creation time stamp, within folder '\results\tp2'.
            # The .txt file contains header 'RunTest_1 TP 2 Header Message'.
            [runtest_1_test_procedure_2, r'runtest_1_tp_2*.txt', RESULTS_DIR + r'\tp2', 'RunTest_1 TP 2 Header Message']
        ]

        for test_procedure_routine, log_name_wildcard, result_dir, header_msg in test_data:
            test_name = None
            if not os.path.exists(result_dir):
                os.makedirs(result_dir)

            self.assertFalse(remove_log_if_exists(result_dir, log_name_wildcard), 'Txt logs could not be cleared.')
            expected_timestamp = time.strftime("%m_%d_%Y_%H%M%S", time.localtime())
            run_test(function_to_run=test_procedure_routine, results_dir_path=result_dir, header_message=header_msg)
            self.assertTrue(check_log_if_exists(result_dir, log_name_wildcard),
                            'No txt log file was created during Run Test procedure.')
            actual_timestamp = get_log_timestamp(result_dir, log_name_wildcard)
            self.assertEqual(expected_timestamp, actual_timestamp, 'Timestamp on the file does not match.')
            log_list = glob.glob(os.path.join(result_dir, '*.txt'))
            log_name = log_list[0]
            with open(log_name, 'r') as log_file:
                temp = re.search(r'TEST *: *(.*)\n', log_file.read())
                if temp:
                    test_name = temp[1]
                self.assertIsNotNone(test_name, 'No test name found in log file.')
                self.assertEqual(test_name, header_msg, 'Test name found in the log file does not match the expected.')

    # @[RunTest_1_TCASE_2]
    # @{RunTest_1}
    def test_runtest_1_TCASE_2(self):
        test_data = [
            # Verify that executing Test Procedure runtest_2_tp_1
            # produces .txt file with verification results equal to
            # 8 PASSED and 7 FAILED, and Test procedure logs start
            # time and end time, with the difference of 17.3 seconds.
            [runtest_2_test_procedure_1, r'runtest_2_tp_1*.txt', 'RunTest_1 TCASE 2 TP 1', 8, 7, 17.3],

            # Verify that executing Test Procedure runtest_2_tp_2
            # produces .txt file with verification results equal to
            # 1 PASSED and 14 FAILED, and Test procedure logs start
            # time and end time, with the difference of 10 seconds.
            [runtest_2_test_procedure_2, r'runtest_2_tp_2*.txt', 'RunTest_1 TCASE 2 TP 2', 1, 14, 10],

            # Verify that executing Test Procedure runtest_2_tp_3
            # produces .txt file with verification results equal to
            # 10 PASSED and 0 FAILED, and Test procedure logs start
            # time and end time, with the difference of 1 second.
            [runtest_2_test_procedure_3, r'runtest_2_tp_3*.txt', 'RunTest_1 TCASE 2 TP 3', 10, 0, 1],

            # Verify that executing Test Procedure runtest_2_tp_4
            # produces .txt file with verification results equal to
            # 0 PASSED and 1 FAILED due to triggered failure, and
            # Test procedure logs start time and end time, with the
            # difference of 1.5 seconds.
            [runtest_2_test_procedure_4, r'runtest_2_tp_4*.txt', 'RunTest_1 TCASE 2 TP 4', 1, 3, 1.5],

            # Verify that executing Test Procedure runtest_2_tp_5
            # produces .txt file with verification results equal to
            # 0 PASSED and 1 FAILED due to triggered failure, and
            # Test procedure logs start time and end time, with the
            # difference of 0 seconds.
            [runtest_2_test_procedure_5, r'runtest_2_tp_5*.txt', 'RunTest_1 TCASE 2 TP 5', 0, 1, 0]
        ]

        for test_procedure_routine, log_name_wildcard, header_msg, exp_pass, exp_fail, timespan in test_data:
            passed_count_of_verify = 0
            failed_count_of_verify = 0
            passed_count_in_summary = 0
            failed_count_in_summary = 0
            test_start_time = None
            test_end_time = None

            self.assertFalse(remove_log_if_exists(RESULTS_DIR, log_name_wildcard),
                             'Txt logs could not be cleared.')
            time_started = time.ctime()
            run_test(function_to_run=test_procedure_routine, results_dir_path=RESULTS_DIR, header_message=header_msg)
            time_ended = time.ctime()
            self.assertTrue(check_log_if_exists(RESULTS_DIR, log_name_wildcard),
                            'No txt log file was created during Run Test procedure.')

            log_list = glob.glob(os.path.join(RESULTS_DIR, log_name_wildcard))
            log_name = log_list[0]
            with open(log_name, 'r') as log_file:
                temp = re.search(r'Test start time = *(.*)\n', log_file.read())
                if temp:
                    test_start_time = temp[1]
                self.assertIsNotNone(test_start_time, 'No test start time found in log file.')
                self.assertEqual(test_start_time, time_started, 'Test start time is not equal.')

                log_file.seek(0)
                temp = re.search(r'Test end time = *(.*)\n', log_file.read())
                if temp:
                    test_end_time = temp[1]
                self.assertIsNotNone(test_end_time, 'No test end time found in log file.')
                self.assertEqual(test_end_time, time_ended, 'Test end time is not equal.')

                log_file.seek(0)
                for record in re.findall(r'Test number: *\d* *(?:PASSED|FAILED)', log_file.read()):
                    if 'PASSED' in record:
                        passed_count_of_verify += 1
                    else:
                        failed_count_of_verify += 1

                log_file.seek(0)
                for record in re.findall(r'Exception occurred: *FAILED', log_file.read()):
                    failed_count_of_verify += 1

                log_file.seek(0)
                for record in re.findall(r'No verifications performed: *FAILED', log_file.read()):
                    failed_count_of_verify += 1

                log_file.seek(0)
                summary_part = re.search(r'Total number [a-zA-Z ]* *: *(\d*)\nTotal number [a-zA-Z ]*: *(\d*)', log_file.read())
                if summary_part:
                    passed_count_in_summary = int(summary_part[1])
                    failed_count_in_summary = int(summary_part[2])

            self.assertEqual(passed_count_in_summary, passed_count_of_verify, 'Summary PASSED count does not match')
            self.assertEqual(passed_count_in_summary, exp_pass,  'Summary PASSED count does not match')

            self.assertEqual(failed_count_in_summary, failed_count_of_verify, 'Summary FAILED count does not match')
            self.assertEqual(failed_count_in_summary, exp_fail,  'Summary FAILED count does not match')


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

    # Unit tests results stored into temporary file
    temp_summary = os.path.join(RESULTS_DIR, 'temp_summary.log')
    with open(temp_summary, 'w') as output_file:
        unittest.TextTestRunner(output_file).run(unittest.TestLoader().loadTestsFromTestCase(TestDatalogging))

    # Merge result log with summary
    complete_log = os.path.join(RESULTS_DIR, 'test_datalogging.log')
    with open(complete_log, 'w') as l:
        for root, subfolder, files in os.walk(os.path.abspath(RESULTS_DIR)):
            for file in files:
                if file.endswith('txt'):
                    with open(os.path.join(root, file), 'r') as f:
                        l.write(f.read())
        with open(temp_summary, 'r') as f:
            l.write(f.read())
        os.remove(temp_summary)

