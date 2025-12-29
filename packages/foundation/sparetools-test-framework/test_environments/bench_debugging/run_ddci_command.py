import os

from ngapy.util.custom_logging import setup_logging_from_config
from ngapy.util.execute_command import execute_command
from ngapy.util.setup_environment import get_repository_config


def get_ddci_root():
    config = get_repository_config()
    return config.conan_package_config.OpenArbor[2] / f'DDC-I_{config.conan_package_config.OpenArbor[1]}'


def run_ddci_command(command_with_arguments: str):
    ddci_root = get_ddci_root()
    rc, result = execute_command(
        rf'{ddci_root}\bin\env.exe /bin/python /desk/desk-environment.py cmd.exe /c {command_with_arguments}')
    print('\n'.join(result))
    return rc, result


if __name__ == "__main__":
    setup_logging_from_config()
    os.environ['DESK_IP_ADDR'] = '10.16.1.33'
    run_ddci_command(r'tarattrib -debugServicesHonored DEOS')
    run_ddci_command(
        rf'tardebug -target=arm -processHandle=0x14070000 -targetIPAddr={os.environ["DESK_IP_ADDR"]} targetIPPort=1028 -debug -startDbgProcessOnly')
