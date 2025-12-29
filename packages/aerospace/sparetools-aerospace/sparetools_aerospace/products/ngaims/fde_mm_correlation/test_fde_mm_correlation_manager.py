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


class TestOmsFdeMmCorrelationManagerSetup(TestPrepareCmcfDeps):
    def setUp(self) -> None:
        super(TestOmsFdeMmCorrelationManagerSetup, self).setUp()
        self.fde_mm_correlation_manager = self.maintenance_model_composition.fde_mm_correlation_manager


class TestOmsFdeMmCorrelationManager(TestOmsFdeMmCorrelationManagerSetup):
    def test_get_all_correlations(self):
        self.assertGreater(len(self.fde_mm_correlation_manager.get_all_correlations()), 0)
