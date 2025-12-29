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
// File Name: ata_section.py
//
// Program:   TITAN
//
// Purpose:   ATA section representing class.
//
// Notes:     None
//
//********************************************************************************************
//********************************************************************************************
"""


class OmsAtaSection:
    def __init__(self, item_description: dict, external_dependencies, parent):
        self.external_dependencies = external_dependencies
        self.id = item_description['Id']
        self.sequence_id = item_description['ContId']
        self.ata_chapter_id = item_description['AtaChId']
        self.ata_chapter = parent
        self.number = item_description['MajorNumber']
        self.name = item_description['Name']

    def get_full_ata_name(self):
        return f'{self.parent.name} - {self.ata.number} {self.name}'
