#!/usr/bin/env python3
"""Aggregate JSON build summaries produced by matrix tasks."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Dict, List


def read_summaries(log_dir: Path) -> List[Dict]:
    summaries: List[Dict] = []
    for path in sorted(log_dir.glob("build-summary-*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            data["_path"] = str(path)
            summaries.append(data)
        except json.JSONDecodeError:
            continue
    return summaries


def format_summary(summary: Dict) -> str:
    duration = summary.get("duration_seconds", 0)
    target = summary.get("target", "unknown")
    shared = "shared" if summary.get("shared") else "static"
    fips = "fips" if summary.get("enable_fips") else "std"
    install_prefix = summary.get("install_prefix", "")
    return (
        f"[{summary.get('finished', '?')}] target={target} ({shared}/{fips}) "
        f"jobs={summary.get('jobs')} duration={duration:.1f}s -> {install_prefix}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log_dir", help="Directory containing build-summary-*.json files")
    parser.add_argument("--follow", action="store_true", help="Stream summaries in real-time")
    parser.add_argument("--interval", type=float, default=5.0, help="Polling interval when following")
    args = parser.parse_args()

    log_dir = Path(args.log_dir).expanduser().resolve()
    if not log_dir.exists():
        raise SystemExit(f"Log directory not found: {log_dir}")

    seen: set[str] = set()

    def emit_new() -> None:
        for summary in read_summaries(log_dir):
            path = summary.get("_path")
            if path in seen:
                continue
            seen.add(path)
            print(format_summary(summary))

    emit_new()
    if args.follow:
        try:
            while True:
                time.sleep(args.interval)
                emit_new()
        except KeyboardInterrupt:
            pass

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

