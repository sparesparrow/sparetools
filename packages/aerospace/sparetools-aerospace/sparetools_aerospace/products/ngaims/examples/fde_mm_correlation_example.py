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
from time import sleep

from ngapy.bench.bench_factory import BenchStarter
from sparetools_aerospace.products.ngaims.maintenance_model.maintenance_model_composition import MaintenanceModelComposition
from sparetools_aerospace.products.ngaims.test_common import prepare_external_dependencies
from sparetools_aerospace.products.ngaims.test_execution.run_test_functions import prepare_cmcf_bench
from ngapy.util.custom_logging import setup_logging_from_config

CAS_MASTER_INSTANCE = 10


if __name__ == "__main__":
    setup_logging_from_config()
    prepare_cmcf_bench()
    with BenchStarter():
        model, external_dependencies = prepare_external_dependencies()
        maintenance_model = MaintenanceModelComposition(model, external_dependencies)
        fde_manager = maintenance_model.flight_deck_effects_manager
        mm_manager = maintenance_model.maintenance_messages_manager
        ms_manager = maintenance_model.member_systems_manager
        correlation_manager = maintenance_model.fde_mm_correlation_manager
        fde_manager.set_active_cas_master_instance(CAS_MASTER_INSTANCE)
        ms_manager.set_all_ms_status()
        correlation_manager.set_all_correlations()
        sleep(5)
        correlations = correlation_manager.get_all_active_correlations()
        active_fdes = fde_manager.get_all_active_fdes()
        active_mms = mm_manager.get_all_active_mms()
        pass
