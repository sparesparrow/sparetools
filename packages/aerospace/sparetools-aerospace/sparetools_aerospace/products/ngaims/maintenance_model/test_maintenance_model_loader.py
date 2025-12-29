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
// File Name: test_maintenance_model_loader.py
//
// Program:   TITAN
//
// Purpose:   TEST of maintenance model loader
//
// Notes:     None
//
//********************************************************************************************
//********************************************************************************************
"""
from unittest import TestCase

from sparetools_aerospace.products.ngaims.test_common import create_tcrf_model_loader, TestPrepareCmcfDeps


class TestMaintenanceModelLoaderSetupLdi(TestPrepareCmcfDeps):
    def setUp(self) -> None:
        super(TestMaintenanceModelLoaderSetupLdi, self).setUp()


class TestMaintenanceModelLoaderSetupOmi(TestPrepareCmcfDeps):
    def setUp(self) -> None:
        super(TestMaintenanceModelLoaderSetupOmi, self).setUp()


class TestMaintenanceModelLoaderSetupTcrf(TestCase):
    def setUp(self) -> None:
        self.maintenance_model_loader = create_tcrf_model_loader()


class TestMaintenanceModelLoaderLdi(TestMaintenanceModelLoaderSetupLdi):
    def test_load_ldi(self):
        self.assertGreater(len(self.maintenance_model_loader.get_model_data()), 0)
        pass

    def test_back_reference(self):
        maintenance_messages = self.maintenance_model_loader.get_table_data_in_list('Mm')
        first_mm = maintenance_messages[1]
        ata_sec_id = first_mm['AtaMajorSecId']
        ata_sec = self.maintenance_model_loader.get_table_dict('AtaMajorSec')
        ata_sec_back = self.maintenance_model_loader.get_back_reference('AtaMajorSec', 'Mm', first_mm['Id'])
        self.assertEqual(ata_sec_back, ata_sec[ata_sec_id])


class TestMaintenanceModelLoaderOmi(TestMaintenanceModelLoaderSetupOmi):
    def test_load_omi(self):
        self.assertGreater(len(self.maintenance_model_loader.get_model_data()), 0)
        pass


class TestMaintenanceModelLoaderTcrf(TestMaintenanceModelLoaderSetupTcrf):
    def test_load_tcrf(self):
        self.assertGreater(len(self.maintenance_model_loader.get_model_data()), 0)
        pass
