"""
MIA Bootstrap Remediation

MIA-specific bootstrap failure remediation and recovery procedures.
Handles MIA component initialization failures and recovery scenarios.
"""

import asyncio
import logging
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
import time


class MIABootstrapRemediation:
    """MIA-specific bootstrap remediation"""

    def __init__(self, mia_root: Optional[Path] = None):
        self.mia_root = mia_root or Path(__file__).parent
        self.logger = logging.getLogger(__name__)

        # MIA-specific remediation strategies
        self.mia_remediation_strategies = {
            "WORKER_STARTUP_FAILED": self._fix_worker_startup,
            "ZMQ_CONNECTION_FAILED": self._fix_zmq_connection,
            "HARDWARE_ACCESS_DENIED": self._fix_hardware_access,
            "ICD_TYPE_MISMATCH": self._fix_icd_type_mismatch,
            "MCP_SERVER_FAILED": self._fix_mcp_server_failed,
        }

    async def remediate_mia_failures(self, failure_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Remediate MIA-specific bootstrap failures"""
        self.logger.info("Starting MIA-specific remediation")

        failures = failure_summary.get("failures", [])
        mia_failures = [f for f in failures if self._is_mia_failure(f)]

        results = {
            "total_mia_failures": len(mia_failures),
            "remediated": 0,
            "failed": 0,
            "details": []
        }

        for failure in mia_failures:
            fix_result = await self._apply_mia_remediation(failure)
            results["details"].append({
                "failure": failure,
                "fix_result": fix_result
            })

            if fix_result["success"]:
                results["remediated"] += 1
            else:
                results["failed"] += 1

        self.logger.info(f"MIA remediation complete: {results}")
        return results

    def _is_mia_failure(self, failure: Dict[str, Any]) -> bool:
        """Check if failure is MIA-specific"""
        component = failure.get("component", "").lower()
        message = failure.get("message", "").lower()

        mia_indicators = [
            "mia" in component,
            "gpio" in component,
            "obd" in component,
            "rf" in component,
            "zmq" in message,
            "worker" in component,
            "mcp" in component,
            "hardware" in component
        ]

        return any(mia_indicators)

    async def _apply_mia_remediation(self, failure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply MIA-specific remediation"""
        failure_type = failure.get("type", "UNKNOWN")
        component = failure.get("component", "")

        strategy = self.mia_remediation_strategies.get(failure_type)
        if not strategy:
            # Try generic MIA fixes
            return await self._fix_generic_mia_issue(failure)

        try:
            return await strategy(failure)
        except Exception as e:
            self.logger.error(f"MIA remediation failed: {e}")
            return {"success": False, "error": str(e)}

    async def _fix_worker_startup(self, failure: Dict[str, Any]) -> Dict[str, Any]:
        """Fix ZeroMQ worker startup failures"""
        component = failure.get("component", "")

        self.logger.info(f"Fixing worker startup for {component}")

        # Kill any existing processes on the ports
        await self._kill_process_on_port("5555")  # GPIO worker
        await self._kill_process_on_port("5556")  # OBD worker
        await self._kill_process_on_port("5557")  # RF worker

        # Wait for cleanup
        await asyncio.sleep(2.0)

        # Try to restart the specific worker
        if "gpio" in component.lower():
            return await self._restart_worker("gpio")
        elif "obd" in component.lower():
            return await self._restart_worker("obd")
        elif "rf" in component.lower():
            return await self._restart_worker("rf")

        return {"success": False, "reason": "Unknown worker type"}

    async def _fix_zmq_connection(self, failure: Dict[str, Any]) -> Dict[str, Any]:
        """Fix ZeroMQ connection issues"""
        self.logger.info("Fixing ZMQ connection issues")

        # Reset ZMQ context and restart workers
        await self._kill_all_workers()
        await asyncio.sleep(3.0)

        # Restart all workers
        results = []
        for worker_type in ["gpio", "obd", "rf"]:
            result = await self._restart_worker(worker_type)
            results.append(result)

        success_count = sum(1 for r in results if r.get("success"))
        return {
            "success": success_count > 0,
            "workers_restarted": success_count,
            "total_workers": len(results)
        }

    async def _fix_hardware_access(self, failure: Dict[str, Any]) -> Dict[str, Any]:
        """Fix hardware access permission issues"""
        component = failure.get("component", "")

        self.logger.info(f"Fixing hardware access for {component}")

        # GPIO access fix
        if "gpio" in component.lower():
            try:
                # Add user to gpio group
                result = subprocess.run(
                    ["sudo", "usermod", "-a", "-G", "gpio", "mia"],
                    capture_output=True,
                    text=True
                )

                # Reload groups
                subprocess.run(["newgrp", "gpio"], capture_output=True)

                return {"success": True, "method": "gpio_group_add"}

            except Exception as e:
                return {"success": False, "error": str(e)}

        # Serial port access fix
        elif "serial" in component.lower() or "obd" in component.lower() or "rf" in component.lower():
            try:
                # Add user to dialout group for serial access
                result = subprocess.run(
                    ["sudo", "usermod", "-a", "-G", "dialout", "mia"],
                    capture_output=True,
                    text=True
                )

                return {"success": True, "method": "dialout_group_add"}

            except Exception as e:
                return {"success": False, "error": str(e)}

        return {"success": False, "reason": "Unknown hardware type"}

    async def _fix_icd_type_mismatch(self, failure: Dict[str, Any]) -> Dict[str, Any]:
        """Fix ICD type mismatch issues"""
        self.logger.info("Fixing ICD type mismatches")

        try:
            # Regenerate ICD Python classes
            icd_dir = self.mia_root.parent.parent / "foundation" / "sparetools-icd"

            schemas = ["hardware.fbs", "obd.fbs", "rf.fbs"]
            for schema in schemas:
                result = subprocess.run([
                    sys.executable,
                    "tools/fbs_to_python.py",
                    f"schemas/{schema}",
                    "-o",
                    f"{schema.replace('.fbs', '_generated.py')}"
                ], capture_output=True, text=True, cwd=icd_dir)

                if result.returncode != 0:
                    return {"success": False, "error": f"ICD generation failed for {schema}"}

            # Clear Python cache
            for cache_dir in self.mia_root.rglob("__pycache__"):
                if cache_dir.is_dir():
                    import shutil
                    shutil.rmtree(cache_dir)

            return {"success": True, "method": "icd_regeneration"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _fix_mcp_server_failed(self, failure: Dict[str, Any]) -> Dict[str, Any]:
        """Fix MCP server startup failures"""
        self.logger.info("Fixing MCP server startup")

        try:
            # Kill existing MCP processes
            await self._kill_process_by_name("hardware_server.py")

            # Wait and restart
            await asyncio.sleep(2.0)

            # Try to start MCP server
            result = subprocess.run([
                sys.executable,
                "-m",
                "mia.mcp.hardware_server"
            ], capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                return {"success": True, "method": "mcp_restart"}
            else:
                return {"success": False, "error": result.stderr}

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "MCP server start timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _fix_generic_mia_issue(self, failure: Dict[str, Any]) -> Dict[str, Any]:
        """Apply generic MIA fixes"""
        self.logger.info("Applying generic MIA fixes")

        # Try common fixes in order
        fixes = [
            self._restart_all_workers,
            self._clear_mia_cache,
            self._reset_mia_config
        ]

        for fix_func in fixes:
            try:
                result = await fix_func()
                if result["success"]:
                    return result
            except Exception as e:
                self.logger.debug(f"Generic fix failed: {e}")
                continue

        return {"success": False, "reason": "All generic fixes failed"}

    async def _restart_all_workers(self) -> Dict[str, Any]:
        """Restart all MIA workers"""
        self.logger.info("Restarting all MIA workers")

        await self._kill_all_workers()
        await asyncio.sleep(3.0)

        success_count = 0
        for worker_type in ["gpio", "obd", "rf"]:
            result = await self._restart_worker(worker_type)
            if result.get("success"):
                success_count += 1

        return {
            "success": success_count > 0,
            "workers_restarted": success_count,
            "method": "worker_restart"
        }

    async def _clear_mia_cache(self) -> Dict[str, Any]:
        """Clear MIA caches and temporary files"""
        self.logger.info("Clearing MIA caches")

        cache_patterns = [
            "**/__pycache__",
            "**/*.pyc",
            "**/.pytest_cache",
            "**/build",
            "**/dist"
        ]

        cleared_count = 0
        for pattern in cache_patterns:
            for path in Path(self.mia_root).glob(pattern):
                try:
                    if path.is_file():
                        path.unlink()
                    elif path.is_dir():
                        import shutil
                        shutil.rmtree(path)
                    cleared_count += 1
                except Exception:
                    pass

        return {
            "success": True,
            "cache_items_cleared": cleared_count,
            "method": "cache_clear"
        }

    async def _reset_mia_config(self) -> Dict[str, Any]:
        """Reset MIA configuration to defaults"""
        self.logger.info("Resetting MIA configuration")

        # Reset environment variables
        mia_env_vars = [
            "MIA_ZMQ_GPIO_PORT",
            "MIA_ZMQ_OBD_PORT",
            "MIA_ZMQ_RF_PORT",
            "MIA_SIMULATION",
            "MIA_TEST_MODE"
        ]

        for var in mia_env_vars:
            import os
            os.environ.pop(var, None)

        return {"success": True, "method": "config_reset"}

    async def _restart_worker(self, worker_type: str) -> Dict[str, Any]:
        """Restart a specific worker"""
        self.logger.info(f"Restarting {worker_type} worker")

        try:
            # Import and start the worker
            if worker_type == "gpio":
                from .hardware.gpio_worker import GPIOZMQWorker
                worker = GPIOZMQWorker()
            elif worker_type == "obd":
                from .services.obd_worker import OBDZMQWorker
                worker = OBDZMQWorker()
            elif worker_type == "rf":
                from .hardware.rf_worker import RFZMQWorker
                worker = RFZMQWorker()
            else:
                return {"success": False, "error": f"Unknown worker type: {worker_type}"}

            # Start worker in background
            asyncio.create_task(worker.start())

            # Give it time to start
            await asyncio.sleep(2.0)

            return {"success": True, "worker_type": worker_type}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _kill_process_on_port(self, port: str):
        """Kill process using a specific port"""
        try:
            result = subprocess.run(
                ["lsof", "-ti", f":{port}"],
                capture_output=True,
                text=True
            )

            if result.returncode == 0 and result.stdout.strip():
                pid = result.stdout.strip()
                subprocess.run(["kill", "-9", pid], capture_output=True)
                self.logger.info(f"Killed process {pid} on port {port}")

        except Exception as e:
            self.logger.debug(f"Could not kill process on port {port}: {e}")

    async def _kill_process_by_name(self, process_name: str):
        """Kill processes by name pattern"""
        try:
            result = subprocess.run(
                ["pkill", "-f", process_name],
                capture_output=True
            )
            if result.returncode == 0:
                self.logger.info(f"Killed processes matching {process_name}")

        except Exception as e:
            self.logger.debug(f"Could not kill processes by name: {e}")

    async def _kill_all_workers(self):
        """Kill all MIA worker processes"""
        worker_patterns = [
            "gpio_worker.py",
            "obd_worker.py",
            "rf_worker.py",
            "hardware_server.py"
        ]

        for pattern in worker_patterns:
            await self._kill_process_by_name(pattern)

        # Also kill by port
        ports = ["5555", "5556", "5557", "5558"]
        for port in ports:
            await self._kill_process_on_port(port)


async def remediate_mia_bootstrap_failures(summary_file: Path) -> Dict[str, Any]:
    """Convenience function to remediate MIA bootstrap failures"""
    try:
        with open(summary_file, 'r') as f:
            summary = json.load(f)
    except Exception as e:
        return {"success": False, "error": f"Failed to load summary: {e}"}

    remediation = MIABootstrapRemediation()
    return await remediation.remediate_mia_failures(summary)


if __name__ == "__main__":
    # Command line interface
    import argparse

    parser = argparse.ArgumentParser(description="MIA Bootstrap Remediation")
    parser.add_argument("summary_file", type=Path, help="Failure summary JSON file")
    parser.add_argument("--mia-root", type=Path, default=None,
                       help="MIA root directory")

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    async def main():
        result = await remediate_mia_bootstrap_failures(args.summary_file)
        print(json.dumps(result, indent=2))
        return 0 if result.get("remediated", 0) > 0 else 1

    sys.exit(asyncio.run(main()))