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
# Purpose:   Verification of RTAR Test Harness qualification environment
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
import hashlib
import argparse

# Definition of Globally used variables/constants
PASSED = 'PASSED'
FAILED = 'FAILED'
RESULTS_DIR = 'results'
on_fail_msg = 'On Fail method called.\n'
temp_results = r'temp_results.log'


def on_fail_function():
    logging.getLogger().info(on_fail_msg)


class TestQualEnvironment(unittest.TestCase):
    def setUp(self):
        self.th = NgapyTestHarnes()

    def log_results(self):
        logging.info('\n\n')
        logging.info('RESULTS')

    # @[Verify_1_TCASE_0]
    # @{Verify_1}
    def test_verify_1_TCASE_0(self):
        logging.info('\n\nTesting Source Files MD5 matches release\n')
        hash_list = list()
        ok_hash_num = 0
        not_ok_hash_num = 0
        md5_file_found = False
        # read .md5 file
        root_path = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(root_path,'test_harness.md5'), 'r') as md5_file:
            for line in md5_file:
                hash_part, file_part = line.split(" *test_harness\\")
                file_part = os.path.join(root_path, file_part.strip('\n'))
                hash_list.append((file_part, hash_part))
            md5_file_found = True

        for file, hash_n in hash_list:
            f_hash = hashlib.md5()
            with open(file, 'rb') as file_to_calculate_md5:
                f_hash.update(file_to_calculate_md5.read())
                hash_hex = f_hash.hexdigest()
                logging.info(f"Checking {file} expected hash {str(hash_n)} versus actual {str(hash_hex)} ")
                self.assertEqual(hash_n, hash_hex)

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
        unittest.TextTestRunner(output_file).run(unittest.TestLoader().loadTestsFromTestCase(TestQualEnvironment))

    # Merge result log with summary
    complete_log = os.path.join(RESULTS_DIR, 'test_qual_environment.log')
    with open(complete_log, 'w') as l:
        for root, subfolder, files in os.walk(os.path.abspath(RESULTS_DIR)):
            for file in files:
                if file.endswith('txt'):
                    with open(os.path.join(root, file), 'r') as f:
                        l.write(f.read())
        with open(temp_summary, 'r') as f:
            l.write(f.read())
        os.remove(temp_summary)