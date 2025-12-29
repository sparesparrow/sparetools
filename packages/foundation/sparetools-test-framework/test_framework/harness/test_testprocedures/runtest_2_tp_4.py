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


def runtest_2_test_procedure_4():
    th = NgapyTestHarnes()

    verify_data_table = [
        [0,   th.verify,        7,      5],      # FAILED
        [1,   th.verify,        'a',    'b'],    # FAILED
        [0.5, th.verify_le,     8.2,    8.2],    # PASSED
        [0.5, th.verify_gt,     'abc',  50],     # FAILED DUE TO EXCEPTION
        [0,   th.verify_gt,     1,      2]       # NOT VERIFIED DUE TO EXCEPTION
    ]

    for i, (sleep_time, verify_method, a, b) in enumerate(verify_data_table, start=1):
        verify_method(a, b, msg=f'\nArbitrary data verification no. {i}', test_num=i)
        time.sleep(sleep_time)
