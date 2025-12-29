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
// File Name: test_member_systems.py
//
// Program:   TITAN
//
// Purpose:   TEST for member system/manager.
//
// Notes:     None
//
//********************************************************************************************
//********************************************************************************************
"""
import re
from time import sleep

from sparetools_aerospace.products.ngaims.ata.ata_section import OmsAtaSection
from sparetools_aerospace.products.ngaims.constants import MsDispStatus
from sparetools_aerospace.products.ngaims.filter_samples import combine_or, Functor, equality
from sparetools_aerospace.products.ngaims.member_systems.member_system import OmsMemberSystem
from sparetools_aerospace.products.ngaims.test_common import TestPrepareCmcfDeps


def demo_regex_function(value, attributes):
    if re.match(attributes[0], value):
        return True
    return False


class TestOmsMemberSystemsManagerSetup(TestPrepareCmcfDeps):
    def setUp(self) -> None:
        super(TestOmsMemberSystemsManagerSetup, self).setUp()
        self.member_systems_manager = self.maintenance_model_composition.member_systems_manager
        self.test_ms = self.member_systems_manager.get_table_data_in_list()[0]


class TestOmsMemberSystemsManager(TestOmsMemberSystemsManagerSetup):
    def test_get_all_mss(self):
        self.assertGreater(len(self.member_systems_manager.get_all_mss()), 0)

    def test_get_ms_by_mnemonic(self):
        self.assertIsInstance(self.member_systems_manager.get_ms_by_mnemonic(self.test_ms.mnemonic), OmsMemberSystem)
        self.assertEqual(
            self.member_systems_manager.get_ms_by_mnemonic(self.test_ms.mnemonic.lower(), case_sensitive=True), None)
        self.assertIsInstance(
            self.member_systems_manager.get_ms_by_mnemonic(self.test_ms.mnemonic.lower(), case_sensitive=False),
            OmsMemberSystem)

    def test_get_ms_by_name(self):
        self.assertIsInstance(self.member_systems_manager.get_ms_by_name(self.test_ms.name),
                              OmsMemberSystem)
        self.assertIsInstance(self.member_systems_manager.get_ms_by_name(self.test_ms.name.lower(),
                                                                         case_sensitive=False),
                              OmsMemberSystem)

    def test_get_ms_by_id(self):
        self.assertEqual(self.member_systems_manager.get_ms_by_name(self.test_ms.name),
                         self.member_systems_manager.get_ms_by_id(self.test_ms.id))

    #def test_set_all_ms_active(self):
    #    self.member_systems_manager.set_all_ms_status()
    #    sleep(5)
    #    self.member_systems_manager.get_all_ms_status()
    #    active_by_ata_ms_list = self.member_systems_manager.filter_by_attribute(
    #        Functor(equality, 'ate_status', MsDispStatus.NORM_OP))
    #    self.assertGreater(len(active_by_ata_ms_list), 0)

    def test_get_ata_information(self):
        member_system = self.member_systems_manager.get_ms_by_id(self.test_ms.id)
        ata_section = member_system.get_ata_section()
        self.assertIsInstance(ata_section, OmsAtaSection)

    def test_filter(self):
        functor1 = Functor(demo_regex_function, 'name', r'.*Central.*')
        functor2 = Functor(demo_regex_function, 'name', r'.*Radar.*')
        filter_list = self.member_systems_manager.filter_by_attribute([functor1, functor2],
                                                                      combination_function=combine_or)
        self.assertGreater(len(filter_list), 0)

