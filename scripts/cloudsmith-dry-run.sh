#!/usr/bin/env bash
set -euo pipefail

echo "[dry-run] Building sparetools packages before upload..."
conan create packages/sparetools-base --version=1.1.0 --build=missing
conan create packages/sparetools-cpython --version=3.12.7 --build=missing
conan create packages/sparetools-openssl-tools --version=1.1.0 --build=missing
conan create packages/sparetools-openssl --version=3.3.2 --build=missing

echo "[dry-run] Simulating upload to Cloudsmith"
conan upload "sparetools-*/*" -r sparesparrow-conan --dry-run --confirm

