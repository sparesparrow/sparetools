from sparetools.test_environments.jtag.program_flash import ProgramFlash, FlashConfiguration
from sparetools.test_environments.jtag.usb_manager import UsbManager
from sparetools.test_environments.mode_control.mode_control import ModeControl, ConnectionMode, SwitchModeType, \
    NodeType, ModeType, restart_with_mode
from ngapy.util.custom_logging import setup_logging_from_config


class JtagLoader:
    def __init__(self, usb_manager: UsbManager = None, mode_control: ModeControl = None,
                 program_flash: ProgramFlash = None):
        self.usb_manager = usb_manager if usb_manager else UsbManager()
        self.mode_control = mode_control if mode_control else ModeControl(connection_mode=ConnectionMode.SSH_PARAMIKO)
        self.program_flash = program_flash if program_flash else ProgramFlash()
        self.usb_config = self.usb_manager.parse_config_file()

    def flash_dpm_image(self, flash_configuration: FlashConfiguration, instance: int):
        flash_configuration.jtag_id = flash_configuration.jtag_id if flash_configuration.jtag_id else \
                                      self.usb_config[('DPM', str(instance))][2]
        restart_with_mode(self.mode_control, NodeType.SW, 1, SwitchModeType.NORMAL)
        restart_with_mode(self.mode_control, NodeType.SW, 2, SwitchModeType.NORMAL)
        self.usb_manager.disable_dpm_instance(0)
        self.usb_manager.enable_dpm_instance(instance)
        restart_with_mode(self.mode_control, NodeType.DPM, instance, ModeType.JTAG)
        self.program_flash.run_flash_command(flash_configuration)
        restart_with_mode(self.mode_control, NodeType.DPM, instance, ModeType.NORMAL)


def main():
    setup_logging_from_config()
    loader = JtagLoader()
    config = FlashConfiguration(r'd:\User\Michal\Builds\RR-PRVT-ISB782\Boot_MP\DPM_BOOT.bin',
                                r'\\az18stns04\AEROSPS\PLATFORMS\NGPLATFORM_B\Builds\ENGINEERING'
                                r'\V1_2022-75-004\SOURCE\EXTERNAL_DEPENDENCIES\BUILD_XILINX_HW_ABS_SVCS_APU_FSBL'
                                r'\link_output\HW_ABS_SVCS_APU_FSBL.elf',
                                '0x0',
                                None)

    #loader.flash_dpm_image(config, 2)
    #config.offset = '0x06600000'



    config.flash_binary = r'd:\User\Michal\Builds\TestLCD\Latest\GA_TITAN_DPM_2_Base_HW\LCD.bin'
    loader.flash_dpm_image(config, 2)
    #config.offset = '0x08400000'
    #config.flash_binary = r'd:\User\Michal\Builds\RR-PRVT-ISB749\Hyperstart_Output\flt_hypstart_DPM2.bin'
    #loader.flash_dpm_image(config, 2)

    #config = FlashConfiguration(r'd:\User\Michal\Builds\NT-PRVT-ISB751\Boot_MP\DPM_BOOT.bin',
    #
    #                            r'\\az18stns04\AEROSPS\PLATFORMS\NGPLATFORM_B\Builds\ENGINEERING'
    #                            r'\V8_2021-75-007\SOURCE\EXTERNAL_DEPENDENCIES\BUILD_XILINX_HW_ABS_SVCS_APU_FSBL'
    #                            r'\link_output\HW_ABS_SVCS_APU_FSBL.elf',
    #                            '0x0',
    #                            None)
    #loader.flash_dpm_image(config, 2)
    #config.offset = '0x06600000'
    #config.flash_binary = r'd:\User\Michal\Builds\NT-PRVT-ISB751\LCD\DPM2_LCD.bin'
    #loader.flash_dpm_image(config, 2)
    #config.offset = '0x08400000'
    #config.flash_binary = r'd:\User\Michal\Builds\NT-PRVT-ISB751\Hyperstart_Output\flt_hypstart_DPM2.bin'
    #loader.flash_dpm_image(config, 2)


if __name__ == "__main__":
    main()
