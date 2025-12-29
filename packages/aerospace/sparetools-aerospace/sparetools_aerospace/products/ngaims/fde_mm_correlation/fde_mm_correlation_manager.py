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
from ngapy.io_platform.message_composition import get_complete_validity
from sparetools_aerospace.products.ngaims.common_functions import set_status_for_multiple_entities
from sparetools_aerospace.products.ngaims.fde_mm_correlation.fde_mm_correlation import OmsFdeMmCorrelation
from sparetools_aerospace.products.ngaims.filter_samples import Functor, equality
from sparetools_aerospace.products.ngaims.maintenance_model.model_base_manager import ModelBaseManager


class OmsFdeMmCorrelationManager(ModelBaseManager):
    def __init__(self, maintenance_model, external_dependencies, internal_dependencies=None):
        super(OmsFdeMmCorrelationManager, self).__init__()
        fde_mm_correlation_model = maintenance_model.get_table_dict('FdeMmCorr')
        # This is unlike most of managers, who are based on ID based table. This is based on M:N relation.
        for index, value in enumerate(fde_mm_correlation_model):
            self.model_dict[index] = OmsFdeMmCorrelation(value, external_dependencies, internal_dependencies)
        self.end_tick = 0
        self.external_dependencies = external_dependencies
        self.internal_dependencies = internal_dependencies

    def get_all_correlations(self):
        return super(OmsFdeMmCorrelationManager, self).get_table_dict()

    def get_all_active_correlations(self, tick=0):
        self.get_transitions_correlations()
        return self.filter_by_attribute(Functor(equality, 'ate_status', True))

    def get_transitions_correlations(self, tick=0):
        correlations = self.external_dependencies.ate.get_active_fdes(tick)
        self.end_tick = correlations.data.endTick
        transitions = []
        for key, correlation in self.model_dict.items():
            correlation_transition_list = list(filter(lambda transition: transition.type == 'MmFdeCorrelation' and
                                                                         transition.fdeId == correlation.fde.sequence_id and
                                                                         transition.mmId == correlation.mm.sequence_id,
                                                      correlations.data.transitions))
            correlation.store_transition_list(correlation_transition_list, self.end_tick)
            if correlation_transition_list:
                transitions.append(correlation)
        return transitions

    # Note: It is your responsibility to set MS status (To set MM) and CAS validity/priority
    def set_all_correlations(self, status=True, custom_list=None, validity=get_complete_validity()):
        set_status_for_multiple_entities(self.external_dependencies.input_io_manager,
                                         self.get_execution_list(custom_list),
                                         status,
                                         validity)
