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
// File Name: test_maintenance_message_manager.py
//
// Program:   TITAN
//
// Purpose:   TEST for MM manager
//
// Notes:     None
//
//********************************************************************************************
//********************************************************************************************
"""
from sparetools_aerospace.products.ngaims.test_common import TestPrepareCmcfDeps


class TestMmManagerFactorySetup(TestPrepareCmcfDeps):
    def setUp(self) -> None:
        super(TestMmManagerFactorySetup, self).setUp()
        self.mm_manager = self.maintenance_model_composition.maintenance_messages_manager


class TestMmManagerFactory(TestMmManagerFactorySetup):
    def test_get_all_mm(self):
        self.assertGreater(len(self.mm_manager.get_all_mms()), 0)
