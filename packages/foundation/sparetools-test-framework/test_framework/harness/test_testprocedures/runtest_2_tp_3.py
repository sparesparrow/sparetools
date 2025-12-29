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
try:
    from ..test_harness import NgapyTestHarnes
except (ImportError, ValueError):
    from sparetools.test_framework.harness import NgapyTestHarnes

import time


def runtest_2_test_procedure_3():
    th = NgapyTestHarnes()

    verify_data_table = [
        [0.1, th.verify,        50,     50],     # PASSED
        [0.1, th.verify_ne,     7,      6],      # PASSED
        [0.1, th.verify,        'b',    'b'],    # PASSED
        [0.1, th.verify_le,     8.2,    8.2],    # PASSED
        [0.1, th.verify_string, 'st',  'st'],    # PASSED
        [0.1, th.verify,        5,      5],      # PASSED
        [0.1, th.verify,        8.2,    8.2],    # PASSED
        [0.1, th.verify_string, 'a',    'a'],    # PASSED
        [0.1, th.verify_string, 's',    's'],    # PASSED
        [0.1, th.verify_gt,     6,      5]       # PASSED
    ]

    for i, (sleep_time, verify_method, a, b) in enumerate(verify_data_table, start=1):
        verify_method(a, b, msg=f'\nArbitrary data verification no. {i}', test_num=i)
        time.sleep(sleep_time)
