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
from sparetools_aerospace.products.ngaims.constants import MsDispStatus
from sparetools_aerospace.products.ngaims.filter_samples import Functor, id_limit_function
from sparetools_aerospace.products.ngaims.maintenance_model.maintenance_model_composition import MaintenanceModelComposition
from sparetools_aerospace.products.ngaims.test_common import prepare_external_dependencies
from sparetools_aerospace.products.ngaims.test_execution.run_test_functions import prepare_cmcf_bench
from ngapy.util.custom_logging import setup_logging_from_config


if __name__ == "__main__":
    setup_logging_from_config()
    prepare_cmcf_bench()
    with BenchStarter():
        model, external_dependencies = prepare_external_dependencies()
        mm_manager = MaintenanceModelComposition(model, external_dependencies).maintenance_messages_manager
        member_systems_manager = MaintenanceModelComposition(model, external_dependencies).member_systems_manager
        member_systems_manager.set_all_ms_status(MsDispStatus.NORM_OP)

        mm_list = mm_manager.get_all_mms()
        mm_manager.set_all_mms(True)
        # This is crashing Onboard CMCF. Already communicated with team.
        # mm_manager.set_all_mms(True)
        sleep(5)
        rst = mm_manager.get_all_active_mms()
        for mm in mm_list.values():
            if mm in rst:
                print(f'{mm.id}/{mm.name} successfully set to Active')
            else:
                print(f'{mm.id}/{mm.name} failed set to Active')

        print(rst)
