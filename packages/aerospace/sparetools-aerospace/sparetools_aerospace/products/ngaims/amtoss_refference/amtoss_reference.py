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
// File Name: amtoss_reference.py
//
// Program:   TITAN
//
// Purpose:   Amtoss Reference unit representation class.
//
// Notes:     None
//
//********************************************************************************************
//********************************************************************************************
"""


class OmsAmtossReference:
    def __init__(self, item_description: dict, external_dependencies, internal_dependencies):
        self.external_dependencies = external_dependencies
        self.internal_dependencies = internal_dependencies
        self.id = item_description['Id']
        self.sequence_id = item_description['ContId']
        self.doc_type = item_description['DocType']
        self.ata_chapter_id = item_description['AtaChapterId']
        self.ata_section = item_description['AtaSection']
        self.ata_subject = item_description['AtaSubject']
        self.unit_nbr = item_description['UnitNbr']
        self.function_code = item_description['FunctionCode']
        self.seq_nbr = item_description['SeqNbr']
        self.config = item_description['Config']
        self.variant_nbr = item_description['VariantNbr']
        self.scheme_nbr = item_description['SchemeNbr']
        self.figure_nbr = item_description['FigureNbr']
        self.page_nbr = item_description['PageNbr']
        self.item_nbr = item_description['ItemNbr']
        self.part_nbr = item_description['PartNbr']
        self.effectivity = item_description['Effectivity']
        self.jic_nbr = item_description['JicNbr']
        self.other = item_description['Other']
