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
// File Name: ata_manager.py
//
// Program:   TITAN
//
// Purpose:   ATA manager class.
//
// Notes:     None
//
//********************************************************************************************
//********************************************************************************************
"""
from sparetools_aerospace.products.ngaims.ata.ata_chapter import OmsAtaChapter
from sparetools_aerospace.products.ngaims.maintenance_model.model_base_manager import ModelBaseManager


class OmsAtaManager(ModelBaseManager):
    def __init__(self, maintenance_model, external_dependencies):
        super(OmsAtaManager, self).__init__()
        ata_model = maintenance_model.get_table_dict('AtaCh')
        for key, value in ata_model.items():
            self.model_dict[key] = OmsAtaChapter(value, external_dependencies)

    def get_ata_chapter_by_id(self, ata_chapter_id):
        return super(OmsAtaManager, self).search_by_id(ata_chapter_id)

    def get_ata_section_by_id(self, ata_section):
        for chapter in self.get_all_ata_chapters().values():
            for section in chapter.ata_sections:
                if section.id == ata_section:
                    return section
        return None

    def get_all_ata_chapters(self):
        return super(OmsAtaManager, self).get_table_dict()
