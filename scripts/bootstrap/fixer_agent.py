#!/usr/bin/env python3
"""
Bootstrap Fixer Agent

Automated remediation agent that fixes bootstrap failures based on test results.
Analyzes failure summaries and applies appropriate fixes to restore system functionality.
"""

import json
import logging
import subprocess
import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import time
import tempfile
import shutil


class BootstrapFixerAgent:
    """Automated bootstrap failure remediation agent"""

    def __init__(self, workspace_root: Optional[Path] = None):
        self.workspace_root = workspace_root or Path.cwd()
        self.logger = logging.getLogger(__name__)

        # Remediation strategies by failure type
        self.remediation_strategies = {
            "MISSING_DEPENDENCY": self._fix_missing_dependency,
            "IMPORT_ERROR": self._fix_import_error,
            "ASSERTION_ERROR": self._fix_assertion_error,
            "CONAN_INSTALL_FAILED": self._fix_conan_install_failed,
            "BUILD_FAILED": self._fix_build_failed,
            "TEST_FAILED": self._fix_test_failed,
            "ICD_GENERATION_FAILED": self._fix_icd_generation_failed,
        }

        # Track applied fixes to avoid loops
        self.applied_fixes: List[str] = []

    async def remediate_failures(self, summary_json: Dict[str, Any]) -> Dict[str, Any]:
        """Main remediation entry point

        Args:
            summary_json: Bootstrap failure summary from test runner

        Returns:
            Remediation results
        """
        self.logger.info("Starting bootstrap failure remediation")

        failures = summary_json.get("failures", [])
        results = {
            "total_failures": len(failures),
            "remediated": 0,
            "failed_remediation": 0,
            "retry_recommended": False,
            "details": []
        }

        for failure in failures:
            failure_type = failure.get("type", "UNKNOWN")
            fix_result = await self._apply_remediation(failure)

            results["details"].append({
                "failure": failure,
                "remediation_result": fix_result
            })

            if fix_result["success"]:
                results["remediated"] += 1
            else:
                results["failed_remediation"] += 1

        # Recommend retry if any fixes were applied
        results["retry_recommended"] = results["remediated"] > 0

        self.logger.info(f"Remediation complete: {results}")
        return results

    async def _apply_remediation(self, failure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply appropriate remediation for a failure"""
        failure_type = failure.get("type", "UNKNOWN")
        failure_id = f"{failure_type}:{failure.get('component', 'unknown')}"

        # Avoid applying the same fix multiple times
        if failure_id in self.applied_fixes:
            return {
                "success": False,
                "reason": "Fix already applied",
                "fix_id": failure_id
            }

        strategy = self.remediation_strategies.get(failure_type)
        if not strategy:
            return {
                "success": False,
                "reason": f"No remediation strategy for {failure_type}",
                "fix_id": failure_id
            }

        try:
            self.logger.info(f"Applying remediation for {failure_id}")
            result = await strategy(failure)

            if result["success"]:
                self.applied_fixes.append(failure_id)

            return result

        except Exception as e:
            self.logger.error(f"Remediation failed for {failure_id}: {e}")
            return {
                "success": False,
                "reason": f"Remediation exception: {e}",
                "fix_id": failure_id
            }

    async def _fix_missing_dependency(self, failure: Dict[str, Any]) -> Dict[str, Any]:
        """Fix missing dependency issues"""
        package = failure.get("package", "")
        component = failure.get("component", "")

        if not package:
            return {"success": False, "reason": "No package specified"}

        self.logger.info(f"Installing missing dependency: {package}")

        try:
            # Try pip install first
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", package],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                return {"success": True, "method": "pip", "package": package}

            # Try apt install for system packages
            if package in ["build-essential", "python3-dev", "libssl-dev"]:
                result = subprocess.run(
                    ["sudo", "apt", "update", "&&", "sudo", "apt", "install", "-y", package],
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=120
                )

                if result.returncode == 0:
                    return {"success": True, "method": "apt", "package": package}

            return {"success": False, "reason": "All installation methods failed"}

        except subprocess.TimeoutExpired:
            return {"success": False, "reason": "Installation timeout"}

    async def _fix_import_error(self, failure: Dict[str, Any]) -> Dict[str, Any]:
        """Fix Python import errors"""
        module = failure.get("module", "")
        component = failure.get("component", "")

        if not module:
            return {"success": False, "reason": "No module specified"}

        self.logger.info(f"Fixing import error for module: {module}")

        # Check if it's a path issue
        if module.startswith("sparetools") or module.startswith("mia"):
            # Fix Python path
            module_path = self._find_module_path(module)
            if module_path:
                if str(module_path) not in sys.path:
                    sys.path.insert(0, str(module_path))
                    return {"success": True, "method": "path_fix", "module": module}

        # Try installing the module
        return await self._fix_missing_dependency({
            "package": module.replace(".", "-"),
            "component": component
        })

    async def _fix_assertion_error(self, failure: Dict[str, Any]) -> Dict[str, Any]:
        """Fix assertion errors, often related to ICD issues"""
        error_msg = failure.get("message", "")
        component = failure.get("component", "")

        self.logger.info(f"Fixing assertion error in {component}: {error_msg}")

        # Common assertion error fixes
        if "ICD" in error_msg or "schema" in error_msg.lower():
            return await self._fix_icd_generation_failed(failure)

        # Check for version mismatches
        if "version" in error_msg.lower():
            return await self._fix_version_mismatch(failure)

        # Regenerate problematic files
        if component:
            return await self._regenerate_component(component)

        return {"success": False, "reason": "Unknown assertion error type"}

    async def _fix_conan_install_failed(self, failure: Dict[str, Any]) -> Dict[str, Any]:
        """Fix Conan installation failures"""
        package = failure.get("package", "")
        error_msg = failure.get("message", "")

        self.logger.info(f"Fixing Conan install failure for {package}")

        try:
            # Clear Conan cache
            result = subprocess.run(
                ["conan", "remove", "*", "-f"],
                capture_output=True,
                text=True,
                cwd=self.workspace_root
            )

            # Try reinstall
            result = subprocess.run(
                ["conan", "install", ".", "--build=missing"],
                capture_output=True,
                text=True,
                cwd=self.workspace_root
            )

            if result.returncode == 0:
                return {"success": True, "method": "cache_clear_reinstall"}

            return {"success": False, "reason": "Reinstall failed"}

        except Exception as e:
            return {"success": False, "reason": f"Conan fix failed: {e}"}

    async def _fix_build_failed(self, failure: Dict[str, Any]) -> Dict[str, Any]:
        """Fix build failures"""
        component = failure.get("component", "")
        error_msg = failure.get("message", "")

        self.logger.info(f"Fixing build failure for {component}")

        # Clean build artifacts
        build_dirs = ["build", "dist", "__pycache__", "*.pyc"]
        for pattern in build_dirs:
            for path in Path(self.workspace_root).rglob(pattern):
                if path.is_file():
                    path.unlink()
                elif path.is_dir():
                    shutil.rmtree(path)

        # Try rebuild
        try:
            result = subprocess.run(
                [sys.executable, "setup.py", "build_ext", "--inplace"],
                capture_output=True,
                text=True,
                cwd=self.workspace_root
            )

            if result.returncode == 0:
                return {"success": True, "method": "rebuild"}

        except Exception:
            pass

        return {"success": False, "reason": "Rebuild failed"}

    async def _fix_test_failed(self, failure: Dict[str, Any]) -> Dict[str, Any]:
        """Fix test failures"""
        test_name = failure.get("test", "")
        error_msg = failure.get("message", "")

        self.logger.info(f"Fixing test failure: {test_name}")

        # Many test failures are due to environment issues
        # Try standard fixes

        # Fix 1: Clean test cache
        for path in Path(self.workspace_root).rglob("__pycache__"):
            if path.is_dir():
                shutil.rmtree(path)

        # Fix 2: Reinstall test dependencies
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-e", ".[test]"],
                capture_output=True,
                text=True,
                cwd=self.workspace_root
            )

            if result.returncode == 0:
                return {"success": True, "method": "reinstall_test_deps"}

        except Exception:
            pass

        return {"success": False, "reason": "Test fix failed"}

    async def _fix_icd_generation_failed(self, failure: Dict[str, Any]) -> Dict[str, Any]:
        """Fix ICD generation failures"""
        self.logger.info("Regenerating ICD artifacts")

        try:
            # Run ICD generation tools
            icd_dir = self.workspace_root / "packages" / "foundation" / "sparetools-icd"

            # Generate Python classes
            result = subprocess.run(
                [sys.executable, "tools/fbs_to_python.py", "schemas/hardware.fbs", "-o", "hardware_generated.py"],
                capture_output=True,
                text=True,
                cwd=icd_dir
            )

            if result.returncode != 0:
                return {"success": False, "reason": "ICD Python generation failed"}

            # Generate MCP tools
            result = subprocess.run(
                [sys.executable, "tools/fbs_to_mcp.py", "schemas/"],
                capture_output=True,
                text=True,
                cwd=icd_dir
            )

            if result.returncode != 0:
                return {"success": False, "reason": "ICD MCP generation failed"}

            return {"success": True, "method": "icd_regeneration"}

        except Exception as e:
            return {"success": False, "reason": f"ICD regeneration failed: {e}"}

    async def _fix_version_mismatch(self, failure: Dict[str, Any]) -> Dict[str, Any]:
        """Fix version mismatch issues"""
        self.logger.info("Fixing version mismatches")

        try:
            # Update all requirements
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "--upgrade", "-r", "requirements-dev.txt"],
                capture_output=True,
                text=True,
                cwd=self.workspace_root
            )

            if result.returncode == 0:
                return {"success": True, "method": "upgrade_dependencies"}

        except Exception:
            pass

        return {"success": False, "reason": "Version fix failed"}

    async def _regenerate_component(self, component: str) -> Dict[str, Any]:
        """Regenerate a specific component"""
        self.logger.info(f"Regenerating component: {component}")

        try:
            # Component-specific regeneration logic
            if "icd" in component.lower():
                return await self._fix_icd_generation_failed({})

            # Generic regeneration - try rebuild
            return await self._fix_build_failed({"component": component})

        except Exception as e:
            return {"success": False, "reason": f"Component regeneration failed: {e}"}

    def _find_module_path(self, module_name: str) -> Optional[Path]:
        """Find the path for a Python module"""
        # Search in workspace
        for root in ["packages", "sparetools", "src"]:
            search_path = self.workspace_root / root
            if search_path.exists():
                for path in search_path.rglob("**"):
                    if path.is_dir() and path.name == module_name.replace(".", "_"):
                        return path
                    elif path.is_file() and path.name == f"{module_name.replace('.', '_')}.py":
                        return path.parent

        return None

    async def run_bootstrap_retry(self) -> Dict[str, Any]:
        """Run bootstrap retry after applying fixes"""
        self.logger.info("Running bootstrap retry")

        try:
            result = subprocess.run(
                [sys.executable, "scripts/bootstrap/bootstrap.py"],
                capture_output=True,
                text=True,
                cwd=self.workspace_root,
                timeout=300  # 5 minute timeout
            )

            return {
                "success": result.returncode == 0,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }

        except subprocess.TimeoutExpired:
            return {"success": False, "reason": "Bootstrap retry timeout"}

        except Exception as e:
            return {"success": False, "reason": f"Bootstrap retry failed: {e}"}


async def main():
    """Command line interface for the fixer agent"""
    import argparse

    parser = argparse.ArgumentParser(description="Bootstrap Fixer Agent")
    parser.add_argument("summary_file", help="Bootstrap failure summary JSON file")
    parser.add_argument("--workspace", type=Path, default=None,
                       help="Workspace root directory")
    parser.add_argument("--auto-retry", action="store_true",
                       help="Automatically retry bootstrap after fixes")

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Load failure summary
    try:
        with open(args.summary_file, 'r') as f:
            summary = json.load(f)
    except Exception as e:
        print(f"Failed to load summary file: {e}")
        return 1

    # Run remediation
    agent = BootstrapFixerAgent(args.workspace)
    results = await agent.remediate_failures(summary)

    print(json.dumps(results, indent=2))

    # Auto-retry if requested and fixes were applied
    if args.auto_retry and results.get("retry_recommended"):
        print("Applying fixes and retrying bootstrap...")
        retry_result = await agent.run_bootstrap_retry()

        print("Retry results:")
        print(json.dumps(retry_result, indent=2))

        return 0 if retry_result.get("success") else 1

    return 0 if results["remediated"] > 0 else 1


if __name__ == "__main__":
    import asyncio
    sys.exit(asyncio.run(main()))