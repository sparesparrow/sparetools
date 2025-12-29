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
from unittest import TestCase

from ngapy.bench.bench_factory import BenchStarter
from sparetools_aerospace.products.ngaims.examples.ate_example import execute_all_ate_apis
from sparetools_aerospace.products.ngaims.test_common import prepare_full_external_dependencies_for_cmcf_unit_test, \
    prepare_external_dependencies
from ngapy.util.custom_logging import setup_logging_from_config


class TestOmsCmcfAteMessages(TestCase):
    def test_get_all_ate_messages(self):
        setup_logging_from_config()
        prepare_full_external_dependencies_for_cmcf_unit_test()
        with BenchStarter():
            model, external_dependencies = prepare_external_dependencies()
            execute_all_ate_apis(external_dependencies.ate)
