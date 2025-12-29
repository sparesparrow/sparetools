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
import struct
from dataclasses import dataclass


@dataclass
class LogEntry:
    full_log: str
    time_stamp: float
    time_stamp_sys_time: float
    seq_number: int
    user_seq_number: int


class LogFileParser:
    def __init__(self, error_file_path):
        self.file_path = error_file_path
        self.lines = None

    def _read_file_to_struct(self, file_path=None):
        if not file_path:
            file_path = self.file_path
        with open(file_path, 'r', errors='ignore') as reader:
            file_data = reader.read()
        # lines = file_data.split("\b0")
        lines = list()
        try:
            while True:
                index = file_data.index("sw", 1)
                lines.append(file_data[:index])
                file_data = file_data[index:]
        except Exception:
            lines.append(file_data)

        new_lines = list()
        for line in lines:
            new_lines.extend(line.split("\\"))

        rslts = list(filter(lambda line: line.strip().startswith('sw'), new_lines))
        lines = [rslt.strip() for rslt in rslts]

        self.lines = lines
        return lines

    def parse_log_file(self, file_path=None):
        if not file_path:
            file_path = self.file_path
        return self._read_file_to_struct(file_path)

    def parse_binary_log_file(self, file_path=None) -> list:
        if not file_path:
            file_path = self.file_path
        offset = 0
        record_list = list()
        with open(file_path, 'rb') as reader:
            buffer = reader.read()
            while offset < len(buffer):
                try:
                    # First 8 bytes is garbage - C++ vtable
                    # Last 4 bytes are C++ pointer to log data... Also garbage
                    _, time_stamp, time_stamp_sys_time, seq_number, user_seq_num, log_data_size, _ = \
                        struct.unpack_from('8sddLLL4s',
                                           buffer,
                                           offset)
                    offset += struct.calcsize('8sddLLL4s')
                    log_data = struct.unpack_from(f'{log_data_size - 1}s', buffer, offset)[0].decode('ansi')
                    offset += log_data_size
                    record_list.append(LogEntry(log_data, time_stamp, time_stamp_sys_time, seq_number, user_seq_num))
                # Log is circular buffer with some maximum size. Therefore there might be some incomplete record,
                # which cannot be used/parsed. For now, just skip it.
                except struct.error:
                    pass
        return record_list

    def find_errors_in_log_file(self, error_name, err_desc_to_skip=None, err_desc_to_find=None):
        if not self.lines:
            self.parse_log_file()
            if not self.lines:
                return list()
        found_list = list()
        for item in self.lines:
            if error_name in item:
                if err_desc_to_skip and err_desc_to_skip in item:
                    continue
                if err_desc_to_find:
                    if err_desc_to_find in item:
                        found_list.append(item)
                else:
                    found_list.append(item)

        return found_list

    def find_latest_error_in_file(self, error_name, err_desc_to_skip=None, err_desc_to_find=None):
        found_list = self.find_errors_in_log_file(error_name, err_desc_to_skip, err_desc_to_find)
        if not found_list:
            return None
        return found_list[-1]
