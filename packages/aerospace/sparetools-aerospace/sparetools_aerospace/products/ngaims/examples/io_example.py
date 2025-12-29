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
import math
import random

from ngapy.bench.bench_factory import BenchStarter
from ngapy.io_platform.message_composition import get_complete_validity
from sparetools_aerospace.products.ngaims.io_parameters.parameters_manager import IoParameterType
from sparetools_aerospace.products.ngaims.test_common import prepare_external_dependencies
from sparetools_aerospace.products.ngaims.test_execution.run_test_functions import prepare_cmcf_bench
from ngapy.util.custom_logging import setup_logging_from_config

if __name__ == "__main__":
    setup_logging_from_config()
    prepare_cmcf_bench()
    with BenchStarter():
        model, external_dependencies = prepare_external_dependencies()
        all_params = external_dependencies.input_io_manager.get_table_data_in_list()
        #tested_params = []
        #tested_params_count = 10
        #current_params_count = 0
        #for param in all_params:
        #    if param.port_type == IoParameterType.VT_FLOAT32_e:
        #        tested_params.append(param)
        #        current_params_count += 1
        #    if current_params_count >= tested_params_count:
        #        break

        for i in range(100):
            set_vector = [(int(random.randint(0, 255)), get_complete_validity()) for i in range(len(all_params))]
            external_dependencies.input_io_manager.set_values(all_params, set_vector)
            get_vector = external_dependencies.input_io_manager.get_values(all_params)
        #for index in range(len(all_params)):
        #    if not math.isclose(set_vector[index][0], get_vector[index][0], rel_tol=1e-5):
        #        assert False
        #    assert set_vector[index][1] == get_vector[index][1]
