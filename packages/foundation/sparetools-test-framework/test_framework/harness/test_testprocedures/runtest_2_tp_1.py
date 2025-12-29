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


def runtest_2_test_procedure_1():
    th = NgapyTestHarnes()
    
    verify_data_table = [
        [0,   th.verify,        5,      5],      # PASSED
        [0,   th.verify,        'a',    'b'],    # FAILED
        [1,   th.verify,        'none', '5'],    # FAILED
        [0,   th.verify,        5,      5],      # PASSED
        [2,   th.verify_ne,     5,      6],      # PASSED
        [0,   th.verify_string, 's ',  ' tr'],   # FAILED
        [1.5, th.verify_le,     8.2,    8.2],    # PASSED
        [0,   th.verify_string, 'st',  'str'],   # FAILED
        [1,   th.verify,        8.1,    8.2],    # FAILED
        [1,   th.verify_gt,     4,      5],      # FAILED
        [0,   th.verify_ge,     100.0,  5],      # PASSED
        [0,   th.verify_le,     8.05,    8.07],  # PASSED
        [4,   th.verify_string, 'str',  'str'],  # PASSED
        [0.2, th.verify_gt,     1,      2],      # FAILED
        [0,   th.verify_gt,     2,      1]       # PASSED
    ]

    for i, (sleep_time, verify_method, a, b) in enumerate(verify_data_table, start=1):
        verify_method(a, b, msg=f'\nArbitrary data verification no. {i}', test_num=i)
        time.sleep(sleep_time)
