import os
import time
from pathlib import Path

from sparetools.test_environments.bench_debugging.parse_dbg_files import compose_source_map, compose_ld_library_path
from sparetools.test_environments.bench_debugging.run_ddci_command import run_ddci_command, get_ddci_root
from sparetools.test_environments.bench_debugging.statmon import StatmonReader
from sparetools.test_environments.desk_environment.desk_environment import setup_desk_environment
from ngapy.util.custom_logging import setup_logging_from_config
from ngapy.util.execute_command import execute_command


def prepare_vs_debugging(build_path, ip='10.16.1.33', application_name='MaintenanceCMCF', with_module_reset=False):
    os.environ['DESK_IP_ADDR'] = ip
    os.environ['DDCI_Home'] = str(get_ddci_root()).replace('\\', '\\\\')
    os.environ['LD_LIBRARY_PATH'] = compose_ld_library_path(build_path)
    if with_module_reset:
        run_ddci_command(r'tarattrib -downloadingPermitted=true DEOS')
        time.sleep(5)
    run_ddci_command(r'tarattrib -downloadingPermitted=false DEOS')
    time.sleep(5)
    process_list = StatmonReader(ip, 1026).read_process_list()
    run_ddci_command(r'tarattrib -debugServicesHonored DEOS')
    rc, result = run_ddci_command(
        rf'tardebug -target=arm -processHandle={process_list[application_name][0]} -targetIPAddr={os.environ["DESK_IP_ADDR"]} targetIPPort=1028 -debug -startDbgProcessOnly')
    if rc == 0:
        for line in result:
            if 'gdbserver port is' in line:
                gdb_port = [int(s) for s in line.split() if s.isdigit()][0]
                os.environ['GDBSRV_PORT'] = str(gdb_port)

    with open(Path(__file__).parent / 'launch.vs.json', 'r') as vs_launch_config:
        os.makedirs(build_path / '.vs', exist_ok=True)
        with open(build_path / '.vs' / 'launch.vs.json', 'w') as target_vs_launch_config:
            formatted = vs_launch_config.read().replace('source_file_map', compose_source_map(build_path))
            target_vs_launch_config.write(formatted)


def run_visual_studio(vs_location=r'C:\Program Files (x86)\Microsoft Visual Studio\2017\Professional\Common7\IDE\devenv.exe',
                      project_dir=r'd:\User\Michal\Repos\oms-dev\_Build'):
    setup_desk_environment(get_ddci_root())
    execute_command(
        f'"{vs_location}" {project_dir} /Project',
        wait_till_finish=False)


if __name__ == "__main__":
    setup_logging_from_config()
    build_path = Path(r'd:\User\Michal\Repos\oms-dev\_Build')
    prepare_vs_debugging(build_path, ip='10.16.1.33', application_name='MaintenanceTCRF', with_module_reset=True)
    run_visual_studio()
