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
// Copyright: Honeywell International, 2021
//
// File Name: test_lru_manager.py
//
// Program:   TITAN
//
// Purpose:   TEST for LRU manager
//
// Notes:     None
//
//********************************************************************************************
//********************************************************************************************
"""
from sparetools_aerospace.products.ngaims.test_common import TestPrepareCmcfDeps


class TestLruManagerFactorySetup(TestPrepareCmcfDeps):
    def setUp(self) -> None:
        super(TestLruManagerFactorySetup, self).setUp()
        self.lru_manager = self.maintenance_model_composition.lru_manager


class TestMmManagerFactory(TestLruManagerFactorySetup):
    def test_get_all_mm(self):
        self.assertGreater(len(self.lru_manager.get_all_lrus()), 0)
