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
"""
//********************************************************************************************
//
//
// File Name: maintenance_model_composition.py
//
// Program:   TITAN
//
// Purpose:   Maintenance model composition
//
// Notes:     None
//
//********************************************************************************************
//********************************************************************************************
"""
import munch

from sparetools_aerospace.products.ngaims.amtoss_refference.amtoss_reference_manager import OmsAmtossReferenceManager
from sparetools_aerospace.products.ngaims.ata.ata_manager import OmsAtaManager
from sparetools_aerospace.products.ngaims.bus.bus_manager import OmsBusManager
from sparetools_aerospace.products.ngaims.cmcf_fault_reports.cmcf_fault_report_manager import OmsCmcfFaultReportManager
from sparetools_aerospace.products.ngaims.fde_mm_correlation.fde_mm_correlation_manager import OmsFdeMmCorrelationManager
from sparetools_aerospace.products.ngaims.fligh_deck_effect.flight_deck_effect_severity_manager import \
    OmsFlightDeckEffectSeverityManager
from sparetools_aerospace.products.ngaims.fligh_deck_effect.flight_deck_effects_manager import OmsFlightDeckEffectManager
from sparetools_aerospace.products.ngaims.fligh_deck_effect.root_cause_manager import OmsRootCauseManager
from sparetools_aerospace.products.ngaims.flight_phase.flight_phase_manager import OmsOmsFlightPhaseManager
from sparetools_aerospace.products.ngaims.lru.lru_manager import OmsLruManager
from sparetools_aerospace.products.ngaims.maintenance_messages.ambiguous_maintenance_messages_manager import \
    OmsAmbiguousMaintenanceMessageManager
from sparetools_aerospace.products.ngaims.maintenance_messages.maintenance_messages_manager import OmsMaintenanceMessageManager
from sparetools_aerospace.products.ngaims.member_systems.member_systems_manager import OmsMemberSystemsManager
from sparetools_aerospace.products.ngaims.nvm.nvm_manager import OmsNvmFilesManager, OmsNvmCollectionManager
from sparetools_aerospace.products.ngaims.fault_report.fault_report_manager import FaultReportManager


class MaintenanceModelComposition:
    # Maintenance model and dependencies are out to have this module testable
    def __init__(self, maintenance_model, external_dependencies):
        self.nvm_files_manager = OmsNvmFilesManager(maintenance_model, external_dependencies)
        self.nvm_collections_manager = OmsNvmCollectionManager(maintenance_model, external_dependencies)

        self.flight_phase_manager = OmsOmsFlightPhaseManager(maintenance_model, external_dependencies)
        self.bus_manager = OmsBusManager(maintenance_model, external_dependencies)
        self.lru_manager = OmsLruManager(maintenance_model, external_dependencies)
        self.ata_manager = OmsAtaManager(maintenance_model, external_dependencies)

        self.amtoss_reference_manager = OmsAmtossReferenceManager(maintenance_model, external_dependencies)

        self.cmcf_fault_report_manager = OmsCmcfFaultReportManager(maintenance_model, external_dependencies)
        self.member_systems_manager = OmsMemberSystemsManager(maintenance_model, external_dependencies,
                                                              munch.munchify({'ata_manager': self.ata_manager,
                                                                              'cmcf_fault_report_manager':
                                                                                  self.cmcf_fault_report_manager,
                                                                              'nvm_files_manager': self.nvm_files_manager
                                                                              }))
        self.maintenance_messages_manager = \
            OmsMaintenanceMessageManager(maintenance_model, external_dependencies,
                                         munch.munchify({'ata_manager': self.ata_manager,
                                                         'member_systems_manager': self.member_systems_manager,
                                                         'amtoss_reference_manager': self.amtoss_reference_manager,
                                                         }))

        self.ambiguous_maintenance_messages_manager = OmsAmbiguousMaintenanceMessageManager(maintenance_model,
                                                                                            external_dependencies,
                                                                                            munch.munchify({
                                                                                                'maintenance_messages_manager': self.maintenance_messages_manager
                                                                                            }))
        self.flight_deck_effect_severity_manager = OmsFlightDeckEffectSeverityManager(maintenance_model,
                                                                                      external_dependencies)
        self.root_cause_manager = OmsRootCauseManager(maintenance_model, external_dependencies)
        self.flight_deck_effects_manager = \
            OmsFlightDeckEffectManager(maintenance_model, external_dependencies,
                                       munch.munchify({'flight_deck_effect_severity_manager':
                                                           self.flight_deck_effect_severity_manager,
                                                       'root_cause_manager': self.root_cause_manager,
                                                       'amtoss_reference_manager': self.amtoss_reference_manager,
                                                       }))
        self.fde_mm_correlation_manager = \
            OmsFdeMmCorrelationManager(maintenance_model, external_dependencies,
                                       munch.munchify({'flight_deck_effects_manager':
                                                           self.flight_deck_effects_manager,
                                                       'maintenance_messages_manager': self.maintenance_messages_manager
                                                       }))
        self.fault_report_manager = FaultReportManager(maintenance_model, external_dependencies)
        # TODO: Finish remaining connections. Currently, there are Equations, Buses, LRUs. But those are not covered by
        # OMS code yet, therefore it is not a priority.
