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
from sparetools_aerospace.products.ngaims.cmcf_fault_reports.cmcf_fault_report import OmsCmcfFaultReport
from sparetools_aerospace.products.ngaims.maintenance_model.model_base_manager import ModelBaseManager


class OmsCmcfFaultReportManager(ModelBaseManager):
    def __init__(self, maintenance_model, external_dependencies):
        self.external_dependencies = external_dependencies
        super(OmsCmcfFaultReportManager, self).__init__()
        cmcf_fr_model = maintenance_model.get_table_dict('CmcFr')
        for key, value in cmcf_fr_model.items():
            self.model_dict[key] = OmsCmcfFaultReport(value, external_dependencies)

    def get_all_cmcf_fault_reports(self):
        return super(OmsCmcfFaultReportManager, self).get_table_dict()
