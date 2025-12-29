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
import os
import time
import logging
from filecmp import cmp
from pathlib import Path

from sparetools_aerospace.products.ngaims.file_transfer_apps.file_transfer_apps import Bdtte
from sparetools_aerospace.products.ngaims.test_execution.run_test_functions import prepare_cmcf_bench
from ngapy.bench.bench_factory import BenchStarter
from ngapy.util.custom_logging import setup_logging_from_config

log = logging.getLogger('__main__.' + __name__)

TARGET_LOCAL_DIR = os.environ["ENV_REPOSITORY_ROOT"] + "\\Build\\TARS_Lab_INSU1\\GA_TITAN\\APU\\MP00\\"
SRC_FILE = TARGET_LOCAL_DIR + "1_cmcf_hdb_info.txt"
DST_FILE = TARGET_LOCAL_DIR + "cmcf_hdb_info.txt"

if __name__ == "__main__":
    file_existed = False
    try:
        with open(SRC_FILE, mode='x') as file:
            file.write('42')
    except FileExistsError:
        file_existed = True

    setup_logging_from_config()
    with Bdtte() as bdtte:
        prepare_cmcf_bench()
        with BenchStarter():
            time.sleep(5)

        transfer_info = bdtte.get_file_transfers()[0]
        expected_dest = Path(DST_FILE).resolve(strict=False)
        real_dest = transfer_info.destination.resolve(strict=False)
        if real_dest != expected_dest:
            log.info('Destination path is wrong')

    if os.path.isfile(DST_FILE) and cmp(SRC_FILE, DST_FILE, shallow=False):
        log.info('File successfully transferred')
    else:
        log.info('Something went wrong')

    if not file_existed:
        os.remove(SRC_FILE)
    os.remove(DST_FILE)
