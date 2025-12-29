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

import re
from dataclasses import dataclass

from sparetools_aerospace.products.ngaims.error_log.error_log_manager import LogFileParser, LogEntry


@dataclass
class NgaimsLogEntry(LogEntry):
    def __init__(self, parent: LogEntry):
        super(NgaimsLogEntry, self).__init__(parent.full_log, parent.time_stamp, parent.time_stamp_sys_time,
                                             parent.seq_number, parent.user_seq_number)

    @property
    def fault_number(self) -> int:
        m = self.re_search()
        return int(m.group(1)) if m else ''

    @property
    def fault_name(self) -> str:
        m = self.re_search()
        return m.group(2) if m else ''

    def re_search(self):
        return re.search('([0-9]+|INFO:)[ ]+([^ ]+)[ ]+(.*)', self.full_log)

    @property
    def fault_message(self) -> str:
        m = self.re_search()
        return m.group(3) if m else ''


class NgaimsLogParser(LogFileParser):
    def parse_ngaims_log(self, file_path=None):
        if not file_path:
            file_path = self.file_path
        parsed_log_list = super(NgaimsLogParser, self).parse_binary_log_file(file_path)
        parsed_log = list()
        for log_line in parsed_log_list:
            parsed_log.append(NgaimsLogEntry(log_line))
        return parsed_log

    def find_errors_in_log_file(self, error_name, err_desc_to_skip=None, err_desc_to_find=None):
        found_list = list()
        for log_entry in self.parse_ngaims_log():
            if error_name in log_entry.full_log:
                if err_desc_to_skip and err_desc_to_skip in log_entry.fault_message:
                    continue
                if err_desc_to_find:
                    if err_desc_to_find in log_entry.fault_message:
                        found_list.append(log_entry)
                else:
                    found_list.append(log_entry)
        return found_list


if __name__ == '__main__':
    SKIP_ERR_MSG = "Missing static equation"
    log = NgaimsLogParser(r'c:\_Work\_Titan\_GIT\oms-dev\Build\TARS_Lab_INSU1\GA_TITAN\APU\oms_cmcf.log')
    log.parse_ngaims_log()
    result = log.find_errors_in_log_file(["swEqInitFail"], err_desc_to_skip=SKIP_ERR_MSG)
    pass
