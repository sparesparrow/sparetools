#!/usr/bin/env bash
set -euo pipefail

echo "[devcontainer] Installing Trivy repository..."
apt-get update
apt-get install -y wget gnupg apt-transport-https lsb-release
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | gpg --dearmor -o /usr/share/keyrings/trivy.gpg
echo "deb [signed-by=/usr/share/keyrings/trivy.gpg] https://aquasecurity.github.io/trivy-repo/deb stable main" > /etc/apt/sources.list.d/trivy.list
apt-get update
apt-get install -y trivy

echo "[devcontainer] Installing Syft..."
curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin

echo "[devcontainer] Initialising Conan cache..."
conan profile detect || true
conan config set general.revisions_enabled=1

echo "[devcontainer] Setup complete."

