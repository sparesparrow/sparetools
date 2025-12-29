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
import random
import string
from time import sleep

from ngapy.bench.bench_factory import BenchStarter
from sparetools_aerospace.products.ngaims.constants import MsDispStatus
from sparetools_aerospace.products.ngaims.maintenance_model.maintenance_model_composition import MaintenanceModelComposition
from sparetools_aerospace.products.ngaims.test_common import prepare_external_dependencies
from sparetools_aerospace.products.ngaims.test_execution.run_test_functions import prepare_cmcf_bench
from ngapy.util.custom_logging import setup_logging_from_config

if __name__ == "__main__":
    setup_logging_from_config()
    prepare_cmcf_bench()
    with BenchStarter():
        model, external_dependencies = prepare_external_dependencies()
        member_systems_manager = MaintenanceModelComposition(model, external_dependencies).member_systems_manager

        mss = member_systems_manager.get_all_mss()
        member_systems_manager.set_all_ms_status(MsDispStatus.NORM_OP)
        member_systems_manager.run_system_config_simulation()
        for i in range(100):
            for ms in member_systems_manager.get_all_mss().values():
                for ms_config in ms.ms_configs:
                    ms.set_system_config_data(ms_config.FnId, str(ms_config.FnId) + ' ' + ''.join(
                        random.choices(string.ascii_letters + string.digits,
                                       k=random.randrange(0, 10))))
            delays = [ms.delay_to_transmit_all_system_configs() for ms in member_systems_manager.get_all_mss().values()]
            sleep(max(delays))
            all_ms_config_values = member_systems_manager.get_all_ms_config_values()
            pprint.pprint(vars(all_ms_config_values), indent=1)

        member_systems_manager.stop_system_config_simulation()
