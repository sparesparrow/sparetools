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
import os
from unittest import TestCase

from pathlib import Path

from sparetools.core.configuration import get_config_manager
from sparetools.core.configuration.config_manager import get_conan_merged_configuration


class Test(TestCase):
    def test_get_config_manager(self):
        cl1 = get_config_manager()
        cl2 = get_config_manager()
        self.assertEqual(cl1, cl2)

        cl3 = get_config_manager(additional_arguments={'ENV_TARGET_PATH': 'Test',
                                                      'bamboo_working_directory': 'Test'})
        self.assertNotEqual(cl1, cl3)

    def test_config_without_conan(self):
        conf = get_conan_merged_configuration(Path(__file__).parent / 'test')
        self.assertIsNotNone(conf)


# Commented out conan-dependent tests as they require ngapy conan integration
# class TestWithConan(ConanFunctionsTestsSetup):
#     def test_config_with_conan(self):
#         install_packages_for_repository(self.conan_path)
#         conf = get_conan_merged_configuration(self.conan_path)
#         self.assertIsNotNone(conf)
