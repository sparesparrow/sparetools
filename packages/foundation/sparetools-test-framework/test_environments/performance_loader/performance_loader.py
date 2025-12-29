import os
import re
import time

from tqdm import tqdm

import unittest
import sys
from pathlib import Path
from collections import defaultdict

from lxml import objectify

from sparetools.test_environments.mode_control.mode_control import restart_with_mode, NodeType, ModeType, ConnectionMode, ModeControl
from ngapy.exceptions.ngapy_exceptions import NgapyRuntimeError
from ngapy.util.custom_logging import setup_logging_from_config

from copy import deepcopy
# from ngapy.util.execute_command import execute_command


class PerformanceLoaderAPI(object):
    def __init__(self, name: str, data_loader: Path, config_file: Path):
        self.name = name
        self.data_loader = data_loader
        self.config_file = config_file
        self.dl = None

    def __enter__(self):
        import PythonApi.DL_API as DL_API
        self.dl = DL_API.DataLoaderApi()
        self.dl.initialize(self.name, dataloader_path=str(self.data_loader).replace('\\', '/'),
                           config_file_path=str(self.config_file).replace('\\', '/'))
        return self.dl

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.dl.shutdown()


class PerformanceLoader:
    def __init__(self, loader_path: Path = Path(r'c:\Program Files (x86)\PerformanceLoader'),
                 data_loader: Path = None,
                 config_file: Path = None):
        self.loader_path = loader_path
        if data_loader is None:
            data_loader = loader_path / 'pswLoader.exe'
        self.data_loader = data_loader
        if config_file is None:
            config_file = loader_path / 'PerformanceLoader.pdl'
        self.config_file = config_file
        sys.path.append(str(self.loader_path / 'Python'))
        self.targets = self.parse_config_targets(self.config_file)

    def python_loader(self, modules_haf_list: list):
        from sparetools.test_environments.performance_loader.PerformanceLoadDPM import main
        unzip = list(zip(*modules_haf_list))
        modules = '+'.join(unzip[0])
        haf_files = '+'.join(unzip[1])
        # execute_command(rf'py "{self.loader_path}\Python\PerformanceLoadDPM.py" {modules} {haf_files}')
        main([modules, haf_files])

    def native_loader(self, part_number_list: list, repository_id: int = 1):
        import PythonApi.DL_Util as DL_Util
        target_info_element = DL_Util.TargetTags()
        part_number_list = [x.upper() for x in part_number_list]

        targets = self.parse_config_targets(self.config_file)
        with PerformanceLoaderAPI('Test', self.data_loader, self.config_file) as performance_loader:
            part_number_objects = self.load_current_repository_parts(repository_id, performance_loader)
            part_numbers_to_load = list(
                filter(lambda part_number: part_number.number in part_number_list, part_number_objects.values()))
            if len(part_number_list) != len(part_numbers_to_load):
                found = [part_number.number for part_number in part_number_objects.values()]
                raise NgapyRuntimeError(f'Some of par-numbers was not found in repository. '
                                        f'Details: \nRequested: {part_number_list}\n'
                                        f'Found: {found}\n'
                                        f'Not Found: {set(part_number_list) - set(found)}\n')
            for part_number_to_load in part_numbers_to_load:
                load_targets = performance_loader.list_targets_for_part(part_number_to_load)
                for target in load_targets:
                    targets[target[target_info_element.load_target_name]].parts.append(part_number_to_load)

            for load_target in targets.values():
                if load_target.parts:
                    performance_loader.add_target(load_target, DL_Util.OperationType().upload)
            performance_loader.start(DL_Util.OperationType().upload)

            # self.print_status(performance_loader)
            tqdm_dict = defaultdict(lambda: tqdm(total=100, unit='%'))
            status_element = DL_Util.TargetStatusTags()
            target_status_list = []
            while performance_loader.operation_in_progress(operation=DL_Util.OperationType().upload,
                                                           status_data=target_status_list):
                self.update_progress_bar(status_element, target_status_list, tqdm_dict)
                time.sleep(0.5)
            self.update_progress_bar(status_element, target_status_list, tqdm_dict)
        pass

    def native_loader_2(self, part_number_list: list, repository_id: int = 1):
        import PythonApi.DL_Util as DL_Util
        target_info_element = DL_Util.TargetTags()
        targets = deepcopy(self.targets)

        with PerformanceLoaderAPI('Test', self.data_loader, self.config_file) as performance_loader:
            part_number_objects = self.load_current_repository_parts(repository_id, performance_loader)
            part_numbers_to_load = []
            for part_number in part_number_list:
                part_number_object = DL_Util.Part()
                part_number_object.repository_id = repository_id
                part_number_object.number = part_number[0].upper()
                part_number_object.path = str(part_number[2])
                part_number_object.description = ''
                for target in part_number[1]:
                    if target in targets:
                        targets[target].parts.append(part_number_object)

            for load_target in targets.values():
                if load_target.parts:
                    performance_loader.add_target(load_target, DL_Util.OperationType().upload)
            performance_loader.start(DL_Util.OperationType().upload)

            # self.print_status(performance_loader)
            tqdm_dict = defaultdict(lambda: tqdm(total=100, unit='%'))
            status_element = DL_Util.TargetStatusTags()
            target_status_list = []
            while performance_loader.operation_in_progress(operation=DL_Util.OperationType().upload,
                                                           status_data=target_status_list):
                self.update_progress_bar(status_element, target_status_list, tqdm_dict)
                time.sleep(2)
            self.update_progress_bar(status_element, target_status_list, tqdm_dict)
        pass

    @staticmethod
    def update_progress_bar(status_element, target_status_list, tqdm_dict):
        import PythonApi.DL_Util as DL_Util
        for target_status in target_status_list:
            progress_bar = tqdm_dict[str(target_status[status_element.id])]
            progress_bar.set_description(
                f'{str(target_status[status_element.id])} - '
                f'{DL_Util.DataLoader().interpret_target_status(target_status[status_element.status])}')
            progress_bar.update(target_status[status_element.upload_ratio] - progress_bar.n)
            for part_status in target_status[status_element.parts]:
                progress_bar = tqdm_dict[part_status[status_element.part_number]]
                progress_bar.set_description(
                    f'{part_status[status_element.part_number]} - '
                    f'{DL_Util.DataLoader().interpret_part_status(part_status[status_element.part_status])}')
                progress_bar.update(part_status[status_element.part_load_ratio] - progress_bar.n)

    @staticmethod
    def print_status(self, performance_loader):
        import PythonApi.DL_Util as DL_Util

        status_element = DL_Util.TargetStatusTags()
        target_status_list = []
        while performance_loader.operation_in_progress(operation=DL_Util.OperationType().upload,
                                                       status_data=target_status_list):
            for target_status in target_status_list:
                print("Target " + str(target_status[status_element.id]) + ": " + \
                      str(target_status[status_element.upload_ratio]) + "% (" + \
                      DL_Util.DataLoader().interpret_target_status(target_status[status_element.status]) + ")")
                for part_status in target_status[status_element.parts]:
                    print("| Part[" + part_status[status_element.part_number] + "]: " + \
                          DL_Util.DataLoader().interpret_part_status(
                              part_status[status_element.part_status]) + " (" + \
                          str(part_status[status_element.part_load_ratio]) + "%)")
            print("|")
            DL_Util.time.sleep(3)
        failed = False
        for target_status in target_status_list:
            if target_status[status_element.status] != DL_Util.DataLoader().target_status.complete:
                failed = True
            print("Target " + str(target_status[status_element.id]) + ": " + \
                  str(target_status[status_element.upload_ratio]) + "% (" + \
                  DL_Util.DataLoader().interpret_target_status(target_status[status_element.status]) + ")")
            for part_status in target_status[status_element.parts]:
                print("| Part[" + part_status[status_element.part_number] + "]: " + \
                      DL_Util.DataLoader().interpret_part_status(part_status[status_element.part_status]) + " (" + \
                      str(part_status[status_element.part_load_ratio]) + "%)")
        print("---------------------------------\n")

    @staticmethod
    def load_current_repository_parts(repository_id, performance_loader):
        import PythonApi.DL_Util as DL_Util
        part_number_objects = defaultdict(DL_Util.Part)
        part_list = performance_loader.list_all_parts(repository_id=repository_id)
        part_info_element = DL_Util.PartTags()
        for part in part_list:
            if part[part_info_element.part_available]:
                found_part = part_number_objects[part[part_info_element.part_number]]
                found_part.repository_id = part[part_info_element.repository_id]
                found_part.number = part[part_info_element.part_number]
                found_part.path = part[part_info_element.path]
                found_part.description = part[part_info_element.part_description]
        return part_number_objects

    @staticmethod
    def test_functions(performance_loader):
        import PythonApi.DL_Util as DL_Util
        result = performance_loader.find_targets()
        targets = performance_loader.list_all_loadable_targets()

        for target in targets:
            print(PerformanceLoader.target_from_dict(target))

        result = performance_loader.list_all_combined_targets()
        parts = performance_loader.list_all_parts(1)
        result = performance_loader.list_targets_for_part(PerformanceLoader.part_from_dict(parts[0]))

        result = performance_loader.list_all_download_parts(1)
        result = performance_loader.list_all_loadable_parts(1)
        result = performance_loader.dataloader.get_hardware_id(1)

        result = performance_loader.find_targets()
        result = performance_loader.find_targets()
        result = performance_loader.find_targets()
        result = performance_loader.find_targets()

    @staticmethod
    def convert_haf_folder_to_part_number(folder: str) -> str:
        return folder[:5] + '-' + folder[5:9] + '-' + folder[-4:]

    @staticmethod
    def part_from_dict(part: dict):
        import PythonApi.DL_Util as DL_Util
        part_info_element = DL_Util.PartTags()
        part_object = DL_Util.Part()
        part_info_element.repository_id = part[part_info_element.repository_id]
        part_info_element.number = part[part_info_element.part_number]
        part_info_element.path = part[part_info_element.path]
        part_info_element.description = part[part_info_element.part_description]
        return part_info_element

    @staticmethod
    def target_from_dict(target: dict):
        import PythonApi.DL_Util as DL_Util
        target_info_element = DL_Util.TargetTags()
        target_object = DL_Util.Target()
        target_object.target_id = target[target_info_element.load_target_id]

        match = re.match('([A-Z]*) ([0-9]*).*', target[target_info_element.load_target_name])
        if match:
            if 'SWITCH' in target[target_info_element.load_target_name]:
                target_object.hardware_id = 'SWITCH'
                target_object.position = str(int(match[2]) + 2)
            else:
                target_object.hardware_id = 'HNP' + match[1]
                target_object.position = str(int(match[2]))
        return target_object

    @staticmethod
    def parse_config_targets(config_path):
        import PythonApi.DL_Util as DL_Util
        targets = {}
        with open(config_path, encoding="utf-8") as config_xml:
            xml = config_xml.read()
        root = objectify.fromstring(xml)
        for target in root.Server.Targets.iterchildren():
            target_object = DL_Util.Target()
            target_object.hardware_id = target.attrib['HardwareId']
            target_object.position = target.attrib['Position']
            targets[target.attrib['Description']] = target_object
            # targets[target.attrib['Description']] = {'HardwareId': target.attrib['HardwareId'],
            #                                         'Position': target.attrib['Position'],
            #                                         'IpAddress': target.attrib['IpAddress']
            #                                         }
        return targets


class TestPerformanceLoader(unittest.TestCase):
    def test_load(self):
        setup_logging_from_config()
        loader = PerformanceLoader()
        loader.python_loader([('DPM2', 'HNP5eED120749')])
        loader.python_loader([('DPM2', 'HNP56EL120749')])

    def test_load_native(self):
        setup_logging_from_config()
        loader = PerformanceLoader()
        loader.native_loader([('DPM2', 'HNP5eED120749')])
        loader.native_loader([('DPM2', 'HNP56EL120749')])


if __name__ == "__main__":
    setup_logging_from_config()
    loader = PerformanceLoader()
    mode_control = ModeControl(connection_mode=ConnectionMode.SSH_PARAMIKO)

    restart_with_mode(mode_control, NodeType.DPM, 2, ModeType.BOOT)
    time.sleep(5)

    if True:
        loader.native_loader(['HNP51-EL12-0805',
                              'HNP36-ED12-0PVT', ])
    else:
        loader.native_loader(['HNP56-ED12-0772',
                              'HNP5e-EL12-0772', ])
    restart_with_mode(mode_control, NodeType.DPM, 2, ModeType.NORMAL)
