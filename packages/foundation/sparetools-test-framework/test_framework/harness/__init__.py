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
from .test_harness import NgapyTestHarnes, run_test
from .test_logging import ThLogger
from .test_integration import IntegrationTestHarness, run_integration_tests
from .test_cross_platform import CrossPlatformTestHarness, run_cross_platform_tests
from .test_performance import PerformanceTestHarness, run_performance_tests
from .test_security import SecurityTestHarness, run_security_tests
from .test_dependency_analysis import DependencyAnalysisHarness, run_dependency_analysis

__version__ = '2.0.1'
__VDD_info__ = '69004821, Rev A (candidate)'
