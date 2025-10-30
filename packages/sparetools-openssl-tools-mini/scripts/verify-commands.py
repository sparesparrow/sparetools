#!/usr/bin/env python3
"""
verify-commands.py - Verify custom Conan commands functionality

This script tests the custom Conan commands installed by the bootstrap script:
- conan openssl:build
- conan openssl:graph
- conan --help (to verify command visibility)
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


class CommandVerificationError(Exception):
    """Custom exception for command verification errors"""
    pass


class ConanCommandVerifier:
    """Verifier for custom Conan commands"""
    
    def __init__(self, conan_path: Optional[str] = None):
        self.conan_path = conan_path or 'conan'
        self.tests_passed = 0
        self.tests_failed = 0
        self.temp_dir = None
    
    def log(self, message: str, color: str = Colors.END) -> None:
        """Log a message with optional color"""
        print(f"{color}{message}{Colors.END}")
    
    def log_step(self, step: str) -> None:
        """Log a step with formatting"""
        self.log(f"\n{Colors.BOLD}🔧 {step}{Colors.END}")
    
    def log_success(self, message: str) -> None:
        """Log a success message"""
        self.log(f"✅ {message}", Colors.GREEN)
        self.tests_passed += 1
    
    def log_failure(self, message: str) -> None:
        """Log a failure message"""
        self.log(f"❌ {message}", Colors.RED)
        self.tests_failed += 1
    
    def log_warning(self, message: str) -> None:
        """Log a warning message"""
        self.log(f"⚠️  {message}", Colors.YELLOW)
    
    def run_command(self, cmd: List[str], cwd: Optional[Path] = None, 
                   capture_output: bool = True) -> Tuple[int, str, str]:
        """Run a command and return returncode, stdout, stderr"""
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=capture_output,
                text=True,
                check=False
            )
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            raise CommandVerificationError(f"Command failed: {' '.join(cmd)} - {e}")
    
    def check_conan_installation(self) -> bool:
        """Check if Conan is installed and accessible"""
        self.log_step("Checking Conan installation")
        
        try:
            returncode, stdout, stderr = self.run_command([self.conan_path, '--version'])
            if returncode == 0:
                version = stdout.strip().split()[-1]
                self.log_success(f"Conan {version} is installed and accessible")
                return True
            else:
                self.log_failure(f"Conan command failed: {stderr}")
                return False
        except FileNotFoundError:
            self.log_failure("Conan command not found")
            return False
    
    def check_command_visibility(self) -> bool:
        """Check if custom commands are visible in conan --help"""
        self.log_step("Checking command visibility in conan --help")
        
        try:
            returncode, stdout, stderr = self.run_command([self.conan_path, '--help'])
            if returncode != 0:
                self.log_failure(f"conan --help failed: {stderr}")
                return False
            
            # Check for openssl commands
            if 'openssl' in stdout:
                self.log_success("OpenSSL commands visible in conan --help")
                return True
            else:
                self.log_failure("OpenSSL commands not visible in conan --help")
                return False
        except Exception as e:
            self.log_failure(f"Failed to check command visibility: {e}")
            return False
    
    def test_openssl_build_help(self) -> bool:
        """Test conan openssl:build --help command"""
        self.log_step("Testing conan openssl:build --help")
        
        try:
            returncode, stdout, stderr = self.run_command([
                self.conan_path, 'openssl:build', '--help'
            ])
            
            if returncode != 0:
                self.log_failure(f"conan openssl:build --help failed: {stderr}")
                return False
            
            # Check for expected help content
            expected_keywords = ['build', 'openssl', 'fips', 'profile']
            found_keywords = [kw for kw in expected_keywords if kw.lower() in stdout.lower()]
            
            if len(found_keywords) >= 2:
                self.log_success("conan openssl:build --help works and shows expected content")
                return True
            else:
                self.log_failure("conan openssl:build --help output doesn't contain expected keywords")
                return False
        except Exception as e:
            self.log_failure(f"Failed to test openssl:build help: {e}")
            return False
    
    def test_openssl_graph_help(self) -> bool:
        """Test conan openssl:graph --help command"""
        self.log_step("Testing conan openssl:graph --help")
        
        try:
            returncode, stdout, stderr = self.run_command([
                self.conan_path, 'openssl:graph', '--help'
            ])
            
            if returncode != 0:
                self.log_failure(f"conan openssl:graph --help failed: {stderr}")
                return False
            
            # Check for expected help content
            expected_keywords = ['graph', 'dependencies', 'json', 'analyze']
            found_keywords = [kw for kw in expected_keywords if kw.lower() in stdout.lower()]
            
            if len(found_keywords) >= 2:
                self.log_success("conan openssl:graph --help works and shows expected content")
                return True
            else:
                self.log_failure("conan openssl:graph --help output doesn't contain expected keywords")
                return False
        except Exception as e:
            self.log_failure(f"Failed to test openssl:graph help: {e}")
            return False
    
    def create_test_conanfile(self) -> Path:
        """Create a test conanfile.txt for testing"""
        self.log_step("Creating test conanfile.txt")
        
        if not self.temp_dir:
            self.temp_dir = tempfile.mkdtemp()
        
        conanfile_path = Path(self.temp_dir) / 'conanfile.txt'
        
        conanfile_content = """[requires]
openssl/3.6.0

[generators]
CMakeToolchain
CMakeDeps
"""
        
        with open(conanfile_path, 'w') as f:
            f.write(conanfile_content)
        
        self.log_success(f"Created test conanfile.txt at {conanfile_path}")
        return conanfile_path
    
    def test_graph_analyzer(self) -> bool:
        """Test the graph analyzer with a test conanfile"""
        self.log_step("Testing graph analyzer with test conanfile")
        
        try:
            conanfile_path = self.create_test_conanfile()
            conanfile_dir = conanfile_path.parent
            
            # Run graph command
            returncode, stdout, stderr = self.run_command([
                self.conan_path, 'openssl:graph', '--json'
            ], cwd=conanfile_dir)
            
            if returncode != 0:
                self.log_failure(f"conan openssl:graph --json failed: {stderr}")
                return False
            
            # Try to parse JSON output
            try:
                json_data = json.loads(stdout)
                if isinstance(json_data, dict):
                    self.log_success("Graph analyzer produces valid JSON output")
                    return True
                else:
                    self.log_failure("Graph analyzer output is not a JSON object")
                    return False
            except json.JSONDecodeError:
                self.log_failure("Graph analyzer output is not valid JSON")
                return False
        except Exception as e:
            self.log_failure(f"Failed to test graph analyzer: {e}")
            return False
    
    def test_command_error_handling(self) -> bool:
        """Test error handling of custom commands"""
        self.log_step("Testing command error handling")
        
        try:
            # Test with invalid arguments
            returncode, stdout, stderr = self.run_command([
                self.conan_path, 'openssl:build', '--invalid-flag'
            ])
            
            # Should fail with non-zero exit code
            if returncode != 0:
                self.log_success("Command correctly handles invalid arguments")
                return True
            else:
                self.log_failure("Command should fail with invalid arguments")
                return False
        except Exception as e:
            self.log_failure(f"Failed to test error handling: {e}")
            return False
    
    def cleanup(self) -> None:
        """Clean up temporary files"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)
            self.log(f"Cleaned up temporary directory: {self.temp_dir}")
    
    def run_all_tests(self) -> bool:
        """Run all verification tests"""
        self.log(f"{Colors.BOLD}🚀 Starting Conan commands verification{Colors.END}")
        
        try:
            # Run all tests
            tests = [
                self.check_conan_installation,
                self.check_command_visibility,
                self.test_openssl_build_help,
                self.test_openssl_graph_help,
                self.test_graph_analyzer,
                self.test_command_error_handling
            ]
            
            for test in tests:
                try:
                    test()
                except Exception as e:
                    self.log_failure(f"Test {test.__name__} failed with exception: {e}")
            
            # Print summary
            self.log(f"\n{Colors.BOLD}📊 Verification Summary{Colors.END}")
            self.log_success(f"Tests passed: {self.tests_passed}")
            if self.tests_failed > 0:
                self.log_failure(f"Tests failed: {self.tests_failed}")
                return False
            else:
                self.log_success("All tests passed!")
                return True
                
        finally:
            self.cleanup()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Verify custom Conan commands functionality",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python3 verify-commands.py
    python3 verify-commands.py --conan-path /usr/local/bin/conan
        """
    )
    
    parser.add_argument('--conan-path', 
                       help='Path to conan executable (default: conan)')
    
    args = parser.parse_args()
    
    verifier = ConanCommandVerifier(conan_path=args.conan_path)
    
    try:
        success = verifier.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        verifier.log("Verification interrupted by user", Colors.YELLOW)
        sys.exit(1)
    except Exception as e:
        verifier.log_failure(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()





