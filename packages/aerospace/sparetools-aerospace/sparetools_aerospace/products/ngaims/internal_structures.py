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
// File Name: internal_structures.py
//
// Program:   TITAN
//
// Purpose:   internal structures.
//
// Notes:     None
//
//********************************************************************************************
//********************************************************************************************
"""


class Ata:
    def __init__(self, item_description: dict):
        self.ata_chapter_name = item_description['AsecName']
        self.ata_chapter_number = item_description['AsecNumber']
        self.ata_section_name = item_description['AchName']
        self.ata_section_number = item_description['AchNumber']
