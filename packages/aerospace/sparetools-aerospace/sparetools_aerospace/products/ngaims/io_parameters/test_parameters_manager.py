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
// File Name: test_input_parameters_manager.py
//
// Program:   TITAN
//
// Purpose:   TEST for input parameters manager
//
// Notes:     None
//
//********************************************************************************************
//********************************************************************************************
"""
from unittest import TestCase

from ngapy.io_platform.message_composition import get_complete_validity
from sparetools_aerospace.products.ngaims.test_common import TestPrepareCmcfDeps


class TestInputParameterManagerLdiConfig(TestPrepareCmcfDeps):
    def setUp(self) -> None:
        super(TestInputParameterManagerLdiConfig, self).setUp()
        self.input_parameter_manager = self.external_dependencies.input_io_manager


class TestInputParameterManagerLdiConfigFunctions(TestInputParameterManagerLdiConfig):
    def test_construction(self):
        self.assertGreater(len(self.input_parameter_manager.get_all_params()), 0)

    # Following tests are disabled, because are not reliably executed on Bamboo
    #def test_get_parameters(self):
    #    parameters = [self.input_parameter_manager.get_parameter_by_logical_name('aytCapable_FCS.1'),
    #                  self.input_parameter_manager.get_parameter_by_logical_name('calibrated_airspeed_voted_ACSS_ada.1'),
    #                  self.input_parameter_manager.get_parameter_by_logical_name('acss_air_data_source_ACSS_ada.1'),
    #                  self.input_parameter_manager.get_parameter_by_logical_name('exception_handling_fault_ACSS_ada.1')]
    #    self.assertEqual(len(self.input_parameter_manager.get_values(parameters)), len(parameters))
#
    #def test_set_parameters(self):
    #    parameters = [self.input_parameter_manager.get_parameter_by_logical_name('aytCapable_FCS.1'),
    #                  self.input_parameter_manager.get_parameter_by_logical_name('calibrated_airspeed_voted_ACSS_ada.1'),
    #                  self.input_parameter_manager.get_parameter_by_logical_name('acss_air_data_source_ACSS_ada.1'),
    #                  self.input_parameter_manager.get_parameter_by_logical_name('exception_handling_fault_ACSS_ada.1')]
    #    test_set = [(1, get_complete_validity()), (1, get_complete_validity()), (1, get_complete_validity()),
    #                (1, get_complete_validity())]
    #    self.input_parameter_manager.set_values(parameters, test_set)
    #    result = self.input_parameter_manager.get_values(parameters)
    #    self.assertEqual(result, test_set)
#
    #def test_set_parameters_queue_mode(self):
    #    parameters = [self.input_parameter_manager.get_parameter_by_logical_name('aytCapable_FCS.1'),
    #                  self.input_parameter_manager.get_parameter_by_logical_name('calibrated_airspeed_voted_ACSS_ada.1'),
    #                  self.input_parameter_manager.get_parameter_by_logical_name('acss_air_data_source_ACSS_ada.1'),
    #                  self.input_parameter_manager.get_parameter_by_logical_name('exception_handling_fault_ACSS_ada.1')]
    #    test_set = [(1, get_complete_validity()), (1, get_complete_validity()), (1, get_complete_validity()),
    #                (1, get_complete_validity())]
#
    #    self.input_parameter_manager.start_queued_mode()
    #    for index in range(10):
    #        self.input_parameter_manager.set_values(parameters, test_set)
    #    self.assertEqual(len(test_set), len(self.input_parameter_manager.set_queue_parameters))
    #    self.assertEqual(len(test_set), len(self.input_parameter_manager.set_queue_values))
    #    self.input_parameter_manager.stop_queued_mode()
    #    self.assertEqual(0, len(self.input_parameter_manager.set_queue_parameters))
    #    self.assertEqual(0, len(self.input_parameter_manager.set_queue_values))
#