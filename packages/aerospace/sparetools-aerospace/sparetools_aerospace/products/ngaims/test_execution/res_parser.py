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
################################################################################
#
# res_parser.py
#
# Description:
#
# Test results parsing utilities.
#
# The module defines interface and functionality for parsing Test result files.
#
# Arguments:
# - res_name - Name of Test result to parse.
#
################################################################################

################################################################################
# Imports

import os
import sys
import logging
import xml.etree.ElementTree as et

from sparetools_aerospace.products.ngaims.setup_environment import get_oms_repository_root

log = logging.getLogger('__main__.' + __name__)

################################################################################
# Public variables

# Arguments.

try:
    RES_NAME = sys.argv[1]
except:
    RES_NAME = None

# Test result exit codes.

RES_EXIT_CODES = {
    "valid": 0,
    "passed": 0,
    "failed": -1,
    "error": 40,
    "incomplete": 41,
    "inconclusive": 42,
    "blocked": 43,
    "partially_blocked": 44,
    "permanently_failed": 45,
    "deferred": 46
}

# Other.

RES_DIR = str(get_oms_repository_root()) + "/../tests/results"


################################################################################
# Public interface

# The function determines Test result file.
def determine_res_file():
    res_file_name = None
    exit_code = RES_EXIT_CODES["error"]

    if os.path.isfile(os.path.join(RES_DIR, RES_NAME, ".xml")) and \
            os.path.isfile(os.path.join(RES_DIR, RES_NAME, ".txt")):
        res_file_name = RES_NAME
        exit_code = RES_EXIT_CODES["valid"]

        return res_file_name, exit_code

    files = [file for file in os.listdir(RES_DIR) if (file.startswith(RES_NAME) and file.endswith(".xml"))]

    time_stamp = 0.0
    for file in files:
        actual_time_stamp = os.path.getctime(os.path.join(RES_DIR, file))
        if actual_time_stamp > time_stamp:
            time_stamp = actual_time_stamp
            res_file_name = file

    if res_file_name:
        res_file_name = res_file_name.replace(".xml", "")

    if os.path.isfile(os.path.join(RES_DIR, res_file_name + ".txt")):
        exit_code = RES_EXIT_CODES["valid"]

    return res_file_name, exit_code


# The function parses Test result file.
def parse_res_file(
        res_file_name  # Name of Test result file.
):
    res_dict = {}
    exit_code = RES_EXIT_CODES["error"]

    tree = et.parse(res_file_name)
    root = tree.getroot()

    res_dict["error_count"] = eval(root.attrib["errors"])
    res_dict["test_count"] = eval(root.attrib["tests"])
    res_dict["fail_count"] = eval(root.attrib["failures"])
    res_dict["pass_count"] = res_dict["test_count"] - res_dict["fail_count"]

    if res_dict["error_count"] != 0:
        exit_code = RES_EXIT_CODES["error"]

    elif (res_dict["fail_count"] + res_dict["pass_count"]) != res_dict["test_count"]:
        exit_code = RES_EXIT_CODES["incomplete"]

    elif res_dict["fail_count"] != 0:
        exit_code = RES_EXIT_CODES["failed"]

    else:
        exit_code = RES_EXIT_CODES["passed"]

    return res_dict, exit_code


# Main
if __name__ == '__main__':
    log.info("INFO: Running Test result parser ...")

    exit_code = RES_EXIT_CODES["error"]

    if RES_NAME:
        try:
            [res_file_name, exit_code] = determine_res_file()

            if exit_code == RES_EXIT_CODES["valid"]:
                [res_dict, exit_code] = parse_res_file(os.path.join(RES_DIR, res_file_name + ".xml"))
                log.info(
                    f'INFO: Parsed Test result file: {os.path.join(RES_DIR, res_file_name + ".xml")} ...')

        except Exception as ex:
            exit_code = RES_EXIT_CODES["error"]
            log.exception(ex)

    else:
        log.error("ERROR: Invalid Test result name.")

    sys.exit(exit_code)

# res_parser.py
