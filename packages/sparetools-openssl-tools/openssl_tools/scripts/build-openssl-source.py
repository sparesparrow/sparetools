#!/usr/bin/env python3
"""Build OpenSSL from an in-tree source checkout using hybrid builder helpers."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path
from typing import Optional

from ..openssl.hybrid_builder import HybridBuildConfig, run_hybrid_build


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, help="Path to OpenSSL source checkout")
    parser.add_argument("--target", required=True, help="OpenSSL Configure target (e.g. linux-x86_64)")
    parser.add_argument("--install-prefix", required=True, help="Destination directory for install_sw output")
    parser.add_argument("--jobs", type=int, default=os.cpu_count() or 1, help="Parallel build jobs")
    parser.add_argument("--shared", action="store_true", help="Build shared libraries")
    parser.add_argument("--enable-fips", action="store_true", help="Enable FIPS provider build")
    parser.add_argument("--log-dir", help="Directory to write build logs (JSON summary + stdout)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_dir = Path(args.source).resolve()
    install_prefix = Path(args.install_prefix).resolve()
    install_prefix.mkdir(parents=True, exist_ok=True)

    config = HybridBuildConfig(
        source_dir=source_dir,
        install_prefix=install_prefix,
        openssl_target=args.target,
        shared=bool(args.shared),
        enable_fips=bool(args.enable_fips),
        jobs=args.jobs,
    )

    started = dt.datetime.utcnow()
    run_hybrid_build(config)
    finished = dt.datetime.utcnow()

    if args.log_dir:
        log_dir = Path(args.log_dir).resolve()
        log_dir.mkdir(parents=True, exist_ok=True)
        summary_path = log_dir / f"build-summary-{started.strftime('%Y%m%d-%H%M%S')}.json"
        summary = {
            "source": str(source_dir),
            "install_prefix": str(install_prefix),
            "target": args.target,
            "shared": bool(args.shared),
            "enable_fips": bool(args.enable_fips),
            "jobs": args.jobs,
            "started": started.isoformat() + "Z",
            "finished": finished.isoformat() + "Z",
            "duration_seconds": (finished - started).total_seconds(),
        }
        summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

