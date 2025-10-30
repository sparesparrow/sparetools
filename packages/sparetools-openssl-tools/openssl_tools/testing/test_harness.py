#!/usr/bin/env python3
"""
Advanced Test Harness for OpenSSL Conan Package
Based on ngapy-dev test_harness.py with enhanced verification methods
"""

import os
import sys
import time
import json
import logging
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import xml.etree.ElementTree as ET
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestResult(Enum):
    """Test result enumeration"""
    PASS = "PASS"
    FAIL = "FAIL"
    SKIP = "SKIP"
    ERROR = "ERROR"

@dataclass
class TestCase:
    """Test case data class"""
    name: str
    description: str = ""
    expected_result: Any = None
    actual_result: Any = None
    result: TestResult = TestResult.PASS
    duration: float = 0.0
    error_message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TestSuite:
    """Test suite data class"""
    name: str
    description: str = ""
    test_cases: List[TestCase] = field(default_factory=list)
    start_time: float = 0.0
    end_time: float = 0.0
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    skipped_tests: int = 0
    error_tests: int = 0

class ThLogger:
    """Test harness logger - pattern from ngapy-dev"""
    
    def __init__(self, results_dir: Path):
        self.results_dir = results_dir
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize log files
        self.test_log_file = None
        self.junit_xml_log = None
        self._initialize_log_files()
    
    def _initialize_log_files(self):
        """Initialize log files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Test log file
        test_log_path = self.results_dir / f"test_log_{timestamp}.txt"
        self.test_log_file = open(test_log_path, 'w')
        
        # JUnit XML log
        junit_log_path = self.results_dir / f"junit_report_{timestamp}.xml"
        self.junit_xml_log = open(junit_log_path, 'w')
        
        logger.info(f"📝 Log files initialized: {test_log_path}, {junit_log_path}")
    
    def log_result(self, test_name: str, result: str, test_num: int = 0):
        """Log test result"""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] Test {test_num}: {test_name} - {result}\n"
        
        if self.test_log_file:
            self.test_log_file.write(log_entry)
            self.test_log_file.flush()
        
        logger.info(f"🧪 Test {test_num}: {test_name} - {result}")
    
    def log_junit_result(self, test_name: str, result: str, description: str = "", 
                        testnum: int = 0, timestamp: str = ""):
        """Log JUnit XML result"""
        if not timestamp:
            timestamp = datetime.now().isoformat()
        
        # This would be expanded to write proper JUnit XML
        # For now, we'll store the data for later XML generation
        pass
    
    def close_test_log_file(self):
        """Close test log file"""
        if self.test_log_file:
            self.test_log_file.close()
    
    def create_test_log_file(self, filename: str):
        """Create test log file"""
        if self.junit_xml_log:
            self.junit_xml_log.close()
        
        self.junit_xml_log = open(filename, 'w')

class NgapyTestHarness:
    """Advanced test harness - pattern from ngapy-dev test_harness.py"""
    
    def __init__(self, results_dir: Path):
        self.results_dir = results_dir
        self.th_logger = ThLogger(results_dir)
        self.test_suites: List[TestSuite] = []
        self.current_suite: Optional[TestSuite] = None
        self.test_counter = 0
        
        # Verification methods
        self.verification_methods = {
            "verify": self._verify_equal,
            "verify_ne": self._verify_not_equal,
            "verify_tol": self._verify_tolerance,
            "verify_gt": self._verify_greater_than,
            "verify_lt": self._verify_less_than,
            "verify_contains": self._verify_contains,
            "verify_regex": self._verify_regex,
            "verify_file_exists": self._verify_file_exists,
            "verify_file_content": self._verify_file_content,
            "verify_command": self._verify_command
        }
    
    def start_test_suite(self, name: str, description: str = ""):
        """Start a new test suite"""
        self.current_suite = TestSuite(
            name=name,
            description=description,
            start_time=time.time()
        )
        self.test_suites.append(self.current_suite)
        
        logger.info(f"🚀 Starting test suite: {name}")
        if description:
            logger.info(f"📋 Description: {description}")
    
    def end_test_suite(self):
        """End current test suite"""
        if self.current_suite:
            self.current_suite.end_time = time.time()
            self.current_suite.total_tests = len(self.current_suite.test_cases)
            
            # Count results
            for test_case in self.current_suite.test_cases:
                if test_case.result == TestResult.PASS:
                    self.current_suite.passed_tests += 1
                elif test_case.result == TestResult.FAIL:
                    self.current_suite.failed_tests += 1
                elif test_case.result == TestResult.SKIP:
                    self.current_suite.skipped_tests += 1
                elif test_case.result == TestResult.ERROR:
                    self.current_suite.error_tests += 1
            
            duration = self.current_suite.end_time - self.current_suite.start_time
            logger.info(f"✅ Test suite '{self.current_suite.name}' completed in {duration:.2f}s")
            logger.info(f"📊 Results: {self.current_suite.passed_tests} passed, "
                       f"{self.current_suite.failed_tests} failed, "
                       f"{self.current_suite.skipped_tests} skipped, "
                       f"{self.current_suite.error_tests} errors")
            
            self.current_suite = None
    
    def verify(self, actual: Any, expected: Any, msg: str = "", 
               test_num: int = 0, on_fail: Optional[Callable] = None) -> bool:
        """Verify actual equals expected - pattern from ngapy-dev"""
        return self._run_verification("verify", actual, expected, msg, test_num, on_fail)
    
    def verify_ne(self, actual: Any, expected: Any, msg: str = "", 
                  test_num: int = 0, on_fail: Optional[Callable] = None) -> bool:
        """Verify actual not equals expected"""
        return self._run_verification("verify_ne", actual, expected, msg, test_num, on_fail)
    
    def verify_tol(self, actual: float, expected: float, tolerance: float, 
                   msg: str = "", test_num: int = 0, on_fail: Optional[Callable] = None) -> bool:
        """Verify actual within tolerance of expected"""
        return self._run_verification("verify_tol", actual, expected, msg, test_num, on_fail, tolerance)
    
    def verify_gt(self, actual: float, expected: float, msg: str = "", 
                  test_num: int = 0, on_fail: Optional[Callable] = None) -> bool:
        """Verify actual greater than expected"""
        return self._run_verification("verify_gt", actual, expected, msg, test_num, on_fail)
    
    def verify_lt(self, actual: float, expected: float, msg: str = "", 
                  test_num: int = 0, on_fail: Optional[Callable] = None) -> bool:
        """Verify actual less than expected"""
        return self._run_verification("verify_lt", actual, expected, msg, test_num, on_fail)
    
    def verify_contains(self, container: Union[str, List], item: Any, 
                        msg: str = "", test_num: int = 0, on_fail: Optional[Callable] = None) -> bool:
        """Verify container contains item"""
        return self._run_verification("verify_contains", container, item, msg, test_num, on_fail)
    
    def verify_regex(self, text: str, pattern: str, msg: str = "", 
                     test_num: int = 0, on_fail: Optional[Callable] = None) -> bool:
        """Verify text matches regex pattern"""
        return self._run_verification("verify_regex", text, pattern, msg, test_num, on_fail)
    
    def verify_file_exists(self, file_path: Union[str, Path], msg: str = "", 
                           test_num: int = 0, on_fail: Optional[Callable] = None) -> bool:
        """Verify file exists"""
        return self._run_verification("verify_file_exists", file_path, None, msg, test_num, on_fail)
    
    def verify_file_content(self, file_path: Union[str, Path], expected_content: str, 
                            msg: str = "", test_num: int = 0, on_fail: Optional[Callable] = None) -> bool:
        """Verify file contains expected content"""
        return self._run_verification("verify_file_content", file_path, expected_content, msg, test_num, on_fail)
    
    def verify_command(self, command: List[str], expected_return_code: int = 0, 
                       msg: str = "", test_num: int = 0, on_fail: Optional[Callable] = None) -> bool:
        """Verify command executes successfully"""
        return self._run_verification("verify_command", command, expected_return_code, msg, test_num, on_fail)
    
    def _run_verification(self, method_name: str, actual: Any, expected: Any, 
                         msg: str, test_num: int, on_fail: Optional[Callable], 
                         *args) -> bool:
        """Run verification method with error handling"""
        if test_num == 0:
            test_num = self.test_counter + 1
            self.test_counter += 1
        
        start_time = time.time()
        
        try:
            method = self.verification_methods[method_name]
            result = method(actual, expected, *args)
            
            duration = time.time() - start_time
            
            # Create test case
            test_case = TestCase(
                name=f"{method_name}_{test_num}",
                description=msg,
                expected_result=expected,
                actual_result=actual,
                result=TestResult.PASS if result else TestResult.FAIL,
                duration=duration,
                metadata={"method": method_name, "args": args}
            )
            
            # Add to current suite
            if self.current_suite:
                self.current_suite.test_cases.append(test_case)
            
            # Log result
            result_text = "PASS" if result else "FAIL"
            self.th_logger.log_result(test_case.name, result_text, test_num)
            self.th_logger.log_junit_result(test_case.name, result_text, msg, test_num)
            
            if not result and on_fail:
                on_fail()
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Verification error: {e}"
            
            # Create error test case
            test_case = TestCase(
                name=f"{method_name}_{test_num}",
                description=msg,
                expected_result=expected,
                actual_result=actual,
                result=TestResult.ERROR,
                duration=duration,
                error_message=error_msg,
                metadata={"method": method_name, "args": args}
            )
            
            if self.current_suite:
                self.current_suite.test_cases.append(test_case)
            
            self.th_logger.log_result(test_case.name, "ERROR", test_num)
            logger.error(f"❌ {error_msg}")
            
            return False
    
    def _verify_equal(self, actual: Any, expected: Any) -> bool:
        """Verify actual equals expected"""
        return actual == expected
    
    def _verify_not_equal(self, actual: Any, expected: Any) -> bool:
        """Verify actual not equals expected"""
        return actual != expected
    
    def _verify_tolerance(self, actual: float, expected: float, tolerance: float) -> bool:
        """Verify actual within tolerance of expected"""
        return abs(actual - expected) <= tolerance
    
    def _verify_greater_than(self, actual: float, expected: float) -> bool:
        """Verify actual greater than expected"""
        return actual > expected
    
    def _verify_less_than(self, actual: float, expected: float) -> bool:
        """Verify actual less than expected"""
        return actual < expected
    
    def _verify_contains(self, container: Union[str, List], item: Any) -> bool:
        """Verify container contains item"""
        return item in container
    
    def _verify_regex(self, text: str, pattern: str) -> bool:
        """Verify text matches regex pattern"""
        import re
        return bool(re.search(pattern, text))
    
    def _verify_file_exists(self, file_path: Union[str, Path], _) -> bool:
        """Verify file exists"""
        return Path(file_path).exists()
    
    def _verify_file_content(self, file_path: Union[str, Path], expected_content: str) -> bool:
        """Verify file contains expected content"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            return expected_content in content
        except Exception:
            return False
    
    def _verify_command(self, command: List[str], expected_return_code: int) -> bool:
        """Verify command executes successfully"""
        try:
            result = subprocess.run(command, capture_output=True, text=True)
            return result.returncode == expected_return_code
        except Exception:
            return False
    
    def generate_junit_xml(self) -> Path:
        """Generate JUnit XML report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        xml_path = self.results_dir / f"junit_report_{timestamp}.xml"
        
        # Create root element
        root = ET.Element("testsuites")
        
        for suite in self.test_suites:
            # Create testsuite element
            suite_elem = ET.SubElement(root, "testsuite")
            suite_elem.set("name", suite.name)
            suite_elem.set("tests", str(suite.total_tests))
            suite_elem.set("failures", str(suite.failed_tests))
            suite_elem.set("errors", str(suite.error_tests))
            suite_elem.set("skipped", str(suite.skipped_tests))
            suite_elem.set("time", str(suite.end_time - suite.start_time))
            
            for test_case in suite.test_cases:
                # Create testcase element
                case_elem = ET.SubElement(suite_elem, "testcase")
                case_elem.set("name", test_case.name)
                case_elem.set("time", str(test_case.duration))
                
                if test_case.result == TestResult.FAIL:
                    failure_elem = ET.SubElement(case_elem, "failure")
                    failure_elem.set("message", test_case.error_message or "Test failed")
                elif test_case.result == TestResult.ERROR:
                    error_elem = ET.SubElement(case_elem, "error")
                    error_elem.set("message", test_case.error_message or "Test error")
                elif test_case.result == TestResult.SKIP:
                    skip_elem = ET.SubElement(case_elem, "skipped")
                    skip_elem.set("message", "Test skipped")
        
        # Write XML file
        tree = ET.ElementTree(root)
        tree.write(xml_path, encoding="utf-8", xml_declaration=True)
        
        logger.info(f"📊 JUnit XML report generated: {xml_path}")
        return xml_path
    
    def generate_summary_report(self) -> Path:
        """Generate summary report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.results_dir / f"test_summary_{timestamp}.json"
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_suites": len(self.test_suites),
            "total_tests": sum(suite.total_tests for suite in self.test_suites),
            "total_passed": sum(suite.passed_tests for suite in self.test_suites),
            "total_failed": sum(suite.failed_tests for suite in self.test_suites),
            "total_skipped": sum(suite.skipped_tests for suite in self.test_suites),
            "total_errors": sum(suite.error_tests for suite in self.test_suites),
            "suites": []
        }
        
        for suite in self.test_suites:
            suite_summary = {
                "name": suite.name,
                "description": suite.description,
                "total_tests": suite.total_tests,
                "passed_tests": suite.passed_tests,
                "failed_tests": suite.failed_tests,
                "skipped_tests": suite.skipped_tests,
                "error_tests": suite.error_tests,
                "duration": suite.end_time - suite.start_time
            }
            summary["suites"].append(suite_summary)
        
        with open(report_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"📊 Summary report generated: {report_path}")
        return report_path
    
    def cleanup(self):
        """Cleanup resources"""
        self.th_logger.close_test_log_file()
        if self.th_logger.junit_xml_log:
            self.th_logger.junit_xml_log.close()

def run_test(function_to_run: Callable, results_dir_path: Path, 
             header_message: str = "") -> bool:
    """Run test function with comprehensive reporting - pattern from ngapy-dev"""
    logger.info(f"🚀 Running test: {function_to_run.__name__}")
    
    if header_message:
        logger.info(f"📋 {header_message}")
    
    # Initialize test harness
    harness = NgapyTestHarness(results_dir_path)
    
    try:
        # Run the test function
        function_to_run(harness)
        
        # End any open test suite
        harness.end_test_suite()
        
        # Generate reports
        junit_xml = harness.generate_junit_xml()
        summary_report = harness.generate_summary_report()
        
        # Check if all tests passed
        total_failed = sum(suite.failed_tests for suite in harness.test_suites)
        total_errors = sum(suite.error_tests for suite in harness.test_suites)
        
        success = (total_failed == 0 and total_errors == 0)
        
        if success:
            logger.info("🎉 All tests passed!")
        else:
            logger.error(f"💥 Tests failed: {total_failed} failures, {total_errors} errors")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Test execution failed: {e}")
        return False
        
    finally:
        harness.cleanup()

# Example test functions
def test_openssl_basic_functionality(harness: NgapyTestHarness):
    """Test basic OpenSSL functionality"""
    harness.start_test_suite("OpenSSL Basic Functionality", "Test basic OpenSSL operations")
    
    # Test OpenSSL version
    harness.verify_command(["openssl", "version"], 0, "OpenSSL version command should succeed")
    
    # Test OpenSSL help
    harness.verify_command(["openssl", "help"], 0, "OpenSSL help command should succeed")
    
    # Test if OpenSSL binary exists
    harness.verify_file_exists("/usr/bin/openssl", "OpenSSL binary should exist")

def test_openssl_crypto_operations(harness: NgapyTestHarness):
    """Test OpenSSL cryptographic operations"""
    harness.start_test_suite("OpenSSL Crypto Operations", "Test cryptographic operations")
    
    # Test hash generation
    harness.verify_command(["openssl", "dgst", "-sha256", "-binary"], 0, "SHA256 hash should work")
    
    # Test random number generation
    harness.verify_command(["openssl", "rand", "-hex", "16"], 0, "Random number generation should work")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="OpenSSL Test Harness")
    parser.add_argument("--results-dir", type=Path, default=Path("test_results"),
                       help="Results directory")
    parser.add_argument("--test-suite", choices=["basic", "crypto", "all"], default="all",
                       help="Test suite to run")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create results directory
    args.results_dir.mkdir(parents=True, exist_ok=True)
    
    success = True
    
    if args.test_suite in ["basic", "all"]:
        success &= run_test(test_openssl_basic_functionality, args.results_dir, 
                           "Testing basic OpenSSL functionality")
    
    if args.test_suite in ["crypto", "all"]:
        success &= run_test(test_openssl_crypto_operations, args.results_dir,
                           "Testing OpenSSL cryptographic operations")
    
    if success:
        logger.info("🎉 All test suites passed!")
        sys.exit(0)
    else:
        logger.error("💥 Some test suites failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
