"""Utilities for the hybrid (Perl + Python) OpenSSL build flow."""

from __future__ import annotations

import logging
import os
import shutil
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Mapping, Optional, Sequence

from ..execute_command import execute_command
from .provider_ordering import ProviderOrderer, get_provider_exclusions_for_version

LOG = logging.getLogger(__name__)


@dataclass(slots=True)
class HybridBuildConfig:
    """Configuration for the hybrid OpenSSL build helper."""

    source_dir: Path
    install_prefix: Path
    openssl_target: str
    shared: bool = True
    enable_fips: bool = False
    configure_args: Sequence[str] = ()
    perl_executable: str = "perl"
    python_executable: str = "python3"
    jobs: Optional[int] = None
    environment: Optional[Mapping[str, str]] = None
    configure_script: Optional[Path] = None
    run_tests: bool = True
    openssl_version: str = "3.6.0"  # For provider ordering
    enable_legacy: bool = False  # Enable legacy provider


def run_hybrid_build(config: HybridBuildConfig) -> None:
    """Execute the four-stage hybrid build.

    1. Provider ordering analysis (OpenSSL 3.6+)
    2. Perl Configure (authoritative dependency ordering)
    3. Python enhancement script (optional)
    4. make / make test / make install_sw
    """

    _analyze_provider_ordering(config)
    _run_perl_configure(config)
    _run_python_enhancement(config)
    _run_make_targets(config)


def _analyze_provider_ordering(config: HybridBuildConfig) -> None:
    """Analyze and optimize provider build order for OpenSSL 3.6+."""
    LOG.info("Analyzing provider dependencies for OpenSSL %s", config.openssl_version)
    
    # Get recommended exclusions
    exclusions = get_provider_exclusions_for_version(config.openssl_version)
    
    # Create provider orderer
    orderer = ProviderOrderer(
        openssl_version=config.openssl_version,
        enable_fips=config.enable_fips,
        enable_legacy=config.enable_legacy,
        excluded_algorithms=exclusions
    )
    
    # Get build order
    build_order = orderer.get_build_order()
    LOG.info("Provider build order: %s", " -> ".join(build_order))
    
    # Validate provider availability
    availability = orderer.validate_provider_availability(str(config.source_dir))
    missing = [name for name, avail in availability.items() if not avail]
    if missing:
        LOG.warning("Missing provider sources: %s", ", ".join(missing))
    
    # Generate Makefile fragment for provider dependencies
    makefile_fragment = orderer.get_make_dependencies()
    fragment_path = config.source_dir / "providers.mk"
    with open(fragment_path, "w") as f:
        f.write(makefile_fragment)
    LOG.info("Provider Makefile fragment written to %s", fragment_path)


def _run_perl_configure(config: HybridBuildConfig) -> None:
    args = [config.openssl_target]

    if config.shared:
        args.append("shared")
    else:
        args.append("no-shared")

    if not config.shared:
        args.append("no-pic")

    if config.enable_fips:
        args.append("enable-fips")

    args.extend(config.configure_args)
    args.extend(
        [
            f"--prefix={config.install_prefix}",
            f"--openssldir={config.install_prefix / 'ssl'}",
        ]
    )

    command = " ".join([config.perl_executable, "Configure", *args])
    LOG.info("Hybrid build: running Perl Configure with target %s", config.openssl_target)
    _run(command, cwd=config.source_dir, env=config.environment)


def _run_python_enhancement(config: HybridBuildConfig) -> None:
    script = config.configure_script or _ensure_configure_script(config.source_dir)
    if not script.exists():
        LOG.warning("Hybrid build: configure.py not found at %s, skipping enhancement stage", script)
        return

    command = f"{config.python_executable} {script} enhance --makefile-only"
    LOG.info("Hybrid build: executing Python enhancement script %s", script)
    _run(command, cwd=config.source_dir, env=config.environment, ignore_errors=True)


def _run_make_targets(config: HybridBuildConfig) -> None:
    jobs_flag = f"-j{config.jobs}" if config.jobs else ""

    make_command = "make" if os.name != "nt" else "nmake"

    build_cmd = " ".join(filter(None, [make_command, jobs_flag]))
    LOG.info("Hybrid build: compiling with %s", build_cmd.strip())
    _run(build_cmd, cwd=config.source_dir, env=config.environment)

    if config.run_tests:
        LOG.info("Hybrid build: running test suite (best effort)")
        _run(f"{make_command} test", cwd=config.source_dir, env=config.environment, ignore_errors=True)

    LOG.info("Hybrid build: installing to %s", config.install_prefix)
    _run(f"{make_command} install_sw", cwd=config.source_dir, env=config.environment)


def _run(command: str, *, cwd: Path, env: Optional[Mapping[str, str]], ignore_errors: bool = False) -> None:
    rc, output = execute_command(command, cwd=cwd, env=env)
    if rc != 0 and not ignore_errors:
        raise RuntimeError(f"Command failed ({rc}): {command}\nOutput: {os.linesep.join(output)}")


def _ensure_configure_script(source_dir: Path) -> Path:
    """Ensure the hybrid configure.py script exists in the source directory."""

    destination = source_dir / "configure.py"
    if destination.exists():
        return destination

    try:
        with resources.as_file(
            resources.files("openssl_tools.openssl") / "hybrid_configure.py"
        ) as packaged_script:
            LOG.info("Hybrid build: deploying packaged configure.py to %s", destination)
            shutil.copy2(packaged_script, destination)
    except FileNotFoundError:
        LOG.warning("Hybrid build: packaged configure.py not found; skipping enhancement stage")

    return destination
