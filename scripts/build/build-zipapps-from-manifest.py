#!/usr/bin/env python3
"""
Build all SpareTools zipapps from manifest

Reads the zipapps.yaml manifest file and builds all defined zipapps
using the build-zipapp.py script.
"""

import argparse
import os
import sys
import subprocess
import yaml
from pathlib import Path
from typing import Dict, List, Any


def print_status(msg):
    """Print status message."""
    print(f"[BUILD-ALL] {msg}", flush=True)


def print_error(msg):
    """Print error message."""
    print(f"[ERROR] {msg}", file=sys.stderr, flush=True)


def load_manifest(manifest_path: Path) -> List[Dict[str, Any]]:
    """Load zipapp manifest from YAML file."""
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest file not found: {manifest_path}")

    with open(manifest_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    if 'zipapps' not in data:
        raise ValueError("Manifest must contain a 'zipapps' key")

    return data['zipapps']


def build_zipapp(zipapp_config: Dict[str, Any], build_script_path: Path, output_dir: Path) -> bool:
    """Build a single zipapp using the build-zipapp.py script."""
    name = zipapp_config.get('name', 'unknown')
    source = zipapp_config.get('source')
    output = zipapp_config.get('output')
    main = zipapp_config.get('main')
    bundle_deps = zipapp_config.get('bundle_deps', [])
    exclude = zipapp_config.get('exclude', [])
    description = zipapp_config.get('description', '')

    if not source:
        print_error(f"Zipapp '{name}': missing 'source' field")
        return False

    if not output:
        print_error(f"Zipapp '{name}': missing 'output' field")
        return False

    print_status(f"Building {name}: {description}")

    # Construct command for build-zipapp.py
    cmd = [
        sys.executable, str(build_script_path),
        source,
        "-o", str(output_dir / output)
    ]

    # Add optional arguments
    if main:
        cmd.extend(["-m", main])

    if bundle_deps:
        cmd.extend(["--bundle-deps"] + bundle_deps)

    if exclude:
        for pattern in exclude:
            cmd.extend(["--exclude", pattern])

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print_status(f"✓ Built {output}")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"✗ Failed to build {name}")
        print_error(f"Command: {' '.join(cmd)}")
        print_error(f"Error: {e.stderr}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Build all SpareTools zipapps from manifest",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Build all zipapps to current directory
  python build-zipapps-from-manifest.py

  # Build to specific output directory
  python build-zipapps-from-manifest.py -o ../dist

  # Build specific zipapps
  python build-zipapps-from-manifest.py --names sparetools-bootstrap sparetools-audit-conan
        """
    )

    parser.add_argument(
        "-m", "--manifest",
        type=Path,
        default=Path(__file__).parent / "zipapps.yaml",
        help="Path to zipapps manifest YAML file"
    )

    parser.add_argument(
        "-o", "--output-dir",
        type=Path,
        default=Path.cwd(),
        help="Output directory for built zipapps"
    )

    parser.add_argument(
        "--names",
        nargs="+",
        metavar="NAME",
        help="Only build specific zipapps by name"
    )

    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continue building other zipapps if one fails"
    )

    args = parser.parse_args()

    # Find the build-zipapp.py script
    build_script_path = Path(__file__).parent / "build-zipapp.py"
    if not build_script_path.exists():
        print_error(f"build-zipapp.py not found at: {build_script_path}")
        sys.exit(1)

    # Load manifest
    try:
        zipapps = load_manifest(args.manifest)
        print_status(f"Loaded {len(zipapps)} zipapp definitions from {args.manifest}")
    except Exception as e:
        print_error(f"Failed to load manifest: {e}")
        sys.exit(1)

    # Filter zipapps if names specified
    if args.names:
        name_set = set(args.names)
        zipapps = [z for z in zipapps if z.get('name') in name_set]
        if not zipapps:
            print_error(f"No zipapps found matching names: {args.names}")
            sys.exit(1)
        print_status(f"Filtered to {len(zipapps)} zipapps: {', '.join(z.get('name', 'unknown') for z in zipapps)}")

    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Build each zipapp
    built = 0
    failed = 0

    for zipapp_config in zipapps:
        success = build_zipapp(zipapp_config, build_script_path, args.output_dir)
        if success:
            built += 1
        else:
            failed += 1
            if not args.continue_on_error:
                print_error("Stopping due to build failure (use --continue-on-error to continue)")
                sys.exit(1)

    # Summary
    print_status("=" * 50)
    print_status(f"Build Summary: {built} built, {failed} failed")
    if failed > 0:
        print_error(f"Total zipapps: {len(zipapps)} (failed: {failed})")
        sys.exit(1)
    else:
        print_status(f"All {built} zipapps built successfully")
        print_status(f"Output directory: {args.output_dir}")


if __name__ == "__main__":
    main()

