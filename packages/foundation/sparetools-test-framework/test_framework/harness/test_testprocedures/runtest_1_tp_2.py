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


def runtest_1_test_procedure_2():
    th = NgapyTestHarnes()
    th.verify(5, 5,     '\nThis is verification number 1', 1)
    th.verify('a', 'b', '\nThis is verification number 2', 2)
    th.verify_ne(5, 6,  '\nThis is verification number 3', 3)
    th.verify(8.2, 8.2, '\nThis is verification number 4', 4)
    th.verify_le(7, 5,  '\nThis is verification number 5', 5)

