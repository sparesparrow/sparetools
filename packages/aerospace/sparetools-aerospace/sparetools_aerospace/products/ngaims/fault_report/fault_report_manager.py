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
from sparetools_aerospace.products.ngaims.fault_report.fault_report import FaultReport
from sparetools_aerospace.products.ngaims.maintenance_model.model_base_manager import ModelBaseManager
from sparetools_aerospace.products.ngaims.filter_samples import Functor, equality


class FaultReportManager(ModelBaseManager):
    def __init__(self, maintenance_model, external_dependencies):
        self.external_dependencies = external_dependencies
        super(FaultReportManager, self).__init__()
        fr_model = maintenance_model.get_table_dict('Fr')
        for key, value in fr_model.items():
            self.model_dict[key] = FaultReport(value, external_dependencies)

    def get_all_fault_reports(self):
        return super(FaultReportManager, self).get_table_dict()

    def get_mms_for_selected_ms(self, ms_id: int):
        mms_list = list()
        fr_list = super(FaultReportManager, self).get_table_data_in_list()
        for fr in fr_list:
            if fr.ms_id == ms_id:
                mms_list.append(fr.mm_id)
        return sorted(mms_list)
