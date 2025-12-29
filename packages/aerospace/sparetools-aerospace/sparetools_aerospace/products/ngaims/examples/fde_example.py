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


def clean_fdes():
    fde_manager.set_all_fdes(False)
    sleep(5)
    fde_manager.get_all_active_fdes()


if __name__ == "__main__":
    setup_logging_from_config()
    prepare_cmcf_bench()
    with BenchStarter():
        model, external_dependencies = prepare_external_dependencies()
        fde_manager = MaintenanceModelComposition(model, external_dependencies).flight_deck_effects_manager
        fde_manager.set_active_cas_master_instance()
        # select first CAS master instance
        fde_manager.set_active_cas_master_instance(fde_manager.cas_master_instances[0])
        clean_fdes()

        cas_fdes = fde_manager.filter_by_attribute(fde_manager.get_functor_for_cas_fdes())
        generic_fdes = fde_manager.filter_by_attribute(fde_manager.get_functor_for_generic_fdes())

        single_cas_fde = cas_fdes[0]
        # set Source Select signal for setting FDE
        single_cas_fde.set_status(False)
        # set manually selected signal for CAS FDE - result in this case is, that FDE is not set, CAS Master is [0]
        single_cas_fde.set_status(True, instance=fde_manager.cas_master_instances[1])

        fde_manager.set_all_fdes([1, 1], cas_fdes)
        sleep(5)
        active_fdes = fde_manager.get_all_active_fdes()
        print(len(active_fdes), active_fdes)
        clean_fdes()

        fde_manager.set_all_fdes([1, 0], cas_fdes)
        sleep(5)
        active_fdes = fde_manager.get_all_active_fdes()
        inhibited_active_fdes = fde_manager.get_all_inhibited_fdes()
        print(len(active_fdes), active_fdes)
        print(len(inhibited_active_fdes), inhibited_active_fdes)

        clean_fdes()

        fde_manager.set_all_fdes(True, generic_fdes)
        sleep(5)
        active_fdes = fde_manager.get_all_active_fdes()
        print(len(active_fdes), active_fdes)

        clean_fdes()

        transitions = fde_manager.get_transitions_fdes()
