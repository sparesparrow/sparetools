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
// File Name: test_ata_manager.py
//
// Program:   TITAN
//
// Purpose:   TEST for ATA manager.
//
// Notes:     None
//
//********************************************************************************************
//********************************************************************************************
"""
from sparetools_aerospace.products.ngaims.test_common import TestPrepareCmcfDeps


class TestOmsAtaManagerSetup(TestPrepareCmcfDeps):
    def setUp(self) -> None:
        super(TestOmsAtaManagerSetup, self).setUp()
        self.ata_manager = self.maintenance_model_composition.ata_manager


class TestOmsAtaManager(TestOmsAtaManagerSetup):
    def test_get_all_ata(self):
        self.assertGreater(len(self.ata_manager.get_all_ata_chapters()), 0)

    def test_get_ata_section(self):
        ata_chapters = self.ata_manager.get_all_ata_chapters()
        first_id = list(ata_chapters.values())[0].id
        self.assertEqual(self.ata_manager.get_ata_chapter_by_id(first_id), list(ata_chapters.values())[0])

    def test_get_ata_chapter(self):
        ata_chapters = self.ata_manager.get_all_ata_chapters()
        for chapter in list(ata_chapters.values()):
            if len(chapter.ata_sections):
                test_ata_section = chapter.ata_sections[0].id
                ata_section = chapter.ata_sections[0]
        self.assertEqual(self.ata_manager.get_ata_section_by_id(test_ata_section), ata_section)
