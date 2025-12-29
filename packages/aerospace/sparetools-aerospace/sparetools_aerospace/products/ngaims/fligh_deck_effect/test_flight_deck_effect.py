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
// File Name: test_flight_deck_effect.py
//
// Program:   TITAN
//
// Purpose:   TEST for Flight Deck Effect
//
// Notes:     None
//
//********************************************************************************************
//********************************************************************************************
"""
from sparetools_aerospace.products.ngaims.test_common import TestPrepareCmcfDeps


class TestFdeManagerFactorySetup(TestPrepareCmcfDeps):
    def setUp(self) -> None:
        super(TestFdeManagerFactorySetup, self).setUp()
        self.rc_manager = self.maintenance_model_composition.root_cause_manager
        self.fde_manager = self.maintenance_model_composition.flight_deck_effects_manager
        self.fde_severity_manager = self.maintenance_model_composition.flight_deck_effect_severity_manager


class TestFdeManagerFactory(TestFdeManagerFactorySetup):
    def test_get_all_mm(self):
        self.assertGreater(len(self.rc_manager.get_all_rcs()), 0)
        self.assertGreater(len(self.fde_manager.get_all_fdes()), 0)
        # self.assertGreater(len(self.fde_severity_manager.get_all_fde_severities()), 0)
