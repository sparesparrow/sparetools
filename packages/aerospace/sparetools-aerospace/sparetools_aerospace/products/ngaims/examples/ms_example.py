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
import pprint
from time import sleep

from ngapy.bench.bench_factory import BenchStarter
from sparetools_aerospace.products.ngaims.constants import MsDispStatus
from sparetools_aerospace.products.ngaims.filter_samples import Functor, equality
from sparetools_aerospace.products.ngaims.maintenance_model.maintenance_model_composition import MaintenanceModelComposition
from sparetools_aerospace.products.ngaims.test_common import prepare_external_dependencies
from sparetools_aerospace.products.ngaims.test_execution.run_test_functions import prepare_cmcf_bench
from ngapy.util.custom_logging import setup_logging_from_config

if __name__ == "__main__":
    setup_logging_from_config()

    model, external_dependencies = prepare_external_dependencies()
    member_systems_manager = MaintenanceModelComposition(model, external_dependencies).member_systems_manager

    #member_systems_manager.set_all_ms_status(MsDispStatus.NORM_OP)

    member_systems_manager.set_all_ms_status(MsDispStatus.FN_TEST)
    sleep(10)
    member_systems_manager.set_all_ms_status(MsDispStatus.IO_FAILURE)
    sleep(10)
    member_systems_manager.set_all_ms_status(MsDispStatus.LRU_NO_COMM)
    sleep(10)