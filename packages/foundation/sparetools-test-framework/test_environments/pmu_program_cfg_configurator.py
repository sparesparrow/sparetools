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
from pathlib import Path
import csv

from ngapy.exceptions.ngapy_exceptions import NgapyRuntimeError
from ngapy.util.copy_tools import copy_file


class PmuProgramConfiguration:
    def __init__(self, pmu_folder: Path):
        if type(pmu_folder) == str:
            pmu_folder = Path(pmu_folder)
        self.pmu_folder = pmu_folder
        self.program_cfg_file = self.pmu_folder / r'Program_cfg.csv'
        if not (self.pmu_folder / r'Program_cfg.csv').exists():
            raise NgapyRuntimeError('Incorrect path passed to PmuProgramConfiguration. '
                                    'It is not correct of does not contain valid Program_cfg.csv')
        self.program_cfg_rows = list()
        self.parse_config()

    def parse_config(self):
        with open(self.program_cfg_file, newline='') as csv_file:
            self.program_cfg_rows = list(csv.reader(csv_file, delimiter=','))
        return self.program_cfg_rows

    def get_index_by_partition(self, partition_id):
        for row in self.program_cfg_rows:
            if len(row) > 2 and str(partition_id) in row[2]:
                return row
        else:
            return None

    def write_config(self):
        copy_file(self.program_cfg_file, self.pmu_folder / 'Program_cfg_backup.csv')
        with open(self.program_cfg_file, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            writer.writerows(self.program_cfg_rows)
        copy_file(self.program_cfg_file, self.pmu_folder / 'Program_cfg_ALL.csv')

    def set_partition_to_run(self, partition_id):
        self.set_partition_to(partition_id, 'Run')

    def set_partition_to_not_equipped(self, partition_id):
        self.set_partition_to(partition_id, 'NOT_EQUIPPED')

    def set_partition_to(self, partition_id, to):
        row = self.get_index_by_partition(partition_id)
        row[1] = to


if __name__ == '__main__':
    program_config = PmuProgramConfiguration(
        Path(r'c:\_Work\_Titan\_GIT\oms-dev-clean\Build\TARS_Lab_INSU1\GA_TITAN\PMU'))
    program_config.set_partition_to_run(3)
    program_config.write_config()
