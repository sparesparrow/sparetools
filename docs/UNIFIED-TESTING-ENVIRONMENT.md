# SpareTools: ngapy-style Unified Testing Environment

## Executive Summary

Create a unified source of Conan recipes and Python scripts with bundled CPython that can be dropped into any repository to create a consistent testing environment. This plan is inspired by ngapy's test harness architecture while maintaining SpareTools' zero-copy, Conan-based approach.

## Goal

Enable **one-command setup** for any repository to get:
- ✅ Bundled CPython 3.12.7 (hermetic, no system dependencies)
- ✅ Unified test harness (ngapy-style verification framework)
- ✅ Consistent CI/CD workflows
- ✅ Cross-platform compatibility
- ✅ JUnit XML output for CI integration

## Architecture Overview

```
sparetools/
├── packages/
│   ├── foundation/
│   │   ├── sparetools-cpython/         # Bundled Python 3.12.7
│   │   ├── sparetools-base/            # Core utilities
│   │   └── sparetools-test-harness/    # ← NEW: Test framework
│   └── consumers/
│       └── sparetools-obd-sim/
├── scripts/
│   ├── bootstrap.py                    # ← NEW: Universal bootstrap
│   ├── test_runner.py                  # ← NEW: Unified test runner
│   └── ...
├── templates/                          # ← NEW: Repository templates
│   ├── generic/
│   │   ├── conanfile.py.template
│   │   ├── pytest.ini.template
│   │   └── .github/workflows/ci.yml.template
│   ├── mia/
│   └── mcp/
└── test/
    ├── unit/
    ├── integration/
    └── test_bootstrap.py                # ← NEW: Bootstrap validation
```

## Key Improvements from ngapy Analysis

### 1. Structured Test Harness (ngapy-style)

**What ngapy does well:**
- Custom test harness with verification methods (`verify()`, `verify_tol()`, `verify_range()`, etc.)
- Structured logging with pass/fail tracking
- JUnit XML output for CI integration
- Test procedure execution framework

**SpareTools adaptation:**
- Package as `sparetools-test-harness` Conan package
- Use bundled CPython from `sparetools-cpython`
- Integrate with pytest for compatibility
- Maintain ngapy's verification API for familiarity

### 2. Universal Bootstrap Script

**Location:** `scripts/bootstrap.py`

**Purpose:** Single command to set up SpareTools in ANY repository

```python
#!/usr/bin/env python3
"""
Universal SpareTools bootstrap script.
Usage: python bootstrap.py [--project-type mia|android|mcp|generic]
"""
import subprocess
import sys
import os
from pathlib import Path

def bootstrap_sparetools(project_type="generic", sparetools_repo=None):
    """Bootstrap SpareTools environment with bundled CPython."""
    
    print("🔧 SpareTools Bootstrap Starting...")
    
    # Step 1: Install Conan if needed
    ensure_conan()
    
    # Step 2: Install sparetools-cpython (bundled Python)
    install_bundled_python(sparetools_repo)
    
    # Step 3: Get bundled Python executable
    bundled_python = get_bundled_python()
    
    # Step 4: Set up virtual environment using bundled Python
    setup_venv(bundled_python)
    
    # Step 5: Install sparetools-test-harness
    install_test_harness(sparetools_repo)
    
    # Step 6: Install Python dependencies
    install_python_deps(project_type)
    
    # Step 7: Set up pre-commit hooks
    setup_hooks()
    
    # Step 8: Create project-specific config
    create_config(project_type)
    
    print("✅ SpareTools Bootstrap Complete!")
    print(f"   Activate with: source .venv/bin/activate")
    print(f"   Run tests with: python scripts/test_runner.py")

def ensure_conan():
    """Ensure Conan is available."""
    try:
        subprocess.run(["conan", "--version"], check=True, 
                      capture_output=True, stdout=subprocess.DEVNULL)
        print("✅ Conan found")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("📦 Installing Conan...")
        subprocess.run([sys.executable, "-m", "pip", "install", "conan>=2.0"], 
                      check=True)

def install_bundled_python(sparetools_repo=None):
    """Install sparetools-cpython package."""
    print("🐍 Installing bundled CPython 3.12.7...")
    
    if sparetools_repo:
        # Build from local repo
        cmd = [
            "conan", "create", 
            f"{sparetools_repo}/packages/foundation/sparetools-cpython",
            "--version=3.12.7",
            "--build=missing"
        ]
    else:
        # Install from remote
        cmd = [
            "conan", "install",
            "--tool-requires=sparetools-cpython/3.12.7",
            "--build=missing",
            "-of", ".conan"
        ]
    
    subprocess.run(cmd, check=True)

def get_bundled_python():
    """Get path to bundled Python executable."""
    # Query Conan for Python location
    result = subprocess.run(
        ["conan", "install", "--tool-requires=sparetools-cpython/3.12.7", 
         "--build=missing", "-of", ".conan", "--format=json"],
        capture_output=True, text=True, check=True
    )
    
    # Parse JSON to get executable path
    import json
    data = json.loads(result.stdout)
    # Extract from conf_info or use default location
    python_exe = Path(".conan") / "bin" / "python3.12"
    if not python_exe.exists():
        python_exe = Path(".conan") / "bin" / "python3"
    if not python_exe.exists():
        python_exe = Path(".conan") / "bin" / "python"
    
    return python_exe

def setup_venv(bundled_python):
    """Create venv using bundled Python."""
    print(f"📦 Creating venv with {bundled_python}")
    subprocess.run([str(bundled_python), "-m", "venv", ".venv"], check=True)

def install_test_harness(sparetools_repo=None):
    """Install sparetools-test-harness package."""
    print("🧪 Installing test harness...")
    
    if sparetools_repo:
        cmd = [
            "conan", "create",
            f"{sparetools_repo}/packages/foundation/sparetools-test-harness",
            "--version=2.0.0",
            "--build=missing"
        ]
    else:
        cmd = [
            "conan", "install",
            "--requires=sparetools-test-harness/2.0.0",
            "--build=missing",
            "-of", ".conan"
        ]
    
    subprocess.run(cmd, check=True)

def install_python_deps(project_type):
    """Install Python dependencies."""
    venv_pip = ".venv/bin/pip"
    
    # Core dependencies
    deps = [
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0",
        "pytest-xdist>=3.0.0",  # Parallel execution
        "black>=23.0.0",
        "ruff>=0.1.0",
        "mypy>=1.0.0",
        "junit-xml>=1.9",  # For JUnit XML output
    ]
    
    # Project-specific dependencies
    if project_type == "mia":
        deps.extend(["python-can", "elm327-emulator"])
    elif project_type == "android":
        deps.extend(["adb-shell", "python-adb"])
    elif project_type == "mcp":
        deps.extend(["mcp", "anthropic"])
    
    subprocess.run([venv_pip, "install"] + deps, check=True)

def setup_hooks():
    """Set up git hooks."""
    try:
        subprocess.run([".venv/bin/pre-commit", "install"], 
                     check=False, capture_output=True)
    except:
        pass  # Optional

def create_config(project_type):
    """Create project-specific configuration."""
    # Create pytest.ini
    pytest_ini = """[pytest]
testpaths = test
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --strict-markers
    --tb=short
    --junitxml=test-results/junit.xml
    --cov=.
    --cov-report=html
    --cov-report=term
"""
    Path("pytest.ini").write_text(pytest_ini)
    
    # Create .ruff.toml
    ruff_toml = """line-length = 100
target-version = "py312"
"""
    Path(".ruff.toml").write_text(ruff_toml)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Bootstrap SpareTools environment"
    )
    parser.add_argument(
        "--project-type", 
        choices=["generic", "mia", "android", "mcp"], 
        default="generic",
        help="Project type for specialized dependencies"
    )
    parser.add_argument(
        "--sparetools-repo",
        type=str,
        help="Path to local SpareTools repository (for development)"
    )
    args = parser.parse_args()
    bootstrap_sparetools(args.project_type, args.sparetools_repo)
```

### 3. Test Harness Package (ngapy-style)

**Location:** `packages/foundation/sparetools-test-harness/`

**Structure:**
```
sparetools-test-harness/
├── conanfile.py
├── README.md
└── sparetools_test_harness/
    ├── __init__.py
    ├── test_harness.py          # Core harness (ngapy-style)
    ├── test_logging.py          # Logging utilities
    ├── pytest_plugin.py        # Pytest integration
    └── verification.py          # Verification methods
```

**Key Features:**
- ngapy-compatible API (`verify()`, `verify_tol()`, `verify_range()`, etc.)
- JUnit XML output
- Structured logging
- Pytest integration
- Works with bundled CPython

**conanfile.py:**
```python
from conan import ConanFile
from conan.tools.files import copy

class SparetoolsTestHarnessConan(ConanFile):
    name = "sparetools-test-harness"
    version = "2.0.0"
    package_type = "python-require"
    description = "Unified test harness for SpareTools projects (ngapy-style)"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/sparetools"
    
    # Require bundled Python
    tool_requires = "sparetools-cpython/3.12.7"
    python_requires = "sparetools-base/2.0.0"
    
    exports_sources = "sparetools_test_harness/**/*.py"
    
    def package(self):
        copy(self, "**/*.py", src=self.source_folder, 
             dst=self.package_folder, keep_path=True)
    
    def package_info(self):
        self.buildenv_info.append_path("PYTHONPATH", self.package_folder)
```

### 4. Unified Test Runner

**Location:** `scripts/test_runner.py`

```python
#!/usr/bin/env python3
"""
SpareTools unified test runner.
Provides ngapy-like test orchestration across projects.
"""
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Dict
import json

class TestRunner:
    """Unified test runner for all SpareTools projects."""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.venv_python = self.project_root / ".venv/bin/python"
        self.results_dir = self.project_root / "test-results"
        self.results_dir.mkdir(exist_ok=True)
        
    def run_unit_tests(self, coverage=True, parallel=True) -> int:
        """Run unit tests with optional coverage."""
        cmd = [str(self.venv_python), "-m", "pytest", "test/unit/"]
        
        if coverage:
            cmd.extend([
                "--cov=.",
                "--cov-report=html:test-results/coverage",
                "--cov-report=term"
            ])
        
        if parallel:
            cmd.extend(["-n", "auto"])  # pytest-xdist
        
        cmd.extend([
            "--junitxml=test-results/junit-unit.xml"
        ])
        
        return subprocess.run(cmd, cwd=self.project_root).returncode
    
    def run_integration_tests(self) -> int:
        """Run integration tests."""
        cmd = [
            str(self.venv_python), "-m", "pytest", 
            "test/integration/",
            "--junitxml=test-results/junit-integration.xml"
        ]
        return subprocess.run(cmd, cwd=self.project_root).returncode
    
    def run_linters(self) -> int:
        """Run code quality checks."""
        checks = [
            {
                "name": "Black",
                "cmd": [str(self.venv_python), "-m", "black", "--check", "."]
            },
            {
                "name": "Ruff",
                "cmd": [str(self.venv_python), "-m", "ruff", "check", "."]
            },
            {
                "name": "MyPy",
                "cmd": [str(self.venv_python), "-m", "mypy", "scripts/", "--ignore-missing-imports"]
            },
        ]
        
        failed = []
        for check in checks:
            result = subprocess.run(
                check["cmd"], 
                cwd=self.project_root,
                capture_output=True
            )
            if result.returncode != 0:
                failed.append(check["name"])
                print(f"❌ {check['name']} failed")
                print(result.stdout.decode())
                print(result.stderr.decode())
            else:
                print(f"✅ {check['name']} passed")
        
        return 1 if failed else 0
    
    def run_security_scan(self) -> int:
        """Run security scanning (if available)."""
        # Check for trivy
        try:
            result = subprocess.run(
                ["trivy", "fs", "--security-checks", "vuln", "."],
                cwd=self.project_root,
                capture_output=True
            )
            return result.returncode
        except FileNotFoundError:
            print("⚠️  Trivy not found, skipping security scan")
            return 0
    
    def run_all(self, include_security=False) -> int:
        """Run all tests and checks."""
        print("🧪 Running SpareTools Test Suite")
        print("=" * 60)
        
        results = {
            "Linters": self.run_linters(),
            "Unit Tests": self.run_unit_tests(),
            "Integration Tests": self.run_integration_tests(),
        }
        
        if include_security:
            results["Security Scan"] = self.run_security_scan()
        
        print("\n" + "=" * 60)
        print("📊 Test Results:")
        for name, code in results.items():
            status = "✅ PASS" if code == 0 else "❌ FAIL"
            print(f"  {name}: {status}")
        
        # Generate summary JSON
        summary = {
            "timestamp": str(Path(__file__).stat().st_mtime),
            "results": results,
            "overall": "PASS" if max(results.values()) == 0 else "FAIL"
        }
        (self.results_dir / "summary.json").write_text(json.dumps(summary, indent=2))
        
        return max(results.values())

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run SpareTools test suite")
    parser.add_argument("--unit-only", action="store_true")
    parser.add_argument("--integration-only", action="store_true")
    parser.add_argument("--lint-only", action="store_true")
    parser.add_argument("--security", action="store_true")
    args = parser.parse_args()
    
    runner = TestRunner()
    
    if args.unit_only:
        sys.exit(runner.run_unit_tests())
    elif args.integration_only:
        sys.exit(runner.run_integration_tests())
    elif args.lint_only:
        sys.exit(runner.run_linters())
    else:
        sys.exit(runner.run_all(include_security=args.security))
```

### 5. Test Harness Implementation (ngapy-style)

**Location:** `packages/foundation/sparetools-test-harness/sparetools_test_harness/test_harness.py`

```python
"""
SpareTools Test Harness - ngapy-style verification framework
"""
import numbers
import time
import traceback
from typing import Optional, Callable, Any
from pathlib import Path

try:
    from .test_logging import ThLogger
except ImportError:
    # Fallback for direct import
    from sparetools_test_harness.test_logging import ThLogger


class SpareToolsTestHarness:
    """Test harness with ngapy-compatible API."""
    
    def __init__(self, results_dir: Optional[Path] = None):
        """Initialize test harness."""
        self.__output_format__ = "dec"
        self.__callback_function__ = None
        self.th_logger = ThLogger()
        self.results_dir = results_dir or Path("test-results")
        self.results_dir.mkdir(exist_ok=True)
    
    def verify(self, actual, expected, msg="", test_num=0, on_fail=None) -> bool:
        """Verify equality (ngapy-compatible)."""
        value = (actual == expected)
        text = [f"Verify {msg + ' ' if msg else ''}:"]
        
        if self.__output_format__ == "hex" and isinstance(expected, int) and isinstance(actual, int):
            text.append(f"\t  Expected : 0x{expected:x}")
            text.append(f"\t  Actual   : 0x{actual:x}")
        else:
            text.append(f"\t  Expected : {expected}")
            text.append(f"\t  Actual   : {actual}")
        
        self.th_logger.log_result(value, text, test_num)
        self.th_logger.log_junit_result(
            value, text, description=msg, testnum=test_num, 
            timestamp=time.ctime()
        )
        
        if not value:
            self.handle_on_fail(on_fail)
        
        return value
    
    def verify_tol(self, actual, expected, tolerance, msg="", test_num=0, on_fail=None) -> bool:
        """Verify with tolerance (ngapy-compatible)."""
        if not isinstance(tolerance, numbers.Number):
            raise ValueError("tolerance must be numeric")
        
        value = False
        if isinstance(actual, numbers.Number) and isinstance(expected, numbers.Number):
            value = ((expected + tolerance) >= actual) & ((expected - tolerance) <= actual)
        else:
            raise ValueError('invalid data types for verification')
        
        text = [f"Verify {msg + ' ' if msg else ''}:"]
        text.append(f"\t  Expected : {expected} +/- {tolerance}")
        text.append(f"\t  Actual   : {actual}")
        
        self.th_logger.log_result(value, text, test_num)
        self.th_logger.log_junit_result(
            value, text, description=msg, testnum=test_num,
            timestamp=time.ctime()
        )
        
        if not value:
            self.handle_on_fail(on_fail)
        
        return value
    
    def verify_range(self, actual, min_value, max_value, msg="", test_num=0, on_fail=None) -> bool:
        """Verify value in range (ngapy-compatible)."""
        if not all(isinstance(x, numbers.Number) for x in [actual, min_value, max_value]):
            raise ValueError('invalid data types for verification')
        
        value = (actual >= min_value) and (actual <= max_value)
        text = [f"Verify {msg + ' ' if msg else ''}:"]
        text.append(f"\t  Expected : {min_value} <= Actual <= {max_value}")
        text.append(f"\t  Actual   : {actual}")
        
        self.th_logger.log_result(value, text, test_num)
        self.th_logger.log_junit_result(
            value, text, description=msg, testnum=test_num,
            timestamp=time.ctime()
        )
        
        if not value:
            self.handle_on_fail(on_fail)
        
        return value
    
    # Additional verification methods: verify_ne, verify_lt, verify_gt, 
    # verify_le, verify_ge, verify_string, verify_percent, etc.
    # (Following ngapy's API)
    
    @staticmethod
    def handle_on_fail(on_fail):
        """Handle on_fail callback."""
        try:
            if hasattr(on_fail, '__iter__'):
                for obj in on_fail:
                    obj.run()
            else:
                if callable(on_fail):
                    on_fail()
                elif hasattr(on_fail, 'run'):
                    on_fail.run()
        except:
            pass


def run_test(function_to_run: Callable, results_dir_path: Path, header_message: str) -> str:
    """
    Run a test procedure (ngapy-compatible).
    Returns: "pass", "fail", or "abort"
    """
    th_logger = ThLogger()
    time_stamp = time.strftime("%m_%d_%Y_%H%M%S", time.localtime())
    
    import inspect
    test_name = Path(inspect.getfile(function_to_run)).stem
    log_file_basename = f"{test_name}_{time_stamp}.txt"
    junit_xml_log_file_basename = f"{test_name}_{time_stamp}.xml"
    
    abs_results_dir_path = results_dir_path.resolve()
    abs_path_log_filename = abs_results_dir_path / log_file_basename
    abs_path_junit_xml_log_filename = abs_results_dir_path / junit_xml_log_file_basename
    
    if log_file_basename:
        th_logger.__test_log__.open_test_log_file(str(abs_path_log_filename), header_message)
    
    # Extract test description
    test_descr = header_message
    for line in header_message.split('\n'):
        if 'description' in line.lower():
            test_descr = line.split(':  ')[1] if ':  ' in line else header_message
            break
    
    if junit_xml_log_file_basename:
        header_info_dict = {
            "TestProcedureName": f"{test_name}.py",
            "Description": test_descr
        }
        th_logger.__junit_xml_log__.set_header_info_dict(header_info_dict)
    
    # Run test
    try:
        result = "fail"
        function_to_run()
        if not th_logger.__test_log__.get_test_failures():
            if th_logger.__test_log__.get_test_passes():
                result = "pass"
            else:
                th_logger.log_result(0, "No verifications performed:", 0)
    except Exception:
        th_logger.__test_log__.write_test_log(traceback.format_exc())
        th_logger.__junit_xml_log__.write_test_result(
            False, traceback.format_exc(),
            description="Test exception occurred",
            testnum=-1, timestamp=time.ctime()
        )
        result = "abort"
    
    th_logger.__test_log__.close_test_log_file()
    th_logger.__junit_xml_log__.create_test_log_file(str(abs_path_junit_xml_log_filename))
    
    return result
```

### 6. Repository Templates

**Location:** `templates/`

Each template includes:
- `conanfile.py.template` - Uses sparetools packages
- `pytest.ini.template` - Test configuration
- `pyproject.toml.template` - Python project config
- `.github/workflows/ci.yml.template` - CI workflow
- `test/unit/__init__.py` - Test structure
- `test/integration/__init__.py` - Integration test structure

### 7. Integration with Existing SpareTools

**Changes to existing packages:**

1. **sparetools-base**: Add test harness utilities (if needed)
2. **sparetools-cpython**: Already provides bundled Python ✅
3. **New package**: `sparetools-test-harness` - Test framework

**No breaking changes** to existing packages.

## Implementation Plan

### Phase 1: Core Test Harness (Week 1)
- [ ] Create `sparetools-test-harness` package
- [ ] Implement core verification methods (ngapy-compatible API)
- [ ] Implement logging and JUnit XML output
- [ ] Add pytest integration

### Phase 2: Bootstrap Script (Week 1-2)
- [ ] Create universal `bootstrap.py`
- [ ] Integrate with Conan for package installation
- [ ] Support local repo development mode
- [ ] Add project type detection

### Phase 3: Test Runner (Week 2)
- [ ] Create unified `test_runner.py`
- [ ] Integrate with test harness
- [ ] Add parallel execution support
- [ ] Generate summary reports

### Phase 4: Templates (Week 2-3)
- [ ] Create generic template
- [ ] Create MIA-specific template
- [ ] Create MCP-specific template
- [ ] Create Android-specific template

### Phase 5: Documentation & Testing (Week 3)
- [ ] Write quick start guide
- [ ] Create integration tests for bootstrap
- [ ] Test cross-repo compatibility
- [ ] Update main README

## Usage Examples

### In a New Repository

```bash
# 1. Download bootstrap script
curl -O https://raw.githubusercontent.com/sparesparrow/sparetools/main/scripts/bootstrap.py

# 2. Run bootstrap
python bootstrap.py --project-type generic

# 3. Activate environment
source .venv/bin/activate

# 4. Run tests
python scripts/test_runner.py
```

### In Existing MIA Repository

```bash
cd mia

# Update to use new bootstrap
curl -O https://raw.githubusercontent.com/sparesparrow/sparetools/main/scripts/bootstrap.py
python bootstrap.py --project-type mia

# Everything just works
source .venv/bin/activate
pytest  # Uses bundled Python
conan install .  # Uses sparetools packages
```

### Using Test Harness in Tests

```python
"""Example test using SpareTools test harness"""
from sparetools_test_harness import SpareToolsTestHarness

def test_example():
    """Example test with verification."""
    th = SpareToolsTestHarness()
    
    # ngapy-style verification
    th.verify(2 + 2, 4, "Basic arithmetic", test_num=1)
    th.verify_tol(3.14159, 3.14, 0.01, "Pi approximation", test_num=2)
    th.verify_range(5, 1, 10, "Value in range", test_num=3)
```

## Benefits

1. **DRY Principle** - One source of truth for all tooling
2. **Consistency** - Same environment in all repos
3. **Onboarding** - New contributors run one command
4. **Portability** - Works on Linux, macOS, Windows
5. **Isolation** - No system dependencies required
6. **Maintainability** - Update once, benefit everywhere
7. **ngapy Compatibility** - Familiar API for teams using ngapy
8. **CI Integration** - JUnit XML output works with all CI systems

## Migration Path

### For Existing Projects

1. **Add bootstrap script** to repository
2. **Run bootstrap** to set up environment
3. **Gradually migrate tests** to use test harness (optional)
4. **Update CI workflows** to use test runner

### Backward Compatibility

- Existing pytest tests continue to work
- Test harness is optional (can use pytest directly)
- No changes required to existing Conan recipes

## Next Steps

1. Review and approve this plan
2. Create GitHub issue for tracking
3. Begin Phase 1 implementation
4. Test with sample repositories
5. Document and release
