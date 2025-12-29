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
// File Name: ambiguous_maintenance_message.py
//
// Program:   TITAN
//
// Purpose:   Ambiguous MM representation class.
//
// Notes:     None
//
//********************************************************************************************
//********************************************************************************************
"""


# LDI Table - AmbiguousMmHasPattern
class OmsAmbiguousMmFrPos:
    def __init__(self, fr_description, parent):
        self.parent = parent
        self.fr_id = fr_description[1]['FrId']
        self.position = fr_description[1]['Position']


# LDI Table - IsolatedMmHasPattern
class OmsAmbiguousMmIsoPattern:
    def __init__(self, iso_description, parent):
        self.parent = parent
        self.iso_mm_id = iso_description[1]['IsolatedMmId']
        self.pattern = iso_description[1]['Pattern']


# LDI Table - AmbiguousMm
class OmsAmbiguousMm:
    def __init__(self, item_description: dict, external_dependencies, internal_dependencies, parent):
        self.external_dependencies = external_dependencies
        self.internal_dependencies = internal_dependencies
        self.id = item_description['Id']
        self.sequence_id = item_description['ContId']
        self.mm_id = item_description['MmId']
        self.default_mm_id = item_description['DefaultMmId']

        self.fr_positions = []
        for fr_description in item_description['AmbiguousMmPatternFrs']:
            self.fr_positions.append(OmsAmbiguousMmFrPos(fr_description, self))

        self.iso_patterns = []
        for iso_description in item_description['IsolatedMmPatternMms']:
            self.iso_patterns.append(OmsAmbiguousMmIsoPattern(iso_description, self))
