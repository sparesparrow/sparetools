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
from sparetools_aerospace.products.ngaims.test_common import TestPrepareCmcfDeps


class TestOmsCmcfFaultReportManagerSetup(TestPrepareCmcfDeps):
    def setUp(self) -> None:
        super(TestOmsCmcfFaultReportManagerSetup, self).setUp()
        self.cmcf_fault_report_manager = self.maintenance_model_composition.cmcf_fault_report_manager


class TestOmsCmcfFaultReportManager(TestOmsCmcfFaultReportManagerSetup):
    def test_get_cmcf_frs(self):
        self.assertGreater(len(self.cmcf_fault_report_manager.get_all_cmcf_fault_reports()), 0)
