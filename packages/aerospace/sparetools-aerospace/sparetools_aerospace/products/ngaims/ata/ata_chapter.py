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
// File Name: ata_chapter.py
//
// Program:   TITAN
//
// Purpose:   ATA Chapter representing class.
//
// Notes:     None
//
//********************************************************************************************
//********************************************************************************************
"""
from sparetools_aerospace.products.ngaims.ata.ata_section import OmsAtaSection


class OmsAtaChapter:
    def __init__(self, item_description: dict, external_dependencies):
        self.external_dependencies = external_dependencies
        self.id = item_description['Id']
        self.sequence_id = item_description['ContId']
        self.number = item_description['Number']
        self.name = item_description['Name']
        self.ata_sections = []
        for ata_section in item_description['AtaMajorSecs']:
            self.ata_sections.append(OmsAtaSection(ata_section, external_dependencies, self))
