"""Deployment orchestrator for embedded systems.

This module provides deployment orchestration functionality for
building and deploying to embedded devices.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from sparetools.mcp_core.core.exceptions import DeploymentError, ErrorCode
from sparetools.mcp_core.devices import DeviceDetector, DeviceInfo
from sparetools.mcp_core.deployment.profiles import ConanProfileManager

logger = logging.getLogger(__name__)


class DeploymentMode(Enum):
    """Deployment execution mode."""

    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"


class DeploymentStatus(Enum):
    """Status of a deployment."""

    PENDING = "pending"
    BUILDING = "building"
    FLASHING = "flashing"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class DeploymentTarget:
    """Configuration for a deployment target."""

    device: DeviceInfo
    profile: str
    firmware_path: Optional[Path] = None
    flash_args: List[str] = field(default_factory=list)
    verify: bool = True
    reset_after: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format.

        Returns:
            Dictionary representation
        """
        return {
            "device": self.device.to_dict(),
            "profile": self.profile,
            "firmware_path": str(self.firmware_path) if self.firmware_path else None,
            "flash_args": self.flash_args,
            "verify": self.verify,
            "reset_after": self.reset_after,
        }


@dataclass
class DeploymentResult:
    """Result of a deployment operation."""

    target: DeploymentTarget
    status: DeploymentStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    error: Optional[str] = None
    logs: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format.

        Returns:
            Dictionary representation
        """
        return {
            "target": self.target.to_dict(),
            "status": self.status.value,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": (
                (self.end_time - self.start_time).total_seconds()
                if self.end_time
                else None
            ),
            "error": self.error,
            "logs": self.logs,
        }


class DeploymentOrchestrator:
    """Orchestrator for multi-device deployments."""

    def __init__(
        self,
        project_dir: Optional[Union[str, Path]] = None,
    ) -> None:
        """Initialize the deployment orchestrator.

        Args:
            project_dir: Project directory path
        """
        self.project_dir = Path(project_dir) if project_dir else Path.cwd()
        self.detector = DeviceDetector()
        self.profiles = ConanProfileManager(self.project_dir / "conan-profiles")
        self._targets: List[DeploymentTarget] = []
        self._results: List[DeploymentResult] = []

    def add_target(self, target: DeploymentTarget) -> None:
        """Add a deployment target.

        Args:
            target: Deployment target to add
        """
        self._targets.append(target)

    def clear_targets(self) -> None:
        """Clear all deployment targets."""
        self._targets.clear()

    def auto_detect_targets(
        self,
        device_filter: Optional[str] = None,
        default_profile: str = "esp32s3",
    ) -> List[DeploymentTarget]:
        """Auto-detect connected devices and create targets.

        Args:
            device_filter: Optional device type filter
            default_profile: Default profile to use

        Returns:
            List of detected deployment targets
        """
        devices = self.detector.detect_all()

        if device_filter:
            devices = [d for d in devices if d.device_type == device_filter]

        targets = []
        for device in devices:
            # Determine appropriate profile
            profile = self.profiles.get_profile(device.variant)
            if profile is None:
                profile = self.profiles.get_profile(device.device_type)

            profile_name = profile.name if profile else default_profile

            target = DeploymentTarget(
                device=device,
                profile=profile_name,
            )
            targets.append(target)
            self._targets.append(target)

        return targets

    async def deploy(
        self,
        device_filter: Optional[str] = None,
        mode: str = "sequential",
        dry_run: bool = False,
    ) -> str:
        """Deploy firmware to devices.

        Args:
            device_filter: Optional device type filter
            mode: Deployment mode ("sequential" or "parallel")
            dry_run: If True, simulate deployment without executing

        Returns:
            JSON string with deployment results
        """
        # Auto-detect targets if none configured
        if not self._targets:
            self.auto_detect_targets(device_filter)

        if not self._targets:
            return json.dumps({
                "status": "no_targets",
                "message": "No deployment targets found",
            })

        self._results.clear()

        if dry_run:
            return self._dry_run()

        deployment_mode = DeploymentMode(mode.lower())

        if deployment_mode == DeploymentMode.PARALLEL:
            await self._deploy_parallel()
        else:
            await self._deploy_sequential()

        return self._generate_report()

    async def _deploy_sequential(self) -> None:
        """Deploy to targets sequentially."""
        for target in self._targets:
            result = await self._deploy_target(target)
            self._results.append(result)

    async def _deploy_parallel(self) -> None:
        """Deploy to targets in parallel."""
        tasks = [self._deploy_target(target) for target in self._targets]
        self._results = await asyncio.gather(*tasks)

    async def _deploy_target(self, target: DeploymentTarget) -> DeploymentResult:
        """Deploy to a single target.

        Args:
            target: Deployment target

        Returns:
            Deployment result
        """
        result = DeploymentResult(
            target=target,
            status=DeploymentStatus.PENDING,
            start_time=datetime.now(),
        )

        try:
            # Build phase
            result.status = DeploymentStatus.BUILDING
            result.logs.append(f"Building for {target.profile}...")
            await self._build(target)

            # Flash phase
            result.status = DeploymentStatus.FLASHING
            result.logs.append(f"Flashing to {target.device.port}...")
            await self._flash(target)

            # Verify phase
            if target.verify:
                result.status = DeploymentStatus.VERIFYING
                result.logs.append("Verifying deployment...")
                await self._verify(target)

            result.status = DeploymentStatus.COMPLETED
            result.logs.append("Deployment completed successfully")

        except Exception as e:
            result.status = DeploymentStatus.FAILED
            result.error = str(e)
            result.logs.append(f"Deployment failed: {e}")
            logger.error(f"Deployment to {target.device.port} failed: {e}")

        finally:
            result.end_time = datetime.now()

        return result

    async def _build(self, target: DeploymentTarget) -> None:
        """Build firmware for target.

        Args:
            target: Deployment target
        """
        # In a real implementation, this would run the build system
        # For now, we just simulate it
        await asyncio.sleep(0.1)

        # Check if firmware exists
        if target.firmware_path and not target.firmware_path.exists():
            raise DeploymentError(
                f"Firmware not found: {target.firmware_path}",
                target=target.device.port,
                code=ErrorCode.BUILD_FAILED,
            )

    async def _flash(self, target: DeploymentTarget) -> None:
        """Flash firmware to target device.

        Args:
            target: Deployment target
        """
        # In a real implementation, this would use esptool or similar
        await asyncio.sleep(0.1)

        # Basic validation
        if not target.device.port:
            raise DeploymentError(
                "No device port specified",
                code=ErrorCode.FLASH_FAILED,
            )

    async def _verify(self, target: DeploymentTarget) -> None:
        """Verify deployment to target.

        Args:
            target: Deployment target
        """
        await asyncio.sleep(0.1)

    def _dry_run(self) -> str:
        """Generate dry-run report.

        Returns:
            JSON string with dry-run results
        """
        result = {
            "status": "dry_run",
            "targets": [
                {
                    "device": t.device.to_dict(),
                    "profile": t.profile,
                    "actions": ["build", "flash", "verify" if t.verify else "skip_verify"],
                }
                for t in self._targets
            ],
        }
        return json.dumps(result, indent=2)

    def _generate_report(self) -> str:
        """Generate deployment report.

        Returns:
            JSON string with deployment report
        """
        successful = sum(1 for r in self._results if r.status == DeploymentStatus.COMPLETED)
        failed = sum(1 for r in self._results if r.status == DeploymentStatus.FAILED)

        report = {
            "summary": {
                "total": len(self._results),
                "successful": successful,
                "failed": failed,
            },
            "results": [r.to_dict() for r in self._results],
        }
        return json.dumps(report, indent=2)

    def get_results(self) -> List[DeploymentResult]:
        """Get deployment results.

        Returns:
            List of deployment results
        """
        return self._results.copy()
