#!/usr/bin/env python3
"""
OpenSSL Test Harness
Based on ngapy-dev test harness patterns for comprehensive testing
"""

import json
import logging
import numbers
import os
import time
import traceback
import inspect
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

import yaml


class TestLogger:
    """Test logging class based on ngapy-dev patterns"""
    
    def __init__(self, results_dir: Path):
        self.results_dir = results_dir
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Test counters
        self.test_passes = 0
        self.test_failures = 0
        self.total_passes = 0
        self.total_failures = 0
        
        # Log files
        self.test_log_file = None
        self.junit_xml_file = None
        
        # Callback function
        self.callback_function = None
        
    def open_test_log_file(self, log_file_path: Path, header_message: str):
        """Open test log file"""
        self.test_log_file = open(log_file_path, 'w')
        self.test_log_file.write(f"{header_message}\n")
        self.test_log_file.write(f"Test started at: {datetime.now().isoformat()}\n")
        self.test_log_file.write("=" * 80 + "\n")
        
    def close_test_log_file(self):
        """Close test log file"""
        if self.test_log_file:
            self.test_log_file.write("=" * 80 + "\n")
            self.test_log_file.write(f"Test completed at: {datetime.now().isoformat()}\n")
            self.test_log_file.write(f"Total passes: {self.total_passes}\n")
            self.test_log_file.write(f"Total failures: {self.total_failures}\n")
            self.test_log_file.close()
            
    def write_test_log(self, message: str):
        """Write message to test log"""
        if self.test_log_file:
            self.test_log_file.write(f"{message}\n")
            self.test_log_file.flush()
            
    def log_result(self, passed: bool, messages: List[str], test_num: int):
        """Log test result"""
        timestamp = datetime.now().isoformat()
        
        # Update counters
        if passed:
            self.test_passes += 1
            self.total_passes += 1
            status = "PASS"
        else:
            self.test_failures += 1
            self.total_failures += 1
            status = "FAIL"
            
        # Log to file
        self.write_test_log(f"[{timestamp}] {status} - Test {test_num}")
        for message in messages:
            self.write_test_log(f"  {message}")
            
        # Log to console
        logging.info(f"{status} - Test {test_num}: {messages[0] if messages else 'No message'}")
        
    def log_junit_result(self, passed: bool, messages: List[str], 
                        description: str = "", testnum: int = 0, 
                        timestamp: str = ""):
        """Log result in JUnit XML format"""
        # This would be implemented with proper JUnit XML generation
        # For now, we'll store the data for later XML generation
        pass
        
    def create_junit_xml_file(self, xml_file_path: Path):
        """Create JUnit XML file"""
        # Generate JUnit XML format
        xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<testsuite name="OpenSSL Tests" tests="{self.total_passes + self.total_failures}" 
           failures="{self.total_failures}" errors="0" time="0.0">
"""
        
        # Add individual test cases (simplified)
        for i in range(self.total_passes + self.total_failures):
            xml_content += f"""  <testcase name="test_{i}" classname="OpenSSLTest" time="0.0">
  </testcase>
"""
            
        xml_content += "</testsuite>"
        
        with open(xml_file_path, 'w') as f:
            f.write(xml_content)
            
    def get_test_passes(self) -> int:
        return self.test_passes
        
    def get_test_failures(self) -> int:
        return self.test_failures
        
    def get_total_test_passes(self) -> int:
        return self.total_passes
        
    def get_total_test_failures(self) -> int:
        return self.total_failures


class OpenSSLTestHarness:
    """OpenSSL Test Harness based on ngapy-dev patterns"""
    
    def __init__(self, results_dir: Optional[Path] = None):
        self.results_dir = results_dir or Path("test_results")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        self.output_format = "dec"  # decimal, hex, etc.
        self.callback_function = None
        self.test_logger = TestLogger(self.results_dir)
        
    def verify(self, actual: Any, expected: Any, msg: str = "", 
               test_num: int = 0, on_fail: Optional[Callable] = None) -> bool:
        """Verify equality"""
        value = (actual == expected)
        text = [f"Verify {msg + ' ' if msg else ''}:"]
        
        if self.output_format == "hex" and isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
            text.append(f"\t  Expected : 0x{expected:x}")
            text.append(f"\t  Actual   : 0x{actual:x}")
        else:
            text.append(f"\t  Expected : {expected}")
            text.append(f"\t  Actual   : {actual}")
            
        self.test_logger.log_result(value, text, test_num)
        
        if not value:
            self._handle_on_fail(on_fail)
            
        return value
        
    def verify_ne(self, actual: Any, expected: Any, msg: str = "", 
                  test_num: int = 0, on_fail: Optional[Callable] = None) -> bool:
        """Verify not equal"""
        value = (actual != expected)
        text = [f"Verify {msg + ' ' if msg else ''}:"]
        
        if self.output_format == "hex" and isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
            text.append(f"\t  Expected : <> 0x{expected:x}")
            text.append(f"\t  Actual   : 0x{actual:x}")
        else:
            text.append(f"\t  Expected : <> {expected}")
            text.append(f"\t  Actual   : {actual}")
            
        self.test_logger.log_result(value, text, test_num)
        
        if not value:
            self._handle_on_fail(on_fail)
            
        return value
        
    def verify_tol(self, actual: Union[int, float], expected: Union[int, float], 
                   tolerance: Union[int, float], msg: str = "", 
                   test_num: int = 0, on_fail: Optional[Callable] = None) -> bool:
        """Verify with tolerance"""
        if not isinstance(tolerance, numbers.Number):
            raise ValueError("Tolerance must be a numeric value")
            
        if not isinstance(actual, numbers.Number) or not isinstance(expected, numbers.Number):
            raise ValueError("Actual and expected must be numeric values")
            
        value = ((expected + tolerance) >= actual) and ((expected - tolerance) <= actual)
        
        text = [f"Verify {msg + ' ' if msg else ''}:"]
        text.append(f"\t  Expected : {expected} +/- {tolerance}")
        text.append(f"\t  Actual   : {actual}")
        
        self.test_logger.log_result(value, text, test_num)
        
        if not value:
            self._handle_on_fail(on_fail)
            
        return value
        
    def verify_range(self, actual: Union[int, float], min_value: Union[int, float], 
                     max_value: Union[int, float], msg: str = "", 
                     test_num: int = 0, on_fail: Optional[Callable] = None) -> bool:
        """Verify value is in range"""
        if not all(isinstance(x, numbers.Number) for x in [actual, min_value, max_value]):
            raise ValueError("All values must be numeric")
            
        value = (min_value <= actual <= max_value)
        
        text = [f"Verify {msg + ' ' if msg else ''}:"]
        text.append(f"\t  Expected : {min_value} <= Actual <= {max_value}")
        text.append(f"\t  Actual   : {actual}")
        
        self.test_logger.log_result(value, text, test_num)
        
        if not value:
            self._handle_on_fail(on_fail)
            
        return value
        
    def verify_string(self, actual: str, expected: str, case_sensitive: bool = True, 
                      msg: str = "", test_num: int = 0, 
                      on_fail: Optional[Callable] = None) -> bool:
        """Verify string equality"""
        if not isinstance(actual, str) or not isinstance(expected, str):
            raise ValueError("Both actual and expected must be strings")
            
        if case_sensitive:
            value = (actual == expected)
        else:
            value = (actual.upper() == expected.upper())
            
        text = [f"Verify {msg + ' ' if msg else ''}:"]
        text.append(f"\t  Expected : {expected}")
        text.append(f"\t  Actual   : {actual}")
        
        self.test_logger.log_result(value, text, test_num)
        
        if not value:
            self._handle_on_fail(on_fail)
            
        return value
        
    def verify_file_exists(self, file_path: Union[str, Path], msg: str = "", 
                          test_num: int = 0, on_fail: Optional[Callable] = None) -> bool:
        """Verify file exists"""
        path = Path(file_path)
        value = path.exists() and path.is_file()
        
        text = [f"Verify {msg + ' ' if msg else ''}:"]
        text.append(f"\t  Expected : File exists")
        text.append(f"\t  Actual   : {'File exists' if value else 'File does not exist'}")
        text.append(f"\t  Path     : {path}")
        
        self.test_logger.log_result(value, text, test_num)
        
        if not value:
            self._handle_on_fail(on_fail)
            
        return value
        
    def verify_directory_exists(self, dir_path: Union[str, Path], msg: str = "", 
                               test_num: int = 0, on_fail: Optional[Callable] = None) -> bool:
        """Verify directory exists"""
        path = Path(dir_path)
        value = path.exists() and path.is_dir()
        
        text = [f"Verify {msg + ' ' if msg else ''}:"]
        text.append(f"\t  Expected : Directory exists")
        text.append(f"\t  Actual   : {'Directory exists' if value else 'Directory does not exist'}")
        text.append(f"\t  Path     : {path}")
        
        self.test_logger.log_result(value, text, test_num)
        
        if not value:
            self._handle_on_fail(on_fail)
            
        return value
        
    def verify_command_success(self, command: List[str], msg: str = "", 
                              test_num: int = 0, on_fail: Optional[Callable] = None,
                              cwd: Optional[Path] = None) -> bool:
        """Verify command executes successfully"""
        import subprocess
        
        try:
            result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, timeout=300)
            value = (result.returncode == 0)
            
            text = [f"Verify {msg + ' ' if msg else ''}:"]
            text.append(f"\t  Expected : Command succeeds (return code 0)")
            text.append(f"\t  Actual   : Return code {result.returncode}")
            text.append(f"\t  Command  : {' '.join(command)}")
            
            if result.stdout:
                text.append(f"\t  Output   : {result.stdout[:200]}...")
            if result.stderr:
                text.append(f"\t  Error    : {result.stderr[:200]}...")
                
        except subprocess.TimeoutExpired:
            value = False
            text = [f"Verify {msg + ' ' if msg else ''}:"]
            text.append(f"\t  Expected : Command succeeds")
            text.append(f"\t  Actual   : Command timed out")
            text.append(f"\t  Command  : {' '.join(command)}")
            
        except Exception as e:
            value = False
            text = [f"Verify {msg + ' ' if msg else ''}:"]
            text.append(f"\t  Expected : Command succeeds")
            text.append(f"\t  Actual   : Exception: {e}")
            text.append(f"\t  Command  : {' '.join(command)}")
            
        self.test_logger.log_result(value, text, test_num)
        
        if not value:
            self._handle_on_fail(on_fail)
            
        return value
        
    @staticmethod
    def _handle_on_fail(on_fail: Optional[Callable]):
        """Handle on_fail callback"""
        if on_fail:
            try:
                if callable(on_fail):
                    on_fail()
            except Exception as e:
                logging.warning(f"on_fail callback failed: {e}")


def run_test(function_to_run: Callable, results_dir_path: Path, 
             header_message: str) -> str:
    """
    Run a test procedure function
    Based on ngapy-dev run_test pattern
    
    Args:
        function_to_run: Function to be executed, should contain verifications
        results_dir_path: Target directory to store log files
        header_message: String type, formatted, can be as simple as test name
        
    Returns:
        One of three options ("abort", "pass", "fail") based on the actual result
    """
    test_logger = TestLogger(results_dir_path)
    timestamp = time.strftime("%m_%d_%Y_%H%M%S", time.localtime())
    test_name = os.path.basename(inspect.getfile(function_to_run)).removesuffix('.py')
    log_file_basename = test_name + "_" + timestamp + ".txt"
    junit_xml_log_file_basename = test_name + "_" + timestamp + ".xml"
    
    abs_results_dir_path = results_dir_path.resolve()
    abs_path_log_filename = abs_results_dir_path / log_file_basename
    abs_path_junit_xml_log_filename = abs_results_dir_path / junit_xml_log_file_basename
    
    # Open test log file
    test_logger.open_test_log_file(abs_path_log_filename, header_message)
    
    # Try to extract test description
    test_descr = header_message
    for line in header_message.split('\n'):
        if 'description' in line.lower():
            test_descr = line.split(':  ')[1] if ':  ' in line else line
            break
            
    # Run test
    try:
        result = "fail"
        function_to_run()
        
        if not test_logger.get_test_failures():
            if test_logger.get_test_passes():
                result = "pass"
            else:
                test_logger.log_result(False, ["No verifications performed:"], 0)
                
    except Exception as e:
        test_logger.write_test_log(traceback.format_exc())
        logging.getLogger().warning(traceback.format_exc())
        test_logger.log_result(False, ["Exception occurred:"], 0)
        result = "abort"
        
    # Close log file
    test_logger.close_test_log_file()
    
    # Create JUnit XML file
    test_logger.create_junit_xml_file(abs_path_junit_xml_log_filename)
    
    return result


class OpenSSLTestSuite:
    """OpenSSL Test Suite for organizing tests"""
    
    def __init__(self, name: str, results_dir: Optional[Path] = None):
        self.name = name
        self.results_dir = results_dir or Path("test_results")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        self.tests = []
        self.results = {}
        
    def add_test(self, test_function: Callable, description: str = ""):
        """Add a test to the suite"""
        self.tests.append({
            'function': test_function,
            'description': description or test_function.__name__
        })
        
    def run_all_tests(self) -> Dict[str, str]:
        """Run all tests in the suite"""
        logging.info(f"Running test suite: {self.name}")
        
        for test in self.tests:
            test_name = test['function'].__name__
            description = test['description']
            
            logging.info(f"Running test: {test_name}")
            
            result = run_test(
                test['function'],
                self.results_dir,
                f"Test: {test_name}\nDescription: {description}"
            )
            
            self.results[test_name] = result
            logging.info(f"Test {test_name} result: {result}")
            
        return self.results
        
    def generate_report(self) -> Path:
        """Generate test report"""
        report_path = self.results_dir / f"{self.name}_report.json"
        
        report = {
            'suite_name': self.name,
            'timestamp': datetime.now().isoformat(),
            'total_tests': len(self.tests),
            'results': self.results,
            'summary': {
                'passed': sum(1 for r in self.results.values() if r == 'pass'),
                'failed': sum(1 for r in self.results.values() if r == 'fail'),
                'aborted': sum(1 for r in self.results.values() if r == 'abort')
            }
        }
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        logging.info(f"Test report generated: {report_path}")
        return report_path


# Example test functions
def test_openssl_version():
    """Test OpenSSL version"""
    harness = OpenSSLTestHarness()
    
    # This would be implemented with actual OpenSSL version checking
    harness.verify_string("3.5.0", "3.5.0", msg="OpenSSL version", test_num=1)
    

def test_openssl_libraries():
    """Test OpenSSL libraries exist"""
    harness = OpenSSLTestHarness()
    
    # This would be implemented with actual library checking
    harness.verify_file_exists("libssl.so", msg="SSL library exists", test_num=1)
    harness.verify_file_exists("libcrypto.so", msg="Crypto library exists", test_num=2)


if __name__ == '__main__':
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Create test suite
    suite = OpenSSLTestSuite("OpenSSL Basic Tests")
    suite.add_test(test_openssl_version, "Test OpenSSL version")
    suite.add_test(test_openssl_libraries, "Test OpenSSL libraries")
    
    # Run tests
    results = suite.run_all_tests()
    
    # Generate report
    report_path = suite.generate_report()
    
    print(f"Test results: {results}")
    print(f"Report saved to: {report_path}")
