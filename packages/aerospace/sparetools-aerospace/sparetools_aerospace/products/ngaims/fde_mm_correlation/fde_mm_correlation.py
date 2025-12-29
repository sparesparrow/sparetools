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
from ngapy.io_platform.message_composition import get_complete_validity
from sparetools_aerospace.products.ngaims.fde_mm_common import FdeMmCommon


class OmsFdeMmCorrelation(FdeMmCommon):
    def __init__(self, item_description: dict, external_dependencies, internal_dependencies):
        self.external_dependencies = external_dependencies
        self.internal_dependencies = internal_dependencies
        self.fde_id = item_description['FdeId']
        self.mm_id = item_description['MmId']
        self.fde = internal_dependencies.flight_deck_effects_manager.search_by_id(self.fde_id)
        self.mm = internal_dependencies.maintenance_messages_manager.search_by_id(self.mm_id)

    # Note: It is your responsibility to set MS status (To set MM) and CAS validity/priority
    def set_status(self, status, validity=get_complete_validity()):
        self.fde.set_status(status, validity)
        self.mm.set_status(status, validity)
