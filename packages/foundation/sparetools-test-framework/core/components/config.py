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
"""
//********************************************************************************************
//
//
// File Name: config.py
//
// Program:   TITAN
//
// Purpose:   Config class for results and logging.
//
// Notes:     TODO: This might be removed and data stored into yaml config
//
//********************************************************************************************
//********************************************************************************************
"""


class SingletonType(type):
    """Simple singleton metaclass to replace ngapy.util.singleton.SingletonType"""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Config(metaclass=SingletonType):

    def __init__(self):
        self.opytee_log_path = None
        self.opytee_results_dir_path = None
        self.opytee_workarea_dir_path = None

    def get_opytee_log_path(self):
        return self.opytee_log_path

    def set_opytee_log_path(self, path):
        self.opytee_log_path = path

    def get_opytee_results_dir_path(self):
        return self.opytee_results_dir_path

    def set_opytee_results_dir_path(self, path):
        self.opytee_results_dir_path = path

    def get_opytee_workarea_dir_path(self):
        return self.opytee_workarea_dir_path

    def set_opytee_workarea_dir_path(self, path):
        self.opytee_workarea_dir_path = path
